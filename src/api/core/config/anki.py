import json
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.models.core import Option

class SearchParameters(BaseModel):
    deck: str = Field(min_length=1, max_length=100)
    note_type: str = Field(min_length=1, max_length=100)
    text_field: str = Field(min_length=1, max_length=100)


class AnkiSettings(BaseModel):
    port: int = 8765
    to_analyze: list[SearchParameters] = []


def load_settings_from_db(db: Session) -> AnkiSettings:
    result = db.execute(
        select(Option.value).where(Option.name == "anki")
    )
    settings_json_str = result.scalar()

    if not settings_json_str:
        return AnkiSettings()

    settings = AnkiSettings.model_validate(json.loads(settings_json_str))

    return settings


