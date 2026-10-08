import QtQuick 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    color: "transparent"
    
    Column {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md
        
        // Action cards
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md
            
            Repeater {
                model: ListModel {
                    ListElement { 
                        title: "Learn Anything"
                        subtitle: "Adaptive teaching & quizzes"
                        icon: "📚"
                        module: "learning"
                    }
                    ListElement { 
                        title: "Solve Problems"
                        subtitle: "Research & analysis"
                        icon: "🔬"
                        module: "research"
                    }
                    ListElement { 
                        title: "Create & Build"
                        subtitle: "Code, design, automate"
                        icon: "🛠️"
                        module: "code"
                    }
                    ListElement { 
                        title: "Explore Universe"
                        subtitle: "Simulations & discovery"
                        icon: "🌌"
                        module: "simulations"
                    }
                    ListElement { 
                        title: "Manage Life"
                        subtitle: "Health, tasks, wellness"
                        icon: "💚"
                        module: "health"
                    }
                }
                
                delegate: ActionCard {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 100
                }
            }
        }
        
        // Footer tagline
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "LIMITLESS • INTELLIGENT • ALWAYS WITH YOU"
            color: Theme.colors.textSecondary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.small
            font.weight: Font.Bold
            letterSpacing: 2
        }
        
        // Pagination dots (placeholder)
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: Theme.spacing.sm
            
            Repeater {
                model: 3
                
                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: index === 0 ? Theme.colors.accentBlue : Theme.colors.textSecondary
                    opacity: index === 0 ? 1.0 : 0.3
                }
            }
        }
    }
}