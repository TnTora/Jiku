from fastapi import APIRouter, status, Depends, HTTPException

from api.db import get_db
from api.db.models.core import Morpheme

from api.schemas.core import KnownMorphemes
from api.core.anki import get_decks, get_note_types, get_all_note_types_fields, AnkiError

from sqlalchemy import select, distinct, func
from sqlalchemy.orm import Session

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
def get_anki_decks_info():
    try:
        decks = get_decks()
        note_types = get_note_types()
        note_types_fields = get_all_note_types_fields(note_types)
    except AnkiError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=e.msg) from e
    else:
        return {"decks": decks, "note_types": note_types, "note_types_fields": note_types_fields}

