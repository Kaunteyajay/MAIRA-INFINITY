"""
Audio Capture System

Handles microphone input with voice activity detection.
"""

import asyncio
import logging
import threading
from typing import Optional
import numpy as np
import sounddevice as sd
import webrtcvad

from maira.core.event_bus import EventBus, UserSpeechStartEvent, UserSpeechEndEvent

logger = logging.getLogger(__name__)

class AudioCapture:
    """Real-time audio capture with VAD."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.sample_rate = 16000  # Required for VAD
        self.frame_duration = 30  # ms
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        # VAD setup
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 0-3
        
        # State
        self.is_capturing = False
        self.is_speaking = False
        self.audio_buffer = []
        self.speech_frames = []
        self.silence_frames = 0
        self.max_silence_frames = 30  # ~1 second of silence to stop
        
        # Event loop reference stored at capture start so the audio thread
        # can schedule coroutines safely via run_coroutine_threadsafe
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Threading
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
    async def start_capture(self) -> None:
        """Start audio capture."""
        if self.is_capturing:
            return
        
        try:
            self.is_capturing = True
            self._stop_event.clear()
            # Store the running event loop so the audio thread can schedule coroutines
            self._loop = asyncio.get_running_loop()
            
            # Start capture thread
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()
            
            logger.info("Audio capture started")
            
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            self.is_capturing = False
            raise
    
    async def stop_capture(self) -> None:
        """Stop audio capture."""
        if not self.is_capturing:
            return
        
        self.is_capturing = False
        self._stop_event.set()
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.0)
        
        logger.info("Audio capture stopped")
    
    def _capture_loop(self) -> None:
        """Main capture loop running in separate thread."""
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16,
                blocksize=self.frame_size,
                callback=self._audio_callback
            ):
                while not self._stop_event.wait(0.1):
                    continue
                    
        except Exception as e:
            logger.exception(f"Audio capture error: {e}")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        """Process audio frames."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        # Convert to bytes for VAD
        audio_bytes = indata.tobytes()
        
        # Run VAD
        try:
            is_speech = self.vad.is_speech(audio_bytes, self.sample_rate)
        except Exception as e:
            logger.warning(f"VAD error: {e}")
            is_speech = False
        
        # Speech state machine
        if is_speech:
            if not self.is_speaking:
                # Speech started
                self.is_speaking = True
                self.speech_frames = []
                self.silence_frames = 0
                
                # Notify speech start using stored loop
                if self._loop:
                    asyncio.run_coroutine_threadsafe(
                        self.event_bus.publish(UserSpeechStartEvent()),
                        self._loop
                    )
                logger.debug("Speech started")
            
            # Collect speech frames
            self.speech_frames.append(indata.copy())
            self.silence_frames = 0
            
        else:
            if self.is_speaking:
                self.silence_frames += 1
                
                # Continue collecting a few frames after speech stops
                if self.silence_frames <= 5:  # ~150ms buffer
                    self.speech_frames.append(indata.copy())
                
                # End speech after sufficient silence
                if self.silence_frames >= self.max_silence_frames:
                    self._end_speech()
    
    def _end_speech(self) -> None:
        """Process completed speech segment."""
        if not self.is_speaking or not self.speech_frames:
            return
        
        # Combine speech frames
        speech_audio = np.concatenate(self.speech_frames)
        duration_ms = len(speech_audio) * 1000 // self.sample_rate
        
        self.is_speaking = False
        self.speech_frames = []
        self.silence_frames = 0
        
        # Notify speech end with audio data using stored loop
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._process_speech_end(speech_audio, duration_ms),
                self._loop
            )
        
        logger.debug(f"Speech ended, duration: {duration_ms}ms")
    
    async def _process_speech_end(self, audio_data: np.ndarray, duration_ms: int) -> None:
        """Process speech end event."""
        # Store audio for STT processing
        self.audio_buffer = audio_data
        
        # Publish event
        await self.event_bus.publish(UserSpeechEndEvent(duration_ms=duration_ms))
    
    def get_last_audio(self) -> Optional[np.ndarray]:
        """Get the last captured speech audio."""
        if len(self.audio_buffer) > 0:
            return self.audio_buffer.copy()
        return None
    
    def clear_buffer(self) -> None:
        """Clear audio buffer."""
        self.audio_buffer = []