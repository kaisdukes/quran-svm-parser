from enum import Enum, auto


class SegmentType(Enum):
    PREFIX = auto()
    STEM = auto()
    SUFFIX = auto()
