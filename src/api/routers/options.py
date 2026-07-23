import json
from fastapi import APIRouter, status, Depends

from api.core.config import load_settings_from_db
from api.schemas.core import AnkiSettings
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
        old_settings = AnkiSettings.model_validate(json.loads(settings.value))
        for new_params in new_settings.to_analyze:
            for old_params in old_settings.to_analyze:
                if(old_params.deck != new_params.deck or old_params.note_type != new_params.note_type):
                    continue
                if(old_params.text_field != new_params.text_field or old_params.skip_brackets != new_params.skip_brackets):
                    new_settings.to_update.add((new_params.deck, new_params.note_type))
                    break
        settings.value = new_settings.model_dump_json()

    db.commit()

