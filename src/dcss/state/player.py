from enum import Enum


class MovementSpeed(Enum):
    UNKNOWN = 0
    VERY_SLOW = 1
    SLOW = 2
    AVERAGE = 3
    QUICK = 4
    VERY_QUICK = 5


class AttackSpeed(Enum):
    UNKNOWN = 0
    BLINDINGLY_FAST = 1
    EXTREMELY_FAST = 2
    VERY_FAST = 3
    QUITE_FAST = 4
    ABOVE_AVERAGE = 5
    AVERAGE = 6
    BELOW_AVERAGE = 7
    QUITE_SLOW = 8
    VERY_SLOW = 9
    EXTREMELY_SLOW = 10