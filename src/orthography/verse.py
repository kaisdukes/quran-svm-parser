from dataclasses import dataclass
from typing import List

from .location import Location
from .token import Token


@dataclass
class Verse:
    location: Location
    tokens: List[Token]
