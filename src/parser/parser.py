from .stack import Stack
from .queue import Queue
from .parser_action import ParserAction
from .action_type import ActionType
from .action_classifier import ActionClassifier
from ..morphology.part_of_speech import PartOfSpeech
from ..morphology.voice_type import VoiceType
from ..morphology.pronoun import get_pronoun
from ..syntax.syntax_node import SyntaxNode
from ..syntax.syntax_graph import SyntaxGraph
from ..syntax.relation import Relation
from ..syntax.word_type import WordType
from ..syntax.phrase_classifier import PhraseClassifier
from ..syntax.subgraph import subgraph_end
from ..lexicography.lemma_service import LemmaService
from ..svm.model import Model


class Parser:

    def __init__(self, model: Model, lemma_service: LemmaService, graph: SyntaxGraph):
        self.stack = Stack()
        self.queue = Queue(graph)
        self._graph = graph
        self._action_classifier = ActionClassifier(model, lemma_service, graph, self.stack, self.queue)

    def parse(self):
        n = 0
        action: ParserAction | None = None
        while (action := self._action_classifier.action()) is not None:
            self.execute(action)
            n += 1
            if n > 250:
                raise RuntimeError('Failed to parse graph after 250 steps.')
        self._post_process()

    def execute(self, action: ParserAction):
        if action.type == ActionType.SHIFT:
            self._shift()
        elif action.type == ActionType.RIGHT:
            self._right(action.relation)
        elif action.type == ActionType.LEFT:
            self._left(action.relation)
        elif action.type == ActionType.PHRASE:
            self._phrase()
        elif action.type == ActionType.REDUCE:
            self._reduce(action.stack_index)
        elif action.type == ActionType.SUBGRAPH:
            self._subgraph()
        elif action.type == ActionType.SUBJECT:
            self._subject()
        elif action.type == ActionType.EMPTY:
            self._empty(action.part_of_speech)

    def _shift(self):
        node = self.queue.read()
        if not node:
            raise ValueError('Empty queue.')
        self.stack.add(node)

    def _right(self, relation: Relation):
        self._graph.add_edge(self._stack(0), self._stack(1), relation)

    def _left(self, relation: Relation):
        self._graph.add_edge(self._stack(1), self._stack(0), relation)

    def _phrase(self):
        start = self._stack(1)
        end = self._stack(0)

        if start.is_phrase:
            raise ValueError('Invalid phrase start.')
        if end.is_phrase:
            raise ValueError('Invalid phrase end.')

        phrase_type = PhraseClassifier.phrase_type(self._graph, start, end)
        self.stack.add(self._graph.add_phrase(phrase_type, start, end))

    def _subgraph(self):
        start = self._stack(0)
        end = subgraph_end(self._graph, start)
        if not end:
            raise ValueError('Failed to find subgraph.')

        phrase_type = PhraseClassifier.phrase_type(self._graph, start, end)
        self.stack.add(self._graph.add_phrase(phrase_type, start, end))

    def _reduce(self, stack_index: int):
        if stack_index < 0 or stack_index > 1:
            raise ValueError(f'Invalid reduce: {stack_index}')
        self.stack.reduce(stack_index)

    def _subject(self):
        verb = self._stack(0)
        self.stack.add(self._add_elided_pronoun(verb))
        self._right(self._subject_relation(verb))

    def _empty(self, part_of_speech: PartOfSpeech):

        start = self._stack(0)
        if start.start is not None:
            start = start.start
        word_index = self._graph.word_index(start)
        node = self._graph.insert_elided_word(word_index, part_of_speech, None)

        self.stack.insert(0, node)

    def _stack(self, stack_index: int) -> SyntaxNode:
        return self.stack.node(stack_index)

    def _add_elided_pronoun(self, verb: SyntaxNode) -> SyntaxNode:
        segment = verb.segment
        pronoun = None if not segment else get_pronoun(segment.person, segment.gender, segment.number)
        word_index = self._graph.word_index(verb) + 1
        return self._graph.insert_elided_word(word_index, PartOfSpeech.PRONOUN, pronoun)

    def _subject_relation(self, verb: SyntaxNode) -> Relation:
        segment = verb.segment
        if segment and segment.special:
            return Relation.SPECIAL_SUBJECT
        return Relation.PASSIVE_SUBJECT if segment and segment.voice == VoiceType.PASSIVE else Relation.SUBJECT

    def _post_process(self):
        for i in range(len(self._graph.segment_nodes) - 1, -1, -1):
            verb = self._graph.segment_nodes[i]
            if verb.part_of_speech == PartOfSpeech.VERB and not self._has_subject(verb) and verb.word.type == WordType.TOKEN:
                self._graph.add_edge(self._add_elided_pronoun(verb), verb, self._subject_relation(verb))

    def _has_subject(self, head: SyntaxNode) -> bool:
        for edge in self._graph.edges:
            if edge.head is head:
                relation = edge.relation
                if relation == Relation.SUBJECT or relation == Relation.PASSIVE_SUBJECT or relation == Relation.SPECIAL_SUBJECT:
                    return True
        return False
