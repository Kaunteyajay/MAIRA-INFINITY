"""
Chat ViewModel

Manages chat interface and message processing.
"""

import asyncio
import logging
from PySide6.QtCore import QObject, Signal, Property, Slot, QAbstractListModel, QModelIndex, Qt

from maira.core.event_bus import EventBus, LLMTokenEvent, LLMResponseEvent

logger = logging.getLogger(__name__)


class MessageListModel(QAbstractListModel):
    """List model for chat messages, accessible from QML."""

    RoleText = Qt.UserRole + 1
    RoleRole = Qt.UserRole + 2      # "user" / "assistant" / "tool"
    RoleTime = Qt.UserRole + 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._messages: list[dict] = []

    def roleNames(self):
        return {
            self.RoleText: b"text",
            self.RoleRole: b"role",
            self.RoleTime: b"time",
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._messages)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._messages):
            return None
        msg = self._messages[index.row()]
        if role == self.RoleText:
            return msg["text"]
        if role == self.RoleRole:
            return msg["role"]
        if role == self.RoleTime:
            return msg["time"]
        return None

    def append(self, role: str, text: str, time: str = ""):
        self.beginInsertRows(QModelIndex(), len(self._messages), len(self._messages))
        self._messages.append({"role": role, "text": text, "time": time})
        self.endInsertRows()

    def update_last(self, text: str):
        """Append text to the last message (streaming)."""
        if not self._messages:
            return
        idx = len(self._messages) - 1
        self._messages[idx]["text"] = text
        model_index = self.index(idx)
        self.dataChanged.emit(model_index, model_index, [self.RoleText])


class ChatModel(QObject):
    """Model for chat interface."""

    currentModeChanged = Signal()
    isListeningChanged = Signal()
    isThinkingChanged = Signal()
    messagesChanged = Signal()

    def __init__(self, event_bus: EventBus, orchestrator=None, maira_core=None, parent=None):
        super().__init__(parent)
        self.event_bus = event_bus
        self.orchestrator = orchestrator
        self.maira_core = maira_core

        self._current_mode = "text"
        self._is_listening = False
        self._is_thinking = False
        self._streaming_text = ""

        self._messages = MessageListModel(self)

        asyncio.create_task(self._subscribe_events())

    async def _subscribe_events(self):
        await self.event_bus.subscribe(LLMTokenEvent, self._on_token)
        await self.event_bus.subscribe(LLMResponseEvent, self._on_response_done)

    async def _on_token(self, event: LLMTokenEvent):
        """Append streaming token to the in-progress assistant bubble."""
        self._streaming_text += event.token
        # Update the last message in the list (the assistant bubble added at stream start)
        self._messages.update_last(self._streaming_text)

    async def _on_response_done(self, event: LLMResponseEvent):
        self._is_thinking = False
        self.isThinkingChanged.emit()
        self._streaming_text = ""

    @Property(QObject, constant=True)
    def messages(self):
        return self._messages

    @Property(str, notify=currentModeChanged)
    def currentMode(self):
        return self._current_mode

    @Property(bool, notify=isListeningChanged)
    def isListening(self):
        return self._is_listening

    @Property(bool, notify=isThinkingChanged)
    def isThinking(self):
        return self._is_thinking

    @Slot(str)
    def setCurrentMode(self, mode: str):
        if mode != self._current_mode:
            self._current_mode = mode
            self.currentModeChanged.emit()

    @Slot(str)
    def sendMessage(self, text: str):
        """Send a text message and show it in the chat list."""
        if not text.strip():
            return

        from datetime import datetime
        now = datetime.now().strftime("%H:%M")

        # Add user bubble immediately
        self._messages.append("user", text, now)

        # Add empty assistant bubble that will fill as tokens arrive
        self._messages.append("assistant", "", now)
        self._streaming_text = ""

        self._is_thinking = True
        self.isThinkingChanged.emit()

        if self.orchestrator:
            asyncio.create_task(
                self.orchestrator.process_user_message(
                    text=text,
                    input_mode=self._current_mode
                )
            )
        else:
            logger.warning("No orchestrator connected — message not processed")

    @Slot()
    def startListening(self):
        self._is_listening = True
        self.isListeningChanged.emit()
        if self.maira_core:
            asyncio.create_task(self.maira_core.start_voice_capture())

    @Slot()
    def stopListening(self):
        self._is_listening = False
        self.isListeningChanged.emit()
        if self.maira_core:
            asyncio.create_task(self.maira_core.stop_voice_capture())
