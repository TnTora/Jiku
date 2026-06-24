from api.core.config.anki import AnkiSettings
from api.db import SessionLocal
from api.db.models.core import Option

from sqlalchemy import select

import json

from typing import Literal

type OptionSectionName = Literal["anki"]
type OptionSection = AnkiSettings


option_type = {
    "anki": AnkiSettings
}

def load_settings_from_db(name: OptionSectionName) -> OptionSection:
    if name not in option_type:
        msg = f"'{name}' is not a valid option class."
        raise ValueError(msg)

    with SessionLocal() as db:
        try:
            result = db.execute(
                select(Option.value).where(Option.name == name)
            )
        except Exception:
            return option_type[name]()

        settings_json_str = result.scalar()

        if not settings_json_str:
            settings = option_type[name]()
            db.add(
                Option(
                    name=name,
                    value=settings.model_dump_json(),
                )
            )
            db.commit()
            return settings

        settings = option_type[name].model_validate(json.loads(settings_json_str))

        return settings

