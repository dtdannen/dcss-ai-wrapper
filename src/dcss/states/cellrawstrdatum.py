from enum import Enum


class CellRawStrDatum(Enum):
    """ These are the types of data that may appear in a raw str description of a cell from the server. """
    x = 0
    f = 1
    y = 2
    g = 3
    t = 4
    mf = 5
    col = 6
    mon = 7