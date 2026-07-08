from pydantic import BaseModel, Field
from datetime import datetime


class BookPosition(BaseModel):
    section: str
    ch_pos: int | None = None
    tok_pos: int | None = None


class TocItem(BaseModel):
    title: str
    section: str
    anchor_id: str | None = None


class BookmarkCreate(BookPosition):
    book_id: int
    name: str = Field(min_length=1, max_length=100)
    preview: str | None = None


class BookmarkResponse(BookmarkCreate):
    id: int


class BookmarkRename(BaseModel):
    id: int
    name: str


class BookMetadata(BaseModel):
    title: str
    authors: list[str] = []
    # last_modified: datetime = Field(default_factory=datetime.now)
    raw: dict


class Section(BaseModel):
    key: str
    number: int = -1
    stylesheets: list[str]
    filename: str
    start_ch: int
    start_tok: int


class Book(BaseModel):
    id: int

    title: str
    creators_names: list[str] = []
    raw_metadata: dict | None

    sections: dict[str, Section]
    stylesheets: list[str]
    spine: list[str]
    toc: list[TocItem] = []
    bookmarks: list[BookmarkResponse] = []

    thumb: str | None = None
    original_file: str
    static_url: str

    total_char: int = Field(ge=0, default=0)
    total_tokens: int = Field(ge=0, default=0)

    date_added: datetime
    last_opened: datetime = datetime.min

    last_pos: BookPosition | None = None


class BookRespone(BaseModel):
    book: Book
    status_map: dict[str, int]


class BookInfoResponse(BaseModel):
    id: int
    title: str
    creators: list[str] = []
    thumb: str | None = None
    static_url: str


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CollectionInfoResponse(BaseModel):
    id: int
    name: str


class CollectionRename(BaseModel):
    id: int
    name: str


class CreatorInfoRespone(BaseModel):
    id: int
    name: str


class BookProcessCancel(BaseModel):
    id: str


class BookLastPosUpdate(BookPosition):
    id: int


class BookLastOpenUpdate(BaseModel):
    id: int


class BookProgressStatusUpdate(BaseModel):
    id: int
    new_status: str


class CollectionBookCreate(BaseModel):
    book_id: int
    collection_id: int
