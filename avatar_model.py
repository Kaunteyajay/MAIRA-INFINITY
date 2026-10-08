"""
Avatar ViewModel

Controls avatar state and animations.
"""

import asyncio
import logging
from PySide6.QtCore import QObject, Signal, Property, Slot

from maira.core.event_bus import EventBus, AvatarStateEvent, TTSAudioEvent, UserSpeechStartEvent, UserSpeechEndEvent

logger = logging.getLogger(__name__)

class AvatarModel(QObject):
    """Model for avatar control."""
    
    # Signals
    stateChanged = Signal()
    emotionChanged = Signal()
    audioLevelChanged = Signal()
    
    def __init__(self, event_bus: EventBus, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        
        # Avatar state
        self._state = "idle"
        self._emotion = "neutral"
        self._audio_level = 0.0
        
        # Subscribe to events
        asyncio.create_task(self._setup_event_handlers())
    
    async def _setup_event_handlers(self):
        """Setup event subscriptions."""
        await self.event_bus.subscribe(AvatarStateEvent, self._handle_state_change)
        await self.event_bus.subscribe(TTSAudioEvent, self._handle_audio_level)
        await self.event_bus.subscribe(UserSpeechStartEvent, self._handle_speech_start)
        await self.event_bus.subscribe(UserSpeechEndEvent, self._handle_speech_end)
    
    # Properties
    @Property(str, notify=stateChanged)
    def currentState(self):
        return self._state
    
    @Property(str, notify=emotionChanged)
    def emotion(self):
        return self._emotion
    
    @Property(float, notify=audioLevelChanged)
    def audioLevel(self):
        return self._audio_level
    
    # Event handlers
    async def _handle_state_change(self, event: AvatarStateEvent):
        """Handle avatar state change."""
        if event.state != self._state:
            self._state = event.state
            self.stateChanged.emit()
        
        if event.emotion != self._emotion:
            self._emotion = event.emotion
            self.emotionChanged.emit()
    
    async def _handle_audio_level(self, event: TTSAudioEvent):
        """Handle TTS audio level for lip-sync."""
        self._audio_level = event.audio_level
        self.audioLevelChanged.emit()
    
    async def _handle_speech_start(self, event: UserSpeechStartEvent):
        """Handle user speech start."""
        self._state = "listening"
        self.stateChanged.emit()
    
    async def _handle_speech_end(self, event: UserSpeechEndEvent):
        """Handle user speech end."""
        self._state = "thinking"
        self.stateChanged.emit()
    
    @Slot()
    def setIdleState(self):
        """Set avatar to idle state."""
        asyncio.create_task(self.event_bus.publish(AvatarStateEvent(state="idle")))
    
    @Slot(str)
    def setEmotion(self, emotion: str):
        """Set avatar emotion."""
        asyncio.create_task(self.event_bus.publish(AvatarStateEvent(
            state=self._state, 
            emotion=emotion
        )))