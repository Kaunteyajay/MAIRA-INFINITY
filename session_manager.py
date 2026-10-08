"""
Session Manager

Manages active sessions (Python REPL, Web Search, File Monitor, etc.)
and publishes updates for the Active Sessions widget.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from maira.core.event_bus import EventBus
from maira.infra.db import DatabaseManager

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Session status types."""
    ACTIVE = "active"
    IDLE = "idle" 
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class Session:
    """Active session information."""
    id: str
    name: str
    session_type: str  # "python_repl", "web_search", "file_monitor", "ai_training"
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SessionManager:
    """Manages active application sessions."""
    
    def __init__(self, event_bus: EventBus, db: DatabaseManager):
        self.event_bus = event_bus
        self.db = db
        self._sessions: Dict[str, Session] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start the session manager."""
        logger.info("Starting session manager")
        
        # Start cleanup task (runs every 5 minutes)
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def shutdown(self) -> None:
        """Shutdown the session manager."""
        logger.info("Shutting down session manager")
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Stop all sessions
        for session in self._sessions.values():
            await self.stop_session(session.id)
    
    async def create_session(
        self,
        name: str,
        session_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = Session(
            id=session_id,
            name=name,
            session_type=session_type,
            status=SessionStatus.ACTIVE,
            created_at=now,
            last_activity=now,
            metadata=metadata or {}
        )
        
        self._sessions[session_id] = session
        
        logger.info(f"Created session: {name} ({session_type})")
        await self._publish_sessions_update()
        
        return session_id
    
    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
        metadata: Optional[Dict] = None
    ) -> None:
        """Update session status."""
        if session_id not in self._sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        
        session = self._sessions[session_id]
        session.status = status
        session.last_activity = datetime.now()
        
        if metadata:
            session.metadata.update(metadata)
        
        logger.debug(f"Updated session {session.name}: {status}")
        await self._publish_sessions_update()
    
    async def activity_pulse(self, session_id: str) -> None:
        """Update last activity time for a session."""
        if session_id in self._sessions:
            self._sessions[session_id].last_activity = datetime.now()
    
    async def stop_session(self, session_id: str) -> None:
        """Stop and remove a session."""
        if session_id not in self._sessions:
            return
        
        session = self._sessions.pop(session_id)
        logger.info(f"Stopped session: {session.name}")
        
        await self._publish_sessions_update()
    
    def get_sessions(self) -> List[Session]:
        """Get all active sessions."""
        return list(self._sessions.values())
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a specific session."""
        return self._sessions.get(session_id)
    
    async def _publish_sessions_update(self) -> None:
        """Publish sessions update event."""
        # Just update internal state for now
        # UI will query sessions directly
        pass
    
    async def _cleanup_loop(self) -> None:
        """Cleanup inactive sessions periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                now = datetime.now()
                inactive_sessions = []
                
                for session in self._sessions.values():
                    # Remove sessions inactive for > 1 hour
                    inactive_time = (now - session.last_activity).total_seconds()
                    if inactive_time > 3600:
                        inactive_sessions.append(session.id)
                
                for session_id in inactive_sessions:
                    await self.stop_session(session_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in cleanup loop: {e}")