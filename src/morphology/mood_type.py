from enum import Enum, auto


class MoodType(Enum):
    INDICATIVE = auto(), 'IND'
    SUBJUNCTIVE = auto(), 'SUBJ'
    JUSSIVE = auto(), 'JUS'

    def __init__(self, number_value, tag: str):
        self.number_value = number_value
        self.tag = tag

    @staticmethod
    def parse(tag: str):
        return MoodType.tags.get(tag)


MoodType.tags = {
    moodtype.tag: moodtype
    for moodtype in MoodType
}
