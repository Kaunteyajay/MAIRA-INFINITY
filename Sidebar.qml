import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: sidebar
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    
    property string activeModule: "home"
    
    Column {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        
        // Navigation items
        Repeater {
            model: ListModel {
                ListElement { name: "home"; title: "Home"; subtitle: "Overview"; icon: "🏠" }
                ListElement { name: "chat"; title: "Chat"; subtitle: "Talk to MAIRA"; icon: "💬" }
                ListElement { name: "code"; title: "Code"; subtitle: "Run / Build / Debug"; icon: "💻" }
                ListElement { name: "research"; title: "Research"; subtitle: "Deep Research"; icon: "🔬" }
                ListElement { name: "learning"; title: "Learning"; subtitle: "Teach & Learn"; icon: "📚" }
                ListElement { name: "files"; title: "File System"; subtitle: "Access Files"; icon: "📁" }
                ListElement { name: "apps"; title: "Apps"; subtitle: "Launch Tools"; icon: "🚀" }
                ListElement { name: "automation"; title: "Automation"; subtitle: "Set Workflows"; icon: "⚙️" }
                ListElement { name: "virtuelos"; title: "Virtual OS"; subtitle: "Manage Multiple OS"; icon: "🖥️" }
                ListElement { name: "simulations"; title: "Simulations"; subtitle: "Physics / Chemistry etc."; icon: "🧪" }
                ListElement { name: "multimedia"; title: "Multimedia"; subtitle: "Image / Video / Audio"; icon: "🎨" }
                ListElement { name: "health"; title: "Health"; subtitle: "System & You"; icon: "❤️" }
                ListElement { name: "settings"; title: "Settings"; subtitle: "Customize MAIRA"; icon: "⚙️" }
            }
            
            delegate: SidebarItem {
                width: sidebar.width - Theme.spacing.sm * 2
                isActive: model.name === sidebar.activeModule
                
                onClicked: {
                    sidebar.activeModule = model.name
                    console.log("Switched to module:", model.name)
                }
            }
        }
        
        // Spacer
        Item {
            width: 1
            height: Theme.spacing.xl
        }
        
        // Active Sessions
        SessionsWidget {
            width: parent.width
        }
        
        // Storage & GPU
        StorageWidget {
            width: parent.width
        }
    }
}