"""
Main Window

Primary application window with QML integration.
"""

import logging
from pathlib import Path
from PySide6.QtCore import QUrl, QObject, Signal, Property
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
from PySide6.QtQuick import QQuickWindow

from maira.core.event_bus import EventBus
from maira.infra.config import Config

logger = logging.getLogger(__name__)

class WindowController(QObject):
    """Controller for main window interactions."""
    
    def __init__(self, event_bus: EventBus, config: Config):
        super().__init__()
        self.event_bus = event_bus
        self.config = config
        self._status = "Online"
        self._version = "12.7.3"
    
    statusChanged = Signal()
    
    @Property(str, notify=statusChanged)
    def status(self):
        return self._status
    
    def set_status(self, status: str):
        if self._status != status:
            self._status = status
            self.statusChanged.emit()
    
    @Property(str, constant=True)
    def version(self):
        return self._version

class MainWindow:
    """Main application window."""
    
    def __init__(self, event_bus: EventBus, config: Config, maira_core=None, dev_mode: bool = False):
        self.event_bus = event_bus
        self.config = config
        self.maira_core = maira_core
        self.dev_mode = dev_mode
        
        # QML engine
        self.engine = QQmlApplicationEngine()
        
        # Window controller
        self.controller = WindowController(event_bus, config)
        
        # Setup QML
        self._setup_qml()
    
    def _setup_qml(self):
        """Setup QML engine and context."""
        # Set context properties FIRST
        context = self.engine.rootContext()
        context.setContextProperty("devMode", self.dev_mode)
        
        # Register models
        if self.maira_core:
            # Create model instances
            from maira.ui.viewmodels.system_status_model import SystemStatusModel
            from maira.ui.viewmodels.avatar_model import AvatarModel
            from maira.ui.viewmodels.sidebar_model import SidebarModel
            from maira.ui.viewmodels.chat_model import ChatModel
            
            self.system_status_model = SystemStatusModel(self.event_bus)
            self.avatar_model = AvatarModel(self.event_bus) 
            self.sidebar_model = SidebarModel(self.event_bus, self.maira_core.session_manager)
            self.chat_model = ChatModel(self.event_bus, self.maira_core.orchestrator, self.maira_core)
            
            # Register as context properties
            context.setContextProperty("systemStatusModel", self.system_status_model)
            context.setContextProperty("avatarModel", self.avatar_model)
            context.setContextProperty("sidebarModel", self.sidebar_model)
            context.setContextProperty("chatModel", self.chat_model)
        
        # Register WindowController singleton - AFTER context properties
        # This must be done BEFORE loading QML
        qmlRegisterSingletonType(
            WindowController, 
            "MAIRA.Core", 1, 0, 
            "WindowController", 
            lambda engine: self.controller
        )
        
        # QML import paths
        qml_dir = Path(__file__).parent / "qml"
        self.engine.addImportPath(str(qml_dir))
        self.engine.addImportPath(str(qml_dir / "components"))
        self.engine.addImportPath(str(qml_dir / "pages"))
        self.engine.addImportPath(str(qml_dir / "widgets"))
        self.engine.addImportPath(str(qml_dir / "avatar"))
        self.engine.addImportPath(str(qml_dir))
        
        main_qml = qml_dir / "Main.qml"

        logger.info(f"Loading QML from: {main_qml}")
        self.engine.load(QUrl.fromLocalFile(str(main_qml)))

        if not self.engine.rootObjects():
            logger.error(f"QML file not found or failed to load: {main_qml}")
            raise RuntimeError("Failed to load QML")
        
        logger.info("QML interface loaded successfully")
    
    def show(self):
        """Show the main window."""
        root_objects = self.engine.rootObjects()
        if root_objects:
            window = root_objects[0]
            if isinstance(window, QQuickWindow):
                window.show()
                logger.info("Main window shown")