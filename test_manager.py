import random
import time
from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

from main import MainWindow
from test_recorder import record, ExperimentInfo

MAX_EXPERIMENT_COUNT = 3
MAX_TEST_COUNT = 10


class UIController():
    def __init__(self, target: MainWindow) -> None:
        self.target = target
        self.pos = -1

    def show_next_image(self, fixed_pos: int = None):
        if fixed_pos == None:
            pos = random.randrange(0, 5)
            while self.pos == pos:
                pos = random.randrange(0, 5)
            self.pos = pos
        else:
            self.pos = fixed_pos

        width = self.target.width()
        height = self.target.height()

        hElem = width // 6 - 32
        vElem = height // 6 - 32
        adj = height // 12
        top_adj = adj
        bottom_adj = adj * 2

        if self.pos == 0:
            self.target.image.move(hElem, vElem + top_adj)
        elif self.pos == 1:
            self.target.image.move(width - hElem, vElem + top_adj)
        elif self.pos == 2:
            self.target.image.move(width - hElem, height - vElem - bottom_adj)
        elif self.pos == 3:
            self.target.image.move(hElem, height - vElem - bottom_adj)
        else:
            self.target.image.move(width // 2 - 32, (height - bottom_adj) // 2 + top_adj - 32)

    def reset_window(self):
        for widget in self.target.widgets.values():
            widget.setVisible(True)
            widget.setEnabled(True)
        
        self.target.guide_label.setVisible(False)
        self.target.image.setVisible(False)

    def hide_widgets(self):
        for widget in self.target.widgets.values():
            widget.setVisible(False)
            widget.setEnabled(False)
    
    def set_start_guide(self, visible: bool):
        if self.target.guide_label.isVisible() != visible:
            self.target.guide_label.setVisible(visible)
    
    def set_start_guide_text(self, isEnd: bool):
        if isEnd:
            self.target.guide_label.setText('Finished')
        else:
            self.target.guide_label.setText('Ready')

    def set_image_mode(self):
        self.target.image.setVisible(True)

class ExperimentPhase(Enum):
    UNKNOWN = 0
    TEST_SET_PREPAIRED = 1
    STAND_BY = 2
    READY = 3
    SHOW_IMAGE = 4
    SUBJECT_REACTED = 5
    TEST_SET_ENDED = 6
    EXPERIMENT_ENDED = 7

class Experiment:
    def __init__(self, name: str, ui: MainWindow) -> None:
        self.info = ExperimentInfo(name)
        self.phase = ExperimentPhase.STAND_BY

        self.controller = UIController(ui)
        self.controller.target.onKeyPressed.append(self.subject_reacted)
        self.controller.target.onTimeout.append(lambda: print(self.phase)) 
        self.controller.target.onTimeout.append(self.show_next)
        self.controller.target.onTimeout.append(self.end_test_set)
        self.controller.target.onTimeout.append(self.reset_experiment)

        self.controller.hide_widgets()
        self.controller.set_image_mode()
        self.controller.show_next_image(4)
        self.controller.set_start_guide(True)

        self.prev_time = 0
        self.need_quit = False
        
        self.phase = ExperimentPhase.TEST_SET_PREPAIRED
        self.phase = ExperimentPhase.READY

    def subject_reacted(self, e: QKeyEvent):
        key = e.key()
        if key == Qt.Key.Key_Backspace:
            self.reset_experiment()
            print('Canceled...')
        elif key == Qt.Key.Key_Escape:
            if self.need_quit:
                self.phase = ExperimentPhase.EXPERIMENT_ENDED
                self.end_experiment()
            else:
                self.need_quit = True
            
            return

        elif key == Qt.Key.Key_Alt or key == Qt.Key.Key_Control or key == Qt.Key.Key_Shift:
            pass

        else:
            if self.phase == ExperimentPhase.READY:
                self.phase = ExperimentPhase.SUBJECT_REACTED

                current_time = time.time_ns()
                interval_from_prev = current_time - self.prev_time
                
                # 기록 시작
                if self.info.try_count != 0:
                    self.info.record_time = current_time
                    self.info.last_reaction_time = interval_from_prev

                    print(f"Exp {self.info.exp_count} - Try {self.info.try_count}: {interval_from_prev / 1000000000}")
                    record(self.info)

                # 1 ~ 1.5까지 임의로 멈추어서 다음 테스트를 준비
                self.info.try_count += 1
                if self.info.try_count <= MAX_TEST_COUNT:
                    self.phase = ExperimentPhase.STAND_BY
                    self.controller.target.timer.start(1000 + random.randrange(0, 500))
                else:
                    self.info.exp_count += 1

                    if self.info.exp_count > MAX_EXPERIMENT_COUNT:
                        self.phase = ExperimentPhase.EXPERIMENT_ENDED
                        self.end_experiment()  # 실험 종료
                    else:
                        self.phase = ExperimentPhase.TEST_SET_ENDED
                        self.controller.target.timer.start(1000)
        
        self.need_quit = False

    def show_next(self):
        if self.phase == ExperimentPhase.STAND_BY:
            self.controller.target.timer.stop()

            self.controller.set_start_guide(False)
            self.controller.show_next_image()

            self.prev_time = time.time_ns()
            self.phase = ExperimentPhase.READY

    def end_test_set(self):
        if self.phase == ExperimentPhase.TEST_SET_ENDED:
            print('Test prepairing...')
            self.controller.target.timer.stop()

            self.controller.set_start_guide(True)
            self.controller.set_start_guide_text(True)
            self.controller.show_next_image(4)

            self.phase = ExperimentPhase.TEST_SET_PREPAIRED
            self.controller.target.timer.start(3000)

            return True

    def reset_experiment(self):
        if self.phase == ExperimentPhase.TEST_SET_PREPAIRED:
            self.controller.target.timer.stop()
            
            self.info.try_count = 0
            self.phase = ExperimentPhase.READY

            self.controller.set_start_guide_text(False)
            
    def end_experiment(self):
        if self.phase == ExperimentPhase.EXPERIMENT_ENDED:
            self.controller.reset_window()
            self.controller.target.onKeyPressed.remove(self.subject_reacted)
            self.controller.target.onTimeout.remove(self.show_next)


def start_experiment(ui: MainWindow, name: str):
    print(f'{name} Test Start!')
    Experiment(name, ui)
