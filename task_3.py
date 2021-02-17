import sys

from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,  QMainWindow, QLabel
from PyQt5 import QtWidgets
import requests


# ПЕРЕМЕЩЕНИЕ НА КЛАВИШИ WSAD
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pixmap, self.image = None, None
        self.z = 1
        self.horiz = '0'
        self.vert = '0'
        self.count = 0
        self.unitUI()
        self.plus_button.clicked.connect(self.zoom_in)
        self.minus_button.clicked.connect(self.zoom_out)

    def unitUI(self):
        self.setGeometry(100, 100, 750, 550)
        self.setWindowTitle('Карта')
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(650, 450)
        self.drawmap()

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(650, 50, 51, 148))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 450, 701, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setText("Разблокировать")
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_2.clicked.connect(self.enable)

        self.lineEdit_2 = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setEnabled(False)
        self.horizontalLayout.addWidget(self.lineEdit_2)

        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setEnabled(False)
        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Искать")
        self.pushButton.clicked.connect(self.changecoords)
        self.horizontalLayout.addWidget(self.pushButton)

        self.plus_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.plus_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plus_button.setIcon(icon1)
        self.plus_button.setIconSize(QtCore.QSize(35, 35))
        self.plus_button.setFlat(True)
        self.plus_button.setObjectName("plus_button")
        self.verticalLayout.addWidget(self.plus_button)

        self.minus_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.minus_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minus_button.setIcon(icon2)
        self.minus_button.setIconSize(QtCore.QSize(35, 35))
        self.minus_button.setAutoDefault(False)
        self.minus_button.setDefault(False)
        self.minus_button.setFlat(True)
        self.minus_button.setObjectName("minus_button")
        self.verticalLayout.addWidget(self.minus_button)

        self.setCentralWidget(self.centralwidget)

    def drawmap(self):
        map_request = "https://static-maps.yandex.ru/1.x/"
        x, y, = 650, 450
        search_params = {
            "l": "sat",
            "ll": f'{self.horiz},{self.vert}',
            "z": str(self.z),
            "format": "json",
            "size": f"{x},{y}"
        }

        response = requests.get(map_request, params=search_params)
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(response.content)
        self.image.setPixmap(self.pixmap)

    def enable(self):
        self.lineEdit_2.setEnabled(True)
        self.lineEdit.setEnabled(True)

    def zoom_in(self):
        self.z += 1
        if self.z > 12:
            self.z = 12
        self.drawmap()

    def zoom_out(self):
        self.z -= 1
        if self.z < 2:
            self.z = 2
        self.drawmap()

    def changecoords(self):
        if -70 <= float(self.lineEdit.text()) <= 70:
            self.vert = self.lineEdit.text()
        if -180 <= float(self.lineEdit_2.text()) <= 180:
            self.horiz = self.lineEdit_2.text()
        self.lineEdit.setEnabled(False)
        self.lineEdit_2.setEnabled(False)
        self.drawmap()

    def movemap(self, button):
        if button == 'right':
            if float(self.horiz) < 180:
                self.horiz = str(int(self.horiz) + 1)
        elif button == 'left':
            if float(self.horiz) > -180:
                self.horiz = str(int(self.horiz) - 1)
        elif button == 'up':
            if float(self.vert) < 73:
                self.vert = str(int(self.vert) + 1)
        elif button == 'down':
            if float(self.vert) > -73:
                self.vert = str(int(self.vert) - 1)
        self.drawmap()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.movemap('left')
        elif event.key() == Qt.Key_W:
            self.movemap('up')
        elif event.key() == Qt.Key_S:
            self.movemap('down')
        elif event.key() == Qt.Key_D:
            self.movemap('right')
        elif event.key() == Qt.Key_PageUp:
            self.zoom_in()
        elif event.key() == Qt.Key_PageDown:
            self.zoom_out()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
