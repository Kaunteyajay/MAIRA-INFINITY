"""
Event Bus - Core Communication System

Typed publish/subscribe system for decoupling components.
All events are dataclasses for type safety and IDE support.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Set, Type, TypeVar, Union

logger = logging.getLogger(__name__)

# Event type variable
EventType = TypeVar('EventType')

@dataclass(kw_only=True)
class BaseEvent:
    """Base class for all events with timestamp."""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# System Events
@dataclass
class SystemMetricsEvent(BaseEvent):
    """System performance metrics update."""
    cpu_percent: float
    memory_percent: float
    gpu_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int

@dataclass
class ApplicationStatusEvent(BaseEvent):
    """Application status change."""
    status: str  # "online", "offline", "thinking", "listening", "error"
    message: str = ""

# Voice Events
@dataclass
class UserSpeechStartEvent(BaseEvent):
    """User started speaking."""
    pass

@dataclass
class UserSpeechEndEvent(BaseEvent):
    """User stopped speaking."""
    duration_ms: int

@dataclass
class UserSpeechTextEvent(BaseEvent):
    """User speech transcribed to text."""
    text: str
    language: str
    confidence: float

@dataclass
class TTSStartEvent(BaseEvent):
    """Text-to-speech started."""
    text: str
    voice: str

@dataclass
class TTSAudioEvent(BaseEvent):
    """Text-to-speech audio chunk."""
    audio_level: float  # 0.0 to 1.0
    viseme: str = ""  # Mouth shape for lip-sync

@dataclass
class TTSEndEvent(BaseEvent):
    """Text-to-speech finished."""
    duration_ms: int

# Avatar Events
@dataclass
class AvatarStateEvent(BaseEvent):
    """Avatar state change."""
    state: str  # "idle", "listening", "thinking", "speaking", "sleeping"
    emotion: str = "neutral"  # "happy", "curious", "concerned"

# LLM Events
@dataclass
class LLMRequestEvent(BaseEvent):
    """LLM request started."""
    provider: str
    model: str
    conversation_id: str

@dataclass
class LLMTokenEvent(BaseEvent):
    """LLM token received (streaming)."""
    token: str
    conversation_id: str

@dataclass
class LLMToolCallEvent(BaseEvent):
    """LLM tool call detected."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str
    conversation_id: str

@dataclass
class LLMResponseEvent(BaseEvent):
    """LLM response completed."""
    text: str
    tokens_used: int
    provider: str
    conversation_id: str

# Tool Events
@dataclass
class ToolStartedEvent(BaseEvent):
    """Tool execution started."""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str

@dataclass
class ToolProgressEvent(BaseEvent):
    """Tool execution progress."""
    call_id: str
    progress: float  # 0.0 to 1.0
    message: str = ""

@dataclass
class ToolCompletedEvent(BaseEvent):
    """Tool execution completed."""
    call_id: str
    result: Any
    duration_ms: int
    success: bool

# Task Events
@dataclass
class TaskCreatedEvent(BaseEvent):
    """Background task created."""
    task_id: str
    title: str
    task_type: str

@dataclass
class TaskProgressEvent(BaseEvent):
    """Background task progress."""
    task_id: str
    progress: float  # 0.0 to 1.0
    eta_seconds: int = 0
    message: str = ""

@dataclass
class TaskCompletedEvent(BaseEvent):
    """Background task completed."""
    task_id: str
    success: bool
    result: Any = None
    error: str = ""

# Activity Events
@dataclass
class ActivityEvent(BaseEvent):
    """Activity log entry."""
    action: str
    status: str  # "completed", "failed", "rendering", "opened", "sources_found"
    details: str = ""
    icon: str = ""

# Permission Events
@dataclass
class PermissionRequestEvent(BaseEvent):
    """Permission request from tool."""
    tool_name: str
    scope: str
    risk_level: str  # "low", "medium", "high"
    description: str
    request_id: str

@dataclass
class PermissionResponseEvent(BaseEvent):
    """User permission response."""
    request_id: str
    granted: bool
    remember: bool = False  # Remember for future requests

class EventBus:
    """
    Async event bus with typed events.
    Uses regular sets so bound methods are not garbage-collected between subscribe
    and the next publish call (WeakSet drops them immediately).
    """
    
    def __init__(self):
        # Map event type to set of handlers
        self._handlers: Dict[Type[BaseEvent], Set[Callable]] = {}
        self._lock = asyncio.Lock()
        
    async def subscribe(
        self, 
        event_type: Type[EventType], 
        handler: Callable[[EventType], None]
    ) -> None:
        """Subscribe to events of a specific type."""
        async with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = set()
            
            self._handlers[event_type].add(handler)
            logger.debug(f"Subscribed {handler} to {event_type.__name__}")
    
    async def unsubscribe(
        self, 
        event_type: Type[EventType], 
        handler: Callable[[EventType], None]
    ) -> None:
        """Unsubscribe from events."""
        async with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type].discard(handler)
                logger.debug(f"Unsubscribed {handler} from {event_type.__name__}")
    
    async def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)
        
        async with self._lock:
            handlers = self._handlers.get(event_type, set()).copy()
        
        if handlers:
            logger.debug(f"Publishing {event_type.__name__} to {len(handlers)} handlers")
            
            # Call handlers (not awaited - fire and forget)
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event))
                    else:
                        handler(event)
                except Exception as e:
                    logger.exception(f"Error in event handler {handler}: {e}")
    
    def publish_sync(self, event: BaseEvent) -> None:
        """Synchronous publish for use from non-async contexts."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.publish(event))
            else:
                loop.run_until_complete(self.publish(event))
        except RuntimeError:
            # No event loop - create one
            asyncio.run(self.publish(event))
    
    def get_handler_count(self, event_type: Type[BaseEvent]) -> int:
        """Get number of handlers for an event type (for testing)."""
        return len(self._handlers.get(event_type, set()))