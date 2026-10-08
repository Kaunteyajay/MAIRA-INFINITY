"""
Anthropic Claude Provider

Integration with Claude models via the Anthropic API.
"""

import json
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
import anthropic
from anthropic.types import MessageParam, ToolUseBlock

from maira.llm.base import (
    LLMProvider, Message, ToolCall, StreamChunk, 
    ProviderError, RateLimitError, AuthError, ModelNotFoundError
)

logger = logging.getLogger(__name__)

class ClaudeProvider:
    """Claude LLM provider."""
    
    name = "claude"
    supports_tools = True
    supports_vision = True
    
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.default_model = "claude-3-5-sonnet-20241022"
        
    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream chat completion with Claude."""
        try:
            # Convert to Claude format
            claude_messages = self._convert_messages(messages)
            claude_tools = self._convert_tools(tools) if tools else None
            
            # Extract system message
            system_message = None
            if claude_messages and claude_messages[0].get("role") == "system":
                system_message = claude_messages.pop(0)["content"]
            
            # Stream request
            stream = await self.client.messages.create(
                model=model or self.default_model,
                messages=claude_messages,
                tools=claude_tools,
                system=system_message,
                max_tokens=4000,
                stream=True,
                **kwargs
            )
            
            current_tool_call = None
            
            async for event in stream:
                if event.type == "message_start":
                    continue
                elif event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        current_tool_call = ToolCall(
                            id=event.content_block.id,
                            name=event.content_block.name,
                            arguments={}
                        )
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield StreamChunk(text=event.delta.text)
                    elif event.delta.type == "input_json_delta":
                        # Accumulate partial JSON string, parse only at block_stop
                        if current_tool_call:
                            if not hasattr(current_tool_call, '_raw_json'):
                                current_tool_call._raw_json = ""
                            current_tool_call._raw_json += event.delta.partial_json
                elif event.type == "content_block_stop":
                    if current_tool_call:
                        raw = getattr(current_tool_call, '_raw_json', '{}')
                        try:
                            current_tool_call.arguments = json.loads(raw) if raw else {}
                        except json.JSONDecodeError:
                            current_tool_call.arguments = {}
                        yield StreamChunk(tool_call=current_tool_call)
                        current_tool_call = None
                elif event.type == "message_stop":
                    yield StreamChunk(done=True)
                    
        except anthropic.RateLimitError as e:
            raise RateLimitError(f"Claude rate limit: {e}")
        except anthropic.AuthenticationError as e:
            raise AuthError(f"Claude auth error: {e}")
        except anthropic.NotFoundError as e:
            raise ModelNotFoundError(f"Claude model not found: {e}")
        except Exception as e:
            raise ProviderError(f"Claude error: {e}")
    
    def _convert_messages(self, messages: List[Message]) -> List[MessageParam]:
        """Convert to Claude message format."""
        claude_messages = []
        
        for msg in messages:
            # Handle tool results
            if msg.role == "tool":
                # Tool result should be part of previous assistant message
                if claude_messages and claude_messages[-1]["role"] == "assistant":
                    # Add tool result to previous message
                    if "tool_calls" in claude_messages[-1]:
                        claude_messages.append({
                            "role": "user",
                            "content": [{"type": "tool_result", "content": msg.content}]
                        })
                continue
                
            content = msg.content
            
            # Add tool calls if present
            if msg.tool_calls:
                content_blocks = [{"type": "text", "text": content}]
                for tool_call in msg.tool_calls:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.name,
                        "input": tool_call.arguments
                    })
                content = content_blocks
            
            claude_messages.append({
                "role": msg.role,
                "content": content
            })
        
        return claude_messages
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert tools to Claude format."""
        claude_tools = []
        
        for tool in tools:
            claude_tools.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["parameters"]
            })
        
        return claude_tools
    
    async def count_tokens(self, messages: List[Message], model: Optional[str] = None) -> int:
        """Estimate token count."""
        # Rough estimation - Claude doesn't provide exact token counting
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4  # Rough token estimate
    
    def get_models(self) -> List[str]:
        """Get available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022", 
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]