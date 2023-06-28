from typing import List

from ..syntax.syntax_node import SyntaxNode


class Stack:
    def __init__(self):
        self._nodes: List[SyntaxNode] = []

    def add(self, node: SyntaxNode):
        self._nodes.append(node)

    def insert(self, stack_index: int, node: SyntaxNode):
        self._nodes.insert(len(self._nodes) - stack_index - 1, node)

    def reduce(self, stack_index: int):
        size = len(self._nodes)
        index = size - stack_index - 1
        if 0 <= index < size:
            self._nodes.pop(index)
        else:
            raise ValueError(f"Can't reduce: {stack_index}")

    def node(self, stack_index: int):
        size = len(self._nodes)
        index = size - stack_index - 1
        return self._nodes[index] if 0 <= index < size else None

    @property
    def size(self):
        return len(self._nodes)

    def __str__(self):
        return '[' + ' '.join(str(node) for node in self._nodes[::-1]) + ']'
