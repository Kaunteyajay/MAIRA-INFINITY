import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import MAIRA.Core 1.0
import "../theme"

Rectangle {
    id: topBar
    
    color: "transparent"
    
    // Subtle bottom border
    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 1
        color: Theme.colors.panelBorder
        opacity: 0.3
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        
        // Left section - Logo & Title
        RowLayout {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacing.md
            
            // Logo (placeholder)
            Rectangle {
                width: 32
                height: 32
                radius: 16
                color: Theme.colors.accentBlue
                
                Text {
                    anchors.centerIn: parent
                    text: "M"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 18
                }
                
                // Glow effect
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width + 4
                    height: parent.height + 4
                    radius: (parent.width + 4) / 2
                    color: "transparent"
                    border.color: Theme.colors.accentBlue
                    border.width: 2
                    opacity: 0.5
                    
                    SequentialAnimation on opacity {
                        running: true
                        loops: Animation.Infinite
                        PropertyAnimation { to: 0.2; duration: 2000 }
                        PropertyAnimation { to: 0.8; duration: 2000 }
                    }
                }
            }
            
            Column {
                spacing: 0
                
                Text {
                    text: "MAIRA-∞"
                    color: Theme.colors.textPrimary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.panelTitle
                    font.bold: true
                }
                
                Text {
                    text: "Quantum AI Assistant"
                    color: Theme.colors.textSecondary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.tiny
                }
            }
        }
        
        // Status indicator
        RowLayout {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacing.sm
            
            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: Theme.colors.okGreen
                
                SequentialAnimation on opacity {
                    running: WindowController.status === "Online"
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.4; duration: 1000 }
                    PropertyAnimation { to: 1.0; duration: 1000 }
                }
            }
            
            Text {
                text: WindowController.status
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
            }
        }
        
        // Center section - Version info
        Item {
            Layout.fillWidth: true
            
            Text {
                anchors.centerIn: parent
                text: `v${WindowController.version} | Python Core | Neural-Quantum Hybrid`
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                horizontalAlignment: Text.AlignHCenter
            }
        }
        
        // Right section - Status icons and time
        RowLayout {
            Layout.alignment: Qt.AlignVCenter
            spacing: Theme.spacing.lg
            
            // Status icons
            RowLayout {
                spacing: Theme.spacing.sm
                
                // Mic status
                StatusIcon {
                    iconChar: "M"
                    active: false
                    clickable: true
                }
                
                // AI status
                StatusIcon {
                    iconChar: "🧠"
                    active: true
                    // tooltip: "AI: Ready"
                }
                
                // Network status
                StatusIcon {
                    iconChar: "📶"
                    active: true
                    // tooltip: "Network: Connected"
                }
                
                // Brightness
                StatusIcon {
                    iconChar: "☀"
                    active: true
                    // tooltip: "Brightness: Auto"
                }
                
                // Settings
                StatusIcon {
                    iconChar: "⚙"
                    active: false
                    // tooltip: "Settings"
                    clickable: true
                }
            }
            
            // Date and time
            Column {
                Layout.alignment: Qt.AlignVCenter
                
                Text {
                    id: dateText
                    color: Theme.colors.textPrimary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.small
                    horizontalAlignment: Text.AlignRight
                }
                
                Text {
                    id: timeText
                    color: Theme.colors.textSecondary
                    font.family: Theme.fonts.mono
                    font.pixelSize: Theme.fonts.small
                    horizontalAlignment: Text.AlignRight
                }
            }
        }
    }
    
    // Update time every second
    Timer {
        running: true
        repeat: true
        interval: 1000
        
        onTriggered: {
            var now = new Date()
            dateText.text = now.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short', 
                day: '2-digit',
                year: 'numeric'
            })
            timeText.text = now.toLocaleTimeString('en-US', {
                hour12: true,
                hour: '2-digit',
                minute: '2-digit', 
                second: '2-digit'
            })
        }
    }
    
    Component.onCompleted: {
        // Initialize time display
        var now = new Date()
        dateText.text = now.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: '2-digit', 
            year: 'numeric'
        })
        timeText.text = now.toLocaleTimeString('en-US', {
            hour12: true,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        })
    }
}