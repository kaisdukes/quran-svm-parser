from .stack import Stack
from .queue import Queue
from .action_type import ActionType
from .parser_action import ParserAction
from ..morphology.part_of_speech import PartOfSpeech
from ..syntax.word_type import WordType
from ..syntax.syntax_node import SyntaxNode
from ..syntax.syntax_graph import SyntaxGraph
from ..syntax.subgraph import subgraph_end
from ..syntax.relation import Relation
from ..lexicography.lemma_service import LemmaService
from ..svm.model import Model


class ActionClassifier:

    def __init__(
            self,
            model: Model,
            lemma_service: LemmaService,
            graph: SyntaxGraph,
            stack: Stack,
            queue: Queue):

        self._model = model
        self.lemma_service = lemma_service
        self._graph = graph
        self._stack = stack
        self._queue = queue

    def action(self):
        action = self._model.action(self.lemma_service, self._graph, self._stack, self._queue)
        return action if self._is_valid_action(action) else ParserAction.reduce(0)

    def _is_valid_action(self, action: ParserAction):
        if action is None:
            return True

        type = action.type

        if type == ActionType.SHIFT:
            return self._queue.peek() is not None

        if type == ActionType.RIGHT:
            return (self._stack.node(1) is not None
                    and self._graph.head(self._stack.node(0)) is None
                    and not self._graph.is_cyclic_dependency(self._stack.node(0), self._stack.node(1)))

        if type == ActionType.LEFT:
            return (self._stack.node(1) is not None
                    and self._graph.head(self._stack.node(1)) is None
                    and not self._graph.is_cyclic_dependency(self._stack.node(1), self._stack.node(0)))

        if type == ActionType.PHRASE:
            return not self._stack.node(0).is_phrase and not self._stack.node(1).is_phrase

        if type == ActionType.REDUCE:
            return action.stack_index != 1 or self._stack.size >= 2

        if type == ActionType.SUBGRAPH:
            start = self._stack.node(0)
            end = subgraph_end(self._graph, start)
            return end is not None and self._graph.phrase(start, end) is None

        if type == ActionType.SUBJECT:
            return (self._stack.node(0).part_of_speech == PartOfSpeech.VERB
                    and not self._has_subject(self._stack.node(0)))

        if type == ActionType.EMPTY:
            s0 = self._stack.node(0)
            if s0.start is not None:
                s0 = s0.start
            previous = self._graph.previous_segment_node(s0)
            return previous is None or previous.word.type != WordType.ELIDED

        return False

    def _has_subject(self, head: SyntaxNode):
        for edge in self._graph.edges:
            if edge.head is head:
                relation = edge.relation
                if (relation == Relation.SUBJECT
                    or relation == Relation.PASSIVE_SUBJECT
                        or relation == Relation.SPECIAL_SUBJECT):
                    return True
        return False
