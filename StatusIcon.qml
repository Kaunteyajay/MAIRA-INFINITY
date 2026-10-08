import QtQuick 2.15
import QtQuick.Controls 2.15
import "../theme"

Item {
    id: statusIcon
    width: 24
    height: 24
    
    property string iconChar: "?"
    property bool active: false
    property string tooltip: ""
    property bool clickable: false
    signal clicked()

    Text {
        anchors.centerIn: parent
        text: statusIcon.iconChar
        font.pixelSize: 14
        color: statusIcon.active ? Theme.colors.accentBlue : Theme.colors.textSecondary
        opacity: statusIcon.active ? 1.0 : 0.6
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: statusIcon.clickable
        cursorShape: statusIcon.clickable ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: if (statusIcon.clickable) statusIcon.clicked()
    }
}
