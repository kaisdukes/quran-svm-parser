from typing import Dict, Tuple

from .segment import Segment
from .segment_type import SegmentType
from .part_of_speech import PartOfSpeech
from .person_type import PersonType
from .gender_type import GenderType
from .number_type import NumberType
from .mood_type import MoodType
from .voice_type import VoiceType
from .case_type import CaseType
from .state_type import StateType
from .special_type import SpecialType
from ..lexicography.lemma_service import LemmaService


class SegmentReader:
    _affixes: Dict[str, Tuple[SegmentType, PartOfSpeech, str | None]] = {
        '+n:EMPH': (SegmentType.SUFFIX, PartOfSpeech.EMPHATIC, LemmaService.SUFFIX_NOON),
        '+VOC': (SegmentType.SUFFIX, PartOfSpeech.VOCATIVE, LemmaService.VOCATIVE_SUFFIX),
        'A:INTG+': (SegmentType.PREFIX, PartOfSpeech.INTERROGATIVE, None),
        'A:EQ+': (SegmentType.PREFIX, PartOfSpeech.EQUALIZATION, None),
        'f:CONJ+': (SegmentType.PREFIX, PartOfSpeech.CONJUNCTION, LemmaService.PREFIX_FA),
        'f:REM+': (SegmentType.PREFIX, PartOfSpeech.RESUMPTION, LemmaService.PREFIX_FA),
        'f:RSLT+': (SegmentType.PREFIX, PartOfSpeech.RESULT, LemmaService.PREFIX_FA),
        'f:CAUS+': (SegmentType.PREFIX, PartOfSpeech.CAUSE, LemmaService.PREFIX_FA),
        'f:SUP+': (SegmentType.PREFIX, PartOfSpeech.SUPPLEMENTAL, LemmaService.PREFIX_FA),
        'w:SUP+': (SegmentType.PREFIX, PartOfSpeech.SUPPLEMENTAL, LemmaService.PREFIX_WA),
        'w:CONJ+': (SegmentType.PREFIX, PartOfSpeech.CONJUNCTION, LemmaService.PREFIX_WA),
        'w:COM+': (SegmentType.PREFIX, PartOfSpeech.COMITATIVE, LemmaService.PREFIX_WA),
        'w:REM+': (SegmentType.PREFIX, PartOfSpeech.RESUMPTION, LemmaService.PREFIX_WA),
        'w:CIRC+': (SegmentType.PREFIX, PartOfSpeech.CIRCUMSTANTIAL, LemmaService.PREFIX_WA),
        'w:P+': (SegmentType.PREFIX, PartOfSpeech.PREPOSITION, LemmaService.PREFIX_WA),
        'ka+': (SegmentType.PREFIX, PartOfSpeech.PREPOSITION, LemmaService.PREFIX_KA),
        'l:EMPH+': (SegmentType.PREFIX, PartOfSpeech.EMPHATIC, None),
        'bi+': (SegmentType.PREFIX, PartOfSpeech.PREPOSITION, LemmaService.PREFIX_BI),
        'ta+': (SegmentType.PREFIX, PartOfSpeech.PREPOSITION, LemmaService.PREFIX_TA),
        'l:IMPV+': (SegmentType.PREFIX, PartOfSpeech.IMPERATIVE, None),
        'l:PRP+': (SegmentType.PREFIX, PartOfSpeech.PURPOSE, None),
        'sa+': (SegmentType.PREFIX, PartOfSpeech.FUTURE, LemmaService.PREFIX_SA),
        'ya+': (SegmentType.PREFIX, PartOfSpeech.VOCATIVE, LemmaService.PREFIX_YA),
        'ha+': (SegmentType.PREFIX, PartOfSpeech.VOCATIVE, LemmaService.PREFIX_HA),
        'Al+': (SegmentType.PREFIX, PartOfSpeech.DETERMINER, None)
    }

    def __init__(self, lemma_service: LemmaService):
        self.lemma_service = lemma_service

    def read(self, morphology: str, has_stem: bool):
        if morphology.startswith('POS:'):
            return self._read_stem(morphology)

        if morphology.startswith('PRON:'):
            segment = Segment(SegmentType.SUFFIX, PartOfSpeech.PRONOUN)
            self._read_person_gender_number(segment, morphology[5:])
            return segment

        if morphology == 'l:P+':
            if has_stem:
                return self._suffix(PartOfSpeech.PREPOSITION, LemmaService.PREFIX_LA)
            else:
                return self._prefix(PartOfSpeech.PREPOSITION, LemmaService.PREFIX_LA)

        entry = SegmentReader._affixes.get(morphology)
        if (entry is None):
            raise ValueError(f'Unknown morphology: {morphology}')

        type, part_of_speech, lemma = entry
        if type == SegmentType.PREFIX:
            return self._prefix(part_of_speech, lemma)
        else:
            return self._suffix(part_of_speech, lemma)

    def _read_stem(self, morphology: str):
        tags = morphology.split(' ')
        part_of_speech = PartOfSpeech.parse(tags[0][4:])
        segment = Segment(SegmentType.STEM, part_of_speech)

        size = len(tags)
        i = 1
        while i < size:
            tag = tags[i]

            if tag.startswith('ROOT:'):
                i += 1
                continue

            if tag.startswith('LEM:'):
                lemma = tag[4:]
                self._set_lemma(segment, lemma)
                i += 1
                continue

            if tag.startswith('SP:'):
                segment.special = SpecialType.parse(tag[3:])
                i += 1
                continue

            if tag.startswith('MOOD:'):
                segment.mood = MoodType.parse(tag[5:])
                i += 1
                continue

            if tag.startswith('('):
                i += 1
                continue

            if tag == 'NOM':
                segment.case = CaseType.NOMINATIVE
            elif tag == 'GEN':
                segment.case = CaseType.GENITIVE
            elif tag == 'ACC':
                segment.case = CaseType.ACCUSATIVE
            elif tag == 'ACT':
                if i < size - 1 and tags[i + 1] == 'PCPL':
                    i += 1
                else:
                    raise ValueError
            elif tag == 'PASS':
                if i < size - 1 and tags[i + 1] == 'PCPL':
                    i += 1
                else:
                    segment.voice = VoiceType.PASSIVE
            elif tag == 'DEF':
                segment.state = StateType.DEFINITE
            elif tag == 'INDEF':
                segment.state = StateType.INDEFINITE
            elif tag == 'PERF' or tag == 'IMPF' or tag == 'IMPV' or tag == 'VN':
                pass
            else:
                self._read_person_gender_number(segment, tag)

            i += 1

        return segment

    def _read_person_gender_number(self, segment: Segment, tag: str):
        for ch in tag:
            if ch == '1':
                segment.person = PersonType.FIRST
            elif ch == '2':
                segment.person = PersonType.SECOND
            elif ch == '3':
                segment.person = PersonType.THIRD
            elif ch == 'M':
                segment.gender = GenderType.MASCULINE
            elif ch == 'F':
                segment.gender = GenderType.FEMININE
            elif ch == 'S':
                segment.number = NumberType.SINGULAR
            elif ch == 'D':
                segment.number = NumberType.DUAL
            elif ch == 'P':
                segment.number = NumberType.PLURAL
            else:
                raise ValueError(f'Unknown tag: {tag}')

    def _prefix(self, part_of_speech: PartOfSpeech, lemma: str = None):
        segment = Segment(SegmentType.PREFIX, part_of_speech)
        if lemma is not None:
            self._set_lemma(segment, lemma)
        return segment

    def _suffix(self, part_of_speech: PartOfSpeech, lemma: str = None):
        segment = Segment(SegmentType.SUFFIX, part_of_speech)
        if lemma is not None:
            self._set_lemma(segment, lemma)
        return segment

    def _set_lemma(self, segment: Segment, lemma: str):
        self.lemma_service.add(lemma)
        segment.lemma = lemma
