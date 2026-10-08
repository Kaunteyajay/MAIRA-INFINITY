"""
Simple Main Window with QQuickView for faster debugging
"""

import logging
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQuick import QQuickView

from maira.core.event_bus import EventBus
from maira.infra.config import Config

logger = logging.getLogger(__name__)

class SimpleMainWindow:
    """Simplified main window using QQuickView."""

    def __init__(self, event_bus: EventBus, config: Config, maira_core=None, dev_mode: bool = False):
        self.event_bus = event_bus
        self.config = config
        self.maira_core = maira_core

        # Create view
        self.view = QQuickView()
        self.view.setResizeMode(QQuickView.SizeRootObjectToView)

        # Set context properties
        context = self.view.rootContext()
        context.setContextProperty("devMode", dev_mode)

        # Load QML
        qml_dir = Path(__file__).parent / "qml"
        qml_file = qml_dir / "MinimalWindow.qml"

        logger.info(f"Loading QML from: {qml_file}")
        self.view.setSource(QUrl.fromLocalFile(str(qml_file)))

        # Wait for loading
        import time
        time.sleep(0.5)

        logger.info(f"QML Status: {self.view.status()}")

        if self.view.status() != 0:  # 0 = Ready, 1 = Loading, 2 = Error
            logger.error(f"QML failed to load! Status: {self.view.status()}")
            raise RuntimeError("Failed to load QML")

        logger.info("QML loaded successfully with QQuickView")

    def show(self):
        """Show the window."""
        self.view.show()
        logger.info("Window shown")
