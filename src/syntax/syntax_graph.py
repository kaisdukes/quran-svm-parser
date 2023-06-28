from typing import List

from .syntax_node import SyntaxNode
from .word import Word
from .word_type import WordType
from .phrase_type import PhraseType
from .edge import Edge
from .relation import Relation
from ..orthography.token import Token
from ..morphology.part_of_speech import PartOfSpeech


class SyntaxGraph:

    def __init__(self):
        self.words: List[Word] = []
        self.segment_nodes: List[SyntaxNode] = []
        self.phrases: List[SyntaxNode] = []
        self.edges: List[Edge] = []

    def word_index(self, node: SyntaxNode):
        if not node.is_phrase:
            for i, word in enumerate(self.words):
                if word is node.word:
                    return i
        return -1

    def add_word(
            self,
            word_type: WordType,
            token: Token | None,
            elided_text: str | None,
            elided_part_of_speech: PartOfSpeech | None):

        word = Word(word_type, token, elided_text, elided_part_of_speech)
        self.words.append(word)

        index = len(self.segment_nodes)
        if word_type == WordType.ELIDED:
            node = SyntaxNode()
            node.word = word
            node.index = index
            self.segment_nodes.append(node)
        else:
            for segment in token.segments:
                if segment.part_of_speech != PartOfSpeech.DETERMINER:
                    node = SyntaxNode()
                    node.word = word
                    node.segment_number = segment.segment_number
                    node.index = index
                    self.segment_nodes.append(node)
                    index += 1

    def insert_elided_word(
            self,
            word_index: int,
            part_of_speech: PartOfSpeech,
            text: str):

        # node
        self.add_word(WordType.ELIDED, None, text, part_of_speech)
        elided_node_index = self._segment_node_index(self.words[word_index])
        segment_node_count = len(self.segment_nodes)
        elided_node = self.segment_nodes.pop()
        self.segment_nodes.insert(elided_node_index, elided_node)

        # word
        elided_word = self.words.pop()
        self.words.insert(word_index, elided_word)

        # reindex
        for i in range(segment_node_count):
            self.segment_nodes[i].index = i
        return elided_node

    def previous_segment_node(self, node: SyntaxNode):
        index = node.index
        return None if index <= 0 else self.segment_nodes[index - 1]

    def next_segment_node(self, node: SyntaxNode):
        index = node.index
        return None if index == len(self.segment_nodes) - 1 else self.segment_nodes[index + 1]

    def add_phrase(
            self,
            phrase_type: PhraseType,
            start: SyntaxNode,
            end: SyntaxNode):

        node = SyntaxNode()
        node.phrase_type = phrase_type
        node.start = start
        node.end = end
        node.index = len(self.segment_nodes) + len(self.phrases)
        self.phrases.append(node)
        return node

    def phrase(self, start: SyntaxNode, end: SyntaxNode):
        for phrase in self.phrases:
            if phrase.start is start and phrase.end is end:
                return phrase
        return None

    def is_cyclic_dependency(self, dependent: SyntaxNode, head: SyntaxNode):
        node = head
        while (node := self.head(node)) is not None:
            if node is dependent:
                return True
        return False

    def add_edge(self, dependent: SyntaxNode, head: SyntaxNode, relation: Relation):
        if self.head(dependent) is not None:
            raise RuntimeError('Duplicate head node.')
        if self.is_cyclic_dependency(dependent, head):
            raise RuntimeError('Cyclic dependency.')
        self.edges.append(Edge(dependent, head, relation))

    def edge(self, node1: SyntaxNode, node2: SyntaxNode):
        for edge in self.edges:
            if (edge.dependent is node1 and edge.head is node2) or (edge.head is node1 and edge.dependent is node2):
                return edge
        return None

    def head(self, dependent: SyntaxNode):
        for edge in self.edges:
            if edge.dependent is dependent:
                return edge.head
        return None

    def contains_edge(self, edge: Edge):
        return edge in self.edges

    def only_tokens(self):
        graph = SyntaxGraph()
        for word in self.words:
            if word.type != WordType.ELIDED:
                graph.add_word(word.type, word.token, None, None)
        return graph

    @property
    def location(self):
        for word in self.words:
            if word.type == WordType.TOKEN:
                return word.token.location
        raise ValueError

    def _segment_node_index(self, word: Word):
        for i in range(len(self.segment_nodes)):
            if self.segment_nodes[i].word is word:
                return i
        raise ValueError
