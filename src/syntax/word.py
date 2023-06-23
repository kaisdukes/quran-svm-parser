from dataclasses import dataclass

from .word_type import WordType
from ..orthography.token import Token
from ..morphology.part_of_speech import PartOfSpeech


@dataclass
class Word:
    type: WordType
    token: Token
    elided_text: str
    elided_part_of_speech: PartOfSpeech
