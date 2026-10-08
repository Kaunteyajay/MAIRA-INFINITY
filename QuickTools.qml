import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: quickTools
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md
        
        Text {
            text: "QUICK TOOLS"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        // 4x3 Grid of tools
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: 4
            rows: 3
            columnSpacing: Theme.spacing.sm
            rowSpacing: Theme.spacing.sm
            
            Repeater {
                model: ListModel {
                    // Row 1
                    ListElement { name: "Google"; icon: "🔍"; available: true; url: "https://google.com" }
                    ListElement { name: "YouTube"; icon: "📺"; available: true; url: "https://youtube.com" }
                    ListElement { name: "GitHub"; icon: "🐙"; available: true; url: "https://github.com" }
                    ListElement { name: "Terminal"; icon: "⌨️"; available: true; app: "cmd" }
                    
                    // Row 2  
                    ListElement { name: "VS Code"; icon: "💻"; available: true; app: "code" }
                    ListElement { name: "Blender"; icon: "🎭"; available: false; app: "blender" }
                    ListElement { name: "Jupyter"; icon: "📓"; available: true; url: "http://localhost:8888" }
                    ListElement { name: "Docker"; icon: "🐳"; available: false; app: "docker" }
                    
                    // Row 3
                    ListElement { name: "Photoshop"; icon: "🎨"; available: false; app: "photoshop" }
                    ListElement { name: "Excel"; icon: "📊"; available: true; app: "excel" }
                    ListElement { name: "Word"; icon: "📝"; available: true; app: "winword" }
                    ListElement { name: "More..."; icon: "➕"; available: true; action: "show_more" }
                }
                
                delegate: ToolTile {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.preferredWidth: 80
                    Layout.preferredHeight: 60
                }
            }
        }
    }
}

component ToolTile: Rectangle {
    id: toolTile
    
    property string toolName: model.name
    property string toolIcon: model.icon
    property bool available: model.available
    property string toolUrl: model.url || ""
    property string toolApp: model.app || ""
    property string action: model.action || ""
    
    color: available ? Theme.colors.inputBg : Theme.colors.inputBg
    border.color: available ? Theme.colors.inputBorder : Theme.colors.textSecondary
    border.width: 1
    radius: Theme.effects.buttonRadius
    opacity: available ? 1.0 : 0.5
    
    Column {
        anchors.centerIn: parent
        spacing: Theme.spacing.xs
        
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: toolIcon
            font.pixelSize: 24
            opacity: available ? 1.0 : 0.6
        }
        
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: toolName
            color: available ? Theme.colors.textPrimary : Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        enabled: available
        
        onEntered: {
            parent.color = Qt.lighter(Theme.colors.inputBg, 1.2)
            parent.scale = 1.05
        }
        
        onExited: {
            parent.color = Theme.colors.inputBg
            parent.scale = 1.0
        }
        
        onClicked: {
            if (toolUrl) {
                console.log("Opening URL:", toolUrl)
                Qt.openUrlExternally(toolUrl)
            } else if (toolApp) {
                console.log("Launching app:", toolApp)
                // TODO: Implement app launching
            } else if (action === "show_more") {
                console.log("Showing more tools...")
                // TODO: Open tools catalog
            }
        }
    }
    
    // Tooltip for unavailable apps
    Rectangle {
        visible: !available && parent.hovered
        anchors.bottom: parent.top
        anchors.bottomMargin: Theme.spacing.xs
        anchors.horizontalCenter: parent.horizontalCenter
        
        width: tooltipText.width + Theme.spacing.sm * 2
        height: tooltipText.height + Theme.spacing.xs * 2
        
        color: Theme.colors.panelFill
        border.color: Theme.colors.panelBorder
        border.width: 1
        radius: 4
        
        Text {
            id: tooltipText
            anchors.centerIn: parent
            text: "Not installed"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
        }
    }
    
    Behavior on scale {
        PropertyAnimation { duration: Theme.effects.animationDuration }
    }
    
    Behavior on color {
        ColorAnimation { duration: Theme.effects.animationDuration }
    }
}