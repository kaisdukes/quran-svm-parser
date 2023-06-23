from enum import Enum, auto


class PhraseType(Enum):
    SENTENCE = auto(), 'S'
    NOMINAL_SENTENCE = auto(), 'NS'
    VERBAL_SENTENCE = auto(), 'VS'
    CONDITIONAL_SENTENCE = auto(), 'CS'
    PREPOSITION_PHRASE = auto(), 'PP'
    SUBORDINATE_CLAUSE = auto(), 'SC'

    def __init__(self, number_value, tag: str):
        self.number_value = number_value
        self.tag = tag

    @staticmethod
    def parse(tag: str):
        return PhraseType.tags.get(tag)


PhraseType.tags = {
    phrase_type.tag: phrase_type
    for phrase_type in PhraseType
}
