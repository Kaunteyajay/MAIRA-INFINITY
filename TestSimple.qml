import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 800
    height: 600
    title: "MAIRA-∞ - Starting..."

    color: "#0a0e27"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0a0e27" }
            GradientStop { position: 1.0; color: "#1a1f3a" }
        }

        Column {
            anchors.centerIn: parent
            spacing: 30

            Text {
                text: "MAIRA-∞"
                font.pixelSize: 48
                font.bold: true
                color: "#00d9ff"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Limitless AI Desktop Assistant"
                font.pixelSize: 16
                color: "#8892b0"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                width: 300
                height: 4
                color: "#00d9ff"
                radius: 2
                anchors.horizontalCenter: parent.horizontalCenter

                SequentialAnimation on opacity {
                    running: true
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.3; duration: 1000 }
                    PropertyAnimation { to: 1.0; duration: 1000 }
                }
            }

            Text {
                text: "🎤 Press Ctrl+Space for voice input"
                font.pixelSize: 14
                color: "#00d9ff"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: "Status: Ready | Voice: Active | LLM: Connected"
                font.pixelSize: 12
                color: "#4ade80"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // Global shortcut for voice
    Shortcut {
        sequence: "Ctrl+Space"
        onActivated: {
            console.log("🎤 Voice input activated!")
        }
    }
}
