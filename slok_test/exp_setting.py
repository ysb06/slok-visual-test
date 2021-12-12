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
    ExperimentType.BLINK
]

# TEST_LIST = [
#     ExperimentType.BLINK
# ]

LUMINANCE_TEST_SET = [15, 95, 175, 255]
SIZE_TEST_SET = [32, 107, 181, 256]
BLINK_TEST_SET = [1, 2, 3]

STAND_BY_TIME = 1000 * 7
STAND_BY_TIME_RANDOM_ADJUSTMENT = 1000 * 3
