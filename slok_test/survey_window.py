from enum import Enum
from typing import Callable, List, Tuple, Union

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

        self.last_button: Union[SurveyTestButton, None] = None
        self.before_last_button: Union[SurveyTestButton, None] = None
        self.need_to_run_last = False
        controller.target.events.onKeyPress.append(self.run_last_action)

        vlayout = QVBoxLayout()
        vlayout.addSpacing(32)
        for test_name, test_set_values in zip(test_set[0], test_set[1]):
            hlayout = QHBoxLayout()
            hlayout.addSpacing(16)

            label = QLabel(str(test_name.name), self)
            label.setFixedWidth(100)
            hlayout.addWidget(label)
            for item in test_set_values:
                button = SurveyTestButton(self, controller, test_name, item)
                hlayout.addWidget(button)
            hlayout.addStretch(1)
            hlayout.addSpacing(16)

            vlayout.addLayout(hlayout)
        vlayout.addSpacing(32)

        self.setLayout(vlayout)

    def closeEvent(self, a0: QCloseEvent) -> None:
        for callback in self.onClose:
            callback()

    def run_last_action(self, arg=None):
        if self.last_button is not None and self.before_last_button is not None:
            if self.need_to_run_last:
                self.need_to_run_last = False
                self.last_button.run_only_action()
            else:
                self.need_to_run_last = True
                self.before_last_button.run_only_action()


class SurveyTestButton(QPushButton):
    def __init__(self, parent: SurveyWindow, controller: UIController, type: Enum, value) -> None:
        super().__init__(str(value), parent)
        self.parent_window = parent

        self.controller = controller
        self.type = type
        self.value = value

        self.clicked.connect(self.run_action)

    def run_action(self):
        self.controller.show_image_by_type(self.type, self.value)
        print(f'{self.type} [{self.value}]')

        self.parent_window.before_last_button = self.parent_window.last_button
        self.parent_window.last_button = self
    
    def run_only_action(self):
        self.controller.show_image_by_type(self.type, self.value)
        print(f'{self.type} [{self.value}]')
