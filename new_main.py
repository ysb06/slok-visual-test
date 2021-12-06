import sys

from PyQt5.QtWidgets import QApplication
from slok_test.manager import initialize_experiment

from slok_test.window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()
    ex = MainWindow(width, height)
    ex.events.onSubmit.append(initialize_experiment)

    app.exec_()