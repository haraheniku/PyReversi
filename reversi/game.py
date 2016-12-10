import sys

from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    pyqtSlot,
    pyqtProperty,
    Q_ENUMS,
)
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType, QQmlApplicationEngine


DIRECTIONS = {
    "up": (0, -1),
    "up_left": (-1, -1),
    "left": (-1, 0),
    "down_left": (-1, 1),
    "down": (0, 1),
    "down_right": (1, 1),
    "right": (1, 0),
    "up_right": (1, 1),
}


class Player(QObject):
    def __init__(self, parent, color):
        super().__init__(parent)
        self._color = color

    @pyqtProperty(int, constant=True)
    def color(self):
        return self._color

    @pyqtProperty(str, constant=True)
    def name(self):
        if self._color == Game.Disk.BLACK:
            return "black"
        if self._color == Game.Disk.WHITE:
            return "white"
        return "unknown"


class Game(QObject):
    boardChanged = pyqtSignal()
    playerChanged = pyqtSignal()

    class Disk:
        EMPTY = 0
        BLACK = 1
        WHITE = 2

        @classmethod
        def another(cls, disk):
            if disk == Game.Disk.BLACK:
                return Game.Disk.WHITE
            elif disk == Game.Disk.WHITE:
                return Game.Disk.BLACK
            else:
                raise ValueError

    Q_ENUMS(Disk)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._width = 8
        self._height = 8

        # New Game
        self.newGame()

    @pyqtSlot()
    def newGame(self):
        self._players = [
            Player(self, Game.Disk.BLACK),
            Player(self, Game.Disk.WHITE),
        ]
        self._currentPlayer = self._players[0]
        self._initBoard()

    def _initBoard(self):
        # Set all cells to empty
        self._board = [Game.Disk.EMPTY] * self.size

        # Place four disks in a square in the middle of the grid
        mid = self.width // 2
        self._placeDiskXY(mid-1, mid-1, Game.Disk.BLACK)
        self._placeDiskXY(mid, mid, Game.Disk.BLACK)
        self._placeDiskXY(mid-1, mid, Game.Disk.WHITE)
        self._placeDiskXY(mid, mid-1, Game.Disk.WHITE)

        # Emit "boardChanged" signal
        self.boardChanged.emit()

    @pyqtProperty("QList<int>", notify=boardChanged)
    def board(self):
        return self._board

    @pyqtProperty(int, constant=True)
    def width(self):
        return self._width

    @pyqtProperty(int, constant=True)
    def height(self):
        return self._height

    @pyqtProperty(int, constant=True)
    def size(self):
        return self._width * self._height

    @pyqtProperty(Player, notify=playerChanged)
    def currentPlayer(self):
        return self._currentPlayer

    @pyqtProperty(Player, notify=playerChanged)
    def anotherPlayer(self):
        index = self._players.index(self._currentPlayer)
        anotherIndex = int(not index)
        return self._players[anotherIndex]

    def changePlayer(self):
        self._currentPlayer = self.anotherPlayer
        self.playerChanged.emit()

    def getIndex(self, x, y):
        return x + y * self._width

    def getXY(self, index):
        x = index % self._width
        y = index // self._width
        return x, y

    def getDisk(self, index):
        return self._board[index]

    def getDiskXY(self, x, y):
        return self._board[self.getIndex(x, y)]

    def _placeDisk(self, index, color):
        self._board[index] = color

    def _placeDiskXY(self, x, y, color):
        index = self.getIndex(x, y)
        self._placeDisk(index, color)

    @pyqtSlot(int, result=bool)
    def placeDisk(self, index):
        if self.getDisk(index) != Game.Disk.EMPTY:
            return False

        x, y = self.getXY(index)
        fliped = False
        for direction, (dx, dy) in DIRECTIONS.items():
            d = 0
            nx, ny = x, y
            while True:
                nx, ny = nx + dx, ny + dy
                if nx < 0 or nx >= self._width:
                    break
                if  ny < 0 or ny >= self._height:
                    break

                disk = self.getDiskXY(nx, ny)
                if disk == Game.Disk.EMPTY:
                    d = 0
                    break
                if disk != self.anotherPlayer.color:
                    break
                d += 1

            if d > 0:
                for i in range(d+1):
                    nx, ny = x + i * dx, y + i * dy
                    self._placeDiskXY(nx, ny, self._currentPlayer.color)
                fliped = True

        if fliped:
            self.boardChanged.emit()
            self.changePlayer()
        return fliped


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    qmlRegisterType(Game, 'Reversi', 1, 0, 'Game')
    qmlRegisterType(Player, 'Reversi', 1, 0, 'Player')

    engine = QQmlApplicationEngine("reversi.qml")
    # engine.quit.connect(app.quit)

    root = engine.rootObjects()[0]
    game = root.findChild(Game, "game")

    sys.exit(app.exec_())
