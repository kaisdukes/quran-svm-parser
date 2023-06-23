from .person_type import PersonType
from .gender_type import GenderType
from .number_type import NumberType


def get_pronoun(person: PersonType, gender: GenderType, number: NumberType):

    # 1S
    if person == PersonType.FIRST and number == NumberType.SINGULAR:
        return 'أَنَا'

    # 1P
    if person == PersonType.FIRST and number == NumberType.PLURAL:
        return 'نَحْنُ'

    # 2MS
    if person == PersonType.SECOND and gender == GenderType.MASCULINE and number == NumberType.SINGULAR:
        return 'أَنتَ'

    # 2MP
    if person == PersonType.SECOND and gender == GenderType.MASCULINE and number == NumberType.PLURAL:
        return 'أَنتُم'

    # 3MS
    if person == PersonType.THIRD and gender == GenderType.MASCULINE and number == NumberType.SINGULAR:
        return 'هُوَ'

    # 3FS
    if person == PersonType.THIRD and gender == GenderType.FEMININE and number == NumberType.SINGULAR:
        return 'هِىَ'

    # 3MP
    if person == PersonType.THIRD and gender == GenderType.MASCULINE and number == NumberType.PLURAL:
        return 'هُم'

    return None
