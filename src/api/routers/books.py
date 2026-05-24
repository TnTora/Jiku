from fastapi import APIRouter, status, Depends, HTTPException

from api.schemas.books import (
    BookRespone,
    BookLastPosUpdate,
    BookmarkCreate,
    BookmarkResponse,
    CollectionInfoResponse,
    CollectionCreate, BookInfoResponse, CreatorInfoRespone, CollectionRename,
)

from api.db import get_db
from api.db.models.books import Book, Section, LastPosition, BookToken, Bookmark, Creator, Collection
from api.db.models.core import Morpheme, AnkiNote, AnkiNoteMorpheme

from sqlalchemy import select, delete, distinct, func
from sqlalchemy.orm import Session

from api.core.config import config_path

from typing import Annotated

router = APIRouter()


@router.get("/id/{id}", response_model=BookRespone)
def get_book(id: int, db: Annotated[Session, Depends(get_db)]):  # noqa: A002
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


@router.get("/id/{book_id}/{section_name}")
def get_section_content(book_id: int, section_name: str, db: Annotated[Session, Depends(get_db)]):
    filename = db.execute(
        select(Section.filename).where((Section.book_id == book_id) & (Section.key == section_name))
    ).scalar()

    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="section not found",
        )

    content_path = config_path / "books" / str(book_id) / "content" / filename
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


@router.delete("/delete_bookmark/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: int, db: Annotated[Session, Depends(get_db)]):
    bookmark = db.execute(select(Bookmark).where(Bookmark.id == bookmark_id)).scalar()

    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()


@router.get("/books_info", response_model=list[BookInfoResponse])
def get_books(db: Annotated[Session, Depends(get_db)]):

    books = db.execute(
        select(Book)
    ).scalars().all()

    return books


@router.get("/collections", response_model=list[CollectionInfoResponse])
def get_collections(db: Annotated[Session, Depends(get_db)]):

    collections = db.execute(
        select(Collection)
    ).scalars().all()

    return collections


@router.get("/creators", response_model=list[CreatorInfoRespone])
def get_creators(db: Annotated[Session, Depends(get_db)]):

    creators = db.execute(
        select(Creator)
    ).scalars().all()

    return creators


@router.post(
    "/add_collection",
    response_model=CollectionInfoResponse,
    status_code=status.HTTP_201_CREATED)
def add_collection(collection_info: CollectionCreate, db: Annotated[Session, Depends(get_db)]):
    new_collection = Collection(name=collection_info.name)

    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    return new_collection


@router.put(
    "/rename_collection",
    status_code=status.HTTP_202_ACCEPTED)
def rename_collection(data: CollectionRename, db: Annotated[Session, Depends(get_db)]):
    collection = db.execute(
        select(Collection).where(Collection.id == data.id)
    ).scalar()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    collection.name = data.name

    db.commit()


@router.delete("/delete_book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    book = db.execute(select(Book).where(Book.id == book_id)).scalar()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    db.delete(book)
    db.commit()


@router.delete("/delete_collection/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: int, db: Annotated[Session, Depends(get_db)]):
    collection = db.execute(select(Collection).where(Collection.id == collection_id)).scalar()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    db.delete(collection)
    db.commit()

