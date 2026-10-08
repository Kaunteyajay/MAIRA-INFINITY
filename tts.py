"""
Text-to-Speech System

Uses edge-tts for natural speech synthesis with multiple voice options.
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional, AsyncGenerator, Dict, Any
import numpy as np
import soundfile as sf
import sounddevice as sd
import edge_tts

from maira.core.event_bus import EventBus, TTSStartEvent, TTSAudioEvent, TTSEndEvent

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-speech engine using edge-tts."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.voice = "en-IN-NeerjaNeural"  # Default Indian English female voice
        self.rate = "+0%"  # Speech rate
        self.pitch = "+0Hz"  # Pitch adjustment
        
        # Audio state
        self.is_speaking = False
        self._current_stream: Optional[sd.OutputStream] = None
        self._stop_playback = False
        
        # Voice options
        self.available_voices = {
            "english": {
                "female": ["en-US-JennyNeural", "en-IN-NeerjaNeural", "en-GB-SoniaNeural"],
                "male": ["en-US-GuyNeural", "en-IN-PrabhatNeural", "en-GB-RyanNeural"]
            },
            "hinglish": {
                "female": ["en-IN-NeerjaNeural", "hi-IN-SwaraNeural"],
                "male": ["en-IN-PrabhatNeural", "hi-IN-MadhurNeural"]
            }
        }
    
    async def speak(self, text: str, language: str = "english") -> None:
        """Convert text to speech and play audio."""
        if self.is_speaking:
            await self.stop_speaking()
        
        try:
            self.is_speaking = True
            self._stop_playback = False
            
            # Publish start event
            await self.event_bus.publish(TTSStartEvent(
                text=text,
                voice=self.voice
            ))
            
            logger.info(f"TTS: Speaking '{text[:50]}...' with voice {self.voice}")
            
            # Generate and stream audio
            audio_generator = self._generate_speech(text, language)
            await self._stream_audio(audio_generator)
            
        except Exception as e:
            logger.exception(f"TTS error: {e}")
        finally:
            if self.is_speaking:
                await self._finish_speaking(text)
    
    async def stop_speaking(self) -> None:
        """Stop current speech playback."""
        if not self.is_speaking:
            return
        
        self._stop_playback = True
        
        if self._current_stream:
            self._current_stream.stop()
            self._current_stream.close()
            self._current_stream = None
        
        logger.info("TTS: Stopped speaking")
    
    async def _generate_speech(self, text: str, language: str) -> AsyncGenerator[bytes, None]:
        """Generate speech audio data."""
        # Normalize text for better pronunciation
        normalized_text = self._normalize_text(text, language)
        
        # Select appropriate voice
        voice = self._select_voice(language)
        
        # Generate speech using edge-tts
        communicate = edge_tts.Communicate(normalized_text, voice, rate=self.rate, pitch=self.pitch)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
            elif chunk["type"] == "WordBoundary":
                # Could use for more precise lip-sync
                pass
    
    async def _stream_audio(self, audio_generator: AsyncGenerator[bytes, None]) -> None:
        """Stream audio chunks for playback."""
        sample_rate = 24000  # edge-tts default
        
        try:
            # Collect all audio chunks first (edge-tts limitation)
            audio_chunks = []
            async for chunk in audio_generator:
                if self._stop_playback:
                    return
                audio_chunks.append(chunk)
            
            if not audio_chunks:
                return
            
            # Combine chunks
            audio_data = b''.join(audio_chunks)
            
            # Save to temp file and load as numpy array
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                temp_path = Path(tmp_file.name)
            
            # Load audio
            audio_array, sr = sf.read(temp_path)
            temp_path.unlink(missing_ok=True)
            
            if sr != sample_rate:
                # Resample if needed (shouldn't happen with edge-tts)
                logger.warning(f"Unexpected sample rate: {sr}, expected {sample_rate}")
            
            # Play audio with level monitoring
            await self._play_audio_array(audio_array, sr)
            
        except Exception as e:
            logger.exception(f"Audio streaming error: {e}")
    
    async def _play_audio_array(self, audio_data: np.ndarray, sample_rate: int) -> None:
        """Play audio array with real-time level monitoring."""
        chunk_size = 1024
        current_pos = 0
        
        def audio_callback(outdata, frames, time, status):
            nonlocal current_pos
            
            if status:
                logger.warning(f"Audio playback status: {status}")
            
            if self._stop_playback or current_pos >= len(audio_data):
                outdata.fill(0)
                return
            
            # Get chunk
            end_pos = min(current_pos + frames, len(audio_data))
            chunk = audio_data[current_pos:end_pos]
            
            # Fill output buffer
            if len(chunk) < frames:
                # Pad with zeros if needed
                padded_chunk = np.zeros(frames)
                padded_chunk[:len(chunk)] = chunk
                outdata[:] = padded_chunk.reshape(-1, 1)
            else:
                outdata[:] = chunk.reshape(-1, 1)
            
            # Calculate audio level for avatar
            audio_level = np.sqrt(np.mean(chunk ** 2))
            
            # Publish audio event for avatar lip-sync
            asyncio.create_task(self.event_bus.publish(TTSAudioEvent(
                audio_level=min(audio_level * 10, 1.0)  # Scale and cap
            )))
            
            current_pos = end_pos
        
        # Start playback
        try:
            with sd.OutputStream(
                samplerate=sample_rate,
                channels=1,
                callback=audio_callback,
                blocksize=chunk_size
            ) as stream:
                self._current_stream = stream
                
                # Wait for playback to complete
                while current_pos < len(audio_data) and not self._stop_playback:
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.exception(f"Audio playback error: {e}")
        finally:
            self._current_stream = None
    
    def _normalize_text(self, text: str, language: str) -> str:
        """Normalize text for better pronunciation."""
        if language == "hinglish":
            # Simple Hinglish normalizations
            replacements = {
                "aur": "and",
                "hai": "hey",
                "nahi": "nahin", 
                "kya": "kya",
                "matlab": "matlab"
            }
            
            words = text.split()
            normalized_words = []
            
            for word in words:
                lower_word = word.lower()
                if lower_word in replacements:
                    normalized_words.append(replacements[lower_word])
                else:
                    normalized_words.append(word)
            
            return " ".join(normalized_words)
        
        return text
    
    def _select_voice(self, language: str) -> str:
        """Select appropriate voice based on language."""
        if language == "hinglish":
            return "en-IN-NeerjaNeural"  # Indian English works well for Hinglish
        elif language == "english":
            return self.voice
        else:
            return self.voice
    
    async def _finish_speaking(self, text: str) -> None:
        """Clean up after speaking."""
        self.is_speaking = False
        
        # Calculate duration (rough estimate)
        duration_ms = len(text) * 50  # ~50ms per character
        
        await self.event_bus.publish(TTSEndEvent(duration_ms=duration_ms))
    
    def set_voice(self, voice: str) -> None:
        """Change TTS voice."""
        self.voice = voice
        logger.info(f"TTS voice changed to: {voice}")
    
    def set_rate(self, rate_percent: int) -> None:
        """Set speech rate (-50 to +50 percent)."""
        self.rate = f"{rate_percent:+d}%"
        logger.info(f"TTS rate set to: {self.rate}")