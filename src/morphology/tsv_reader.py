from typing import List

from .segment import Segment
from .part_of_speech import PartOfSpeech
from .pronoun_type import PronounType
from .segment_type import SegmentType
from .segment_reader import SegmentReader
from ..orthography.location import Location
from ..orthography.token import Token
from ..lexicography.lemma_service import LemmaService


class TsvReader:
    def __init__(self, lemma_service: LemmaService):
        self.tokens: List[Token] = []
        self.segments: List[Segment] = []
        self._segment_reader = SegmentReader(lemma_service)
        self._morphemes: List[Morpheme] = []
        self._location: Location | None = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._read_token()

    def read_segment(self, line):
        parts = line.split('\t')
        location = Location(int(parts[0]), int(parts[1]), int(parts[2]))
        if self._location is not None and location != self._location:
            self._read_token()
        self._morphemes.append(Morpheme(parts[3], parts[4] if len(parts) >= 5 else None))
        self._location = location

    def _read_token(self):
        self._add_token()
        self._read_segments()

    def _add_token(self):
        self.tokens.append(Token(self._location))

    def _read_segments(self):
        stem: Segment | None = None
        object_pronoun: Segment | None = None

        segment_count = len(self._morphemes)
        segments: List[Segment | None] = [None]*segment_count
        for i in range(segment_count):
            morpheme = self._morphemes[i]
            if morpheme.morphology is None:
                segment = Segment(SegmentType.SUFFIX, PartOfSpeech.PRONOUN)
                segment.person = stem.person
                segment.gender = stem.gender
                segment.number = stem.number
                segment.pronoun_type = PronounType.SUBJECT
            else:
                segment = self._segment_reader.read(morpheme.morphology, stem is not None)

            segment.segment_number = i + 1

            if (segment.part_of_speech == PartOfSpeech.PRONOUN
                    and segment.type == SegmentType.SUFFIX
                    and morpheme.morphology is not None):
                segment.pronoun_type = PronounType.SECOND_OBJECT if object_pronoun is not None else PronounType.OBJECT
                if object_pronoun is None:
                    object_pronoun = segment

            if segment.type == SegmentType.STEM:
                stem = segment

            segments[i] = segment

        self.segments.append(segments)
        self._morphemes.clear()


class Morpheme:
    def __init__(self, arabic, morphology):
        self.arabic = arabic
        self.morphology = morphology
