import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: timeSpace
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md
        
        Text {
            text: "TIME & SPACE"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        // Earth visualization
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            
            Rectangle {
                id: earth
                anchors.centerIn: parent
                width: 60
                height: 60
                radius: 30
                
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#4A90E2" }
                    GradientStop { position: 0.7; color: "#2E5C8A" }
                    GradientStop { position: 1.0; color: "#1A3A5C" }
                }
                
                // Continents (simplified)
                Rectangle {
                    x: 15
                    y: 20
                    width: 20
                    height: 15
                    radius: 8
                    color: "#2EE66B"
                    opacity: 0.8
                }
                
                Rectangle {
                    x: 35
                    y: 30
                    width: 15
                    height: 10
                    radius: 5
                    color: "#2EE66B"
                    opacity: 0.8
                }
                
                // Day/night terminator
                Rectangle {
                    anchors.fill: parent
                    radius: parent.radius
                    color: "black"
                    opacity: 0.3
                    
                    // Simulate day/night based on time
                    rotation: getCurrentRotation()
                    
                    function getCurrentRotation() {
                        var now = new Date()
                        var hours = now.getHours()
                        return (hours / 24) * 360
                    }
                }
                
                RotationAnimation on rotation {
                    duration: 86400000 // 24 hours
                    loops: Animation.Infinite
                    from: 0
                    to: 360
                }
            }
            
            Text {
                anchors.top: earth.bottom
                anchors.topMargin: Theme.spacing.xs
                anchors.horizontalCenter: earth.horizontalCenter
                text: "Earth"
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.tiny
            }
        }
        
        // Date and location info
        Column {
            Layout.fillWidth: true
            spacing: Theme.spacing.xs
            
            Text {
                text: getCurrentDate()
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                font.weight: Font.Medium
                
                function getCurrentDate() {
                    var now = new Date()
                    return now.toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    })
                }
            }
            
            Text {
                text: getCurrentTime()
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.mono
                font.pixelSize: Theme.fonts.small
                
                function getCurrentTime() {
                    var now = new Date()
                    return now.toLocaleTimeString('en-US') + " (UTC" + getUTCOffset() + ")"
                }
                
                function getUTCOffset() {
                    var now = new Date()
                    var offset = -now.getTimezoneOffset() / 60
                    return (offset >= 0 ? "+" : "") + offset
                }
            }
        }
        
        // Sun, Moon, Eclipse info
        Column {
            Layout.fillWidth: true
            spacing: Theme.spacing.xs
            
            InfoRow {
                icon: "☀️"
                label: "Sun"
                value: "06:42 AM"
            }
            
            InfoRow {
                icon: "🌙"
                label: "Moon"
                value: "10:15 PM"
            }
            
            InfoRow {
                icon: "🌑"
                label: "Next Eclipse"
                value: "12d 4h"
            }
        }
    }
    
    // Update time every second
    Timer {
        running: true
        repeat: true
        interval: 1000
        onTriggered: {
            // Force refresh of time displays
            timeSpace.children[0].children[2].children[1].text = Qt.binding(function() {
                var now = new Date()
                return now.toLocaleTimeString('en-US') + " (UTC" + getUTCOffset() + ")"
            })
        }
        
        function getUTCOffset() {
            var now = new Date()
            var offset = -now.getTimezoneOffset() / 60
            return (offset >= 0 ? "+" : "") + offset
        }
    }
}

// Reusable info row
component InfoRow: RowLayout {
    property string icon
    property string label  
    property string value
    
    Text {
        text: icon
        font.pixelSize: 14
        Layout.preferredWidth: 20
    }
    
    Text {
        text: label
        color: Theme.colors.textPrimary
        font.family: Theme.fonts.primary
        font.pixelSize: Theme.fonts.small
        Layout.preferredWidth: 60
    }
    
    Text {
        text: value
        color: Theme.colors.accentCyan
        font.family: Theme.fonts.mono
        font.pixelSize: Theme.fonts.small
    }
}