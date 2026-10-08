import QtQuick 2.15
import QtQuick.Controls 2.15
Item {
    width: 24
    height: 24
    property string iconChar: "?"
    property bool active: false
    property bool clickable: false
    signal clicked()
    Text {
        anchors.centerIn: parent
        text: iconChar
        font.pixelSize: 14
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: clickable
        onClicked: if (clickable) parent.clicked()
    }
}
