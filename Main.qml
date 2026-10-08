import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import MAIRA.Core 1.0
import "theme"
import "components"
import "pages"

ApplicationWindow {
    id: mainWindow
    
    width: 1312
    height: 1199
    minimumWidth: 1280
    minimumHeight: 720
    
    title: "MAIRA-∞ - Limitless AI Desktop Assistant"
    
    color: Theme.colors.bgDeep
    
    // Background with space/nebula effect
    Rectangle {
        anchors.fill: parent
        color: Theme.colors.bgDeep
        
        // Space background gradient
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.colors.bgSpace }
                GradientStop { position: 1.0; color: Theme.colors.bgDeep }
            }
        }
        
        // Animated particles (stars)
        Repeater {
            model: 100
            
            Rectangle {
                width: Math.random() * 3 + 1
                height: width
                color: Theme.colors.textSecondary
                opacity: Math.random() * 0.7 + 0.3
                radius: width / 2
                
                x: Math.random() * mainWindow.width
                y: Math.random() * mainWindow.height
                
                // Twinkling animation
                SequentialAnimation on opacity {
                    running: true
                    loops: Animation.Infinite
                    PropertyAnimation {
                        to: 0.2
                        duration: Math.random() * 2000 + 1000
                        easing.type: Easing.InOutSine
                    }
                    PropertyAnimation {
                        to: 0.8
                        duration: Math.random() * 2000 + 1000
                        easing.type: Easing.InOutSine
                    }
                }
            }
        }
    }
    
    // Main layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top Bar
        TopBar {
            Layout.fillWidth: true
            Layout.preferredHeight: 45
        }
        
        // Main content area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            
            // Left Sidebar
            Sidebar {
                Layout.preferredWidth: 210
                Layout.fillHeight: true
            }
            
            // Center content
            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                // Load the current page
                Loader {
                    id: pageLoader
                    anchors.fill: parent
                    source: "pages/Home.qml"
                }
            }
            
            // Right column widgets (only on Home page)
            Loader {
                Layout.preferredWidth: 380
                Layout.fillHeight: true
                active: pageLoader.source.toString().includes("Home.qml")
                
                sourceComponent: RightColumn {
                    
                }
            }
        }
        
        // Bottom action cards
        BottomCards {
            Layout.fillWidth: true
            Layout.preferredHeight: 150
        }
    }
    
    // Global key handlers
    Shortcut {
        sequence: "Ctrl+Space"
        onActivated: {
            console.log("Push-to-talk activated")
            // TODO: Implement voice activation
        }
    }
    
    Shortcut {
        sequence: "F11"
        onActivated: {
            if (mainWindow.visibility === Window.FullScreen) {
                mainWindow.showNormal()
            } else {
                mainWindow.showFullScreen()
            }
        }
    }
    
    // Status connections
    Connections {
        target: WindowController
        
        function onStatusChanged() {
            console.log("Application status changed:", WindowController.status)
        }
    }
}