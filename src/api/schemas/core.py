from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

type KnownStatus = Literal[1, 0]

class Morpheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lemma: str = Field(min_length=1, max_length=100)
    inflection: str = Field(min_length=1, max_length=100)
    pos: str = ""
    tag: str = ""


class KnownMorphemes(BaseModel):
    lemmas: int
    inflections: int


class SearchParameters(BaseModel):
    deck: str = Field(min_length=1, max_length=100)
    note_type: str = Field(min_length=1, max_length=100)
    text_field: str = Field(min_length=1, max_length=100)
    skip_brackets: bool = False


class AnkiSettings(BaseModel):
    port: int = 8765
    to_analyze: list[SearchParameters] = []
    to_update: set[tuple[str, str]] = set() # {(deck, note_type)}


class AnkiInfo(BaseModel):
    decks: list[str] = []
    note_types: list[str] = []
    note_types_fields: dict[str, list[str]] = {}


class SearchParametersRespone(BaseModel):
    deck: str = Field(min_length=1, max_length=100)
    note_type: str = Field(min_length=1, max_length=100)
    text_field: str = Field(min_length=1, max_length=100)
    skip_brackets: bool


class AnkiSettingsRespone(BaseModel):
    port: int
    to_analyze: list[SearchParameters]
    to_update: set[tuple[str, str]]


class AnkiInfoRespone(BaseModel):
    decks: list[str]
    note_types: list[str]
    note_types_fields: dict[str, list[str]]
