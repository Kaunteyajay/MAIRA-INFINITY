"""
MAIRA Startup and Integration

Initializes all subsystems and connects them together.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from maira.core.event_bus import EventBus, UserSpeechEndEvent
from maira.core.orchestrator import ConversationOrchestrator
from maira.core.session_manager import SessionManager
from maira.core.permissions import PermissionGate
from maira.llm.router import LLMRouter
from maira.voice.capture import AudioCapture
from maira.voice.stt import STTEngine
from maira.voice.tts import TTSEngine
from maira.tools.registry import ToolRegistry
from maira.tools.web_search import WebSearchTool
from maira.infra.config import Config
from maira.infra.db import DatabaseManager

logger = logging.getLogger(__name__)

class MAIRACore:
    """Core MAIRA system integration."""
    
    def __init__(self, config: Config, db: DatabaseManager):
        self.config = config
        self.db = db
        
        # Core systems
        self.event_bus: Optional[EventBus] = None
        self.llm_router: Optional[LLMRouter] = None
        self.session_manager: Optional[SessionManager] = None
        self.permission_gate: Optional[PermissionGate] = None
        
        # Voice systems
        self.audio_capture: Optional[AudioCapture] = None
        self.stt_engine: Optional[STTEngine] = None
        self.tts_engine: Optional[TTSEngine] = None
        
        # Tool systems
        self.tool_registry: Optional[ToolRegistry] = None
        
        # Main orchestrator
        self.orchestrator: Optional[ConversationOrchestrator] = None
    
    async def initialize(self) -> None:
        """Initialize all MAIRA subsystems."""
        logger.info("Initializing MAIRA core systems...")
        
        try:
            # 1. Event bus (core communication)
            self.event_bus = EventBus()
            
            # 2. Session manager
            self.session_manager = SessionManager(self.event_bus, self.db)
            
            # 3. Permission gate
            self.permission_gate = PermissionGate(self.event_bus, self.db)
            await self.permission_gate.start()
            
            # 4. LLM router
            self.llm_router = LLMRouter(self.event_bus)
            await self._setup_llm_providers()
            
            # 5. Voice systems
            await self._setup_voice_systems()
            
            # 6. Tool registry
            await self._setup_tools()
            
            # 7. Main orchestrator
            self.orchestrator = ConversationOrchestrator(
                event_bus=self.event_bus,
                llm_router=self.llm_router,
                stt_engine=self.stt_engine,
                tts_engine=self.tts_engine,
                tool_registry=self.tool_registry,
                permission_gate=self.permission_gate,
                db=self.db
            )
            
            # 8. Start orchestrator
            await self.orchestrator.start()
            
            # 9. Start session manager
            await self.session_manager.start()
            
            logger.info("MAIRA core initialization complete")
            
        except Exception as e:
            logger.exception(f"MAIRA core initialization failed: {e}")
            raise
    
    async def _setup_llm_providers(self) -> None:
        """Setup LLM providers with API keys."""
        api_keys = {}
        
        anthropic_key = self.config.get("llm.keys.anthropic", "")
        openai_key = self.config.get("llm.keys.openai", "")
        google_key = self.config.get("llm.keys.google", "")
        
        if anthropic_key:
            api_keys["anthropic"] = anthropic_key
        if openai_key:
            api_keys["openai"] = openai_key  
        if google_key:
            api_keys["google"] = google_key
        
        await self.llm_router.setup_providers(api_keys)
        
        if not api_keys:
            logger.warning("No LLM API keys configured - only local Ollama will be available")
    
    async def _setup_voice_systems(self) -> None:
        """Setup voice capture, STT, and TTS."""
        try:
            self.audio_capture = AudioCapture(self.event_bus)
            
            stt_model = self.config.get("voice.stt_model", "small")
            self.stt_engine = STTEngine(self.event_bus, stt_model)
            await self.stt_engine.initialize()
            
            self.tts_engine = TTSEngine(self.event_bus)
            
            tts_voice = self.config.get("voice.tts_voice", "en-IN-NeerjaNeural")
            self.tts_engine.set_voice(tts_voice)
            
            # Connect audio capture to STT
            await self.event_bus.subscribe(
                UserSpeechEndEvent,
                self._handle_speech_for_stt
            )
            
            logger.info("Voice systems initialized")
            
        except Exception as e:
            logger.exception(f"Voice system setup failed: {e}")
    
    async def _setup_tools(self) -> None:
        """Setup tool registry and available tools."""
        self.tool_registry = ToolRegistry()
        
        search_api_key = self.config.get("tools.search_api_key", "")
        web_search = WebSearchTool(api_key=search_api_key if search_api_key else None)
        self.tool_registry.register_tool(web_search)
        
        logger.info(f"Tool registry initialized with {len(self.tool_registry._tools)} tools")
    
    async def _handle_speech_for_stt(self, event) -> None:
        """Handle speech end event and trigger STT."""
        if self.audio_capture and self.stt_engine:
            audio_data = self.audio_capture.get_last_audio()
            if audio_data is not None:
                await self.stt_engine.transcribe_audio(audio_data)
                self.audio_capture.clear_buffer()
    
    async def start_voice_capture(self) -> None:
        """Start listening for voice input."""
        if self.audio_capture:
            await self.audio_capture.start_capture()
    
    async def stop_voice_capture(self) -> None:
        """Stop voice input."""
        if self.audio_capture:
            await self.audio_capture.stop_capture()
    
    async def shutdown(self) -> None:
        """Shutdown all systems gracefully."""
        logger.info("Shutting down MAIRA core systems...")
        
        try:
            if self.audio_capture:
                await self.audio_capture.stop_capture()
            
            if self.stt_engine:
                await self.stt_engine.shutdown()
            
            if self.tts_engine:
                await self.tts_engine.stop_speaking()
            
            if self.session_manager:
                await self.session_manager.shutdown()
            
            logger.info("MAIRA core shutdown complete")
            
        except Exception as e:
            logger.exception(f"Error during shutdown: {e}")