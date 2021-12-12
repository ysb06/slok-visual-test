from random import randrange
from typing import Union

from PyQt5.QtCore import QTimer

from slok_test.exp_setting import *
from slok_test.window import MainWindow


class UIController:
    def __init__(self, target: MainWindow) -> None:
        self.target = target
        target.events.onTimeout.append(self.end_wait)
    
    def move_window_to_target(self):
        self.target.move(
            self.target.target_monitor.left(),
            self.target.target_monitor.top()
        )

        width = self.target.target_monitor.width()
        height = self.target.target_monitor.height()

        # 위치 초기화 코드로 재정비 필요
        self.target.resize(
            width,
            height
        )
        self.target.image.resetPosition()
        self.target.guide_label.setGeometry(
            width // 2 - 120, height // 2 - 100, 240, 64
        )

    def setInputFormVisible(self, visible: bool):
        for widget in self.target.widgets.values():
            widget.setVisible(visible)
            widget.setEnabled(visible)
    
    def setGuideText(self, visible: bool, text: str = 'None'):
        self.target.guide_label.setText(text)
        self.target.guide_label.setVisible(visible)

    def hide_all(self):
        for widget in self.target.widgets.values():
            widget.setVisible(False)
            widget.setEnabled(False)
        self.target.guide_label.setVisible(False)
        self.target.image.setVisible(False)
    
    def start_timer(self, msec_time: int, random: int = 0):
        if random != 0:
            random = randrange(-random, random)
        else:
            random = 0

        self.target.timer.start(msec_time + random)
    
    def end_wait(self):
        self.target.timer.stop()
    
    def show_image(self, size: int = 128, brightness: int = 127, frequency: float = 0):
        self.target.image.setVisible(True)
        self.target.image.setSize(size)
        self.target.image.setBrightness(brightness)

        self.target.image.setBlink(frequency)
        
        self.target.image.update()

    def show_image_by_type(self, exp_type: ExperimentType, value: Union[int, float]):
        if exp_type == ExperimentType.LUMINANCE:
            self.show_image(brightness=value, size=128)
        elif exp_type == ExperimentType.SIZE:
            self.show_image(size=value)
        elif exp_type == ExperimentType.BLINK:
            self.show_image(frequency=value)
        else:
            self.show_image()

    def dispose(self):
        self.target.events.onKeyPress.clear()
        self.target.events.onTimeout.clear()
        
        self.target.move(0, 0)
        self.target.resize(
            self.target.main_monitor.width(),
            self.target.main_monitor.height()
        )
