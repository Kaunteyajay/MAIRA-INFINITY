"""
MAIRA Application Bootstrap

Main application class that sets up PySide6 + asyncio integration and 
initializes all subsystems.
"""

import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import qasync

from maira.core.event_bus import EventBus
from maira.infra.config import Config
from maira.infra.db import DatabaseManager
from maira.startup import MAIRACore

logger = logging.getLogger(__name__)

class MAIRAApplication:
    """Main MAIRA application with Qt + asyncio integration."""
    
    def __init__(
        self,
        dev_mode: bool = False,
        offline_mode: bool = False,
        config_path: Optional[Path] = None,
        data_dir: Optional[Path] = None
    ):
        self.dev_mode = dev_mode
        self.offline_mode = offline_mode
        self.config_path = config_path
        self.data_dir = data_dir
        
        # Core systems (initialized in run())
        self.qt_app: Optional[QApplication] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.config: Optional[Config] = None
        self.db: Optional[DatabaseManager] = None
        self.maira_core: Optional[MAIRACore] = None
        self.main_window: Optional[MainWindow] = None
        
        # Shutdown flag
        self._shutdown_requested = False
    
    async def initialize_async_systems(self) -> None:
        """Initialize async subsystems."""
        logger.info("Initializing async systems...")
        
        # Configuration
        self.config = Config(config_path=self.config_path, data_dir=self.data_dir)
        await self.config.load()
        
        # Database
        self.db = DatabaseManager(self.config.data_dir / "maira.db")
        await self.db.initialize()
        
        # Initialize MAIRA core
        self.maira_core = MAIRACore(self.config, self.db)
        await self.maira_core.initialize()
        
        logger.info("Async systems initialized successfully")
    
    def initialize_qt_systems(self) -> None:
        """Initialize Qt/UI systems."""
        logger.info("Initializing Qt systems...")

        # Try to use QML-based fancy UI, fallback to pure Python if it fails
        try:
            from maira.ui.main_window import MainWindow
            
            self.main_window = MainWindow(
                event_bus=self.maira_core.event_bus,
                config=self.config,
                maira_core=self.maira_core,
                dev_mode=self.dev_mode
            )
            logger.info("Qt QML UI initialized successfully")
            
        except Exception as e:
            logger.warning(f"QML UI failed to load ({e}), falling back to simple UI")
            from maira.ui.pure_py_window import PurePythonWindow
            
            self.main_window = PurePythonWindow(
                event_bus=self.maira_core.event_bus,
                config=self.config,
                maira_core=self.maira_core,
                dev_mode=self.dev_mode
            )
            logger.info("Pure Python UI initialized successfully")

        logger.info("Qt systems initialized successfully")
    
    async def shutdown_async_systems(self) -> None:
        """Shutdown async systems gracefully."""
        logger.info("Shutting down async systems...")
        
        if self.maira_core:
            await self.maira_core.shutdown()
        
        if self.db:
            await self.db.close()
        
        logger.info("Async systems shutdown complete")
    
    def run(self) -> int:
        """Run the application with Qt + asyncio integration."""
        # Create Qt application
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName("MAIRA-∞")
        self.qt_app.setApplicationVersion("12.7.3")
        self.qt_app.setOrganizationName("MAIRA Team")
        
        # High DPI scaling is automatic in PySide6 6.7+; AA_UseHighDpiPixmaps still useful
        self.qt_app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        try:
            # Setup asyncio event loop with Qt integration
            self.event_loop = qasync.QEventLoop(self.qt_app)
            asyncio.set_event_loop(self.event_loop)

            # Run async initialization AND Qt init inside the loop
            # so that asyncio.create_task() works in viewmodels
            async def _bootstrap():
                await self.initialize_async_systems()
                self.initialize_qt_systems()

            self.event_loop.run_until_complete(_bootstrap())

            # Show main window
            if self.main_window:
                self.main_window.show()

            # Setup shutdown handler
            self.qt_app.aboutToQuit.connect(self._on_about_to_quit)

            logger.info("MAIRA-∞ startup complete")

            # Run event loop
            with self.event_loop:
                return self.event_loop.run_until_complete(self._run_until_quit())

        except Exception as e:
            logger.exception(f"Application startup failed: {e}")
            return 1
    
    async def _run_until_quit(self) -> int:
        """Run until application quit is requested."""
        # Create a future that completes when quit is requested
        quit_future = asyncio.Future()
        
        def on_quit():
            if not quit_future.done():
                quit_future.set_result(0)
        
        # Connect quit signal
        if self.qt_app:
            self.qt_app.aboutToQuit.connect(on_quit)
        
        # Wait for quit
        return await quit_future
    
    def _on_about_to_quit(self) -> None:
        """Handle application about to quit."""
        if not self._shutdown_requested:
            self._shutdown_requested = True
            logger.info("Application quit requested")
            
            # Run async shutdown
            if self.event_loop and not self.event_loop.is_closed():
                try:
                    self.event_loop.run_until_complete(self.shutdown_async_systems())
                except Exception as e:
                    logger.exception(f"Error during shutdown: {e}")