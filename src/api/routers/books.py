from fastapi import APIRouter, status
from pathlib import Path
from api.schemas.books import Book, BookInfoResponse, BookPosition, BookLastPosUpdate

from os import getenv

config_base = getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"


################# Temp Testing ####################
import json

with Path("test_epub.json").open() as f:
    test_books_json = json.load(f)

books = {}

for test_book_json in test_books_json:
    book = Book.model_validate(test_book_json)
    books[book.id] = book

###################################################

router = APIRouter()


@router.get("/id/{id}", response_model=Book)
def get_book(id: int):
    return books[id]

@router.get("/id/{id}/{section_name}")
def get_section_content(id: int, section_name: str):
    content_path = config_path / "books" / str(id) / "content" / books[id].sections[section_name].filename
    content = content_path.read_text()
    # TODO: replase jiku:// with api url
    return content


@router.put(
    "/update_last_pos",
    status_code=status.HTTP_202_ACCEPTED)
def update_last_pos(pos_update: BookLastPosUpdate):
    book = books[pos_update.id]
    book.last_pos = BookPosition(
        section=pos_update.section,
        tok_pos=pos_update.tok_pos,
        ch_pos=pos_update.ch_pos,
    )

@router.get("/all", response_model=list[BookInfoResponse])
def get_books():
    books_info = [{
        "id": book.id,
        "metadata": book.metadata,
        "thumb": book.thumb,
        "static_url": book.static_url
        } for book in books.values()
    ]
    return books_info
