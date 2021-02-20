# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     Большая задача по Maps API. ЧАСТЬ №10, 11                 #
#                Авторы решения: Аксенов Никита и Прохорова Анна                #
#                                                                               #
#                        Примечания по работе программы:                        #
# 1. Перемещение карты с помощью клавиш вверх/вниз/вправо/влево сделать не      #
#    удалось из-за особенности работы PyQt5. Поэтому были использованы кнопки   #
#    WASD (W - вверх, A - влево, S - вниз, D - вправо).                         #
# 2. Для корректного отображения иконок увеличения и уменьшения масштаба,       #
#    изменения слоя карты, в папке с запускаемой программой должны быть         #
#    изображения plus.png, minus.png, layers.png.                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5 import QtWidgets
import requests

MAP_WIDTH, MAP_HEIGHT = 650, 450
LAYERS = ['sat', 'sat,skl', 'map']
GET_MAP_SERVER = "https://static-maps.yandex.ru/1.x/"
GEOCODER_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"
GEOCODER_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
MAP_EDGE_LIMITS = [0, 21, 70, 80, 83]


def click_on_map(function):
    def wrapper(self, event):
        if event.x() <= MAP_WIDTH and event.y() <= MAP_HEIGHT:
            if event.button() == Qt.LeftButton:
                left = True
            else:
                left = False
            function(self, event, left)

    return wrapper


def map_edge_limits(function):
    def wrapper(self, point_mode):
        first_z = self.z
        max_longitude = 180
        if point_mode:
            for i in range(self.z, 18):
                self.z = i
                try:
                    max_latitude = MAP_EDGE_LIMITS[self.z]
                except IndexError:
                    max_latitude = 84
                if not float(self.latitude) > max_latitude and \
                        not float(self.latitude) < -max_latitude and \
                        not float(self.latitude) > max_longitude and \
                        not float(self.latitude) < -max_longitude:
                    break
        else:
            try:
                max_latitude = MAP_EDGE_LIMITS[self.z]
            except IndexError:
                max_latitude = 84
        if float(self.latitude) > max_latitude:
            self.latitude = max_latitude
            self.z = first_z
        if float(self.latitude) < -max_latitude:
            self.latitude = -max_latitude
            self.z = first_z
        if float(self.latitude) > max_longitude:
            self.longitude = max_longitude
            self.z = first_z
        if float(self.latitude) < -max_longitude:
            self.longitude = -max_longitude
            self.z = first_z
        function(self, point_mode)

    return wrapper


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.layer = 0
        self.z = 1
        self.longitude = '0'
        self.latitude = '0'

        self.toponym_address = None
        self.postal_code = None
        self.point = None

        self.unitUI()

        self.coordinate_search_button.clicked.connect(self.changecoords)
        self.address_search_button.clicked.connect(self.makepoint)
        self.reset_button.clicked.connect(self.reset_point)
        self.plus_button.clicked.connect(self.zoom_in)
        self.minus_button.clicked.connect(self.zoom_out)
        self.layers_button.clicked.connect(self.change_layer)
        self.with_postal_code_checkbox.clicked.connect(self.add_postal_code)

    def unitUI(self):
        self.setGeometry(100, 100, 700, 650)
        self.setWindowTitle('Карта')

        self.map = QLabel(self)
        self.map.move(0, 0)
        self.map.resize(MAP_WIDTH, MAP_HEIGHT)
        self.drawmap(False)

        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(650, 50, 51, 148))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 450, 650, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.longitude_input = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.longitude_input.setObjectName("longitude_input")
        self.longitude_input.setPlaceholderText('Широта')
        self.horizontalLayout.addWidget(self.longitude_input)

        self.latitude_input = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.latitude_input.setObjectName("latitude_input")
        self.latitude_input.setPlaceholderText('Долгота')
        self.horizontalLayout.addWidget(self.latitude_input)

        self.coordinate_search_button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.coordinate_search_button.setObjectName("coordinate_search_button")
        self.coordinate_search_button.setText("Искать")
        self.horizontalLayout.addWidget(self.coordinate_search_button)

        self.plus_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.plus_button.setText("")
        plus_icon = QtGui.QIcon()
        plus_icon.addPixmap(QtGui.QPixmap("plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.plus_button.setIcon(plus_icon)
        self.plus_button.setIconSize(QtCore.QSize(35, 35))
        self.plus_button.setFlat(True)
        self.plus_button.setObjectName("plus_button")
        self.verticalLayout.addWidget(self.plus_button)

        self.minus_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.minus_button.setText("")
        minus_icon = QtGui.QIcon()
        minus_icon.addPixmap(QtGui.QPixmap("minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minus_button.setIcon(minus_icon)
        self.minus_button.setIconSize(QtCore.QSize(35, 35))
        self.minus_button.setAutoDefault(False)
        self.minus_button.setDefault(False)
        self.minus_button.setFlat(True)
        self.minus_button.setObjectName("minus_button")
        self.verticalLayout.addWidget(self.minus_button)

        self.layers_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.layers_button.setText("")
        layers_icon = QtGui.QIcon()
        layers_icon.addPixmap(QtGui.QPixmap("layers.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.layers_button.setIcon(layers_icon)
        self.layers_button.setIconSize(QtCore.QSize(35, 35))
        self.layers_button.setAutoDefault(False)
        self.layers_button.setDefault(False)
        self.layers_button.setFlat(True)
        self.layers_button.setObjectName("layers_button")
        self.verticalLayout.addWidget(self.layers_button)

        self.address_search_label = QLabel(self)
        self.address_search_label.setText('Поиск по адресу:')
        self.address_search_label.move(20, 550)

        self.address_search_input = QLineEdit(self)
        self.address_search_input.resize(309, 28)
        self.address_search_input.move(130, 551)

        self.address_search_button = QPushButton('Найти', self)
        self.address_search_button.resize(60, 30)
        self.address_search_button.move(440, 550)

        self.reset_button = QPushButton('Сброс', self)
        self.reset_button.resize(60, 30)
        self.reset_button.move(500, 550)

        self.search_result_label = QLabel(self)
        self.search_result_label.resize(630, 30)
        self.search_result_label.move(20, 580)
        self.search_result_label.setText('Для навигации используйте клавиши W-вверх, A-влево, S-вниз, D-вправо '
                                         '(не забудьте про раскладку!)')

        self.with_postal_code_checkbox = QtWidgets.QCheckBox(self)
        self.with_postal_code_checkbox.setGeometry(QtCore.QRect(570, 555, 101, 20))
        self.with_postal_code_checkbox.setObjectName("with_index")
        self.with_postal_code_checkbox.setText('С индексом')

    @map_edge_limits
    def drawmap(self, point_mode):
        x, y, = 650, 450
        search_params = {
            "l": str(LAYERS[self.layer]),
            "ll": f'{self.longitude},{self.latitude}',
            "z": str(self.z),
            "format": "json",
            "size": f"{x},{y}",
            "pt": self.point
        }

        response = requests.get(GET_MAP_SERVER, params=search_params)
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(response.content)
        self.map.setPixmap(self.pixmap)

    def geocoder(self, geocode):
        geocoder_params = {
            "apikey": GEOCODER_API_KEY,
            "geocode": geocode,
            "format": "json"}
        response = requests.get(GEOCODER_API_SERVER, params=geocoder_params)
        if not response:
            self.toponym_address = None
            self.postal_code = None
            self.search_result_label.setText('Адрес не найден!')
            return

        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
        except IndexError:
            self.toponym_address = None
            self.postal_code = None
            self.search_result_label.setText('Адрес не найден!')
            return
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_latitude, toponym_longitude = toponym_coodrinates.split(" ")
        self.toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
        try:
            self.postal_code = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        except KeyError:
            self.postal_code = None
        if self.with_postal_code_checkbox.isChecked() and self.postal_code:
            self.search_result_label.setText(f'Адрес объекта: {self.postal_code}, {self.toponym_address}')
        else:
            self.search_result_label.setText(f'Адрес объекта: {self.toponym_address}')
        return toponym_latitude, toponym_longitude

    def makepoint(self):
        toponym_to_find = "".join(self.address_search_input.text())
        try:
            toponym_latitude, toponym_longitude = self.geocoder(toponym_to_find)
            self.point = f"{toponym_latitude},{toponym_longitude},pmgnm1"
            self.latitude_input.setText(toponym_latitude)
            self.longitude_input.setText(toponym_longitude)
            self.changecoords(True)
        except TypeError:
            self.search_result_label.setText('Адрес не найден!')

    def reset_point(self):
        self.point = None
        self.toponym_address = None
        self.postal_code = None
        self.address_search_input.setText('')
        self.search_result_label.setText('')
        self.latitude_input.setText('')
        self.longitude_input.setText('')
        self.drawmap(False)

    def add_postal_code(self):
        if self.toponym_address:
            if self.with_postal_code_checkbox.isChecked() and self.postal_code:
                self.search_result_label.setText(f'Адрес объекта: {self.postal_code}, {self.toponym_address}')
            else:
                self.search_result_label.setText(f'Адрес объекта: {self.toponym_address}')

    def zoom_in(self):
        self.z += 1
        if self.z > 17:
            self.z = 17
        self.drawmap(False)

    def zoom_out(self):
        self.z -= 1
        if self.z < 1:
            self.z = 1
        self.drawmap(False)

    def change_layer(self):
        self.layer += 1
        self.layer %= 3
        self.drawmap(False)

    def changecoords(self, *point_mode):
        if not point_mode:
            point_mode = False
        try:
            self.longitude = str(float(self.latitude_input.text()))
            self.latitude = str(float(self.longitude_input.text()))
            self.drawmap(point_mode)
        except ValueError:
            self.search_result_label.setText('Неверный формат ввода!')

    def movemap(self, button):
        if button == 'right':
            self.longitude = str(float(self.longitude) + 1)
        elif button == 'left':
            self.longitude = str(float(self.longitude) - 1)
        elif button == 'up':
            self.latitude = str(float(self.latitude) + 1)
        elif button == 'down':
            self.latitude = str(float(self.latitude) - 1)
        self.drawmap(False)

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
            latitude = str(float(self.longitude) + ((x - MAP_WIDTH / 2) * (1.45 / 2 ** self.z)))
            longitude = str(float(self.latitude) - ((y - MAP_HEIGHT / 2) * (1.2 / 2 ** self.z)))
            self.point = f"{latitude},{longitude},pmgnm1"
            self.geocoder(f"{latitude},{longitude}")
            self.latitude_input.setText(latitude)
            self.longitude_input.setText(longitude)
            self.drawmap(False)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
