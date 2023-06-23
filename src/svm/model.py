from pathlib import Path
from typing import List
import joblib

from scipy.sparse import lil_matrix
from sklearn.svm import SVC

from .instance import Instance
from .ensemble import Ensemble
from ..syntax.syntax_graph import SyntaxGraph
from ..parser.stack import Stack
from ..parser.queue import Queue
from ..parser.parser_action import decode_parser_action
from ..lexicography.lemma_service import LemmaService


class SvmModel:
    def __init__(self, action: int | None = None, model: SVC | None = None):
        self.action = action
        self.model = model


class Model:
    def __init__(self, svm_models: List[SvmModel | None]):
        self._svm_models = svm_models

    def action(self, lemma_service: LemmaService, graph: SyntaxGraph, stack: Stack, queue: Queue):
        classifier_index = Ensemble.classifier_index(stack.node(0))
        svm_model = self._svm_models[classifier_index]
        if svm_model == None:
            return None

        action = svm_model.action
        if action is None:
            instance = Instance.instance(lemma_service, graph, stack, queue)
            feature_vector = instance.feature_vector

            matrix = lil_matrix((1, instance.size))
            for index in feature_vector:
                matrix[0, index] = 1

            action = int(svm_model.model.predict(matrix)[0])

        return decode_parser_action(action)


def load_model(modelPath: Path):
    modelCount = Ensemble.ENSEMBLE_COUNT
    svm_models: List[SvmModel | None] = [None]*modelCount
    for i in range(modelCount):

        txt_file = modelPath / f'{i:02d}.txt'
        if txt_file.exists():
            with open(txt_file, 'r') as file:
                action = int(file.read().strip())
                svm_models[i] = SvmModel(action=action)
                continue

        svm_file = modelPath / f'{i:02d}.svm'
        if svm_file.exists():
            model: SVC = joblib.load(svm_file)
            svm_models[i] = SvmModel(model=model)

    return Model(svm_models)
