from typing import List
from pathlib import Path
import shutil
import joblib

from scipy.sparse import lil_matrix
from sklearn.svm import SVC
import numpy as np

from ..morphology.part_of_speech import PartOfSpeech

from .ensemble import Ensemble
from .instance import Instance
from ..lexicography.lemma_service import LemmaService
from ..syntax.syntax_graph import SyntaxGraph
from ..parser.parser import Parser
from ..parser.oracle import Oracle
from ..parser.stack import Stack
from ..parser.queue import Queue
from ..parser.parser_action import ParserAction, decode_parser_action, encode_parser_action
from ..lexicography.lemma_service import LemmaService
from ..syntax.syntax_graph import SyntaxGraph


class SvmProblem:

    def __init__(self):
        self._feature_vectors: List[List[int]] = []
        self._feature_count: int = 0
        self._labels: List[int] = []

    def add(self, instance: Instance, action: ParserAction):
        feature_vector = instance.feature_vector
        self._feature_vectors.append(feature_vector)
        self._feature_count = instance.size
        label = encode_parser_action(action)
        self._labels.append(label)

    def build_matrix(self):
        matrix = lil_matrix((len(self._feature_vectors), self._feature_count))

        for i, feature_vector in enumerate(self._feature_vectors):
            for j in feature_vector:
                matrix[i, j] = 1

        return (matrix, self._labels)


def train(lemma_service: LemmaService, graphs: List[SyntaxGraph], model_folder: Path):

    # recreate model folder
    if model_folder.exists():
        shutil.rmtree(model_folder)
    model_folder.mkdir()

    print('Preparing training data...')
    problems = _build_svm_problems(lemma_service, graphs)

    # train models
    for i, problem in enumerate(problems):
        if problem is None:
            continue

        matrix, labels = problem.build_matrix()
        filename = f'{i:02d}'

        if np.unique(labels).size == 1:
            with open(model_folder / f'{filename}.txt', 'w') as f:
                f.write(str(labels[0]))
        else:
            print(f'Training model {i}')
            model = SVC(C=0.5, kernel='poly', degree=2, gamma=0.2, coef0=0)
            model.fit(matrix, labels)
            joblib.dump(model, model_folder / f'{filename}.svm')


def _build_svm_problems(lemma_service: LemmaService, graphs: List[SyntaxGraph]):
    problems: List[SvmProblem | None] = [None]*Ensemble.ENSEMBLE_COUNT

    # parse each graph
    for expected_graph in graphs:

        # apply expected actions
        actions = Oracle(expected_graph, expected_graph.only_tokens()).expected_actions()
        output_graph = expected_graph.only_tokens()
        parser = Parser(None, None, output_graph)
        stack = parser.stack
        queue = parser.queue
        for action in actions:
            _add_instance(problems, lemma_service, output_graph, stack, queue, action)
            parser.execute(action)

        # stop parsing
        _add_instance(problems, lemma_service, output_graph, stack, queue, None)

    return problems


def _add_instance(problems: List[SvmProblem],
                  lemma_service: LemmaService,
                  graph: SyntaxGraph,
                  stack: Stack,
                  queue: Queue,
                  action: ParserAction | None):

    classifier_index = Ensemble.classifier_index(stack.node(0))

    if problems[classifier_index] is None:
        problems[classifier_index] = SvmProblem()

    instance = Instance.instance(lemma_service, graph, stack, queue)
    problems[classifier_index].add(instance, action)
