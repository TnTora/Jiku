from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi.sse import EventSourceResponse, ServerSentEvent

from api.schemas.books import (
    BookRespone,
    BookLastPosUpdate,
    BookmarkCreate,
    BookmarkResponse,
    CollectionInfoResponse,
    CollectionCreate,
    BookInfoResponse,
    CreatorInfoRespone,
    CollectionRename,
    CollectionBookCreate,
    BookmarkRename,
    BookProcessCancel,
    BookLastOpenUpdate,
)

from api.db import get_db
from api.db.models.core import Morpheme, AnkiNote, AnkiNoteMorpheme
from api.db.models.books import (
    Book,
    Section,
    LastPosition,
    BookToken,
    Bookmark,
    Creator,
    Collection,
    CreatorBook,
    CollectionBook, BookTokenCount
)

from api.core.text_analysis.ebook_processing import process_ebub
from api.core.config import config_path, tmp_path
from api.core.config.shared import redis_host

from sqlalchemy import select, func
from sqlalchemy.orm import Session

import json
import redis.asyncio as redis
import shutil

from datetime import datetime, timedelta, UTC

from typing import Annotated, TYPE_CHECKING

if TYPE_CHECKING:
    from celery.contrib.abortable import AbortableAsyncResult

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
        select(BookToken.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, BookToken.inflection == AnkiNoteMorpheme.morph_inflection)
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .join(BookTokenCount, BookTokenCount.morph_inflection == BookToken.inflection)
        .where(BookTokenCount.book_id == id)
        .group_by(BookToken.lemma)
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


@router.put(
    "/update_last_opened",
    status_code=status.HTTP_202_ACCEPTED)
def update_last_opened(data: BookLastOpenUpdate, db: Annotated[Session, Depends(get_db)]):
    book = db.execute(select(Book).where(Book.id == data.id)).scalar()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    book.last_opened = datetime.now(UTC)

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


@router.put(
    "/rename_bookmark",
    status_code=status.HTTP_202_ACCEPTED)
def rename_bookmark(data: BookmarkRename, db: Annotated[Session, Depends(get_db)]):
    bookmark = db.execute(
        select(Bookmark).where(Bookmark.id == data.id)
    ).scalar()

    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    bookmark.name = data.name

    db.commit()


@router.delete("/delete_bookmark/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: int, db: Annotated[Session, Depends(get_db)]):
    bookmark = db.execute(select(Bookmark).where(Bookmark.id == bookmark_id)).scalar()

    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")

    db.delete(bookmark)
    db.commit()


@router.get("/books_info", response_model=list[BookInfoResponse])
def get_books(  # noqa: PLR0913
    db: Annotated[Session, Depends(get_db)],
    title: str | None = None,
    creator_id: int | None = None,
    collection_id: int | None = None,
    progress: str | None = None,
    ordr: int = 0,
    asc: bool = True,  # noqa: FBT001, FBT002
    limit:int | None = None,
    offset: int = 0):

    stmt = select(Book)

    if creator_id and collection_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="creator_id and collection_id cannot be specified at the same time"
        )

    if creator_id:
        stmt = (stmt
            .join(CreatorBook)
            .join(Creator)
            .where(Creator.id == creator_id)
        )

    if collection_id:
        stmt = (stmt
            .join(CollectionBook)
            .join(Collection)
            .where(Collection.id == collection_id)
        )

    if title:
        stmt = stmt.where(Book.title.ilike(f"%{title}%"))

    if progress:
        if progress in ("new", "reading", "completed"):
            stmt = stmt.where(Book.progress_status == progress)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid progress value"
            )

    if limit:
        stmt = stmt.limit(limit).offset(offset)

    if ordr == 0:
        order = Book.title
    elif ordr == 1:
        order = Book.date_added
    else:
        order = Book.last_opened

    stmt = stmt.order_by(order.asc()) if asc else stmt.order_by(order.desc())

    books = db.execute(
        stmt
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


@router.post(
    "/add_book_to_collection",
    status_code=status.HTTP_201_CREATED)
def add_book_to_collection(data: CollectionBookCreate, db: Annotated[Session, Depends(get_db)]):
    exists = db.execute(
        select(CollectionBook).where((CollectionBook.book_id == data.book_id) & (CollectionBook.collection_id == data.collection_id))
    ).scalars().one_or_none()

    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book alreay found in collection")

    new_pair = CollectionBook(book_id=data.book_id, collection_id=data.collection_id)
    db.add(new_pair)
    db.commit()


@router.delete("/delete_book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Annotated[Session, Depends(get_db)]):
    book = db.execute(select(Book).where(Book.id == book_id)).scalar()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    db.delete(book)
    db.flush()

    for creator in book.creators_:
        has_books = db.execute(
            select(CreatorBook).where(CreatorBook.creator_id == creator.id)
        ).scalar()

        if has_books is None:
            db.delete(creator)

    db.commit()
    shutil.rmtree(config_path / "books" / str(book_id))


@router.delete("/delete_collection/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: int, db: Annotated[Session, Depends(get_db)]):
    collection = db.execute(select(Collection).where(Collection.id == collection_id)).scalar()

    if collection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")

    db.delete(collection)
    db.commit()


active_tasks_ids = {}


@router.put("/stop_book_processing")
def stop_book_processing(data: BookProcessCancel):
    if data.id in active_tasks_ids:
        result: AbortableAsyncResult = process_ebub.AsyncResult(data.id)
        if result.state == "PENDING":
            result.revoke()
        else:
            result.abort()


@router.put("/clear_all_tasks")
def clear_all_tasks():
    for task_id in active_tasks_ids:
        result: AbortableAsyncResult = process_ebub.AsyncResult(task_id)
        if result.state == "PENDING":
            result.revoke()
        else:
            result.abort()

    # active_tasks_ids.clear()


@router.get("/tasks_events", response_class=EventSourceResponse)
async def tasks_events():
    print("tasks_events")
    async with redis.Redis(host=redis_host, port=6379, db=1, decode_responses=True) as redisdb, redisdb.pubsub() as pubsub:
        await pubsub.subscribe("__keyevent@1__:set")

        #If active_tasks_ids is not empty, yield temp status.
        for task_id, filename in active_tasks_ids.items():
            task = {
                "status": "WAITING",
                "result": None,
                "traceback": None,
                "children": None,
                "date_done": None,
                "task_id": task_id,
                "name": filename,
            }
            yield task

        last_message = datetime.now(UTC)

        while True:
            print("waiting for message...")
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
            print(message)

            if not active_tasks_ids and (datetime.now(UTC)-last_message > timedelta(seconds=30)):
                break

            if message is None:
                continue

            print('message["data"]', message["data"], " | ", str(type(message["data"])))

            task = await redisdb.get(message["data"])

            try:
                task = json.loads(task)
                task_id = task["task_id"]
                task_status = task["status"]
            except (TypeError, KeyError, json.JSONDecodeError):
                continue

            if task_id not in active_tasks_ids:
                continue

            last_message = datetime.now(UTC)

            print(task, task_id, task_status, sep="\n")

            name = active_tasks_ids.get(task_id, "Task")
            task["name"] = name

            if task_status in {"FAILURE", "SUCCESS", "CANCELLED", "REVOKED"}:
                del active_tasks_ids[task_id]

            yield task

            if not active_tasks_ids:
                break

        print("unsubscribing...")
        await pubsub.unsubscribe()
        yield ServerSentEvent(event="close", data="")
        print("unsubscribed")



@router.post("/add_book")
def add_book(file: UploadFile):
    if file.filename is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="filename not found")

    print("Saving file: ", file.filename)
    content = file.file.read()
    tmp_file = (tmp_path / file.filename)
    tmp_file.write_bytes(content)

    result = process_ebub.delay(str(tmp_file), file.filename)

    print(f"{result.id = }")
    active_tasks_ids[result.id] = file.filename
    return {"id": result.id}
