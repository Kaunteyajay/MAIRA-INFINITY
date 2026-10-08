import QtQuick 2.15
import "../theme"

Column {
    spacing: Theme.spacing.sm
    
    Text {
        text: "ACTIVE SESSIONS"
        color: Theme.colors.textSecondary
        font.family: Theme.fonts.primary
        font.pixelSize: Theme.fonts.tiny
        font.weight: Font.Bold
    }
    
    Column {
        spacing: Theme.spacing.xs
        
        Repeater {
            model: ListModel {
                ListElement { name: "Python REPL"; status: "running"; color: "#2EE66B" }
                ListElement { name: "Web Search"; status: "active"; color: "#4DA3FF" }
                ListElement { name: "File Monitor"; status: "idle"; color: "#FFC247" }
            }
            
            delegate: Row {
                spacing: Theme.spacing.sm
                
                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: model.color
                    anchors.verticalCenter: parent.verticalCenter
                }
                
                Text {
                    text: model.name
                    color: Theme.colors.textPrimary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.small
                }
                
                Text {
                    text: model.status
                    color: Theme.colors.textSecondary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.tiny
                }
            }
        }
    }
}