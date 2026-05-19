from fastapi import APIRouter, status, Depends, HTTPException

from api.schemas.books import BookInfoResponse, BookPosition, BookLastPosUpdate
from api.schemas.books import Book as BookSchema

from api.db import get_db
from api.db.models.books import Book, Section, LastPosition

from sqlalchemy import select, delete, distinct, func
from sqlalchemy.orm import Session

from api.core.config import config_path

from typing import Annotated


################# Temp Testing ####################
# import json

# with Path("test_epub.json").open() as f:
#     test_books_json = json.load(f)

# books = {}

# for test_book_json in test_books_json:
#     book = Book.model_validate(test_book_json)
#     books[book.id] = book

###################################################

router = APIRouter()


@router.get("/id/{id}", response_model=BookSchema)
def get_book(id: int, db: Annotated[Session, Depends(get_db)]):
    book = db.execute(
        select(Book).where(Book.id == id)
    ).scalar()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book

@router.get("/id/{id}/{section_name}")
def get_section_content(id: int, section_name: str, db: Annotated[Session, Depends(get_db)]):
    filename = db.execute(
        select(Section.filename).where(Section.book_id == id and Section.key == section_name)
    ).scalar()

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="section not found",
        )

    content_path = config_path / "books" / str(id) / "content" / filename
    content = content_path.read_text()
    # TODO: replase jiku:// with api url
    return content


@router.put(
    "/update_last_pos",
    status_code=status.HTTP_202_ACCEPTED)
def update_last_pos(pos_update: BookLastPosUpdate, db: Annotated[Session, Depends(get_db)]):
    last_pos = db.execute(
        select(LastPosition).where(LastPosition.book_id == pos_update.id)
    ).scalar()

    if last_pos is None:
        last_pos = LastPosition(
            book_id=pos_update.id,
            section=pos_update.section,
            tok_pos=pos_update.tok_pos,
            ch_pos=pos_update.ch_pos,
        )
        db.add(last_pos)
    else:
        last_pos.section = pos_update.section
        last_pos.tok_pos = pos_update.tok_pos
        last_pos.ch_pos = pos_update.ch_pos

    db.commit()

@router.get("/all", response_model=list[BookInfoResponse])
def get_books(db: Annotated[Session, Depends(get_db)]):

    books = db.execute(
        select(Book)
    ).scalars().all()

    books_info = [
        {
            "id": book.id,
            "title": book.title,
            "creators": book.creators,
            "thumb": book.thumb,
            "static_url": book.static_url,
        }
        for book in books
    ]
    return books_info
