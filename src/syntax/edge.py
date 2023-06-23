from dataclasses import dataclass

from .syntax_node import SyntaxNode
from .relation import Relation


@dataclass
class Edge:
    dependent: SyntaxNode
    head: SyntaxNode
    relation: Relation
