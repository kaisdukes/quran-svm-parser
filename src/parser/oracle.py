from typing import Dict, List

from .parser import Parser
from .parser_action import ParserAction
from ..morphology.part_of_speech import PartOfSpeech
from ..syntax.syntax_node import SyntaxNode
from ..syntax.syntax_graph import SyntaxGraph
from ..syntax.relation import Relation
from ..syntax.word_type import WordType
from ..syntax.subgraph import subgraph_end


class Oracle:

    def __init__(self, expected_graph: SyntaxGraph, output_graph: SyntaxGraph):
        self._expected_graph = expected_graph
        self._output_graph = output_graph
        self._parser = Parser(None, None, output_graph)
        self._expected_node_map: Dict[int, SyntaxNode] = {}
        self._trace_enabled = False
        self._build_node_map()

    def expected_actions(self) -> List[ParserAction]:
        actions: List[ParserAction] = []
        while (action := self._next()) != None:
            self._parser.execute(action)
            actions.append(action)
        return actions

    def _next(self):

        # s0 and s1 form an edge?
        s0 = self._stack(0)
        s1 = self._stack(1)
        if s0 is not None and s1 is not None:
            edge = self._expected_edge(s0, s1)
            if edge is not None and self._output_graph.edge(s0, s1) is None:
                if edge.dependent is self._expected_node(s0) and self._output_graph.head(s0) is None:
                    self._trace('RIGHT (s0 and s1 form a edge)')
                    return ParserAction.right(edge.relation)
                if not self._output_graph.head(s1):
                    self._trace('LEFT (s0 and s1 form a edge)')
                    return ParserAction.left(edge.relation)

        # reduce phrase internals: s1 has all edges accounted for?
        if self._covers(s0, s1) and self._has_all_edges(s1):
            self._trace('REDUCE(1) (phrase internals: s1 has all edges accounted for)')
            return ParserAction.reduce(1)

        # Build a phrase now if the two top nodes on the stack are adjacent. However delay
        # building the phrase if we're expecting dependents but don't have any yet.
        if (self._expected_phrase(s1, s0) is not None and self._output_graph.phrase(s1, s0) is None
                and s0.index == s1.index + 1
                and (not self._has_any_expected_dependents(s0) or self._has_any_dependents(s0))):
            self._trace('PHRASE (top nodes on the stack are adjacent)')
            return ParserAction.phrase()

        if self._add_subgraph():
            if self._add_elided_subject():
                self._trace('SUBJECT (elided subject at root of subraph)')
                return ParserAction.subject()
            self._trace('SUBGRAPH (root of subgraph detected)')
            return ParserAction.subgraph()

        q0 = self._parser.queue.peek()
        if q0 is None and self._add_elided_subject():
            self._trace('SUBJECT (elided subject)')
            return ParserAction.subject()

        if s0 is not None and self._has_all_edges(s0):
            self._trace('REDUCE(0) (s0 has all edges)')
            return ParserAction.reduce(0)

        if q0 is not None:
            self._trace('SHIFT (queue not empty)')
            return ParserAction.shift()

        s2 = self._stack(2)
        if s2 is not None and self._expected_edge(s0, s2) is not None:
            self._trace('REDUCE(1) (expected edge s0 s2)')
            return ParserAction.reduce(1)

        empty = self._add_empty()
        if empty is not None:
            self._trace('EMPTY (empty category detected')
            return ParserAction.empty(empty)

        if s0 is not None:
            self._trace('REDUCE(0) (stack not empty)')
            return ParserAction.reduce(0)

        self._trace('STOP (no other actions apply)')
        return None

    def _add_empty(self):
        if self._stack(1) is None:
            return None

        n1 = self._expected_node(self._stack(0))
        n2 = self._expected_node(self._stack(1))

        # n1 -> h1 -> n2
        h1 = self._expected_graph.head(n1)
        if (h1 is not None and h1.word is not None
                and h1.word.type == WordType.ELIDED
                and self._expected_graph.head(h1) is n2
                and h1.word.elided_part_of_speech != PartOfSpeech.PRONOUN):
            return h1.word.elided_part_of_speech

        # n1 <- h2 <- n2
        h2 = self._expected_graph.head(n2)
        if (h2 is not None and h2.word is not None
                and h2.word.type == WordType.ELIDED
                and self._expected_graph.head(h2) is n1
                and h2.word.elided_part_of_speech != PartOfSpeech.PRONOUN):
            return h2.word.elided_part_of_speech

        return None

    def _covers(self, phrase_node: SyntaxNode, child_node: SyntaxNode):
        if phrase_node is None or child_node is None:
            return False

        if not phrase_node.is_phrase:
            return False

        if child_node.is_phrase:
            return False

        start = phrase_node.start
        end = phrase_node.end
        return child_node.index >= start.index and child_node.index <= end.index

    def _add_subgraph(self):
        start = self._stack(0)

        if start is None:
            return False

        end = subgraph_end(self._output_graph, start)
        if end is None:
            return False

        if self._output_graph.phrase(start, end) is not None:
            return False

        return self._expected_graph.phrase(self._expected_node(start), self._expected_node(end)) is not None

    def _has_all_edges(self, output_node: SyntaxNode):
        expected_edges = 0
        expected_node = self._expected_node(output_node)
        for edge in self._expected_graph.edges:
            if edge.dependent is expected_node or edge.head is expected_node:
                expected_edges += 1

        output_edges = 0
        for edge in self._output_graph.edges:
            if edge.dependent is output_node or edge.head is output_node:
                output_edges += 1

        return expected_edges == output_edges

    def _add_elided_subject(self):
        output_node = self._stack(0)
        if output_node is None:
            return False

        expected_node = self._expected_node(output_node)
        if expected_node is None:
            return False

        return (self._has_elided_subject(self._expected_graph, expected_node)
                and not self._has_elided_subject(self._output_graph, output_node))

    def _has_elided_subject(self, graph: SyntaxGraph, node: SyntaxNode):
        for edge in graph.edges:
            if edge.head is not node:
                continue

            if edge.relation == Relation.SUBJECT or edge.relation == Relation.PASSIVE_SUBJECT:
                word = edge.dependent.word
                if (word is not None and word.type == WordType.ELIDED
                        and word.elided_part_of_speech == PartOfSpeech.PRONOUN):
                    return True

        return False

    def _has_any_dependents(self, node: SyntaxNode):
        for edge in self._output_graph.edges:
            if edge.head is node:
                return True
        return False

    def _has_any_expected_dependents(self, node: SyntaxNode):
        expected_node = self._expected_node(node)
        for edge in self._expected_graph.edges:
            if edge.head is expected_node:
                return True
        return False

    def _expected_phrase(self, start: SyntaxNode, end: SyntaxNode):
        if start is None or end is None:
            return None
        return self._expected_graph.phrase(self._expected_node(start), self._expected_node(end))

    def _expected_edge(self, node1: SyntaxNode, node2: SyntaxNode):
        expected_node1 = self._expected_node(node1)
        expected_node2 = self._expected_node(node2)
        if expected_node1 is None or expected_node2 is None:
            return None
        return self._expected_graph.edge(expected_node1, expected_node2)

    def _expected_node(self, output_node: SyntaxNode):

        # mapped?
        expected_node = self._expected_node_map.get(id(output_node))
        if expected_node is not None:
            return expected_node

        # phrase
        if output_node.is_phrase:
            for node in self._expected_graph.phrases:
                if node == output_node:
                    self._expected_node_map[id(output_node)] = node
                    return node

        # segment
        match: SyntaxNode | None = None
        for node in self._expected_graph.segment_nodes:
            if node == output_node:
                if match is None:
                    match = node
                    continue
                d1 = abs(output_node.index - node.index)
                d2 = abs(output_node.index - match.index)
                if d1 < d2:
                    match = node

        if match is not None:
            self._expected_node_map[id(output_node)] = match
            return match
        return None

    def _stack(self, stack_index: int):
        return self._parser.stack.node(stack_index)

    def _build_node_map(self):
        index = 0
        for expected_node in self._expected_graph.segment_nodes:
            if expected_node.word.type != WordType.ELIDED:
                output_node = self._output_graph.segment_nodes[index]
                index += 1
                self._expected_node_map[id(output_node)] = expected_node

    def _trace(self, action: str):
        if self._trace_enabled:
            print(f'{action} @ {self._parser.stack}')
