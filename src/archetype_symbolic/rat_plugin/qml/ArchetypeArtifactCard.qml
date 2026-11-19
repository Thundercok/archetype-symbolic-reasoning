import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: pluginCardRoot
    property var cardData: ({})
    property var host: null
    readonly property string visualType: cardData ? (cardData.visual_type || "") : ""
    spacing: 12

    // --- 1. KINH DỊCH (I CHING) ---
    ColumnLayout {
        visible: pluginCardRoot.visualType === "iching"
        Layout.fillWidth: true
        spacing: 10

        RowLayout {
            spacing: 8
            Rectangle {
                radius: 6
                color: host ? Qt.rgba(host.accent.r, host.accent.g, host.accent.b, 0.15) : "#224a78"
                implicitWidth: ichingBadgeText.implicitWidth + 14
                implicitHeight: ichingBadgeText.implicitHeight + 6
                Label {
                    id: ichingBadgeText
                    anchors.centerIn: parent
                    text: "🔮 QUẺ KINH DỊCH"
                    color: host ? host.accent : "#4a90e2"
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                }
            }
            Label {
                text: pluginCardRoot.cardData ? (pluginCardRoot.cardData.question || "") : ""
                font.pixelSize: 12
                color: host ? host.muted : "#777"
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            // 6 Yin/Yang Lines (Drawn from Line 6 down to Line 1)
            Rectangle {
                implicitWidth: 120
                implicitHeight: 88
                radius: 8
                color: host ? host.inputColor : "#f4f4f4"
                border.width: 1
                border.color: host ? host.edge : "#ddd"

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 5
                    Repeater {
                        model: 6
                        Item {
                            readonly property int lineNum: 6 - index
                            readonly property int lineIdx: lineNum - 1
                            readonly property var rawLines: pluginCardRoot.cardData && pluginCardRoot.cardData.lines ? pluginCardRoot.cardData.lines : [1, 1, 1, 1, 1, 1]
                            readonly property int isYang: lineIdx < rawLines.length ? rawLines[lineIdx] : 1
                            readonly property var changingList: pluginCardRoot.cardData && pluginCardRoot.cardData.changing_lines ? pluginCardRoot.cardData.changing_lines : []
                            readonly property bool isChanging: changingList.indexOf(lineNum) !== -1

                            implicitWidth: 92
                            implicitHeight: 7

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 8
                                visible: isYang === 0
                                Rectangle {
                                    width: 40; height: 6; radius: 3
                                    color: isChanging ? (host ? host.warningInk : "#d9534f") : (host ? host.accent : "#4a90e2")
                                }
                                Rectangle {
                                    width: 40; height: 6; radius: 3
                                    color: isChanging ? (host ? host.warningInk : "#d9534f") : (host ? host.accent : "#4a90e2")
                                }
                            }
                            Rectangle {
                                anchors.centerIn: parent
                                visible: isYang === 1
                                width: 88; height: 6; radius: 3
                                color: isChanging ? (host ? host.warningInk : "#d9534f") : (host ? host.accent : "#4a90e2")
                            }
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Label {
                    text: pluginCardRoot.cardData ? (pluginCardRoot.cardData.hexagram_name || "") : ""
                    font.pixelSize: 18
                    font.weight: Font.DemiBold
                    color: host ? host.ink : "#111"
                }
                Label {
                    text: pluginCardRoot.cardData ? ("Thượng: " + (pluginCardRoot.cardData.upper_trigram || "") + " · Hạ: " + (pluginCardRoot.cardData.lower_trigram || "")) : ""
                    font.pixelSize: 12
                    color: host ? host.muted : "#777"
                }
                Label {
                    text: pluginCardRoot.cardData ? (pluginCardRoot.cardData.meaning || "") : ""
                    font.pixelSize: 12
                    color: host ? host.ink : "#111"
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
            }
        }

        Rectangle {
            visible: Boolean(pluginCardRoot.cardData && pluginCardRoot.cardData.advice)
            Layout.fillWidth: true
            radius: 8
            color: host ? host.inputColor : "#f4f4f4"
            border.width: 1
            border.color: host ? host.edge : "#ddd"
            implicitHeight: adviceText.implicitHeight + 14

            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                Label { text: "💡"; font.pixelSize: 14 }
                Label {
                    id: adviceText
                    text: pluginCardRoot.cardData ? (pluginCardRoot.cardData.advice || "") : ""
                    font.pixelSize: 12
                    color: host ? host.ink : "#111"
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
            }
        }
    }

    // --- 2. LENORMAND ORACLE (3 CARDS) ---
    ColumnLayout {
        visible: pluginCardRoot.visualType === "lenormand"
        Layout.fillWidth: true
        spacing: 10

        RowLayout {
            spacing: 8
            Rectangle {
                radius: 6
                color: host ? Qt.rgba(host.accent.r, host.accent.g, host.accent.b, 0.15) : "#224a78"
                implicitWidth: lenoBadgeText.implicitWidth + 14
                implicitHeight: lenoBadgeText.implicitHeight + 6
                Label {
                    id: lenoBadgeText
                    anchors.centerIn: parent
                    text: "🃏 BÀI LENORMAND"
                    color: host ? host.accent : "#4a90e2"
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                }
            }
            Label {
                text: pluginCardRoot.cardData ? (pluginCardRoot.cardData.question || "Trải bài 3 lá") : ""
                font.pixelSize: 12
                color: host ? host.muted : "#777"
                elide: Text.ElideRight
                Layout.fillWidth: true
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: pluginCardRoot.cardData && pluginCardRoot.cardData.cards ? pluginCardRoot.cardData.cards : []
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    implicitHeight: 124
                    radius: 8
                    color: host ? host.inputColor : "#f4f4f4"
                    border.width: 1
                    border.color: host ? host.edge : "#ddd"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 3

                        Label {
                            text: (modelData.slot || "").toUpperCase()
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                            color: host ? host.muted : "#777"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                        Label {
                            text: modelData.icon || "🎴"
                            font.pixelSize: 24
                            Layout.alignment: Qt.AlignHCenter
                        }
                        Label {
                            text: modelData.name || ""
                            font.pixelSize: 12
                            font.weight: Font.DemiBold
                            color: host ? host.ink : "#111"
                            elide: Text.ElideRight
                            Layout.alignment: Qt.AlignHCenter
                        }
                        Label {
                            text: modelData.meaning || ""
                            font.pixelSize: 11
                            color: host ? host.muted : "#777"
                            wrapMode: Text.Wrap
                            elide: Text.ElideRight
                            maximumLineCount: 2
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }
}
