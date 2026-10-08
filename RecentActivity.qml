import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: recentActivity
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        Text {
            text: "RECENT ACTIVITY"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            Column {
                width: recentActivity.width - Theme.spacing.md * 2
                spacing: Theme.spacing.xs
                
                Repeater {
                    model: ListModel {
                        ListElement {
                            time: "19:01"
                            action: "Web search query"
                            status: "12 sources found"
                            statusType: "info"
                        }
                        ListElement {
                            time: "18:58"
                            action: "Python script execution"
                            status: "Completed"
                            statusType: "success"
                        }
                        ListElement {
                            time: "18:56"
                            action: "File analysis: Biology_Notes.pdf"
                            status: "Opened"
                            statusType: "info"
                        }
                        ListElement {
                            time: "18:54"
                            action: "Voice command processed"
                            status: "Success"
                            statusType: "success"
                        }
                        ListElement {
                            time: "18:52"
                            action: "Code compilation"
                            status: "Failed"
                            statusType: "error"
                        }
                        ListElement {
                            time: "18:50"
                            action: "Image generation"
                            status: "Rendering..."
                            statusType: "progress"
                        }
                    }
                    
                    delegate: ActivityRow {
                        width: parent.width
                    }
                }
            }
        }
    }
}

component ActivityRow: Item {
    height: 24
    
    property string activityTime: model.time
    property string activityAction: model.action
    property string activityStatus: model.status
    property string statusType: model.statusType
    
    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacing.sm
        
        // Timestamp
        Text {
            text: "[" + activityTime + "]"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.mono
            font.pixelSize: Theme.fonts.tiny
            Layout.preferredWidth: 45
        }
        
        // Action description
        Text {
            text: activityAction
            color: Theme.colors.textPrimary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            elide: Text.ElideRight
            Layout.fillWidth: true
        }
        
        // Arrow
        Text {
            text: "→"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            Layout.preferredWidth: 15
        }
        
        // Status
        Text {
            text: activityStatus
            color: getStatusColor()
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            Layout.preferredWidth: 80
            
            function getStatusColor() {
                switch(statusType) {
                    case "success": return Theme.colors.okGreen
                    case "error": return Theme.colors.danger
                    case "progress": return Theme.colors.infoBlue
                    case "info": return Theme.colors.infoBlue
                    default: return Theme.colors.textSecondary
                }
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onEntered: parent.color = Theme.colors.inputBg
        onExited: parent.color = "transparent"
        onClicked: console.log("Activity details:", activityAction)
    }
}