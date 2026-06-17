from fastapi import APIRouter, status, Depends, HTTPException

from api.core.config import load_settings_from_db
from api.core.config.anki import AnkiSettings
from api.core.anki import anki_settings
from api.db import get_db
from api.db.models.core import Option

from sqlalchemy import select
from sqlalchemy.orm import Session

from typing import Annotated


router = APIRouter()


@router.get("/anki_settings", response_model=AnkiSettings)
def load_anki_settings():
    settings = load_settings_from_db("anki")
    return settings


@router.put("/anki_settings", status_code=status.HTTP_202_ACCEPTED)
def update_anki_settings(new_settings: AnkiSettings, db: Annotated[Session, Depends(get_db)]):
    settings = db.execute(
            select(Option).where(Option.name == "anki")
    ).scalar()

    if not settings:
        db.add(
            Option(
                name="anki",
                value=new_settings.model_dump_json(),
            )
        )
    else:
        settings.value = new_settings.model_dump_json()

    db.commit()

    # update anki_settings variable used in most backend operations
    anki_settings.port = new_settings.port
    anki_settings.to_analyze = new_settings.to_analyze

