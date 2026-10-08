import QtQuick 2.15
import QtQuick.Particles 2.15
import "../theme"

Rectangle {
    id: avatarStage
    
    color: "transparent"
    
    // Background space effect
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        
        // Particle system for space effect
        ParticleSystem {
            anchors.fill: parent
            
            ImageParticle {
                source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4'%3E%3Ccircle cx='2' cy='2' r='1' fill='%23FFFFFF'/%3E%3C/svg%3E"
                alpha: 0.6
                colorVariation: 0.2
            }
            
            Emitter {
                anchors.fill: parent
                emitRate: 30
                lifeSpan: 8000
                lifeSpanVariation: 2000
                
                velocity: AngleDirection {
                    angle: 90
                    angleVariation: 15
                    magnitude: 20
                    magnitudeVariation: 10
                }
                
                size: 2
                sizeVariation: 1
            }
        }
    }
    
    // Avatar container
    Item {
        anchors.centerIn: parent
        width: 300
        height: 400
        
        // Halo rings behind avatar
        Item {
            anchors.centerIn: parent
            width: 350
            height: 350
            
            Repeater {
                model: 3
                
                Rectangle {
                    id: haloRing
                    anchors.centerIn: parent
                    width: 100 + (index * 60)
                    height: width
                    radius: width / 2
                    color: "transparent"
                    border.color: Theme.colors.accentBlue
                    border.width: 2
                    opacity: 0.6 - (index * 0.15)
                    
                    RotationAnimation on rotation {
                        duration: 15000 + (index * 5000)
                        loops: Animation.Infinite
                        from: 0
                        to: 360
                    }
                    
                    // Pulsing effect
                    SequentialAnimation on opacity {
                        running: true
                        loops: Animation.Infinite
                        PropertyAnimation {
                            to: 0.2 - (index * 0.05)
                            duration: 2000 + (index * 500)
                            easing.type: Easing.InOutSine
                        }
                        PropertyAnimation {
                            to: 0.8 - (index * 0.1)
                            duration: 2000 + (index * 500)
                            easing.type: Easing.InOutSine
                        }
                    }
                }
            }
        }
        
        // Avatar bound to avatarModel from Python backend
        Avatar {
            id: avatar
            anchors.centerIn: parent
            width: 200
            height: 280
            currentState: (typeof avatarModel !== "undefined" && avatarModel !== null)
                          ? avatarModel.currentState : "idle"
            emotion:      (typeof avatarModel !== "undefined" && avatarModel !== null)
                          ? avatarModel.emotion : "neutral"
            audioLevel:   (typeof avatarModel !== "undefined" && avatarModel !== null)
                          ? avatarModel.audioLevel : 0.0
        }
        
        // Holographic orb below avatar
        HolographicOrb {
            anchors.top: avatar.bottom
            anchors.topMargin: 20
            anchors.horizontalCenter: avatar.horizontalCenter
            width: 120
            height: 120
        }
    }
    
    // Greeting card bound to avatar state
    GreetingCard {
        anchors.top: parent.top
        anchors.topMargin: Theme.spacing.lg
        anchors.left: parent.left
        anchors.leftMargin: Theme.spacing.lg
        width: 300
        height: 100
        isListening: (typeof avatarModel !== "undefined" && avatarModel !== null)
                     ? avatarModel.currentState === "listening" : false
        isSpeaking:  (typeof avatarModel !== "undefined" && avatarModel !== null)
                     ? avatarModel.currentState === "speaking" : false
        audioLevel:  (typeof avatarModel !== "undefined" && avatarModel !== null)
                     ? avatarModel.audioLevel : 0.0
    }
}