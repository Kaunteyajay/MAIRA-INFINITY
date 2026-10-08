import QtQuick 2.15
import "../theme"

Item {
    id: orbContainer
    
    // Central orb
    Rectangle {
        id: centralOrb
        anchors.centerIn: parent
        width: 40
        height: 40
        radius: 20
        
        gradient: Gradient {
            GradientStop { position: 0.0; color: Theme.colors.accentCyan }
            GradientStop { position: 1.0; color: Theme.colors.accentBlue }
        }
        
        // Pulsing animation
        SequentialAnimation on opacity {
            running: true
            loops: Animation.Infinite
            PropertyAnimation { to: 0.6; duration: 2000; easing.type: Easing.InOutSine }
            PropertyAnimation { to: 1.0; duration: 2000; easing.type: Easing.InOutSine }
        }
        
        // Inner glow
        Rectangle {
            anchors.centerIn: parent
            width: parent.width - 8
            height: parent.height - 8
            radius: width / 2
            color: "white"
            opacity: 0.3
        }
    }
    
    // Rotating rings around the orb
    Repeater {
        model: 3
        
        Rectangle {
            anchors.centerIn: parent
            width: 60 + (index * 20)
            height: width
            radius: width / 2
            color: "transparent"
            border.color: Theme.colors.accentViolet
            border.width: 1
            opacity: 0.5 - (index * 0.1)
            
            RotationAnimation on rotation {
                duration: 8000 + (index * 3000)
                loops: Animation.Infinite
                from: 0
                to: 360
            }
        }
    }
    
    // Floating small orbs
    Repeater {
        model: 6
        
        Rectangle {
            id: floatingOrb
            width: 4
            height: 4
            radius: 2
            color: Theme.colors.accentBlue
            
            property real angle: (index * 60) * Math.PI / 180
            property real distance: 50
            
            x: parent.width/2 + Math.cos(angle + orbRotation) * distance - width/2
            y: parent.height/2 + Math.sin(angle + orbRotation) * distance - height/2
            
            opacity: 0.7
        }
    }
    
    property real orbRotation: 0
    
    RotationAnimation on orbRotation {
        duration: 12000
        loops: Animation.Infinite
        from: 0
        to: 2 * Math.PI
    }
}