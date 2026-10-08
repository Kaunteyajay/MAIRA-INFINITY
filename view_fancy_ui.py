"""
Standalone Fancy UI Viewer - Shows TestSimple.qml with animations
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType
from PySide6.QtCore import QUrl, QObject, Signal, Property
from PySide6.QtQuick import QQuickWindow

class MockWindowController(QObject):
    """Mock controller for standalone viewing."""
    
    statusChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._status = "Online"
        self._version = "12.7.3"
    
    @Property(str, notify=statusChanged)
    def status(self):
        return self._status
    
    @Property(str, constant=True)
    def version(self):
        return self._version

def main():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Create mock controller
    window_controller = MockWindowController()
    
    # Register WindowController as singleton
    def create_window_controller(engine):
        return window_controller
    
    qmlRegisterSingletonType(
        MockWindowController,
        "MAIRA.Core", 1, 0,
        "WindowController",
        create_window_controller
    )
    
    # Add QML import paths
    qml_dir = Path(__file__).parent / "maira" / "ui" / "qml"
    engine.addImportPath(str(qml_dir))
    
    # Use TestSimple.qml which works
    simple_qml = qml_dir / "TestSimple.qml"
    
    print(f"Loading QML from: {simple_qml}")
    
    # Load QML with error handling
    def on_warnings(warnings):
        for w in warnings:
            print(f"QML WARNING: {w.toString()}")
    
    engine.warnings.connect(on_warnings)
    engine.load(QUrl.fromLocalFile(str(simple_qml)))
    
    if not engine.rootObjects():
        print("ERROR: Failed to load QML file!")
        return 1
    
    # Show window
    root_objects = engine.rootObjects()
    if root_objects:
        window = root_objects[0]
        if isinstance(window, QQuickWindow):
            window.show()
            print("✅ Fancy UI loaded successfully!")
            print("Press Ctrl+C to exit")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
