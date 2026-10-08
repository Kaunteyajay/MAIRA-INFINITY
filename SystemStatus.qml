import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: systemStatus
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    property real cpuPercent:    (typeof systemStatusModel !== "undefined") ? systemStatusModel.cpuPercent    : 0.0
    property real memoryPercent: (typeof systemStatusModel !== "undefined") ? systemStatusModel.memoryPercent : 0.0
    property real gpuPercent:    (typeof systemStatusModel !== "undefined") ? systemStatusModel.gpuPercent    : 0.0
    property real networkSpeed:  (typeof systemStatusModel !== "undefined") ? systemStatusModel.networkSpeed  : 0.0
    property int  processCount:  (typeof systemStatusModel !== "undefined") ? systemStatusModel.processCount  : 0
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm
        
        Text {
            text: "SYSTEM STATUS"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            font.weight: Font.Bold
        }
        
        // CPU
        MetricRow {
            Layout.fillWidth: true
            label: "CPU"
            value: cpuPercent.toFixed(1) + "%"
            percentage: cpuPercent / 100
            color: Theme.widgets.cpuColor
        }
        
        // Memory
        MetricRow {
            Layout.fillWidth: true
            label: "RAM"
            value: memoryPercent.toFixed(1) + "%"
            percentage: memoryPercent / 100
            color: Theme.widgets.memoryColor
        }
        
        // GPU
        MetricRow {
            Layout.fillWidth: true
            label: "GPU"
            value: gpuPercent.toFixed(1) + "%"
            percentage: gpuPercent / 100
            color: Theme.widgets.gpuColor
        }
        
        // Network
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: "Network"
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                Layout.preferredWidth: 60
            }
            
            Text {
                text: networkSpeed.toFixed(2) + " MB/s"
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.mono
                font.pixelSize: Theme.fonts.small
            }
        }
        
        // Processes
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                text: "Processes"
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
            }
            
            Text {
                text: processCount.toString()
                color: Theme.colors.textPrimary
                font.family: Theme.fonts.mono
                font.pixelSize: Theme.fonts.small
            }
        }
    }
}

component MetricRow: RowLayout {
    property string label
    property string value
    property real percentage: 0.0
    property color color: Theme.colors.accentBlue
    
    Text {
        text: label
        color: Theme.colors.textPrimary
        font.family: Theme.fonts.primary
        font.pixelSize: Theme.fonts.small
        Layout.preferredWidth: 40
    }
    
    Text {
        text: value
        color: Theme.colors.textPrimary
        font.family: Theme.fonts.mono
        font.pixelSize: Theme.fonts.small
        Layout.preferredWidth: 50
    }
    
    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 6
        color: Theme.widgets.progressTrack
        radius: 3
        
        Rectangle {
            width: parent.width * percentage
            height: parent.height
            color: getProgressColor()
            radius: parent.radius
            
            function getProgressColor() {
                if (percentage > 0.9) return Theme.widgets.progressError
                if (percentage > 0.8) return Theme.widgets.progressWarning
                return color
            }
            
            Behavior on width {
                PropertyAnimation { duration: 300 }
            }
        }
    }
}