import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: realtimePanel
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    Column {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        Text {
            text: "REAL-TIME INTELLIGENCE"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        Grid {
            columns: 2
            spacing: Theme.spacing.md
            
            Repeater {
                model: ListModel {
                    ListElement { name: "Web Search"; active: true }
                    ListElement { name: "Code Execution"; active: true }
                    ListElement { name: "File Access"; active: false }
                    ListElement { name: "Internet Control"; active: false }
                    ListElement { name: "System Control"; active: false }
                    ListElement { name: "Learning Mode"; active: true }
                }
                
                delegate: Row {
                    spacing: Theme.spacing.sm
                    
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: model.active ? Theme.colors.okGreen : Theme.colors.textSecondary
                        anchors.verticalCenter: parent.verticalCenter
                        
                        SequentialAnimation on opacity {
                            running: model.active
                            loops: Animation.Infinite
                            PropertyAnimation { to: 0.4; duration: 1000 }
                            PropertyAnimation { to: 1.0; duration: 1000 }
                        }
                    }
                    
                    Text {
                        text: model.name
                        color: Theme.colors.textPrimary
                        font.family: Theme.fonts.primary
                        font.pixelSize: Theme.fonts.small
                    }
                    
                    Text {
                        text: model.active ? "Active" : "Inactive"
                        color: model.active ? Theme.colors.okGreen : Theme.colors.textSecondary
                        font.family: Theme.fonts.primary
                        font.pixelSize: Theme.fonts.tiny
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            model.active = !model.active
                            console.log("Toggled", model.name, "to", model.active ? "active" : "inactive")
                        }
                    }
                }
            }
        }
    }
}