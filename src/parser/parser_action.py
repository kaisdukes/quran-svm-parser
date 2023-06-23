from dataclasses import dataclass

from .action_type import ActionType
from ..morphology.part_of_speech import PartOfSpeech
from ..syntax.relation import Relation


@dataclass
class ParserAction:
    type: ActionType
    parameter: Relation | PartOfSpeech | int | None = None

    @staticmethod
    def shift():
        return ParserAction(ActionType.SHIFT)

    @staticmethod
    def right(relation: Relation):
        return ParserAction(ActionType.RIGHT, relation)

    @staticmethod
    def left(relation: Relation):
        return ParserAction(ActionType.LEFT, relation)

    @staticmethod
    def phrase():
        return ParserAction(ActionType.PHRASE)

    @staticmethod
    def reduce(stack_index: int):
        return ParserAction(ActionType.REDUCE, stack_index)

    @staticmethod
    def subgraph():
        return ParserAction(ActionType.SUBGRAPH)

    @staticmethod
    def subject():
        return ParserAction(ActionType.SUBJECT)

    @staticmethod
    def empty(part_of_speech: PartOfSpeech):
        return ParserAction(ActionType.EMPTY, part_of_speech)

    @property
    def relation(self) -> Relation:
        return self.parameter

    @property
    def part_of_speech(self) -> PartOfSpeech:
        return self.parameter

    @property
    def stack_index(self) -> int:
        return self.parameter


def encode_parser_action(action: ParserAction | None):
    if action is None:
        return 0

    relation_count = len(Relation)
    type = action.type

    if type == ActionType.SHIFT:
        return 1
    if type == ActionType.RIGHT:
        return action.relation.value[0] + 1
    if type == ActionType.LEFT:
        return relation_count + action.relation.value[0] + 1
    if type == ActionType.PHRASE:
        return 2 * relation_count + 2
    if type == ActionType.REDUCE:
        return 2 * relation_count + 3 + action.stack_index
    if type == ActionType.SUBGRAPH:
        return 2 * relation_count + 5
    if type == ActionType.SUBJECT:
        return 2 * relation_count + 6
    if type == ActionType.EMPTY:
        if action.part_of_speech == PartOfSpeech.NOUN:
            pos_value = 0
        elif action.part_of_speech == PartOfSpeech.ADJECTIVE:
            pos_value = 1
        elif action.part_of_speech == PartOfSpeech.VERB:
            pos_value = 2
        return 2 * relation_count + 7 + pos_value


def decode_parser_action(value: int):
    if value == 0:
        return None

    relation_count = len(Relation)

    if value == 1:
        return ParserAction.shift()

    n = relation_count + 1
    if value <= n:
        return ParserAction.right(Relation.relations[value - 2])

    n += relation_count
    if value <= n:
        return ParserAction.left(Relation.relations[value - (relation_count + 2)])

    n += 1
    if value == n:
        return ParserAction.phrase()

    n += 2
    if value <= n:
        return ParserAction.reduce(value - (2 * relation_count + 3))

    n += 1
    if value == n:
        return ParserAction.subgraph()

    n += 1
    if value == n:
        return ParserAction.subject()

    pos_value = value - (2 * relation_count + 7)
    if pos_value == 0:
        pos = PartOfSpeech.NOUN
    elif pos_value == 1:
        pos = PartOfSpeech.ADJECTIVE
    elif pos_value == 2:
        pos = PartOfSpeech.VERB
    return ParserAction.empty(pos)
