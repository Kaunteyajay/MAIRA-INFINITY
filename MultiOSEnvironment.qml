import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: multiOS
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        Text {
            text: "MULTI-OS ENVIRONMENT"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        Column {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.sm
            
            Repeater {
                model: ListModel {
                    ListElement {
                        name: "Windows 11"
                        icon: "🪟"
                        status: "active"
                        color: "#0078d4"
                    }
                    ListElement {
                        name: "Ubuntu"
                        icon: "🐧"
                        status: "ready"
                        color: "#E95420"
                    }
                    ListElement {
                        name: "Kali Linux"
                        icon: "🛡️"
                        status: "ready"
                        color: "#367588"
                    }
                    ListElement {
                        name: "macOS"
                        icon: "🍎"
                        status: "unavailable"
                        color: "#007AFF"
                    }
                }
                
                delegate: OSCard {
                    width: parent.width
                    height: 45
                }
            }
        }
    }
}

component OSCard: Rectangle {
    id: osCard
    
    property string osName: model.name
    property string osIcon: model.icon
    property string osStatus: model.status
    property color osColor: model.color
    
    color: osStatus === "active" ? Qt.rgba(osColor.r, osColor.g, osColor.b, 0.2) : Theme.colors.inputBg
    border.color: osStatus === "active" ? osColor : Theme.colors.inputBorder
    border.width: 1
    radius: Theme.effects.buttonRadius
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.md
        
        // Icon
        Text {
            text: osIcon
            font.pixelSize: 20
            Layout.preferredWidth: 24
        }
        
        // OS name and status
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                text: osName
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                font.weight: Font.Medium
            }
            
            Text {
                text: getStatusText()
                color: getStatusColor()
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.tiny
                
                function getStatusText() {
                    switch(osStatus) {
                        case "active": return "Active"
                        case "ready": return "Ready"
                        case "unavailable": return "Unavailable"
                        default: return "Off"
                    }
                }
                
                function getStatusColor() {
                    switch(osStatus) {
                        case "active": return Theme.colors.okGreen
                        case "ready": return Theme.colors.infoBlue
                        case "unavailable": return Theme.colors.textSecondary
                        default: return Theme.colors.warnAmber
                    }
                }
            }
        }
        
        // Status indicator
        Rectangle {
            width: 8
            height: 8
            radius: 4
            color: getIndicatorColor()
            
            function getIndicatorColor() {
                switch(osStatus) {
                    case "active": return Theme.colors.okGreen
                    case "ready": return Theme.colors.infoBlue
                    case "unavailable": return Theme.colors.textSecondary
                    default: return Theme.colors.warnAmber
                }
            }
            
            SequentialAnimation on opacity {
                running: osStatus === "active"
                loops: Animation.Infinite
                PropertyAnimation { to: 0.3; duration: 1000 }
                PropertyAnimation { to: 1.0; duration: 1000 }
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        enabled: osStatus !== "unavailable"
        hoverEnabled: true
        
        onEntered: {
            if (osStatus !== "unavailable") {
                parent.color = Qt.lighter(parent.color, 1.2)
            }
        }
        
        onExited: {
            parent.color = osStatus === "active" ? 
                Qt.rgba(osColor.r, osColor.g, osColor.b, 0.2) : 
                Theme.colors.inputBg
        }
        
        onClicked: {
            if (osStatus === "ready") {
                console.log("Starting OS:", osName)
                // TODO: Implement VM start
            } else if (osStatus === "active") {
                console.log("Switching to OS:", osName)
                // TODO: Implement OS switch
            }
        }
    }
}