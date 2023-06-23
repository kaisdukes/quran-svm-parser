import re
from typing import List

from pydantic import BaseModel, validator

from ..syntax.word_type import WordType


class Response(BaseModel):
    class Config:
        def alias_generator(string: str):
            return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)


class ChapterResponse(Response):
    chapter_number: int
    verse_count: int


class MetadataResponse(Response):
    chapters: List[ChapterResponse]


class SegmentResponse(Response):
    arabic: str | None
    morphology: str | None


class TokenResponse(Response):
    location: List[int]
    segments: List[SegmentResponse]


class VerseResponse(Response):
    tokens: List[TokenResponse]


class GraphLocation(Response):
    location: List[int]
    graph_number: int


class WordResponse(Response):
    type: WordType
    token: TokenResponse | None
    elided_text: str | None
    elided_pos_tag: str | None
    start_node: int
    end_node: int

    @validator('type', pre=True)
    def parse_type(cls, v):
        return WordType.parse(v)


class PhraseNodeResponse(Response):
    start_node: int
    end_node: int
    phrase_tag: str


class EdgeResponse(Response):
    start_node: int
    end_node: int
    dependency_tag: str


class GraphResponse(Response):
    next: GraphLocation | None
    words: List[WordResponse]
    edges: List[EdgeResponse] | None
    phrase_nodes: List[PhraseNodeResponse] | None
