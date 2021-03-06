from typing import Dict, List, Callable
from PyQt5.QtGui import QCloseEvent, QColor, QKeyEvent, QPaintEvent, QPainter, QMouseEvent

import yaml
from PyQt5.QtCore import QPoint, QTimer, Qt
from PyQt5.QtWidgets import (
    QDesktopWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)

import scaner.connector


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        desktop = QDesktopWidget()
        self.main_monitor = desktop.screenGeometry(0)
        target = 0
        if desktop.screenCount() > 1:
            target = 1
        self.target_monitor = desktop.screenGeometry(target)

        self.setWindowTitle('Visual Tester')
        self.move(0, 0)
        self.resize(self.main_monitor.width(), self.main_monitor.height())
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
        self.widgets['ManualButton'] = QPushButton('Manual Mode', self)

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
        self.scaner_connector = scaner.connector.QConnector(parent, debug=False)
        self.scaner_connector.activate()

        self.parent.widgets['SubmitButton'].clicked.connect(self.submitEvent)
        self.parent.widgets['ManualButton'].clicked.connect(self.clickManualButtonEvent)
        self.parent.timer.timeout.connect(self.timeoutEvent)
        self.parent.keyPressEvent = self.keyPressEvent
        self.parent.mousePressEvent = self.mousePressEvent
        self.scaner_connector.onPress.connect(self.simulinkActivatedEvent)

    def submitEvent(self):
        text = self.parent.widgets['ExpNameLineEdit'].text()
        if text != '':
            for callback in self.onSubmit:
                callback(self.parent, text=text)
    
    def clickManualButtonEvent(self):
        for callback in self.onSubmit:
            callback(self.parent, mode='Survey')

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

    def simulinkActivatedEvent(self, key: Qt.Key):
        for callback in self.onKeyPress:
            arg = FakeKeyEvent(key)    # 문제가 될 수 있는 부분, 수정 필요
            callback(arg)


class FakeKeyEvent:
    def __init__(self, key=Qt.Key.Key_End) -> None:
        self.value = key
        
    def key(self):
        return self.value


class FlexibleCircle(QWidget):
    def __init__(self, parent: MainWindow, radius: int = 127) -> None:
        super().__init__(parent)
        self.parent_window = parent
        self.color = QColor(255, 255, 255, 255)
        self.radius = 0
        self.setSize(radius)
        self.resetPosition()
        self.setVisible(False)

        self.blink_timer = QTimer()
        self.__blink_show = True
        self.blink_timer.timeout.connect(self.blink)
    
    def resetPosition(self):
        self.setPosition(
            self.parent_window.width() // 2, 
            self.parent_window.height() // 2
        )

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
        self.blink_timer.stop()
        self.__blink_show = True

        if frequency > 0:
            self.frequency = frequency

            self.blink_timer.setInterval(int(1000 / frequency))
            self.blink_timer.start()    # circle 이미지 클래스로 코드를 옮길 것

    def blink(self):
        if self.__blink_show:
            # self.setFixedSize(0, 0)
            self.__blink_show = False
        else:
            # self.setSize(self.radius)
            self.__blink_show = True
        
        self.update()

    def draw(self):
        if self.isVisible() and self.__blink_show:
            painter = QPainter(self.parent())
            painter.setBrush(self.color)
            painter.drawEllipse(self.pos() + QPoint(self.radius, self.radius), self.radius, self.radius)

        # 이미지 표시기 초기화
        # self.setStyleSheet('color: white; font-size: 36pt')
        # self.move(0, 0)
        # self.setVisible(False)
        # self.setPixmap(QPixmap('images/circle.png').scaledToWidth(64))
        # self.setGeometry(QRect(0, 0, 64, 64))