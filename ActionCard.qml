import QtQuick 2.15
import "../theme"

Rectangle {
    id: actionCard
    
    property string title: model.title
    property string subtitle: model.subtitle  
    property string icon: model.icon
    property string module: model.module
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    // Glow effect
    Rectangle {
        anchors.fill: parent
        anchors.margins: -Theme.effects.glowRadius / 2
        radius: parent.radius + Theme.effects.glowRadius / 2
        color: "transparent"
        border.color: Theme.colors.panelGlow
        border.width: 1
        opacity: 0
        
        Behavior on opacity {
            PropertyAnimation { duration: Theme.effects.animationDuration }
        }
    }
    
    Row {
        anchors.left: parent.left
        anchors.leftMargin: Theme.spacing.md
        anchors.verticalCenter: parent.verticalCenter
        spacing: Theme.spacing.md
        
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: icon
            font.pixelSize: 32
        }
        
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: Theme.spacing.xs
            
            Text {
                text: title
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.panelTitle
                font.weight: Font.Bold
            }
            
            Text {
                text: subtitle
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onEntered: {
            parent.children[0].opacity = 0.6
            parent.scale = 1.02
        }
        
        onExited: {
            parent.children[0].opacity = 0
            parent.scale = 1.0
        }
        
        onClicked: {
            console.log("Action card clicked:", module)
            // TODO: Switch to module
        }
    }
    
    Behavior on scale {
        PropertyAnimation { duration: Theme.effects.animationDuration }
    }
}