from enum import Enum
from typing import Callable, List, Tuple

from PyQt5.QtCore import QPoint, QRect, Qt, QTime, QTimer
from PyQt5.QtGui import (QCloseEvent, QColor, QKeyEvent, QMouseEvent, QPainter,
                         QPaintEvent, QPen, QPixmap)
from PyQt5.QtWidgets import (QDesktopWidget, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget)

from slok_test.controller import UIController


class SurveyWindow(QWidget):
    def __init__(
            self, 
            controller: UIController,
            test_set: Tuple[List[Enum], List[List]]
        ) -> None:
        super().__init__()
        self.onClose: List[Callable[[], None]] = []

        self.setWindowTitle('Survey Mode')
        self.controller = controller

        vlayout = QVBoxLayout()
        vlayout.addSpacing(32)
        for test_name, test_set_values in zip(test_set[0], test_set[1]):
            hlayout = QHBoxLayout()
            hlayout.addSpacing(16)

            label = QLabel(str(test_name.name), self)
            label.setFixedWidth(100)
            hlayout.addWidget(label)
            for item in test_set_values:
                print(test_name, item)
                button = UIControllerButton(self, controller, test_name, item)
                hlayout.addWidget(button)
            hlayout.addStretch(1)
            hlayout.addSpacing(16)

            vlayout.addLayout(hlayout)
        vlayout.addSpacing(32)

        self.setLayout(vlayout)

    def closeEvent(self, a0: QCloseEvent) -> None:
        for callback in self.onClose:
            callback()


class UIControllerButton(QPushButton):
    def __init__(self, parent: QWidget, controller: UIController, type: Enum, value) -> None:
        super().__init__(str(value), parent)
        self.controller = controller
        self.type = type
        self.value = value

        self.clicked.connect(lambda: self.controller.show_image_by_type(self.type, self.value))
        self.clicked.connect(lambda: print(f'{self.type} [{self.value}]'))