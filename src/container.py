from .api.corpus_client import CorpusClient
from .lexicography.lemma_service import LemmaService
from .morphology.morphology_service import MorphologyService
from .syntax.syntax_service import SyntaxService


class Container:

    def __init__(self):
        client = CorpusClient()
        self.lemma_service = LemmaService()
        morphology_service = MorphologyService(client, self.lemma_service)
        self.syntax_service = SyntaxService(client, morphology_service)
