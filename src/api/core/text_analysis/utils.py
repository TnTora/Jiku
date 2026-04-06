from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class Morpheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lemma: str = Field(min_length=1, max_length=100)
    inflection: str = Field(min_length=1, max_length=100)
    pos: str = ""
    tag: str = ""
    status: Literal["unknown", "known", "semi-known"] = "unknown"

