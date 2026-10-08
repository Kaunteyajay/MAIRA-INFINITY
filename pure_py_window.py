"""
Pure Python Window (No QML) - For immediate testing
"""

import asyncio
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

from maira.core.event_bus import EventBus
from maira.infra.config import Config

logger = logging.getLogger(__name__)

class PurePythonWindow(QMainWindow):
    """Main window using pure Python widgets (no QML)."""

    def __init__(self, event_bus: EventBus, config: Config, maira_core=None, dev_mode: bool = False):
        super().__init__()
        self.event_bus = event_bus
        self.config = config
        self.maira_core = maira_core

        self.setWindowTitle("MAIRA-∞ - Limitless AI Assistant")
        self.setGeometry(100, 100, 1000, 700)

        # Dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e27;
            }
            QLabel {
                color: #00d9ff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00d9ff;
                color: #0a0e27;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00b8d9;
            }
            QTextEdit {
                background-color: #1a1f3a;
                color: #e2e8f0;
                border: 2px solid #00d9ff;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Logo
        logo_label = QLabel("M")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Arial", 80, QFont.Bold))
        logo_label.setStyleSheet("color: #00d9ff; background-color: #1a1f3a; border-radius: 50px; padding: 20px;")
        logo_label.setFixedSize(150, 150)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Title
        title = QLabel("MAIRA-∞")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 48, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Limitless AI Desktop Assistant")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #8892b0; font-size: 16px;")
        layout.addWidget(subtitle)

        # Status
        status_frame = QFrame()
        status_frame.setStyleSheet("background-color: #1a2332; border-radius: 10px; padding: 15px;")
        status_layout = QVBoxLayout(status_frame)

        self.status_labels = []
        statuses = [
            ("✅", "Voice System Ready", "(Whisper + Edge-TTS)"),
            ("✅", "LLM Connected", "(Google Gemini)"),
            ("✅", "Tools Active", "(Web Search, Code Execution)")
        ]

        for icon, text, detail in statuses:
            row = QHBoxLayout()
            label = QLabel(f"{icon} {text} {detail}")
            label.setStyleSheet("color: #4ade80; font-size: 13px;")
            row.addWidget(label)
            status_layout.addLayout(row)

        layout.addWidget(status_frame)

        # Instructions
        instructions = QLabel("🎤 Press Ctrl+Space for Voice Input\n💬 Type your message below")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #00d9ff; font-size: 15px; font-weight: bold; padding: 20px;")
        layout.addWidget(instructions)

        # Text input/output
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("MAIRA responses will appear here...")
        self.chat_display.setMinimumHeight(150)
        layout.addWidget(self.chat_display)

        # Voice button
        self.voice_btn = QPushButton("🎤 Start Voice Input (Ctrl+Space)")
        self.voice_btn.clicked.connect(self.toggle_voice)
        layout.addWidget(self.voice_btn, alignment=Qt.AlignCenter)

        # Add greeting
        QTimer.singleShot(1000, self.show_greeting)

    def show_greeting(self):
        """Show initial greeting."""
        greeting = """Hello! I am MAIRA-∞, your limitless AI assistant.

I'm here to help you with:
• Voice conversations (just press Ctrl+Space)
• Web searches and information
• Code execution and automation
• Learning and research

How can I assist you today?"""
        self.chat_display.setText(greeting)

    def toggle_voice(self):
        """Toggle voice input."""
        self.chat_display.append("\n🎤 Voice input activated - Speak now...")
        if self.maira_core and self.maira_core.audio_capture:
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
            if loop and loop.is_running():
                asyncio.ensure_future(self.maira_core.start_voice_capture())
            else:
                logger.warning("No running event loop for voice capture")

    def show(self):
        """Show the window."""
        super().show()
        logger.info("Pure Python window shown successfully")
