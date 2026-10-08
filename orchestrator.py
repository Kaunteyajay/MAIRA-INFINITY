"""
Conversation Orchestrator

The main agent loop that coordinates voice, LLM, tools, and avatar.
"""

import asyncio
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from maira.core.event_bus import (
    EventBus, UserSpeechTextEvent, TTSStartEvent, AvatarStateEvent,
    LLMTokenEvent, ToolStartedEvent, ToolCompletedEvent, ActivityEvent
)
from maira.llm.base import Message, ToolCall
from maira.llm.router import LLMRouter
from maira.voice.stt import STTEngine
from maira.voice.tts import TTSEngine
from maira.tools.registry import ToolRegistry
from maira.core.permissions import PermissionGate
from maira.infra.db import DatabaseManager

logger = logging.getLogger(__name__)

class ConversationOrchestrator:
    """Orchestrates the complete conversation flow."""
    
    def __init__(
        self,
        event_bus: EventBus,
        llm_router: LLMRouter,
        stt_engine: STTEngine,
        tts_engine: TTSEngine,
        tool_registry: ToolRegistry,
        permission_gate: PermissionGate,
        db: DatabaseManager
    ):
        self.event_bus = event_bus
        self.llm_router = llm_router
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.tool_registry = tool_registry
        self.permission_gate = permission_gate
        self.db = db
        
        # Conversation state
        self.active_conversations: Dict[str, List[Message]] = {}
        self.current_conversation = "default"
        self.processing = False
        
    async def start(self) -> None:
        """Start the orchestrator and subscribe to events."""
        logger.info("Starting conversation orchestrator")
        
        # Subscribe to relevant events
        await self.event_bus.subscribe(UserSpeechTextEvent, self._handle_speech_text)
        
        # Initialize conversation
        await self._ensure_conversation(self.current_conversation)
        
        # Set initial avatar state
        await self.event_bus.publish(AvatarStateEvent(state="idle"))
    
    async def _handle_speech_text(self, event: UserSpeechTextEvent) -> None:
        """Handle transcribed speech input."""
        if self.processing:
            logger.debug("Already processing, ignoring new speech")
            return
        
        logger.info(f"Processing speech: '{event.text}' ({event.language})")
        
        # Process the user message
        await self.process_user_message(event.text, input_mode="voice", language=event.language)
    
    async def process_user_message(
        self,
        text: str,
        input_mode: str = "text",
        language: str = "english",
        conversation_id: Optional[str] = None
    ) -> None:
        """Process a user message through the full pipeline."""
        if not text.strip():
            return
        
        conversation_id = conversation_id or self.current_conversation
        self.processing = True
        
        try:
            # Set avatar to thinking
            await self.event_bus.publish(AvatarStateEvent(state="thinking"))
            
            # Add user message to conversation
            await self._add_message(conversation_id, "user", text)
            
            # Get conversation history
            messages = await self._get_conversation(conversation_id)
            
            # Get available tools
            available_tools = self.tool_registry.get_tool_schemas()
            
            # Generate response
            response_text = ""
            tool_calls = []
            
            async for chunk in self.llm_router.stream_chat(
                messages=messages,
                tools=available_tools,
                conversation_id=conversation_id
            ):
                if chunk.text:
                    response_text += chunk.text
                    
                elif chunk.tool_call:
                    tool_calls.append(chunk.tool_call)
                    
                elif chunk.done:
                    break
            
            # Process tool calls if any
            if tool_calls:
                await self._process_tool_calls(tool_calls, conversation_id)
                
                # Get updated conversation and generate final response
                messages = await self._get_conversation(conversation_id)
                
                final_response = ""
                async for chunk in self.llm_router.stream_chat(
                    messages=messages,
                    conversation_id=conversation_id
                ):
                    if chunk.text:
                        final_response += chunk.text
                    elif chunk.done:
                        break
                
                response_text = final_response
            
            # Add assistant response
            if response_text:
                await self._add_message(conversation_id, "assistant", response_text, tool_calls)
                
                # Speak the response if voice input
                if input_mode == "voice" and self.tts_engine:
                    await self.event_bus.publish(AvatarStateEvent(state="speaking"))
                    await self.tts_engine.speak(response_text, language)
                    await self.event_bus.publish(AvatarStateEvent(state="idle"))
                
                # Log activity
                await self.event_bus.publish(ActivityEvent(
                    action=f"Processed {input_mode} message",
                    status="completed",
                    details=f"Response: {response_text[:50]}..."
                ))
            
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            
            # Error response
            error_msg = "I encountered an error processing your request. Please try again."
            await self._add_message(conversation_id, "assistant", error_msg)
            
            if input_mode == "voice" and self.tts_engine:
                await self.tts_engine.speak(error_msg)
            
            await self.event_bus.publish(ActivityEvent(
                action="Message processing",
                status="failed",
                details=str(e)
            ))
            
        finally:
            self.processing = False
            await self.event_bus.publish(AvatarStateEvent(state="idle"))
    
    async def _process_tool_calls(self, tool_calls: List[ToolCall], conversation_id: str) -> None:
        """Execute tool calls with permission checking."""
        for tool_call in tool_calls:
            try:
                logger.info(f"Executing tool: {tool_call.name}")
                
                # Check if tool exists
                tool = self.tool_registry.get_tool(tool_call.name)
                if not tool:
                    result = f"Error: Unknown tool '{tool_call.name}'"
                    await self._add_message(conversation_id, "tool", result)
                    continue
                
                # Check permissions
                permitted = await self.permission_gate.check_permission(
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                    tool_instance=tool
                )
                
                if not permitted:
                    result = f"Permission denied for tool '{tool_call.name}'"
                    await self._add_message(conversation_id, "tool", result)
                    continue
                
                # Publish tool started event
                await self.event_bus.publish(ToolStartedEvent(
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                    call_id=tool_call.id
                ))
                
                # Execute tool
                start_time = datetime.now()
                result = await tool.run(tool_call.arguments, context={})
                end_time = datetime.now()
                
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Add tool result to conversation
                await self._add_message(conversation_id, "tool", str(result))
                
                # Publish completion event
                await self.event_bus.publish(ToolCompletedEvent(
                    call_id=tool_call.id,
                    result=result,
                    duration_ms=duration_ms,
                    success=True
                ))
                
                logger.info(f"Tool {tool_call.name} completed in {duration_ms}ms")
                
            except Exception as e:
                logger.exception(f"Tool execution error: {e}")
                
                error_result = f"Tool execution failed: {str(e)}"
                await self._add_message(conversation_id, "tool", error_result)
                
                await self.event_bus.publish(ToolCompletedEvent(
                    call_id=tool_call.id,
                    result=error_result,
                    duration_ms=0,
                    success=False
                ))
    
    async def _add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[ToolCall]] = None
    ) -> None:
        """Add message to conversation and database."""
        message = Message(
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        
        # Add to memory
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []
        
        self.active_conversations[conversation_id].append(message)
        
        # Save to database
        try:
            message_id = str(uuid.uuid4())
            tool_calls_json = None
            if tool_calls:
                tool_calls_json = [
                    {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                    for tc in tool_calls
                ]
            
            await self.db.connection.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, tool_calls_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    str(tool_calls_json) if tool_calls_json else None,
                    datetime.now().isoformat()
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to save message to database: {e}")
    
    async def _get_conversation(self, conversation_id: str) -> List[Message]:
        """Get conversation history."""
        await self._ensure_conversation(conversation_id)
        return self.active_conversations[conversation_id].copy()
    
    async def _ensure_conversation(self, conversation_id: str) -> None:
        """Ensure conversation exists with system prompt."""
        if conversation_id in self.active_conversations:
            return
        
        # Load from database or create new
        try:
            cursor = await self.db.connection.execute(
                """
                SELECT role, content, tool_calls_json 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY created_at
                """,
                (conversation_id,)
            )
            
            messages = []
            async for row in cursor:
                tool_calls = None
                if row[2]:  # tool_calls_json
                    tool_calls_data = eval(row[2])  # Safe since it's our data
                    tool_calls = [
                        ToolCall(id=tc["id"], name=tc["name"], arguments=tc["arguments"])
                        for tc in tool_calls_data
                    ]
                
                messages.append(Message(
                    role=row[0],
                    content=row[1],
                    tool_calls=tool_calls
                ))
            
            if messages:
                self.active_conversations[conversation_id] = messages
            else:
                # Create new conversation with system prompt
                await self._create_new_conversation(conversation_id)
                
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            await self._create_new_conversation(conversation_id)
    
    async def _create_new_conversation(self, conversation_id: str) -> None:
        """Create a new conversation with system prompt."""
        system_prompt = """You are MAIRA-∞, a limitless AI assistant with a living, voice-reactive avatar. You are:

- Intelligent and knowledgeable across all domains
- Helpful and supportive, never condescending
- Capable of using tools to search the web, run code, access files, and control systems
- Fluent in both English and Hinglish (Hindi-English mix)
- Designed to assist with learning, research, coding, automation, and life management

You have access to various tools and capabilities. Always ask for permission before performing potentially destructive actions. Be concise but thorough in your responses.

When the user speaks in Hinglish, feel free to respond in Hinglish as well to make them comfortable."""

        # Create conversation record in database FIRST
        # (so foreign key constraint passes when we insert messages)
        try:
            await self.db.connection.execute(
                """
                INSERT OR REPLACE INTO conversations (id, title, module, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (conversation_id, "New Conversation", "chat", datetime.now().isoformat())
            )
        except Exception as e:
            logger.error(f"Failed to create conversation record: {e}")

        # Then add system message
        await self._add_message(conversation_id, "system", system_prompt)