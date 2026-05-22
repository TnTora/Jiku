from fastapi import APIRouter, status, Depends, HTTPException

from api.schemas.books import BookInfoResponse, BookRespone, BookLastPosUpdate, BookmarkCreate, BookmarkResponse

from api.db import get_db
from api.db.models.books import Book, Section, LastPosition, BookToken, Bookmark
from api.db.models.core import Morpheme, AnkiNote, AnkiNoteMorpheme

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


@router.get("/id/{id}", response_model=BookRespone)
def get_book(id: int, db: Annotated[Session, Depends(get_db)]):
    book = db.execute(
        select(Book).where(Book.id == id)
    ).scalar()

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    status_result = db.execute(
        select(Morpheme.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, Morpheme.inflection == AnkiNoteMorpheme.morph_inflection)
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .where(Morpheme.lemma.in_(select(BookToken.lemma).distinct()))
        .group_by(Morpheme.lemma)
    )

    status_map = {lemma: status for lemma, status in status_result}  # noqa: C416

    return {"book": book, "status_map": status_map}

@router.get("/id/{id}/{section_name}")
def get_section_content(id: int, section_name: str, db: Annotated[Session, Depends(get_db)]):
    filename = db.execute(
        select(Section.filename).where((Section.book_id == id) & (Section.key == section_name))
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


@router.post(
    "/add_bookmark",
    response_model=BookmarkResponse,
    status_code=status.HTTP_201_CREATED)
def add_bookmark(bookmark: BookmarkCreate, db: Annotated[Session, Depends(get_db)]):
    new_bookmark = Bookmark(
        book_id=bookmark.book_id,
        name=bookmark.name,
        preview=bookmark.preview,
        section=bookmark.section,
        ch_pos=bookmark.ch_pos,
        tok_pos=bookmark.tok_pos,
    )

    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)

    return new_bookmark


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
