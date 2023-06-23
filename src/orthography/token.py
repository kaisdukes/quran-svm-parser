from typing import List

from ..morphology.segment import Segment
from .location import Location


class Token:

    def __init__(self, location: Location):
        self.location = location
        self.segments: List[Segment] | None = None

    def segment(self, segment_number: int):
        return self.segments[segment_number - 1]
