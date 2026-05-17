from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

from .core import Morpheme, KnownStatus

class LineBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    tokens: list[Morpheme]

class LineCreate(BaseModel):
    text: str = Field(min_length=1, max_length=1000)

class LineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    date_added: datetime
    tokens: list[Morpheme]
    line_status_map: dict[str, KnownStatus]

class LastSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lines: list[LineBase]
    status_map: dict[str, KnownStatus]

