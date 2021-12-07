from typing import Dict, List, Callable, Set
from PyQt5.QtGui import QCloseEvent, QColor, QKeyEvent, QPaintEvent, QPainter, QPen, QPixmap, QMouseEvent

import yaml
from PyQt5.QtCore import QPoint, QRect, QTime, QTimer, Qt
from PyQt5.QtWidgets import (
    QDesktopWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)

import scaner.connector


class MainWindow(QWidget):
    def __init__(self, width, height) -> None:
        super().__init__()
        desktop = QDesktopWidget()
        target = 0
        if desktop.screenCount() > 1:
            target = 1
        target_monitor = desktop.screenGeometry(target)

        self.setWindowTitle('Visual Tester')
        self.move(target_monitor.left(), target_monitor.top())
        self.resize(width // 2, height // 2)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.image = FlexibleCircle(self)

        self.guide_label = QLabel('', self)
        self.guide_label.setStyleSheet('font-size: 24pt; color: white')
        self.guide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide_label.setGeometry(
            self.width() // 2 - 120, self.height() // 2 - 100, 240, 64
        )

        self.timer = QTimer()

        # 입력 부분 초기화
        self.widgets: Dict[str, QWidget] = {}
        self.widgets['ExpNameLineEdit'] = QLineEdit(self)
        self.widgets['ExpNameLineEdit'].setPlaceholderText('Input name...')
        self.widgets['SubmitButton'] = QPushButton('Start', self)

        vlayout = QVBoxLayout()
        vlayout.addStretch(1)
        for widget in self.widgets.values():
            vlayout.addWidget(widget)
            vlayout.addSpacing(16)
        vlayout.addStretch(1)
        hlayout = QHBoxLayout()
        hlayout.addStretch(2)
        hlayout.addLayout(vlayout)
        hlayout.addStretch(2)
        self.main_layout = hlayout
        self.setLayout(hlayout)

        self.events = MainWindowEvents(self)

        self.initializeStyle()
        self.show()

    def initializeStyle(self):
        with open('style.yaml') as file:
            style_raw = yaml.load(file, Loader=yaml.FullLoader)

            self.setAutoFillBackground(True)
            self.setStyleSheet('background-color: black')

            widget_styles: Dict[str, Dict] = style_raw['widgets']
            for widget, style in widget_styles.items():
                style_text = '; '.join(
                    [f'{attr}: {value}' for attr, value in style.items()])
                self.widgets[widget].setStyleSheet(style_text)
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.events.scaner_connector.deactivate()
        print('Main Window Closed')
    
    def paintEvent(self, a0: QPaintEvent) -> None:
        self.image.draw()


class MainWindowEvents:
    def __init__(self, parent: MainWindow) -> None:
        self.parent = parent

        self.onSubmit: List[Callable] = []
        self.onTimeout: List[Callable] = []
        self.onKeyPress: List[Callable] = []

        # Scaner UDP Connector 초기화
        self.scaner_connector = scaner.connector.QConnector(parent)
        self.scaner_connector.activate()

        self.parent.widgets['SubmitButton'].clicked.connect(self.submitEvent)
        self.parent.timer.timeout.connect(self.timeoutEvent)
        self.parent.keyPressEvent = self.keyPressEvent
        self.parent.mousePressEvent = self.mousePressEvent
        self.scaner_connector.onPress.connect(self.simulinkActivatedEvent)

    def submitEvent(self):
        text = self.parent.widgets['ExpNameLineEdit'].text()
        if text != '':
            for callback in self.onSubmit:
                callback(self.parent, text)

    def timeoutEvent(self):
        for callback in self.onTimeout:
            if callback() == True:
                return

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        for callback in self.onKeyPress:
            callback(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        for callback in self.onKeyPress:
            arg = FakeKeyEvent()    # 문제가 될 수 있는 부분, 수정 필요
            callback(arg)

    def simulinkActivatedEvent(self):
        for callback in self.onKeyPress:
            arg = FakeKeyEvent()    # 문제가 될 수 있는 부분, 수정 필요
            callback(arg)


class FakeKeyEvent:
    def key(self):
        return Qt.Key.Key_End


class FlexibleCircle(QWidget):
    def __init__(self, parent: MainWindow, radius: int = 50) -> None:
        super().__init__(parent)
        self.color = QColor(255, 255, 255, 255)
        self.radius = 0
        self.setSize(radius)
        self.setPosition(parent.width() // 2, parent.height() // 2)
        self.setVisible(False)

        self.blink_timer = QTimer()
        self.__blink_show = True
    
    def setSize(self, radius: int):
        prev_radius = self.radius
        self.radius = radius
        self.setFixedSize(radius * 2, radius * 2)
        pos = self.pos()
        self.setPosition(pos.x() + prev_radius, pos.y() + prev_radius)

    def setPosition(self, x: int, y: int):
        self.move(x - self.radius, y - self.radius)

    def setBrightness(self, value: int):
        self.color.setAlpha(value)

    def setBlink(self, frequency: int):
        if frequency > 0:
            self.frequency = frequency

            self.blink_timer = QTimer()
            self.blink_timer.timeout.connect(self.blink)
            self.blink_timer.setInterval(int(1000 / frequency))
            self.blink_timer.start()    # circle 이미지 클래스로 코드를 옮길 것
        else:
            raise Exception('Frequency must be over 0')

            

    def blink(self):
        if self.__blink_show:
            self.setFixedSize(0, 0)
            self.__blink_show = False
        else:
            self.setSize(self.radius)
            self.__blink_show = True

    def draw(self):
        if self.isVisible():
            painter = QPainter(self.parent())
            painter.setBrush(self.color)
            painter.drawEllipse(self.pos() + QPoint(self.radius, self.radius), self.radius, self.radius)

        # 이미지 표시기 초기화
        # self.setStyleSheet('color: white; font-size: 36pt')
        # self.move(0, 0)
        # self.setVisible(False)
        # self.setPixmap(QPixmap('images/circle.png').scaledToWidth(64))
        # self.setGeometry(QRect(0, 0, 64, 64))
