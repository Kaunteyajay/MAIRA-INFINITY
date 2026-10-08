import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Rectangle {
    id: sidebarItem
    
    property bool isActive: false
    property string icon: model.icon
    property string title: model.title
    property string subtitle: model.subtitle
    
    signal clicked()
    
    height: 48
    radius: Theme.effects.buttonRadius
    color: isActive ? Theme.colors.accentBlue : (mouseArea.containsMouse ? Theme.colors.buttonHover : "transparent")
    
    // Glow effect for active item
    Rectangle {
        anchors.fill: parent
        anchors.margins: -2
        radius: parent.radius + 2
        color: "transparent"
        border.color: Theme.colors.accentBlue
        border.width: 1
        opacity: isActive ? 0.5 : 0
        visible: isActive
        
        Behavior on opacity {
            PropertyAnimation { duration: Theme.effects.animationDuration }
        }
    }
    
    Row {
        anchors.left: parent.left
        anchors.leftMargin: Theme.spacing.md
        anchors.verticalCenter: parent.verticalCenter
        spacing: Theme.spacing.md
        
        // Icon
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: icon
            font.pixelSize: 20
            color: isActive ? "white" : Theme.colors.accentBlue
        }
        
        // Text
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2
            
            Text {
                text: title
                color: isActive ? "white" : Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.navTitle
                font.weight: Font.Medium
            }
            
            Text {
                text: subtitle
                color: isActive ? "#E0E0E0" : Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
            }
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        
        onClicked: parent.clicked()
    }
    
    Behavior on color {
        ColorAnimation { duration: Theme.effects.animationDuration }
    }
}