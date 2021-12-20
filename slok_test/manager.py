import time
from collections import deque
from enum import Enum
from random import shuffle
from typing import Callable, Dict, Union

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from test_recorder import ExperimentInfo, record

from slok_test.controller import UIController
from slok_test.exp_setting import *
from slok_test.survey_window import SurveyWindow
from slok_test.window import FakeKeyEvent, MainWindow


class ExperimentPhase(Enum):
    UNKNOWN = 0
    EXPERIMENT_STARTED = 1
    TEST_SET_READY = 2
    STAND_BY = 3
    SHOWING_IMAGE = 4
    SUBJECT_REACTED = 5
    TEST_SET_ENDED = 6
    EXPERIMENT_ENDED = 7


def initialize_experiment(sender: MainWindow, text: str = 'None', mode: str = 'Standard'):
    if mode == 'Standard':
        print('Test Mode')
        Experiment(sender, text)
    else:
        print('Survey Mode')
        Survey(sender)


class Experiment:
    def __init__(self, window: MainWindow, name: str) -> None:
        self.info = ExperimentInfo(name)
        self.controller = UIController(window)
        self.state = ExperimentPhase.EXPERIMENT_STARTED
        self.test_order = deque(TEST_LIST)
        self.test_count = len(self.test_order)
        self.test_set = deque()
        self.current_test_type = ExperimentType.NONE

        self.timeout_actions: Dict[ExperimentPhase, Callable[[], None]] = {}
        self.anykey_actions: Dict[ExperimentPhase, Callable[[], None]] = {}
        self.binded_key_actions: Dict[Qt.Key, Callable[[Qt.Key], None]] = {}

        self.start_time = 0

        self.test_value: Union[int, None] = None

        # -----
        window.events.onTimeout.append(self.onTimeout)
        window.events.onKeyPress.append(self.receive_input)
        # -----

        window.events.onTimeout.append(self.print_event)
        window.events.onKeyPress.append(self.print_event)

        self.define_actions()

        self.start_exp()

    def print_event(self, _=None):
        print(self.current_test_type, f'[{self.test_value}]', ':', self.state)

    def onTimeout(self):
        if self.state in self.timeout_actions:
            self.timeout_actions[self.state]()

    def receive_input(self, e: Union[QKeyEvent, FakeKeyEvent]):
        input_key: Qt.Key = e.key()

        if input_key in self.binded_key_actions:
            self.binded_key_actions[input_key](input_key)
        else:
            if self.state in self.anykey_actions:
                self.anykey_actions[self.state]()

    def generate_exp_var(self, exp_type: ExperimentType):
        var_list = []

        if exp_type == ExperimentType.LUMINANCE:
            var_list = LUMINANCE_TEST_SET * \
                (MAX_TEST_COUNT // len(LUMINANCE_TEST_SET) + 1)
        elif exp_type == ExperimentType.SIZE:
            var_list = SIZE_TEST_SET * \
                (MAX_TEST_COUNT // len(SIZE_TEST_SET) + 1)
        elif exp_type == ExperimentType.BLINK:
            var_list = BLINK_TEST_SET * \
                (MAX_TEST_COUNT // len(BLINK_TEST_SET) + 1)
        else:
            raise Exception('Not supported type')

        var_list = var_list[:MAX_TEST_COUNT]
        shuffle(var_list)
        print(var_list, '<-')

        return deque(var_list)

    def define_actions(self):
        # 실험 순서는 self.test_order에 정의
        # 1. 각 테스트 시작 준비
        self.timeout_actions[ExperimentPhase.EXPERIMENT_STARTED] = self.reset_test_set
        self.timeout_actions[ExperimentPhase.TEST_SET_ENDED] = self.reset_test_set
        # 2. 실험자가 아무 키나 누르면 실험 시작
        self.anykey_actions[ExperimentPhase.TEST_SET_READY] = self.stand_by_before_show_cue
        # 3. 약 10초 후 이미지 표시 (시간 랜덤)
        self.timeout_actions[ExperimentPhase.STAND_BY] = self.show_cue
        # 4. 실험대상자가 버튼을 누르면 시간 측정
        self.anykey_actions[ExperimentPhase.SHOWING_IMAGE] = self.subject_reacted
        # 5. 3~4 과정 반복
        # 6. MAX_TEST_COUNT에 다다르면 1~5과정 반복
        self.timeout_actions[ExperimentPhase.SUBJECT_REACTED] = self.stand_by_before_show_cue
        # 7. 모든 실험이 끝나면 실험 종료
        self.anykey_actions[ExperimentPhase.EXPERIMENT_ENDED] = self.finalize_experiment

        self.binded_key_actions[Qt.Key.Key_Escape] = self.finalize_experiment
        self.binded_key_actions[Qt.Key.Key_Backspace] = self.soft_reset_test_set

    def start_exp(self):
        self.controller.hide_all()
        self.controller.move_window_to_target()

        self.print_event()

        self.controller.start_timer(100)

    def reset_test_set(self):
        self.controller.hide_all()
        self.controller.setGuideText(True, '')

        self.info.try_count = 0

        if len(self.test_order) > 0:
            self.current_test_type = self.test_order.popleft()
            self.test_set = self.generate_exp_var(self.current_test_type)
            # self.info.exp_count = self.test_count - len(self.test_order)
            self.info.exp_count = self.current_test_type.name
            self.state = ExperimentPhase.TEST_SET_READY
        else:
            self.state = ExperimentPhase.EXPERIMENT_ENDED
            self.controller.setGuideText(True, 'Exp. Ended')

    def soft_reset_test_set(self):
        self.controller.hide_all()
        self.controller.setGuideText(True, '')

        self.info.try_count = 0
        self.state = ExperimentPhase.TEST_SET_READY

    def stand_by_before_show_cue(self):
        self.controller.hide_all()

        if self.info.try_count < MAX_TEST_COUNT:
            self.state = ExperimentPhase.STAND_BY
            self.controller.start_timer(
                STAND_BY_TIME, STAND_BY_TIME_RANDOM_ADJUSTMENT)
        else:
            self.state = ExperimentPhase.TEST_SET_ENDED
            self.controller.start_timer(1000)

    def show_cue(self):
        self.test_value = self.test_set.pop()

        self.controller.show_image_by_type(
            self.current_test_type, self.test_value)

        self.start_time = time.time_ns()
        self.state = ExperimentPhase.SHOWING_IMAGE

    def subject_reacted(self):
        # Recording...
        end_time = time.time_ns()
        interval_time = end_time - self.start_time
        self.info.record_time = end_time
        self.info.last_reaction_time = interval_time
        self.info.value = self.test_value
        print(f"Exp {self.info.exp_count} [{self.info.value}] Try {self.info.try_count}: {self.info.last_reaction_time / 1000000000} sec")
        record(self.info)

        self.controller.hide_all()
        self.controller.setGuideText(True, '')

        self.info.try_count += 1
        self.state = ExperimentPhase.SUBJECT_REACTED
        self.test_value = None

        self.controller.start_timer(3000)

    def finalize_experiment(self, arg=None):
        self.controller.hide_all()
        self.controller.setInputFormVisible(True)
        self.controller.dispose()
        del self.controller
        del self


class Survey:
    def __init__(self, window: MainWindow) -> None:
        self.controller = UIController(window)
        self.subwindow = SurveyWindow(
            self.controller,
            (
                SURVEY_LIST,
                [
                    LUMINANCE_TEST_SET,
                    SIZE_TEST_SET,
                    BLINK_TEST_SET
                ]
            )
        )
        self.subwindow.show()
        self.subwindow.onClose.append(self.finalize_experiment)

        # 실험과 같은 초기화
        self.controller.hide_all()
        self.controller.move_window_to_target()

    def finalize_experiment(self, arg=None):
        self.controller.hide_all()
        self.controller.setInputFormVisible(True)
        self.controller.dispose()
        del self.controller
        del self
