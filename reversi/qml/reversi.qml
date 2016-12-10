import QtQuick 2.4
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.0
import Reversi 1.0


ApplicationWindow {
    title: "PyReversi"
    visible: true

    Game {
        id: game
        objectName: "game"
    }

    menuBar: MenuBar {
        Menu {
            title: "Game"

            MenuItem {
                text: "New Game"
                shortcut: "Ctrl+N"
                onTriggered: game.newGame()
            }
        }
    }

    statusBar: StatusBar {
        RowLayout {
            anchors.fill: parent
            Label { text: game.currentPlayer.name }
        }
    }

    Grid {
        width: 400; height: 400
        columns: game.width
        anchors.centerIn: parent

        Repeater {
            model: game.size

            Rectangle {
                width: 50; height: 50
                color: "green"
                border.color: "black"
                border.width: 1

                Rectangle {
                    width: 40; height: 40
                    radius: width / 2
                    anchors.centerIn: parent
                    color: getColor(game.board[index])

                    function getColor(disk) {
                        switch (disk) {
                        case Game.BLACK:
                            return "black";
                        case Game.WHITE:
                            return "white";
                        default:
                            return "transparent";
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: game.placeDisk(index)
                }
            }
        }
    }
}