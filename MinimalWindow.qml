import QtQuick 2.15
import QtQuick.Window 2.15

Window {
    id: mainWindow
    visible: true
    width: 900
    height: 650
    title: "MAIRA-∞ - Limitless AI Assistant"
    color: "#0a0e27"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0a0e27" }
            GradientStop { position: 1.0; color: "#1a1f3a" }
        }

        Column {
            anchors.centerIn: parent
            spacing: 40

            // Logo
            Rectangle {
                width: 120
                height: 120
                radius: 60
                color: "#00d9ff"
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    anchors.centerIn: parent
                    text: "M"
                    font.pixelSize: 64
                    font.bold: true
                    color: "#0a0e27"
                }

                SequentialAnimation on opacity {
                    running: true
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.6; duration: 1500 }
                    PropertyAnimation { to: 1.0; duration: 1500 }
                }
            }

            // Title
            Text {
                text: "MAIRA-∞"
                font.pixelSize: 52
                font.bold: true
                color: "#00d9ff"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Limitless AI Desktop Assistant"
                font.pixelSize: 18
                color: "#8892b0"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            // Loading bar
            Rectangle {
                width: 400
                height: 6
                color: "#1a1f3a"
                radius: 3
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    id: progressBar
                    width: parent.width * 0.7
                    height: parent.height
                    color: "#00d9ff"
                    radius: 3

                    SequentialAnimation on width {
                        running: true
                        loops: Animation.Infinite
                        PropertyAnimation { to: parent.parent.width * 0.3; duration: 2000 }
                        PropertyAnimation { to: parent.parent.width * 0.95; duration: 2000 }
                    }
                }
            }

            // Status
            Column {
                spacing: 15
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    text: "✅ Voice: Ready (Whisper + Edge-TTS)"
                    font.pixelSize: 14
                    color: "#4ade80"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "✅ LLM: Connected (Google Gemini)"
                    font.pixelSize: 14
                    color: "#4ade80"
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "✅ Tools: Web Search Active"
                    font.pixelSize: 14
                    color: "#4ade80"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            // Instructions
            Rectangle {
                width: 500
                height: 80
                color: "#1a2332"
                radius: 10
                border.color: "#00d9ff"
                border.width: 2
                anchors.horizontalCenter: parent.horizontalCenter

                Column {
                    anchors.centerIn: parent
                    spacing: 10

                    Text {
                        text: "🎤 Press Ctrl+Space for Voice Input"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#00d9ff"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: "Say: \"Hello MAIRA\" or ask any question!"
                        font.pixelSize: 12
                        color: "#8892b0"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        // Footer
        Text {
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 20
            text: "MAIRA v12.7.3 | Powered by Gemini + Whisper + Edge-TTS"
            font.pixelSize: 11
            color: "#4a5568"
        }
    }
}
