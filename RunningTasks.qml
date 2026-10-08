import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: runningTasks
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: "RUNNING TASKS"
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.tiny
                font.weight: Font.Bold
                Layout.fillWidth: true
            }
            
            Text {
                text: "View All"
                color: Theme.colors.accentBlue
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.tiny
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: console.log("View all tasks")
                }
            }
        }
        
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            Column {
                width: runningTasks.width - Theme.spacing.md * 2
                spacing: Theme.spacing.sm
                
                Repeater {
                    model: ListModel {
                        ListElement { 
                            title: "NEET Paper Analysis"
                            icon: "📝"
                            progress: 78
                            eta: "2 min"
                            status: "analyzing"
                        }
                        ListElement {
                            title: "Physics MCQs Generation" 
                            icon: "🧪"
                            progress: 45
                            eta: "5 min"
                            status: "generating"
                        }
                        ListElement {
                            title: "Code Compilation"
                            icon: "⚙️"
                            progress: 100
                            eta: "0 min"
                            status: "completed"
                        }
                        ListElement {
                            title: "3D Model Rendering"
                            icon: "🎭"
                            progress: 23
                            eta: "12 min"
                            status: "rendering"
                        }
                    }
                    
                    delegate: TaskRow {
                        width: parent.width
                    }
                }
            }
        }
    }
}

component TaskRow: Rectangle {
    id: taskRow
    
    property string taskTitle: model.title
    property string taskIcon: model.icon
    property real taskProgress: model.progress
    property string taskEta: model.eta
    property string taskStatus: model.status
    
    height: 50
    color: "transparent"
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.xs
        spacing: Theme.spacing.sm
        
        // Icon
        Text {
            text: taskIcon
            font.pixelSize: 16
            Layout.preferredWidth: 20
        }
        
        // Task info
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            
            Text {
                text: taskTitle
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm
                
                // Progress bar
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 4
                    color: Theme.widgets.progressTrack
                    radius: 2
                    
                    Rectangle {
                        width: parent.width * (taskProgress / 100)
                        height: parent.height
                        color: getProgressColor()
                        radius: parent.radius
                        
                        function getProgressColor() {
                            if (taskStatus === "completed") return Theme.widgets.progressSuccess
                            if (taskStatus === "error") return Theme.widgets.progressError
                            return Theme.widgets.progressFill
                        }
                        
                        Behavior on width {
                            PropertyAnimation { duration: 500 }
                        }
                    }
                }
                
                // Progress text
                Text {
                    text: taskProgress + "%"
                    color: Theme.colors.textSecondary
                    font.family: Theme.fonts.mono
                    font.pixelSize: Theme.fonts.tiny
                    Layout.preferredWidth: 35
                }
                
                // ETA
                Text {
                    text: taskEta
                    color: Theme.colors.textSecondary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.tiny
                    Layout.preferredWidth: 40
                }
            }
        }
        
        // Action button (pause/cancel)
        Rectangle {
            width: 16
            height: 16
            radius: 8
            color: "transparent"
            border.color: Theme.colors.textSecondary
            border.width: 1
            
            Text {
                anchors.centerIn: parent
                text: taskStatus === "completed" ? "✓" : "⏸"
                color: Theme.colors.textSecondary
                font.pixelSize: 8
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (taskStatus !== "completed") {
                        console.log("Pausing task:", taskTitle)
                    }
                }
            }
        }
    }
    
    // Simulate progress updates
    Timer {
        running: taskStatus !== "completed" && taskStatus !== "error"
        repeat: true
        interval: 2000
        
        onTriggered: {
            if (taskProgress < 100) {
                model.progress = Math.min(100, taskProgress + Math.random() * 10)
                if (model.progress >= 100) {
                    model.status = "completed"
                    model.eta = "0 min"
                }
            }
        }
    }
}