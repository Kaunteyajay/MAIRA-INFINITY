"""
Speech-to-Text System

Local speech recognition using faster-whisper with Hinglish support.
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from maira.core.event_bus import EventBus, UserSpeechTextEvent

logger = logging.getLogger(__name__)

class STTEngine:
    """Speech-to-text engine with faster-whisper."""
    
    def __init__(self, event_bus: EventBus, model_size: str = "small"):
        self.event_bus = event_bus
        self.model_size = model_size
        self.model: Optional[WhisperModel] = None
        self._model_loading = False
        
        # Language detection
        self.hinglish_keywords = {
            "aur", "hai", "hain", "kya", "kaise", "kahan", "kab", "kyun", "nahi", "haan",
            "mera", "tera", "uska", "yeh", "woh", "abhi", "baad", "pehle", "achha",
            "matlab", "samjha", "dekho", "suno", "bolo", "karo", "jaao", "aao"
        }
    
    async def initialize(self) -> None:
        """Initialize the whisper model."""
        if self.model is not None or self._model_loading:
            return
        
        self._model_loading = True
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Load model in thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: WhisperModel(
                    self.model_size,
                    device="auto",  # Use GPU if available
                    compute_type="auto"
                )
            )
            
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
        finally:
            self._model_loading = False
    
    async def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int = 16000) -> None:
        """Transcribe audio data and publish result."""
        if self.model is None:
            await self.initialize()
        
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)
                sf.write(temp_path, audio_data, sample_rate)
            
            # Transcribe in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_file,
                str(temp_path)
            )
            
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            
            if result:
                # Detect language and publish result
                text = result["text"].strip()
                language = self._detect_language(text)
                confidence = result.get("confidence", 0.8)
                
                if text:
                    await self.event_bus.publish(UserSpeechTextEvent(
                        text=text,
                        language=language,
                        confidence=confidence
                    ))
                    
                    logger.info(f"STT result: '{text}' (lang: {language}, conf: {confidence:.2f})")
                else:
                    logger.debug("STT: No speech detected")
        
        except Exception as e:
            logger.exception(f"STT transcription error: {e}")
    
    def _transcribe_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Transcribe audio file (runs in thread)."""
        try:
            segments, info = self.model.transcribe(
                file_path,
                language=None,  # Auto-detect
                task="transcribe",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Combine segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            
            full_text = " ".join(text_parts).strip()
            
            return {
                "text": full_text,
                "language": info.language,
                "confidence": info.language_probability
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is English, Hindi, or Hinglish."""
        words = text.lower().split()
        
        if not words:
            return "unknown"
        
        # Count Hinglish/Hindi words
        hinglish_count = sum(1 for word in words if word in self.hinglish_keywords)
        hinglish_ratio = hinglish_count / len(words)
        
        # Simple heuristic
        if hinglish_ratio > 0.3:
            return "hinglish"
        elif hinglish_ratio > 0.1:
            return "mixed"
        else:
            return "english"
    
    async def shutdown(self) -> None:
        """Cleanup resources."""
        self.model = None
        logger.info("STT engine shutdown")