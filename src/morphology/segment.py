from .segment_type import SegmentType
from .part_of_speech import PartOfSpeech
from .person_type import PersonType
from .gender_type import GenderType
from .number_type import NumberType
from .mood_type import MoodType
from .voice_type import VoiceType
from .case_type import CaseType
from .state_type import StateType
from .pronoun_type import PronounType
from .special_type import SpecialType


class Segment:

    def __init__(self, type: SegmentType, part_of_speech: PartOfSpeech):
        self.type = type
        self.part_of_speech = part_of_speech
        self.segment_number: int | None = None
        self.lemma: str | None = None
        self.person: PersonType | None = None
        self.gender: GenderType | None = None
        self.number: NumberType | None = None
        self.mood: MoodType | None = None
        self.voice: VoiceType | None = None
        self.case: CaseType | None = None
        self.state: StateType | None = None
        self.pronoun_type: PronounType | None = None
        self.special: SpecialType | None = None
