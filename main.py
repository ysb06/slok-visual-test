import sys

from PyQt5.QtWidgets import QApplication
from slok_test.manager import initialize_experiment

from slok_test.window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    exp = MainWindow()
    exp.events.onSubmit.append(initialize_experiment)

    app.exec_()