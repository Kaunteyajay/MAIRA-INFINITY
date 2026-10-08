"""
Ollama Provider

Local LLM inference using Ollama.
"""

import json
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
import httpx

from maira.llm.base import (
    LLMProvider, Message, ToolCall, StreamChunk,
    ProviderError, ModelNotFoundError
)

logger = logging.getLogger(__name__)

class OllamaProvider:
    """Ollama local LLM provider."""
    
    name = "ollama"
    supports_tools = False  # Limited tool support in Ollama
    supports_vision = False  # Depends on model
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.default_model = "llama3.2:3b"  # Lightweight default
        
    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream chat with Ollama."""
        try:
            # Convert messages to Ollama format
            ollama_messages = self._convert_messages(messages)
            
            # Prepare request
            payload = {
                "model": model or self.default_model,
                "messages": ollama_messages,
                "stream": True,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "stop": kwargs.get("stop", [])
                }
            }
            
            # Add tool prompt if tools provided (basic implementation)
            if tools:
                system_prompt = self._create_tool_prompt(tools)
                payload["messages"].insert(0, {
                    "role": "system",
                    "content": system_prompt
                })
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.atext()
                        raise ProviderError(f"Ollama error {response.status_code}: {error_text}")
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                
                                if chunk.get("done", False):
                                    yield StreamChunk(done=True)
                                else:
                                    content = chunk.get("message", {}).get("content", "")
                                    if content:
                                        # Basic tool call detection for Ollama
                                        tool_call = self._extract_tool_call(content)
                                        if tool_call:
                                            yield StreamChunk(tool_call=tool_call)
                                        else:
                                            yield StreamChunk(text=content)
                                            
                            except json.JSONDecodeError as e:
                                logger.warning(f"Invalid JSON from Ollama: {line}")
                                continue
                                
        except httpx.ConnectError:
            raise ProviderError("Cannot connect to Ollama. Is it running on localhost:11434?")
        except Exception as e:
            raise ProviderError(f"Ollama error: {e}")
    
    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Convert to Ollama message format."""
        ollama_messages = []
        
        for msg in messages:
            if msg.role == "tool":
                # Convert tool result to user message
                ollama_messages.append({
                    "role": "user",
                    "content": f"Tool result: {msg.content}"
                })
            else:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return ollama_messages
    
    def _create_tool_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Create system prompt for tool usage."""
        tool_descriptions = []
        
        for tool in tools:
            tool_descriptions.append(
                f"- {tool['name']}: {tool['description']}\n"
                f"  Parameters: {json.dumps(tool['parameters'], indent=2)}"
            )
        
        return f"""You have access to the following tools:

{chr(10).join(tool_descriptions)}

To use a tool, respond with:
TOOL_CALL: {{"name": "tool_name", "arguments": {{"param": "value"}}}}

Always provide the tool call in this exact format."""
    
    def _extract_tool_call(self, content: str) -> Optional[ToolCall]:
        """Extract tool call from response (basic implementation)."""
        if "TOOL_CALL:" in content:
            try:
                # Extract JSON after TOOL_CALL:
                start = content.find("TOOL_CALL:") + len("TOOL_CALL:")
                json_str = content[start:].strip()
                
                # Find the JSON object
                brace_count = 0
                end_pos = 0
                for i, char in enumerate(json_str):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                
                if end_pos > 0:
                    tool_data = json.loads(json_str[:end_pos])
                    return ToolCall(
                        id=f"call_{hash(content) % 10000}",
                        name=tool_data["name"],
                        arguments=tool_data["arguments"]
                    )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse tool call: {e}")
        
        return None
    
    async def count_tokens(self, messages: List[Message], model: Optional[str] = None) -> int:
        """Rough token estimation for local models."""
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4  # Rough estimate
    
    def get_models(self) -> List[str]:
        """Get available Ollama models."""
        # Common lightweight models for local use
        return [
            "llama3.2:3b",
            "llama3.2:1b", 
            "phi3:mini",
            "gemma2:2b",
            "qwen2.5:3b",
            "mistral:7b"
        ]
    
    async def check_connection(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False