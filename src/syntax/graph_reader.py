from typing import TextIO

from ..orthography.location import parse_location
from ..morphology.part_of_speech import PartOfSpeech
from ..morphology.morphology_service import MorphologyService
from ..syntax.syntax_graph import SyntaxGraph
from ..syntax.word_type import WordType
from ..syntax.phrase_type import PhraseType
from ..syntax.relation import Relation


class GraphReader:

    def __init__(self, morphology_service: MorphologyService, reader: TextIO):
        self._morphology_service = morphology_service
        self._reader = reader
        self._graph: SyntaxGraph | None = None
        self._node_sequence_number: int = 0

    def read_graph(self):
        self._graph = SyntaxGraph()
        self._node_sequence_number = 0
        line: str | None

        for line in self._reader:
            line = line.strip()
            if len(line) == 0 or line.startswith('--'):
                continue

            if line == 'go':
                return self._graph

            if '=' in line:
                self._read_node(line)
            else:
                self._read_edge(line)

        return None

    def _read_node(self, line: str):
        parts = line.split(' = ')
        names = parts[0].split(',')
        for name in names:
            node_number = self._parse_node_name(name.strip())
            expected_node_number = self._node_sequence_number + 1
            if node_number != expected_node_number:
                raise ValueError(f'Expected node {expected_node_number} not {node_number}.')

            self._node_sequence_number += 1

        definition = parts[1]
        index = definition.index('(')
        if index == -1:
            raise ValueError("Expected '('.")

        tag = definition[:index]
        value = definition[index + 1: -1]

        phrase_type = PhraseType.parse(tag)
        if tag == 'word':
            self._read_word(WordType.TOKEN, value)
        elif tag == 'reference':
            self._read_word(WordType.REFERENCE, value)
        elif phrase_type is not None:
            self._read_phrase(phrase_type, value)
        else:
            self._read_elided_word(tag, value)

    def _read_word(self, w_type: WordType, value: str):
        self._graph.add_word(
            w_type,
            self._morphology_service.token(parse_location(value)),
            None,
            None)

    def _read_elided_word(self, tag: str, value: str):
        self._graph.add_word(
            WordType.ELIDED,
            None,
            None if value == '*' else value,
            PartOfSpeech.parse(tag))

    def _read_phrase(self, phrase_type: PhraseType, value: str):
        interval = self._read_interval(value)
        self._graph.add_phrase(phrase_type, interval[0], interval[1])

    def _read_edge(self, line: str):
        index = line.index('(')
        if index == -1:
            raise ValueError("Expected '('.")

        name = line[:index]
        relation = Relation.parse(name)
        interval = self._read_interval(line[index + 1: -1])
        self._graph.add_edge(interval[0], interval[1], relation)

    def _read_interval(self, value: str):
        index = value.index('-')
        if index == -1:
            raise ValueError('Expected '-' for node interval.')

        return (self._get_node(value[:index - 1]), self._get_node(value[index + 2:]))

    def _get_node(self, name: str):
        node_index = self._parse_node_name(name) - 1
        segment_nodes = self._graph.segment_nodes
        segment_node_count = len(segment_nodes)

        return (segment_nodes[node_index] if node_index < segment_node_count
                else self._graph.phrases[node_index - segment_node_count])

    @staticmethod
    def _parse_node_name(name: str):
        if name[0] != 'n':
            raise ValueError(f'Node name {name} should start with n.')

        return int(name[1:])
