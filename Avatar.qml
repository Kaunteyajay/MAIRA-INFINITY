import QtQuick 2.15
import "../theme"

Item {
    id: avatarRoot
    
    property string currentState: "idle"  // idle, listening, thinking, speaking, sleeping
    property string emotion: "neutral"    // neutral, happy, curious, concerned
    property real audioLevel: 0.0         // 0.0 to 1.0 for lip-sync
    
    // Avatar base image (placeholder - will be replaced with layered system)
    Rectangle {
        id: avatarBody
        anchors.fill: parent
        color: "transparent"
        
        // Simplified avatar representation for now
        Rectangle {
            id: head
            width: 120
            height: 160
            anchors.centerIn: parent
            radius: 60
            
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#E8D5F0" }
                GradientStop { position: 1.0; color: "#D4C2E0" }
            }
            
            // Eyes
            Row {
                anchors.centerIn: parent
                anchors.verticalCenterOffset: -20
                spacing: 30
                
                Repeater {
                    model: 2
                    
                    Rectangle {
                        id: eye
                        width: 12
                        height: currentState === "sleeping" ? 2 : 12
                        radius: width / 2
                        color: Theme.colors.accentBlue
                        
                        // Blinking animation
                        SequentialAnimation on height {
                            running: currentState !== "sleeping"
                            loops: Animation.Infinite
                            
                            PropertyAnimation { to: 12; duration: 3000 }
                            PropertyAnimation { to: 2; duration: 100 }
                            PropertyAnimation { to: 12; duration: 100 }
                            PropertyAnimation { to: 12; duration: 2000 }
                        }
                        
                        // Glow effect
                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width + 4
                            height: parent.height + 4
                            radius: width / 2
                            color: "transparent"
                            border.color: Theme.colors.accentBlue
                            border.width: 1
                            opacity: 0.6
                        }
                    }
                }
            }
            
            // Mouth for lip-sync
            Rectangle {
                id: mouth
                anchors.centerIn: parent
                anchors.verticalCenterOffset: 30
                width: getMouthWidth()
                height: getMouthHeight()
                radius: width / 2
                color: "#B8A5C5"
                
                function getMouthWidth() {
                    if (currentState === "speaking") {
                        return 8 + (audioLevel * 12)  // Reactive to audio
                    } else if (emotion === "happy") {
                        return 16
                    }
                    return 6
                }
                
                function getMouthHeight() {
                    if (currentState === "speaking") {
                        return 4 + (audioLevel * 8)
                    } else if (emotion === "happy") {
                        return 8
                    }
                    return 3
                }
                
                Behavior on width { PropertyAnimation { duration: 100 } }
                Behavior on height { PropertyAnimation { duration: 100 } }
            }
            
            // Forehead gem
            Rectangle {
                anchors.centerIn: parent
                anchors.verticalCenterOffset: -60
                width: 8
                height: 8
                radius: 4
                color: Theme.colors.accentCyan
                
                // Brightness varies with state
                opacity: currentState === "listening" ? 1.0 : 0.7
                
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width + 6
                    height: parent.height + 6
                    radius: width / 2
                    color: "transparent"
                    border.color: Theme.colors.accentCyan
                    border.width: 1
                    opacity: 0.4
                }
                
                Behavior on opacity { PropertyAnimation { duration: 200 } }
            }
        }
        
        // Hair (simplified)
        Rectangle {
            anchors.centerIn: head
            anchors.verticalCenterOffset: -40
            width: head.width + 20
            height: 100
            radius: 50
            color: Theme.avatar.hairColor
            opacity: 0.8
            z: -1
            
            // Gentle swaying animation
            SequentialAnimation on rotation {
                running: true
                loops: Animation.Infinite
                PropertyAnimation { to: -2; duration: 3000; easing.type: Easing.InOutSine }
                PropertyAnimation { to: 2; duration: 3000; easing.type: Easing.InOutSine }
            }
        }
        
        // Shoulders/armor (simplified)
        Rectangle {
            anchors.top: head.bottom
            anchors.topMargin: -20
            anchors.horizontalCenter: head.horizontalCenter
            width: 160
            height: 80
            radius: 20
            color: "#2A3B5F"
            opacity: 0.8
            
            // Holographic lines
            Repeater {
                model: 3
                
                Rectangle {
                    x: 20 + (index * 40)
                    y: 20
                    width: 30
                    height: 2
                    color: Theme.colors.accentBlue
                    opacity: 0.6
                    
                    SequentialAnimation on opacity {
                        running: true
                        loops: Animation.Infinite
                        PropertyAnimation { to: 0.2; duration: 1000 + (index * 300) }
                        PropertyAnimation { to: 0.8; duration: 1000 + (index * 300) }
                    }
                }
            }
        }
    }
    
    onCurrentStateChanged: {
        console.log("Avatar state:", currentState)
    }
}