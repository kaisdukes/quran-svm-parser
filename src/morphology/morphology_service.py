from pathlib import Path
from typing import List

from .segment import Segment
from .tsv_reader import TsvReader
from ..orthography.chapter import Chapter
from ..orthography.token import Token
from ..orthography.location import Location
from ..orthography.verse import Verse
from ..lexicography.lemma_service import LemmaService
from ..api.corpus_client import CorpusClient
from ..api.responses import SegmentResponse


class MorphologyService:
    MORPHOLOGY_FILE = Path('.data/morphology.tsv')

    def __init__(self, client: CorpusClient, lemma_service: LemmaService):
        self._chapters = [Chapter([]) for _ in range(114)]
        self._download_morphology(client)
        self._read_morphology(lemma_service)

    def token(self, location: Location):
        chapter = self._chapters[location.chapter_number - 1]
        verse = chapter.verses[location.verse_number - 1]
        token = verse.tokens[location.token_number - 1]
        return token

    def _read_morphology(self, lemma_service: LemmaService):

        # morphology
        tokens: List[Token]
        segments: List[List[Segment]]
        with TsvReader(lemma_service) as tsv_reader:
            with open(self.MORPHOLOGY_FILE, 'r') as file:
                for line in file:
                    tsv_reader.read_segment(line.strip())
            tokens = tsv_reader.tokens
            segments = tsv_reader.segments

        # tokens
        verse: Verse = None
        token_count = len(tokens)
        for i in range(token_count):
            token = tokens[i]
            token.segments = segments[i]

            # new verse?
            location = token.location
            chapter_number = location.chapter_number
            verse_number = location.verse_number
            if (verse is None
                or verse.location.chapter_number != chapter_number
                    or verse.location.verse_number != verse_number):
                verse = Verse(Location(chapter_number, verse_number, 0), [])
                self._chapters[chapter_number - 1].verses.append(verse)

            verse.tokens.append(token)

    def _download_morphology(self, client: CorpusClient):

        if self.MORPHOLOGY_FILE.exists():
            return

        self.MORPHOLOGY_FILE.parent.mkdir()

        print('Downloading metadata...')
        chapters = client.metadata().chapters
        token_count = 0

        print('Downloading morphology...')
        with open(self.MORPHOLOGY_FILE, 'w') as writer:
            batch_size = 10
            for chapter in chapters:
                verse_number = 1
                while verse_number <= chapter.verse_count:
                    location = Location(chapter.chapter_number, verse_number)
                    count = min(batch_size, chapter.verse_count - verse_number + 1)
                    verses = client.morphology(location, count)
                    print(f'Downloaded verse {location}')
                    for verse in verses:
                        for token in verse.tokens:
                            location = token.location
                            for segment in token.segments:
                                writer.write(self._write_segment(location, segment))
                                writer.write('\n')
                            token_count += 1
                    verse_number += batch_size
        print(f'Downloaded: {token_count} tokens')

    @staticmethod
    def _write_segment(location: List[int], segment: SegmentResponse):
        line = []
        for number in location:
            line.append(str(number))
            line.append('\t')

        arabic = segment.arabic
        if arabic is not None:
            line.append(arabic)
        line.append('\t')

        morphology = segment.morphology
        if morphology is not None:
            line.append(morphology)
        return ''.join(line)
