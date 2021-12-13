from enum import Enum


class ExperimentType(Enum):
    NONE = 0
    LUMINANCE = 1
    SIZE = 2
    BLINK = 3


MAX_TEST_COUNT = 10

TEST_LIST = [
    ExperimentType.LUMINANCE,
    ExperimentType.SIZE,
    # ExperimentType.BLINK
]

# TEST_LIST = [
#     ExperimentType.BLINK
# ]

LUMINANCE_TEST_SET = [15, 95, 175, 255]     # 0.7 lux, 1.1 lux, 2.1 lux, 3.8 lux
# SIZE_TEST_SET = [32, 107, 181, 256]         # 0.9cm, 3cm, 5.1cm, 7.2cm

                                            # NHTSA 기준
                                            # 최소 0.68도 tan = 0.012, 최적 1.43도 tan = 0.025, 시뮬레이터 눈과 모니터 사이 거리 63cm
SIZE_TEST_SET = [27, 57, 120, 252]          # 0.8cm (최소), 1.6cm (최적, x2.1), 3.3cm (x2.1), 6.9cm (x2.1)
BLINK_TEST_SET = [1, 2, 3]

STAND_BY_TIME = 1000 * 7
STAND_BY_TIME_RANDOM_ADJUSTMENT = 1000 * 3
