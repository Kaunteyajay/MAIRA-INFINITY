"""
Base LLM Types and Interfaces

Provider-neutral types for messages, tool calls, and streaming.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, AsyncIterator, Protocol
from enum import Enum

@dataclass
class Message:
    """Standardized message format across providers."""
    role: str  # system, user, assistant, tool
    content: str
    tool_calls: Optional[List["ToolCall"]] = None
    attachments: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class ToolCall:
    """Standardized tool call format."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class StreamChunk:
    """Streaming response chunk."""
    text: str = ""
    tool_call: Optional[ToolCall] = None
    done: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class LLMProvider(Protocol):
    """Interface that all LLM providers must implement."""
    
    name: str
    supports_tools: bool
    supports_vision: bool
    
    async def stream_chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream chat completion."""
        ...
    
    async def count_tokens(self, messages: List[Message], model: Optional[str] = None) -> int:
        """Count tokens for cost estimation."""
        ...
    
    def get_models(self) -> List[str]:
        """Get available models."""
        ...

class ProviderError(Exception):
    """Base exception for provider errors."""
    pass

class RateLimitError(ProviderError):
    """Rate limit exceeded."""
    pass

class AuthError(ProviderError):
    """Authentication error."""
    pass

class ModelNotFoundError(ProviderError):
    """Model not available."""
    pass