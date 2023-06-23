from enum import Enum, auto


class PartOfSpeech(Enum):
    NOUN = auto(), 'N'
    PROPER_NOUN = auto(), 'PN'
    PRONOUN = auto(), 'PRON'
    DEMONSTRATIVE = auto(), 'DEM'
    RELATIVE = auto(), 'REL'
    ADJECTIVE = auto(), 'ADJ'
    VERB = auto(), 'V'
    PREPOSITION = auto(), 'P'
    INTERROGATIVE = auto(), 'INTG'
    VOCATIVE = auto(), 'VOC'
    NEGATIVE = auto(), 'NEG'
    EMPHATIC = auto(), 'EMPH'
    PURPOSE = auto(), 'PRP'
    IMPERATIVE = auto(), 'IMPV'
    FUTURE = auto(), 'FUT'
    CONJUNCTION = auto(), 'CONJ'
    DETERMINER = auto(), 'DET'
    INITIALS = auto(), 'INL'
    TIME = auto(), 'T'
    LOCATION = auto(), 'LOC'
    ACCUSATIVE = auto(), 'ACC'
    CONDITIONAL = auto(), 'COND'
    SUBORDINATING_CONJUNCTION = auto(), 'SUB'
    RESTRICTION = auto(), 'RES'
    EXCEPTIVE = auto(), 'EXP'
    AVERSION = auto(), 'AVR'
    CERTAINTY = auto(), 'CERT'
    RETRACTION = auto(), 'RET'
    PREVENTIVE = auto(), 'PREV'
    ANSWER = auto(), 'ANS'
    INCEPTIVE = auto(), 'INC'
    SURPRISE = auto(), 'SUR'
    SUPPLEMENTAL = auto(), 'SUP'
    EXHORTATION = auto(), 'EXH'
    IMPERATIVE_VERBAL_NOUN = auto(), 'IMPN'
    EXPLANATION = auto(), 'EXL'
    EQUALIZATION = auto(), 'EQ'
    RESUMPTION = auto(), 'REM'
    CAUSE = auto(), 'CAUS'
    AMENDMENT = auto(), 'AMD'
    PROHIBITION = auto(), 'PRO'
    CIRCUMSTANTIAL = auto(), 'CIRC'
    RESULT = auto(), 'RSLT'
    INTERPRETATION = auto(), 'INT'
    COMITATIVE = auto(), 'COM'

    def __init__(self, number_value, tag: str):
        self.number_value = number_value
        self.tag = tag

    @staticmethod
    def parse(tag: str):
        return PartOfSpeech.tags.get(tag)


PartOfSpeech.tags = {
    part_of_speech.tag: part_of_speech
    for part_of_speech in PartOfSpeech
}
