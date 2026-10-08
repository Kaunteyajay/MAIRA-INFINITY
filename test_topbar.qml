import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
Item {
    width: 400
    height: 45
    RowLayout {
        anchors.fill: parent
        StatusIcon {
            iconChar: "M"
            active: false
        }
    }
}
