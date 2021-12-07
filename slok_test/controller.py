from PyQt5.QtCore import QTimer
from slok_test.window import MainWindow
from random import randrange

class UIController:
    def __init__(self, target: MainWindow) -> None:
        self.target = target
        target.events.onTimeout.append(self.end_wait)
    
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
    
    def show_image(self, size: int = 50, brightness: int = 255, frequency: float = 0):
        self.target.image.setVisible(True)
        self.target.image.setSize(size)
        self.target.image.setBrightness(brightness)

        self.target.image.setBlink(frequency)
        
        self.target.image.update()


    def dispose(self):
        self.target.events.onKeyPress.clear()
        self.target.events.onTimeout.clear()