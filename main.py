import sys
from typing import Dict, List, Callable
from PyQt5.QtGui import QKeyEvent, QPixmap

import yaml
from PyQt5.QtCore import QRect, QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget)

import test_manager


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        screen_rect = app.desktop().screenGeometry()

        self.setWindowTitle('Visual Tester')
        self.move(0, 0)
        self.resize(screen_rect.width() // 2, screen_rect.height() // 2)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 이미지 표시기 초기화
        self.image = QLabel('Blank Image', self)
        self.image.setStyleSheet('color: white; font-size: 36pt')
        self.image.move(0, 0)
        self.image.setVisible(False)
        self.image.setPixmap(QPixmap('images/circle.png').scaledToWidth(64))
        self.image.setGeometry(QRect(0, 0, 64, 64))

        self.guide_label = QLabel('Ready', self)
        self.guide_label.setStyleSheet('font-size: 24pt; color: white')
        self.guide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide_label.setGeometry(self.width() // 2 - 90, self.height() // 2 - 100, 180, 64)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)

        # 입력 부분 초기화
        self.widgets: Dict[str, QWidget] = {}
        self.widgets['ExpNameLineEdit'] = QLineEdit(self)
        self.widgets['ExpNameLineEdit'].setPlaceholderText('Input name...')
        self.widgets['SubmitButton'] = QPushButton('Start', self)
        self.widgets['SubmitButton'].clicked.connect(self.submit)
        
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

        # 마무리
        self.onKeyPressed: List[Callable[[QKeyEvent], None]] = []
        self.onTimeout: List[Callable] = []
        self.initializeStyle()
        self.show()
    
    def initializeStyle(self):
        with open('style.yaml') as file:
            style_raw = yaml.load(file, Loader=yaml.FullLoader)

            self.setAutoFillBackground(True)
            self.setStyleSheet('background-color: black')

            widget_styles: Dict[str, Dict] = style_raw['widgets']
            for widget, style in widget_styles.items():
                style_text = '; '.join([f'{attr}: {value}' for attr, value in style.items()])
                self.widgets[widget].setStyleSheet(style_text)

    def submit(self):
        name = self.widgets['ExpNameLineEdit'].text()
        if name != '':
            test_manager.start_experiment(self, name)
    
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        for callback in self.onKeyPressed:
            callback(a0)
    
    def timeout(self):
        for callback in self.onTimeout:
            if callback() == True:
                return


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainWindow()
   app.exec_()
