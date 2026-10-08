"""
Sidebar ViewModel

Manages sidebar navigation and active sessions.
"""

import asyncio
import logging
from typing import List
from PySide6.QtCore import QObject, Signal, Property, Slot

from maira.core.event_bus import EventBus
from maira.core.session_manager import SessionManager

logger = logging.getLogger(__name__)

class SidebarModel(QObject):
    """Model for sidebar navigation."""
    
    activeModuleChanged = Signal()
    sessionsChanged = Signal()
    
    def __init__(self, event_bus: EventBus, session_manager: SessionManager = None, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.session_manager = session_manager
        
        self._active_module = "home"
        
    @Property(str, notify=activeModuleChanged)
    def activeModule(self):
        return self._active_module
    
    @Slot(str)
    def setActiveModule(self, module: str):
        if module != self._active_module:
            self._active_module = module
            self.activeModuleChanged.emit()
            logger.info(f"Active module changed to: {module}")
    
    @Slot(result=list)
    def getActiveSessions(self):
        """Get list of active sessions for display."""
        if not self.session_manager:
            return [
                {"name": "Python REPL", "status": "running", "color": "#2EE66B"},
                {"name": "Web Search", "status": "active", "color": "#4DA3FF"},
                {"name": "File Monitor", "status": "idle", "color": "#FFC247"}
            ]
        
        sessions = []
        for session in self.session_manager.get_sessions():
            sessions.append({
                "name": session.name,
                "status": session.status.value,
                "color": self._get_status_color(session.status.value)
            })
        
        return sessions
    
    def _get_status_color(self, status: str) -> str:
        """Get color for session status."""
        colors = {
            "running": "#2EE66B",
            "active": "#4DA3FF", 
            "idle": "#FFC247",
            "error": "#FF4D6A",
            "stopped": "#8FA3C7"
        }
        return colors.get(status, "#8FA3C7")