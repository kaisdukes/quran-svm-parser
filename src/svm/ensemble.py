from ..morphology.part_of_speech import PartOfSpeech
from ..syntax.syntax_node import SyntaxNode
from ..syntax.phrase_type import PhraseType


class Ensemble:
    ENSEMBLE_COUNT = len(PartOfSpeech) + len(PhraseType) + 1

    @staticmethod
    def classifier_index(node: SyntaxNode):
        if node is None:
            return 0

        part_of_speech = node.part_of_speech
        if part_of_speech is not None:
            return part_of_speech.value[0]

        phrase_type = node.phrase_type
        if phrase_type is not None:
            return len(PartOfSpeech) + phrase_type.value[0]

        return 0
