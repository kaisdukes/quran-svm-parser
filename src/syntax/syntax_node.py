from .word import Word
from .word_type import WordType
from .phrase_type import PhraseType
from ..morphology.segment import Segment


class SyntaxNode:

    def __init__(self):
        self.word: Word | None = None
        self.segment_number: int = 0
        self.phrase_type: PhraseType | None = None
        self.start: SyntaxNode | None = None
        self.end: SyntaxNode | None = None
        self.index: int = 0

    @property
    def is_phrase(self):
        return self.phrase_type is not None

    @property
    def part_of_speech(self):
        if self.word is None:
            return None
        return self.word.elided_part_of_speech if self.word.type == WordType.ELIDED else self.segment.part_of_speech

    @property
    def segment(self):
        return None if self.word is None or self.word.type == WordType.ELIDED else self.word.token.segment(self.segment_number)

    def __eq__(self, other: 'SyntaxNode'):

        if self.phrase_type != other.phrase_type:
            return False

        if other.phrase_type is not None:
            return self.start == other.start and self.end == other.end

        if self.word.type != other.word.type:
            return False

        if self.word.type == WordType.ELIDED:
            return (self.word.elided_part_of_speech == other.word.elided_part_of_speech
                    and self.word.elided_text == other.word.elided_text)

        return self.segment is other.segment

    def __str__(self):
        return self.phrase_type.tag if self.is_phrase else self.part_of_speech.tag
