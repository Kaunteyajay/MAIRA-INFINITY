import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: greetingCard
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    opacity: Theme.effects.panelOpacity
    
    property string currentMessage: "Hello, I am MAIRA."
    property bool isListening: false
    property bool isSpeaking: false
    property real audioLevel: 0.0
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        // Main greeting text
        Text {
            text: currentMessage
            color: Theme.colors.textPrimary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.heading
            font.weight: Font.Bold
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Subtitle
        Text {
            text: "Your limitless AI companion, ready to assist with anything you need."
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.body
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Voice waveform visualization
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            color: "transparent"
            
            Row {
                anchors.centerIn: parent
                spacing: 2
                
                Repeater {
                    model: 20
                    
                    Rectangle {
                        width: 3
                        height: getBarHeight(index)
                        color: Theme.colors.accentCyan
                        radius: 1.5
                        
                        function getBarHeight(barIndex) {
                            if (isSpeaking) {
                                // Animate bars based on audio level and position
                                var baseHeight = 4
                                var maxHeight = 24
                                var wave = Math.sin((barIndex * 0.5) + (waveOffset * 0.1))
                                return baseHeight + (wave * audioLevel * (maxHeight - baseHeight))
                            } else if (isListening) {
                                // Listening pattern
                                return 8 + Math.random() * 8
                            } else {
                                // Idle - flat line
                                return 4
                            }
                        }
                        
                        Behavior on height {
                            PropertyAnimation { duration: 100 }
                        }
                    }
                }
            }
        }
        
        // Status indicator
        Row {
            Layout.alignment: Qt.AlignRight
            spacing: Theme.spacing.sm
            
            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: getStatusColor()
                
                function getStatusColor() {
                    if (isSpeaking) return Theme.colors.accentBlue
                    if (isListening) return Theme.colors.warnAmber
                    return Theme.colors.okGreen
                }
                
                SequentialAnimation on opacity {
                    running: isListening || isSpeaking
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.3; duration: 500 }
                    PropertyAnimation { to: 1.0; duration: 500 }
                }
            }
            
            Text {
                text: getStatusText()
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                
                function getStatusText() {
                    if (isSpeaking) return "Speaking..."
                    if (isListening) return "Listening..."
                    return "Ready"
                }
            }
        }
    }
    
    property real waveOffset: 0
    
    // Animate waveform
    Timer {
        running: isSpeaking
        repeat: true
        interval: 50
        onTriggered: {
            waveOffset += 1
            audioLevel = 0.3 + Math.random() * 0.7
        }
    }
    
    // Demo state changes
    Timer {
        running: true
        repeat: true
        interval: 3000
        
        onTriggered: {
            var messages = [
                "Hello, I am MAIRA.",
                "How can I assist you today?",
                "Ready for your next command.",
                "Let's explore the universe together."
            ]
            currentMessage = messages[Math.floor(Math.random() * messages.length)]
        }
    }
}