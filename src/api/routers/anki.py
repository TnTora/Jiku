from api.core.config.anki import AnkiInfo
from fastapi.sse import EventSourceResponse, ServerSentEvent
from fastapi import APIRouter, status, Depends, HTTPException

from api.db import get_db
from api.db.models.core import Morpheme, Option

from api.schemas.core import KnownMorphemes
from api.core.anki import get_decks, get_note_types, get_all_note_types_fields, update_morphemes_db, AnkiError
from api.core.config.shared import redis_host
from api.core.config import load_settings_from_db

from sqlalchemy import select, distinct, func
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, UTC
import json

import redis.asyncio as redis

from typing import Annotated

router = APIRouter()

@router.get("/known_morphemes", response_model=KnownMorphemes)
def get_knonw_morphemes(db: Annotated[Session, Depends(get_db)]):
    lemmas = db.execute(
        select(func.count(distinct(Morpheme.lemma)))
    ).scalar()

    if lemmas is None:
        lemmas = 0

    inflections = db.execute(
        select(func.count(Morpheme.inflection))
    ).scalar()

    if inflections is None:
        inflections = 0

    return {"lemmas": lemmas, "inflections": inflections}


@router.get("/anki_decks_info")
def get_anki_decks_info(db: Annotated[Session, Depends(get_db)]):
    anki_info = load_settings_from_db("anki_info")
    return anki_info


@router.put("/update_anki_decks_info")
def update_anki_decks_info(db: Annotated[Session, Depends(get_db)]):
    print("Anki: updating anki decks info")
    try:
        decks = get_decks()
        note_types = get_note_types()
        note_types_fields = get_all_note_types_fields(note_types)
    except AnkiError as e:
        print(f"AnkiError: {e.msg}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.msg) from e
    else:
        anki_info = db.execute(
            select(Option).where(Option.name == "anki_info")
        ).scalar()

        new_anki_info = AnkiInfo(
                decks=decks,
                note_types=note_types,
                note_types_fields=note_types_fields,
            )

        if anki_info is None:
            db.add(
                Option(
                    name="anki_info",
                    value=new_anki_info.model_dump_json()
                )
            )
        else:
            anki_info.value = new_anki_info.model_dump_json()

        db.commit()

syncing_morphs_id = None

@router.put("/sync_morphemes")
def sync_morphemes():
    global syncing_morphs_id

    if syncing_morphs_id is not None:
        result = update_morphemes_db.AsyncResult(syncing_morphs_id)
        result.abort()

    result = update_morphemes_db.delay()
    syncing_morphs_id = result.id
    print(f"{syncing_morphs_id = }")


@router.put("/stop_morphemes_sync")
def stop_morphemes_sync():
    if syncing_morphs_id:
        result = update_morphemes_db.AsyncResult(syncing_morphs_id)
        result.abort()


@router.get("/sync_status", response_class=EventSourceResponse)
async def sync_status():
    global syncing_morphs_id

    print("sync_events")
    async with redis.Redis(host=redis_host, port=6379, db=1, decode_responses=True) as redisdb, redisdb.pubsub() as pubsub:
        await pubsub.subscribe("__keyevent@1__:set")

        if syncing_morphs_id:
            task = {
                "status": "WAITING",
                "result": None,
                "traceback": None,
                "children": None,
                "date_done": None,
                "task_id": syncing_morphs_id,
            }
            yield task

        last_message = datetime.now(UTC)

        while True:
            print("waiting for sync message...")
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30)
            print(f"sync {message = }")

            if syncing_morphs_id is None and (datetime.now(UTC)-last_message > timedelta(seconds=30)):
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

            if task_id != syncing_morphs_id:
                continue

            last_message = datetime.now(UTC)

            print(task, task_id, task_status, sep="\n")

            if task_status in {"FAILURE", "SUCCESS", "CANCELLED"}:
                syncing_morphs_id = None

            yield task

            if syncing_morphs_id is None:
                break

        print("sync unsubscribing...")
        await pubsub.unsubscribe()
        yield ServerSentEvent(event="close", data="")
        print("sync unsubscribed")
