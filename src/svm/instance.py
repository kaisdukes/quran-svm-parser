from typing import List
from enum import Enum

from ..morphology.segment_type import SegmentType
from ..morphology.part_of_speech import PartOfSpeech
from ..morphology.mood_type import MoodType
from ..morphology.voice_type import VoiceType
from ..morphology.case_type import CaseType
from ..morphology.state_type import StateType
from ..morphology.pronoun_type import PronounType
from ..morphology.special_type import SpecialType
from ..syntax.syntax_node import SyntaxNode
from ..syntax.syntax_graph import SyntaxGraph
from ..syntax.relation import Relation
from ..syntax.phrase_type import PhraseType
from ..syntax.subgraph import subgraph_end
from ..lexicography.lemma_service import LemmaService
from ..parser.stack import Stack
from ..parser.queue import Queue


class Instance:

    def __init__(self):
        self.feature_vector: List[int] = []
        self.size: int = 0

    @staticmethod
    def instance(
            lemma_service: LemmaService,
            graph: SyntaxGraph,
            stack: Stack,
            queue: Queue):

        instance = Instance()
        for x in [stack.node(0), stack.node(1), stack.node(2), queue.peek()]:

            instance.add_tagged_enum(x.part_of_speech if x else None, PartOfSpeech)
            instance.add_tagged_enum(x.phrase_type if x else None, PhraseType)

            s = x.segment if x else None
            instance.add_enum(s.voice if s else None, VoiceType)
            instance.add_tagged_enum(s.mood if s else None, MoodType)
            instance.add_enum(s.case if s else None, CaseType)
            instance.add_enum(s.state if s else None, StateType)
            instance.add_enum(s.pronoun_type if s else None, PronounType)
            instance.add_enum(s.type if s else None, SegmentType)
            instance.add_tagged_enum(s.special if s else None, SpecialType)

            lemma = s.lemma if s is not None else None
            instance.add_value(lemma_service.value_of(lemma) if lemma is not None else -1, lemma_service.count)

            for relation in Relation:
                instance.add_bit(Instance._has_dependent(graph, x, relation))

            instance.add_bit(Instance._is_valid_subgraph(graph, x))
            instance.add_bit(Instance._is_edge(graph, stack))

        return instance

    def add_bit(self, bit: bool):
        if bit:
            self.feature_vector.append(self.size)
        self.size += 1

    def add_enum(self, value: Enum | None, enum_type: type[Enum]):
        if value is not None:
            self.feature_vector.append(self.size + value.value)
        self.size += len(enum_type)

    def add_tagged_enum(self, value: Enum | None, enum_type: type[Enum]):
        if value is not None:
            self.feature_vector.append(self.size + value.value[0])
        self.size += len(enum_type)

    def add_value(self, value: int, size: int):
        if value >= 0:
            self.feature_vector.append(self.size + value)
        self.size += size

    @staticmethod
    def _has_dependent(graph: SyntaxGraph, head: SyntaxNode, relation: Relation):
        for edge in graph.edges:
            if edge.head is head and edge.relation is relation:
                return True
        return False

    @staticmethod
    def _is_valid_subgraph(graph: SyntaxGraph, node: SyntaxNode):
        if node is not None and not node.is_phrase and graph.head(node) is None:
            end = subgraph_end(graph, node)
            return end is not None and graph.head(end) is not None and graph.phrase(node, end) is None
        return False

    @staticmethod
    def _is_edge(graph: SyntaxGraph, stack: Stack):
        return (stack.node(0) is not None
                and stack.node(1) is not None
                and graph.edge(stack.node(0), stack.node(1)) is not None)
