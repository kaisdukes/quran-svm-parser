from ..syntax.syntax_node import SyntaxNode
from ..syntax.syntax_graph import SyntaxGraph


class Queue:
    def __init__(self, graph: SyntaxGraph):
        self._graph = graph
        self._node: SyntaxNode | None = graph.segment_nodes[0]

    def peek(self):
        return self._node

    def read(self):
        current_node = self._node
        if current_node is not None:
            self._node = self._graph.next_segment_node(current_node)
        return current_node
