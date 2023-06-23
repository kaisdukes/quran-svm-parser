from src.syntax.syntax_graph import SyntaxGraph


class Elas:

    def __init__(self):
        self._expected_edges: int = 0
        self._output_edges: int = 0
        self._equivalent_edges: int = 0

    def compare(self, expected_graph: SyntaxGraph, output_graph: SyntaxGraph):
        self._expected_edges += len(expected_graph.edges)

        for output_edge in output_graph.edges:
            self._output_edges += 1

            if expected_graph.contains_edge(output_edge):
                self._equivalent_edges += 1

    @property
    def precision(self):
        return self._equivalent_edges / self._output_edges

    @property
    def recall(self):
        return self._equivalent_edges / self._expected_edges

    @property
    def f1_score(self):
        precision = self.precision
        recall = self.recall
        return 2 * (precision * recall) / (precision + recall)
