import sys

from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,  QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5 import QtWidgets
import requests

MAP_WIDTH, MAP_HEIGHT = 650, 450


def click_on_map(function):
    def wrapper(self, event):
        if event.x() <= MAP_WIDTH and event.y() <= MAP_HEIGHT:
            if event.button() == Qt.LeftButton:
                left = True
            else:
                left = False
            function(self, event, left)
    return wrapper


# ПЕРЕМЕЩЕНИЕ НА КЛАВИШИ WSAD
class App(QMainWindow):
    def __init__(self):
        self.LAYERS = ['sat', 'sat,skl', 'map']
        super().__init__()
        self.pixmap, self.image = None, None
        self.z = 1
        self.layer = 0
        self.horiz = '0'
        self.vert = '0'
        self.count = 0
        self.point = None
        self.toponym_address = None
        self.postal_code = None
        self.unitUI()
        self.plus_button.clicked.connect(self.zoom_in)
        self.minus_button.clicked.connect(self.zoom_out)
        self.layers_button.clicked.connect(self.change_layer)
        self.with_index.clicked.connect(self.add_index)

    def unitUI(self):
        self.setGeometry(100, 100, 750, 650)
        self.setWindowTitle('Карта')
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(MAP_WIDTH, MAP_HEIGHT)
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

        self.lineEdit_2 = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)

        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
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

        self.layers_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.layers_button.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("layers.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.layers_button.setIcon(icon3)
        self.layers_button.setIconSize(QtCore.QSize(35, 35))
        self.layers_button.setAutoDefault(False)
        self.layers_button.setDefault(False)
        self.layers_button.setFlat(True)
        self.layers_button.setObjectName("layers_button")
        self.verticalLayout.addWidget(self.layers_button)

        self.setCentralWidget(self.centralwidget)

        self.info = QLabel(self)
        self.info.setText('Поиск по адресу:')
        self.info.move(20, 550)

        self.coord1 = QLineEdit(self)
        self.coord1.resize(309, 28)
        self.coord1.move(130, 551)


        self.btn = QPushButton('Найти', self)
        self.btn.resize(60, 30)
        self.btn.move(440, 550)
        self.btn.clicked.connect(self.makepoint)

        self.btn_reset = QPushButton('Сброс', self)
        self.btn_reset.resize(60, 30)
        self.btn_reset.move(500, 550)
        self.btn_reset.clicked.connect(self.reset_point)

        self.search_result = QLabel(self)
        self.search_result.resize(600, 30)
        self.search_result.move(20, 580)

        self.with_index = QtWidgets.QCheckBox(self)
        self.with_index.setGeometry(QtCore.QRect(570, 555, 101, 20))
        self.with_index.setObjectName("with_index")
        self.with_index.setText('С индексом')

    def drawmap(self):
        map_request = "https://static-maps.yandex.ru/1.x/"
        x, y, = 650, 450
        search_params = {
            "l": str(self.LAYERS[self.layer]),
            "ll": f'{self.horiz},{self.vert}',
            "z": str(self.z),
            "format": "json",
            "size": f"{x},{y}",
            "pt": self.point
        }

        response = requests.get(map_request, params=search_params)
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(response.content)
        self.image.setPixmap(self.pixmap)

    def geocoder(self, geocode):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": geocode,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            self.toponym_address = None
            self.postal_code = None
            self.search_result.setText('NO ADDRESS LIKE THIS')
            return

        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
        except IndexError:
            self.toponym_address = None
            self.postal_code = None
            self.search_result.setText('NO ADDRESS LIKE THIS')
            return
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_latitude, toponym_longitude = toponym_coodrinates.split(" ")
        self.toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        try:
            self.postal_code = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        except KeyError:
            self.postal_code = None
        if self.with_index.isChecked() and self.postal_code:
            self.search_result.setText(f'Адрес объекта: {self.postal_code}, {self.toponym_address}')
        else:
            self.search_result.setText(f'Адрес объекта: {self.toponym_address}')
        return toponym_latitude, toponym_longitude

    def makepoint(self):
        toponym_to_find = "".join(self.coord1.text())
        try:
            toponym_latitude, toponym_longitude = self.geocoder(toponym_to_find)
            self.point = f"{toponym_latitude},{toponym_longitude},pmgnm1"
            self.lineEdit.setText(toponym_latitude)
            self.lineEdit_2.setText(toponym_longitude)
            self.changecoords()
        except TypeError:
            self.search_result.setText('NO ADDRESS LIKE THIS')

    def reset_point(self):
        self.point = None
        self.toponym_address = None
        self.postal_code = None
        self.coord1.setText('')
        self.search_result.setText('')
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.drawmap()

    def add_index(self):
        if self.toponym_address:
            if self.with_index.isChecked() and self.postal_code:
                self.search_result.setText(f'Адрес объекта: {self.postal_code}, {self.toponym_address}')
            else:
                self.search_result.setText(f'Адрес объекта: {self.toponym_address}')

    def zoom_in(self):
        self.z += 1
        if self.z > 17:
            self.z = 17
        self.drawmap()

    def zoom_out(self):
        self.z -= 1
        if self.z < 1:
            self.z = 1
        self.drawmap()

    def change_layer(self):
        self.layer += 1
        self.layer %= 3
        self.drawmap()

    def changecoords(self):
        try:
            if -70 <= float(self.lineEdit.text()) <= 70:
                self.horiz = self.lineEdit.text()
            if -180 <= float(self.lineEdit_2.text()) <= 180:
                self.vert = self.lineEdit_2.text()
            self.drawmap()
        except ValueError:
            self.search_result.setText('Неверный формат ввода!')

    def movemap(self, button):
        if button == 'right':
            if float(self.horiz) < 180:
                self.horiz = str(float(self.horiz) + 1)
        elif button == 'left':
            if float(self.horiz) > -180:
                self.horiz = str(float(self.horiz) - 1)
        elif button == 'up':
            if float(self.vert) < 73:
                self.vert = str(float(self.vert) + 1)
        elif button == 'down':
            if float(self.vert) > -73:
                self.vert = str(float(self.vert) - 1)
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

    @click_on_map
    def mousePressEvent(self, event, left):
        x, y = event.x(), event.y()
        if left:
            latitude = str(float(self.horiz) + ((x - MAP_WIDTH / 2) * (1.45 / 2 ** self.z)))
            longitude = str(float(self.vert) - ((y - MAP_HEIGHT / 2) * (1.2 / 2 ** self.z)))
            self.point = f"{latitude},{longitude},pmgnm1"
            self.geocoder(f"{latitude},{longitude}")
            self.lineEdit.setText(latitude)
            self.lineEdit_2.setText(longitude)
            self.drawmap()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())