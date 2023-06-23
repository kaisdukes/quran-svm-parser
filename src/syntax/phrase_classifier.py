from typing import List


from .syntax_graph import SyntaxGraph
from .syntax_node import SyntaxNode
from .edge import Edge
from .relation import Relation
from .word_type import WordType
from .phrase_type import PhraseType
from ..morphology.part_of_speech import PartOfSpeech


class PhraseClassifier:

    def __init__(self):
        pass

    @staticmethod
    def phrase_type(graph: SyntaxGraph, start: SyntaxNode, end: SyntaxNode):

        if start.is_phrase or end.is_phrase:
            raise ValueError('Expected a pair of segments, not phrases.')

        # A verbal sentence contains a verb which is not a special copula (كان واخواتها).
        # For verbal sentences, we look for either a subject or passive subject relation,
        # or otherwise for the presence of an elided verb.

        # subordinate clauses start with POS:SUB or l:PRP+.
        if (start.part_of_speech == PartOfSpeech.SUBORDINATING_CONJUNCTION
                or start.part_of_speech == PartOfSpeech.PURPOSE):
            return PhraseType.SUBORDINATE_CLAUSE

        genitive = False
        verbal_subject = False
        condition = False
        predicate = False

        # look for edges that are directly covered by the phrase
        for edge in graph.edges:
            if PhraseClassifier._is_minimum_covering_phrase_for_edge(graph, start, end, edge):
                relation = edge.relation
                if relation == Relation.GENITIVE:
                    genitive = True
                elif relation == Relation.SUBJECT or relation == Relation.PASSIVE_SUBJECT:
                    if edge.head.part_of_speech == PartOfSpeech.VERB:
                        verbal_subject = True
                elif relation == Relation.CONDITION:
                    condition = True
                elif (relation == Relation.PREDICATE
                      or relation == Relation.SPECIAL_PREDICATE
                      or relation == Relation.SPECIAL_SUBJECT):
                    predicate = True

        if genitive:
            return PhraseType.PREPOSITION_PHRASE

        if verbal_subject:
            return PhraseType.VERBAL_SENTENCE

        if condition:
            return PhraseType.CONDITIONAL_SENTENCE

        if predicate:
            return PhraseType.NOMINAL_SENTENCE

        # consider elided words covered by the phrase
        start_index = start.index
        end_index = end.index
        for i in range(start_index, end_index + 1):
            segment_node = graph.segment_nodes[i]
            if segment_node.word.type == WordType.ELIDED:
                part_of_speech = segment_node.part_of_speech
                if part_of_speech == PartOfSpeech.VERB or part_of_speech == PartOfSpeech.NOUN:

                    # check that the word isn't covered by a different sub-phrase
                    phrase = PhraseClassifier._minimum_covering_phrase(graph, segment_node)
                    if phrase is None or (phrase.end.index - phrase.start.index >= end_index - start_index):
                        return PhraseType.VERBAL_SENTENCE if part_of_speech == PartOfSpeech.VERB else PhraseType.NOMINAL_SENTENCE

        return PhraseType.SENTENCE

    def _minimum_covering_phrase(graph: SyntaxGraph, segment_node: SyntaxNode):
        index = segment_node.index
        minimum_covering_phrase: SyntaxNode | None = None
        minimum_covering_start = 0
        minimum_covering_end = 0

        for phrase in graph.phrases:

            # covering
            start = phrase.start.index
            end = phrase.end.index
            if index >= start and index <= end:

                # minimum?
                if minimum_covering_phrase is None or end - start < minimum_covering_end - minimum_covering_start:
                    minimum_covering_phrase = phrase
                    minimum_covering_start = start
                    minimum_covering_end = end

        return minimum_covering_phrase

    def _is_minimum_covering_phrase_for_edge(graph: SyntaxGraph, start: SyntaxNode, end: SyntaxNode, edge: Edge):
        return (PhraseClassifier._is_minimum_covering_phrase_for_node(graph, start, end, edge.head)
                and PhraseClassifier._is_minimum_covering_phrase_for_node(graph, start, end, edge.dependent))

    def _is_minimum_covering_phrase_for_node(graph: SyntaxGraph, start: SyntaxNode, end: SyntaxNode, node: SyntaxNode):
        start_index = start.index
        end_index = end.index

        # if the node is itself a phrase, check that it is a sub-phrase
        if node.is_phrase:
            return node.start.index >= start_index and node.end.index <= end_index

        if node.index < start_index or node.index > end_index:
            return False

        # minimum covering phrase?
        phrase = PhraseClassifier._minimum_covering_phrase(graph, node)
        return phrase is None or end_index - start_index <= phrase.end.index - phrase.start.index
