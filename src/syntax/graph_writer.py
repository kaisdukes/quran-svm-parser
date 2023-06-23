from typing import List, TextIO
from src.syntax.edge import Edge

from src.syntax.word import Word
from src.syntax.word_type import WordType

from .syntax_node import SyntaxNode
from .syntax_graph import SyntaxGraph
from ..morphology.part_of_speech import PartOfSpeech


class GraphWriter:

    def __init__(self, writer: TextIO):
        self._writer = writer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._writer.close()

    def write_graphs(self, graphs: List[SyntaxGraph]):
        graph_count = len(graphs)
        for i in range(graph_count):
            graph = graphs[i]
            if i > 0:
                self._writer.write('\n')
            self._write_graph(graph)

    def _write_graph(self, graph: SyntaxGraph):

        # words
        words = graph.words
        if words:
            self._writer.write('-- words\n')
            index = 0
            for word in words:
                index += self._write_word(index, word)
                self._writer.write('\n')

        # phrases
        phrases = graph.phrases
        if phrases:
            self._writer.write('\n-- phrases\n')
            for phrase in phrases:
                self._write_phrase(phrase)
                self._writer.write('\n')

        # edges
        edge_count = len(graph.edges)
        if edge_count > 0:
            self._writer.write('\n-- edges\n')
            for edge in graph.edges:
                self._write_edge(edge)
                self._writer.write('\n')

        # batch
        self._writer.write('\ngo\n')

    def _write_word(self, index: int, word: Word):
        if word.type == WordType.ELIDED:
            return self._write_elided_word(index, word)
        return self._write_token(index, word)

    def _write_token(self, index: int, word: Word):

        # nodes
        start = index
        for segment in word.token.segments:
            if segment.part_of_speech != PartOfSpeech.DETERMINER:
                if index > start:
                    self._writer.write(', ')
                self._write(index)
                index += 1

        # token
        self._writer.write(' = ')
        self._writer.write('reference' if word.type == WordType.REFERENCE else 'word')
        self._writer.write('(')
        self._writer.write(str(word.token.location))
        self._writer.write(')')
        return index - start

    def _write_elided_word(self, index: int, word: Word):
        self._write(index)
        self._writer.write(' = ')
        self._writer.write(word.elided_part_of_speech.tag)
        self._writer.write('(')
        elided_text = word.elided_text
        self._writer.write('*' if elided_text is None else elided_text)
        self._writer.write(')')
        return 1

    def _write_phrase(self, node: SyntaxNode):
        self._write(node.index)
        self._writer.write(' = ')
        self._writer.write(node.phrase_type.tag)
        self._writer.write('(')
        self._write(node.start.index)
        self._writer.write(' - ')
        self._write(node.end.index)
        self._writer.write(')')

    def _write_edge(self, edge: Edge):
        self._writer.write(edge.relation.tag)
        self._writer.write('(')
        self._write(edge.dependent.index)
        self._writer.write(' - ')
        self._write(edge.head.index)
        self._writer.write(')')

    def _write(self, index: int):
        self._writer.write(f'n{index + 1}')
