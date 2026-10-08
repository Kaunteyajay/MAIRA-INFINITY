import QtQuick 2.15
import "../theme"

Column {
    spacing: Theme.spacing.md
    
    // Storage
    Column {
        spacing: Theme.spacing.xs
        
        Text {
            text: "STORAGE"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        Text {
            text: "2.4 TB / 4 TB"
            color: Theme.colors.textPrimary
            font.family: Theme.fonts.mono
            font.pixelSize: Theme.fonts.small
        }
        
        Rectangle {
            width: parent.width
            height: 4
            color: Theme.colors.inputBg
            radius: 2
            
            Rectangle {
                width: parent.width * 0.6
                height: parent.height
                color: Theme.colors.accentBlue
                radius: parent.radius
            }
        }
    }
    
    // GPU
    Column {
        spacing: Theme.spacing.xs
        
        Text {
            text: "GPU"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        Text {
            text: "RTX 5090 (Sim)"
            color: Theme.colors.textPrimary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.small
        }
        
        Row {
            spacing: Theme.spacing.xs
            
            Text {
                text: "67%"
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.mono
                font.pixelSize: Theme.fonts.small
            }
            
            Rectangle {
                width: 60
                height: 4
                color: Theme.colors.inputBg
                radius: 2
                anchors.verticalCenter: parent.verticalCenter
                
                Rectangle {
                    width: parent.width * 0.67
                    height: parent.height
                    color: Theme.colors.accentViolet
                    radius: parent.radius
                }
            }
        }
    }
}