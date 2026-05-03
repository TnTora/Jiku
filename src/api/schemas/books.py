from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class BookPosition(BaseModel):
    section: str
    ch_pos: int | None
    tok_pos: int | None


class TocItem(BaseModel):
    title: str
    section: str


class Bookmark(BookPosition):
    name: str
    preview: str


class BookMetadata(BaseModel):
    title: str
    authors: list[str] = []
    last_modified: datetime = Field(default_factory=datetime.now)
    raw: dict


class BookStats(BaseModel):
    total_char: int = Field(ge=0, default=0)
    total_tokens: int = Field(ge=0, default=0)
    tokens_count: dict[str, int] = {}


class Section(BaseModel):
    key: str
    number: int = -1
    stylesheets: list[str]
    filename: str
    start_ch: int
    start_tok: int


class Book(BaseModel):
    id: int
    sections: dict[str, Section]
    stylesheets: list[str]
    spine: list[str]
    toc: list[TocItem] = []
    bookmarks: list[Bookmark] = []
    metadata: BookMetadata
    original_file: str
    static_url: str
    stats: BookStats


class BookRespone(BaseModel):
    book: Book

