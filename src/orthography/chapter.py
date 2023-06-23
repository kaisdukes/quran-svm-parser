from dataclasses import dataclass
from typing import List

from .verse import Verse


@dataclass
class Chapter:
    verses: List[Verse]
