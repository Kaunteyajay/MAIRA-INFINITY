import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../theme"

Rectangle {
    id: chatBar
    
    color: Theme.colors.panelFill
    border.color: Theme.colors.panelBorder
    border.width: 1
    radius: Theme.effects.panelRadius
    
    property bool isListening: (typeof chatModel !== "undefined" && chatModel !== null) ? chatModel.isListening : false
    property bool isExpanded: false
    property string currentMode: "text"

    // Keep QML mode in sync with the Python model
    Connections {
        target: (typeof chatModel !== "undefined") ? chatModel : null
        function onIsListeningChanged() { chatBar.isListening = chatModel.isListening }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md
        
        // Header with avatar chip
        RowLayout {
            Layout.fillWidth: true
            
            // Mini avatar
            Rectangle {
                width: 32
                height: 32
                radius: 16
                color: Theme.colors.accentBlue
                
                Text {
                    anchors.centerIn: parent
                    text: "M"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
            
            Text {
                text: "Chat with MAIRA..."
                color: Theme.colors.textSecondary
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.small
                Layout.fillWidth: true
            }
        }
        
        // Mode buttons row
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm
            
            Repeater {
                model: ListModel {
                    ListElement { mode: "text"; label: "Text"; icon: "📝" }
                    ListElement { mode: "voice"; label: "Voice"; icon: "🎤" }
                    ListElement { mode: "image"; label: "Image"; icon: "🖼️" }
                    ListElement { mode: "file"; label: "File"; icon: "📁" }
                    ListElement { mode: "code"; label: "Code"; icon: "💻" }
                    ListElement { mode: "web"; label: "Web"; icon: "🌐" }
                    ListElement { mode: "auto"; label: "Auto"; icon: "🤖" }
                }
                
                delegate: ModeButton {
                    isActive: model.mode === currentMode
                    
                    onClicked: {
                        currentMode = model.mode
                        console.log("Mode changed to:", model.mode)
                    }
                }
            }
        }
        
        // Input area
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md
            
            // Main input field
            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(inputField.contentHeight + 20, 60)
                
                TextArea {
                    id: inputField
                    placeholderText: getPlaceholderText()
                    color: Theme.colors.textPrimary
                    font.family: Theme.fonts.primary
                    font.pixelSize: Theme.fonts.body
                    selectByMouse: true
                    wrapMode: TextArea.Wrap
                    
                    background: Rectangle {
                        color: Theme.colors.inputBg
                        border.color: inputField.activeFocus ? Theme.colors.inputFocus : Theme.colors.inputBorder
                        border.width: 1
                        radius: Theme.effects.buttonRadius
                    }
                    
                    function getPlaceholderText() {
                        switch(currentMode) {
                            case "voice": return isListening ? "Listening..." : "Click to speak"
                            case "image": return "Upload an image or drag & drop"
                            case "file": return "Upload a file or drag & drop"
                            case "code": return "Enter code to run or debug"
                            case "web": return "Enter URL or search query"
                            case "auto": return "I'll choose the best tool automatically"
                            default: return "Type your command, question or upload a file..."
                        }
                    }
                    
                    Keys.onPressed: function(event) {
                        if (event.key === Qt.Key_Return) {
                            if (event.modifiers & Qt.ShiftModifier) {
                                // Shift+Enter: new line
                                return
                            } else {
                                // Enter: send message
                                event.accepted = true
                                sendMessage()
                            }
                        }
                    }
                }
            }
            
            // Voice button (special handling for voice mode)
            Rectangle {
                width: 40
                height: 40
                radius: 20
                color: isListening ? Theme.colors.danger : Theme.colors.accentBlue
                visible: currentMode === "voice" || true // Always show for push-to-talk
                
                Text {
                    anchors.centerIn: parent
                    text: isListening ? "⏹️" : "🎤"
                    font.pixelSize: 18
                }
                
                MouseArea {
                    anchors.fill: parent
                    
                    onPressed: {
                        if (currentMode === "voice") {
                            startListening()
                        }
                    }
                    
                    onReleased: {
                        if (currentMode === "voice") {
                            stopListening()
                        }
                    }
                    
                    onClicked: {
                        if (currentMode !== "voice") {
                            // Global push-to-talk
                            toggleListening()
                        }
                    }
                }
                
                // Pulsing animation when listening
                SequentialAnimation on opacity {
                    running: isListening
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.5; duration: 500 }
                    PropertyAnimation { to: 1.0; duration: 500 }
                }
            }
            
            // Send button
            Rectangle {
                width: 40
                height: 40
                radius: 6
                color: Theme.colors.accentBlue
                
                Text {
                    anchors.centerIn: parent
                    text: "➤"
                    color: "white"
                    font.pixelSize: 16
                }
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: sendMessage()
                }
            }
        }
        
        // File drop area overlay
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: Theme.colors.accentBlue
            opacity: 0.1
            radius: Theme.effects.panelRadius
            border.color: Theme.colors.accentBlue
            border.width: 2
            border.style: BorderImage.Dashed
            visible: false
            
            Text {
                anchors.centerIn: parent
                text: "Drop files here"
                color: Theme.colors.accentBlue
                font.family: Theme.fonts.primary
                font.pixelSize: Theme.fonts.body
                font.weight: Font.Bold
            }
        }
    }
    
    function sendMessage() {
        var message = inputField.text.trim()
        if (message.length > 0) {
            if (typeof chatModel !== "undefined" && chatModel !== null) {
                chatModel.setCurrentMode(currentMode)
                chatModel.sendMessage(message)
            } else {
                console.warn("chatModel not available")
            }
            inputField.clear()
        }
    }
    
    function startListening() {
        isListening = true
        if (typeof chatModel !== "undefined" && chatModel !== null) {
            chatModel.startListening()
        }
    }
    
    function stopListening() {
        isListening = false
        if (typeof chatModel !== "undefined" && chatModel !== null) {
            chatModel.stopListening()
        }
    }
    
    function toggleListening() {
        if (isListening) {
            stopListening()
        } else {
            startListening()
        }
    }
    
    // Handle file drops
    DropArea {
        anchors.fill: parent
        
        onEntered: function(drag) {
            if (drag.hasUrls) {
                chatBar.children[0].children[3].visible = true
            }
        }
        
        onExited: {
            chatBar.children[0].children[3].visible = false
        }
        
        onDropped: function(drop) {
            chatBar.children[0].children[3].visible = false
            
            if (drop.hasUrls) {
                for (var i = 0; i < drop.urls.length; i++) {
                    console.log("File dropped:", drop.urls[i])
                    // TODO: Handle file upload
                }
            }
        }
    }
}

component ModeButton: Rectangle {
    property bool isActive: false
    property string buttonMode: model.mode
    property string buttonLabel: model.label
    property string buttonIcon: model.icon
    
    signal clicked()
    
    width: 60
    height: 30
    radius: Theme.effects.buttonRadius
    color: isActive ? Theme.colors.accentBlue : Theme.colors.inputBg
    border.color: isActive ? Theme.colors.accentBlue : Theme.colors.inputBorder
    border.width: 1
    
    Row {
        anchors.centerIn: parent
        spacing: Theme.spacing.xs
        
        Text {
            text: buttonIcon
            font.pixelSize: 12
        }
        
        Text {
            text: buttonLabel
            color: isActive ? "white" : Theme.colors.textPrimary
            font.family: Theme.fonts.primary
            font.pixelSize: Theme.fonts.tiny
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onEntered: {
            if (!isActive) {
                parent.color = Theme.colors.buttonHover
            }
        }
        
        onExited: {
            if (!isActive) {
                parent.color = Theme.colors.inputBg
            }
        }
        
        onClicked: parent.clicked()
    }
    
    Behavior on color {
        ColorAnimation { duration: Theme.effects.animationDuration }
    }
}