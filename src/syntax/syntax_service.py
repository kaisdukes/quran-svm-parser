from pathlib import Path
from typing import List

from .syntax_node import SyntaxNode
from .syntax_graph import SyntaxGraph
from .phrase_type import PhraseType
from .relation import Relation
from .graph_reader import GraphReader
from .graph_writer import GraphWriter
from ..orthography.token import Token
from ..orthography.location import Location
from ..morphology.morphology_service import MorphologyService
from ..morphology.part_of_speech import PartOfSpeech
from ..api.corpus_client import CorpusClient
from ..api.responses import GraphLocation, GraphResponse, TokenResponse


class SyntaxService:
    SYNTAX_FILE = Path('.data/syntax.txt')

    def __init__(self, client: CorpusClient, morphology_service: MorphologyService):
        self.graphs: List[SyntaxGraph] = []
        self._download_syntax(client, morphology_service)
        self._read_syntax(morphology_service)

    def _download_syntax(self, client: CorpusClient, morphology_service: MorphologyService):

        if self.SYNTAX_FILE.exists():
            return

        print('Downloading syntax...')
        graphs: List[SyntaxGraph] = []
        location = GraphLocation(location=[1, 1], graphNumber=1)
        n = 0
        while True:
            graph = client.syntax(location)
            n += 1
            print(f'Downloaded graph {n}')
            graphs.append(SyntaxService._build_graph(morphology_service, graph))
            if (location := graph.next) is None:
                break

        with GraphWriter(open(self.SYNTAX_FILE, 'w')) as writer:
            writer.write_graphs(graphs)

    @staticmethod
    def _build_graph(morphology_service: MorphologyService, graph_response: GraphResponse) -> SyntaxGraph:
        graph = SyntaxGraph()

        for word in graph_response.words:
            elided_pos_tag = word.elided_pos_tag
            graph.add_word(
                word.type,
                SyntaxService._token(morphology_service, word.token),
                word.elided_text,
                PartOfSpeech.parse(elided_pos_tag) if elided_pos_tag else None)

        phrase_nodes = graph_response.phrase_nodes
        if phrase_nodes:
            for phrase_node in phrase_nodes:
                graph.add_phrase(
                    PhraseType.parse(phrase_node.phrase_tag),
                    SyntaxService._node(graph, phrase_node.start_node),
                    SyntaxService._node(graph, phrase_node.end_node))

        edges = graph_response.edges
        if edges:
            for edge in edges:
                graph.add_edge(
                    SyntaxService._node(graph, edge.start_node),
                    SyntaxService._node(graph, edge.end_node),
                    Relation.parse(edge.dependency_tag))

        return graph

    @staticmethod
    def _node(graph: SyntaxGraph, index: int) -> SyntaxNode:
        segment_nodes = graph.segment_nodes
        segment_node_count = len(segment_nodes)
        if index < segment_node_count:
            return segment_nodes[index]
        return graph.phrases[index - segment_node_count]

    @staticmethod
    def _token(morphology_service: MorphologyService, token_response: TokenResponse | None) -> Token | None:
        if token_response is None:
            return None
        location = token_response.location
        return morphology_service.token(Location(location[0], location[1], location[2]))

    def _read_syntax(self, morphologyService: MorphologyService):
        with open(self.SYNTAX_FILE, 'r') as file:
            reader = GraphReader(morphologyService, file)
            while (graph := reader.read_graph()) != None:
                self.graphs.append(graph)
