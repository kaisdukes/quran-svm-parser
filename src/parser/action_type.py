from enum import Enum, auto


class ActionType(Enum):
    SHIFT = auto()
    LEFT = auto()
    RIGHT = auto()
    PHRASE = auto()
    REDUCE = auto()
    SUBGRAPH = auto()
    SUBJECT = auto()
    EMPTY = auto()
