import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15
import "../theme"
import "../components"
import "../widgets"
import "../avatar"

Item {
    id: homePage
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.lg
        
        // Center column - Avatar area
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md
            
            // Real-Time Intelligence panel
            RealtimeIntelligence {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
            }
            
            // Avatar stage — shrinks when there are messages
            AvatarStage {
                Layout.fillWidth: true
                Layout.fillHeight: messageList.count === 0
                Layout.preferredHeight: messageList.count > 0 ? 180 : -1
                visible: true
            }
            
            // Chat messages list — only visible after first message
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: messageList.count > 0
                Layout.preferredHeight: messageList.count > 0 ? -1 : 0
                visible: messageList.count > 0
                color: Theme.colors.panelFill
                border.color: Theme.colors.panelBorder
                border.width: 1
                radius: Theme.effects.panelRadius
                clip: true

                ListView {
                    id: messageList
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.md
                    model: (typeof chatModel !== "undefined" && chatModel !== null) ? chatModel.messages : null
                    spacing: Theme.spacing.sm
                    verticalLayoutDirection: ListView.TopToBottom

                    // Auto-scroll to bottom on new messages
                    onCountChanged: Qt.callLater(function() { messageList.positionViewAtEnd() })

                    delegate: Item {
                        width: messageList.width
                        height: bubbleCol.implicitHeight + Theme.spacing.sm

                        property bool isUser: model.role === "user"

                        Column {
                            id: bubbleCol
                            anchors.right: isUser ? parent.right : undefined
                            anchors.left:  isUser ? undefined : parent.left
                            width: Math.min(parent.width * 0.75, 500)
                            spacing: Theme.spacing.xs

                            // Role label
                            Text {
                                text: isUser ? "You" : "MAIRA"
                                color: isUser ? Theme.colors.accentBlue : Theme.colors.accentCyan
                                font.family: Theme.fonts.primary
                                font.pixelSize: Theme.fonts.tiny
                                font.bold: true
                                anchors.right: isUser ? parent.right : undefined
                            }

                            // Message bubble
                            Rectangle {
                                width: parent.width
                                height: Math.max(bubbleText.implicitHeight + Theme.spacing.md * 2, 32)
                                radius: Theme.effects.panelRadius
                                color: isUser ? Theme.colors.accentBlue : Theme.colors.inputBg
                                border.color: isUser ? "transparent" : Theme.colors.panelBorder
                                border.width: 1

                                Text {
                                    id: bubbleText
                                    anchors {
                                        left: parent.left; right: parent.right
                                        top: parent.top
                                        margins: Theme.spacing.md
                                    }
                                    text: model.text.length === 0
                                          ? (isUser ? "" : "▋")
                                          : model.text
                                    color: Theme.colors.textPrimary
                                    font.family: Theme.fonts.primary
                                    font.pixelSize: Theme.fonts.body
                                    wrapMode: Text.Wrap
                                }
                            }

                            // Timestamp
                            Text {
                                text: model.time
                                color: Theme.colors.textTertiary
                                font.pixelSize: Theme.fonts.tiny
                                anchors.right: isUser ? parent.right : undefined
                            }
                        }
                    }
                }
            }
            
            // Chat bar
            ChatBar {
                Layout.fillWidth: true
                Layout.preferredHeight: 155
            }
            
            // Bottom row - Recent Activity + Multi-OS
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 150
                spacing: Theme.spacing.md
                
                RecentActivity {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
                
                MultiOSEnvironment {
                    Layout.preferredWidth: 200
                    Layout.fillHeight: true
                }
            }
        }
    }
}