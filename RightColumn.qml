import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme" 
import "../widgets"

ColumnLayout {
    spacing: Theme.spacing.md
    anchors.margins: Theme.spacing.md
    
    // System Status
    SystemStatus {
        Layout.fillWidth: true
        Layout.preferredHeight: 140
    }
    
    // Time & Space
    TimeSpace {
        Layout.fillWidth: true
        Layout.preferredHeight: 180
    }
    
    // Quick Tools
    QuickTools {
        Layout.fillWidth: true
        Layout.preferredHeight: 220
    }
    
    // Running Tasks
    RunningTasks {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }
}