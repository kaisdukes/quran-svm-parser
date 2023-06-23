from pathlib import Path
import unittest

from elas import Elas
from split_treebank import split_treebank
from src.container import Container
from src.parser.oracle import Oracle
from src.parser.parser import Parser
from src.svm.train import train
from src.svm.model import load_model


class ParserTest(unittest.TestCase):
    MODEL_FOLDER = Path('.model')

    def setUp(self):
        self.container = Container()
        self.elas = Elas()

    def test_oracle(self):
        for expected_graph in self.container.syntax_service.graphs:

            output_graph = expected_graph.only_tokens()
            oracle = Oracle(expected_graph, output_graph)
            oracle.expected_actions()

            self.elas.compare(expected_graph, output_graph)

            # all output edges should be expected
            for output_edge in output_graph.edges:
                self.assertEqual(expected_graph.contains_edge(output_edge), True)

        self.assertEqual(self.elas.precision, 1.0)
        self.assertEqual(self.elas.recall, 0.945793687759221)

    def test_ten_fold_cross_validation(self):
        for fold in range(10):
            self._train_and_test(fold)

    def _train_and_test(self, fold: int):

        # train
        print(f'Fold {fold}')
        (train_graphs, test_graphs) = split_treebank(self.container.syntax_service, fold)
        lemma_service = self.container.lemma_service
        train(lemma_service, train_graphs, self.MODEL_FOLDER)

        # test
        print('Evaulating...')
        model = load_model(self.MODEL_FOLDER)
        for expected_graph in test_graphs:
            output_graph = expected_graph.only_tokens()
            parser = Parser(model, lemma_service, output_graph)
            try:
                parser.parse()
            except Exception as e:
                print(e)
            self.elas.compare(expected_graph, output_graph)

        print(f'Running precision: {self.elas.precision}')
        print(f'Running recall: {self.elas.recall}')
        print(f'Running F1 score: {self.elas.f1_score}')


if __name__ == '__main__':
    unittest.main()
