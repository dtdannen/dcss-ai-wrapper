from enum import Enum


class TerrainType(Enum):

    """
    Represents terrain of a tile
    """

    NULL_SPELL_SPECIAL_CASE = 0

    WALL = 1
    CLOSED_DOOR = 2
    OPENED_DOOR = 3
    TREE = 4
    LAVA = 5
    SHALLOW_WATER = 6
    DEEP_WATER = 7
    STAIRS_DOWN = 8
    STAIRS_UP = 9
    SHAFT_DOWN = 10
    SHAFT_UP = 11

