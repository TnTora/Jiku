from fastapi import APIRouter, status
from pathlib import Path
from api.schemas.books import Book

from os import getenv

config_base = getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"

import json

with Path("test_epub.json").open() as f:
    test_book_json = json.load(f)
book = Book.model_validate(test_book_json)

books = {1:book}

router = APIRouter()


@router.get("/{id}", response_model=Book)
def get_book(id: int):
    return books[id]

@router.get("/{id}/{section_name}")
def get_section_content(id: int, section_name: str):
    content_path = config_path / "books" / str(id) / "content" / books[id].sections[section_name].filename
    content = content_path.read_text()
    # TODO: replase jiku:// with api url
    return content

