from typing import List

from src.syntax.syntax_graph import SyntaxGraph
from src.syntax.syntax_service import SyntaxService


def split_treebank(syntax_service: SyntaxService, fold: int):

    train_graphs: List[SyntaxGraph] = []
    test_graphs: List[SyntaxGraph] = []

    for i, graph in enumerate(syntax_service.graphs):
        if i % 10 == fold:
            test_graphs.append(graph)
        else:
            train_graphs.append(graph)

    return (train_graphs, test_graphs)
