from enum import Enum, auto


class SpecialType(Enum):
    KAANA = auto(), 'kaAn'
    KAADA = auto(), 'kaAd'
    INNA = auto(), '<in~'

    def __init__(self, number_value, tag: str):
        self.number_value = number_value
        self.tag = tag

    @staticmethod
    def parse(tag: str):
        return SpecialType.tags.get(tag)


SpecialType.tags = {
    special_type.tag: special_type
    for special_type in SpecialType
}
