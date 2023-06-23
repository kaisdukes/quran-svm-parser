from enum import Enum, auto


class WordType(Enum):
    TOKEN = auto(), 'token'
    REFERENCE = auto(), 'reference'
    ELIDED = auto(), 'elided'

    def __init__(self, number_value, tag: str):
        self.number_value = number_value
        self.tag = tag

    @staticmethod
    def parse(tag: str):
        return WordType.tags.get(tag)


WordType.tags = {
    wordtype.tag: wordtype
    for wordtype in WordType
}
