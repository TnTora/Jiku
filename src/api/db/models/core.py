from __future__ import annotations
from api.db import Base

from sqlalchemy import ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import Enum


class KnownStatus(Enum):
    NEW = 0
    KNOWN = 1


class AnkiNoteMorpheme(Base):
    __tablename__ = "ankinote_morpheme"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("ankinotes.nid", ondelete="CASCADE"), nullable=False)
    morph_inflection: Mapped[str] = mapped_column(ForeignKey("morphemes.inflection"), nullable=False)


class Morpheme(Base):
    __tablename__ = "morphemes"

    lemma: Mapped[str] = mapped_column(String, nullable=False)
    inflection: Mapped[str] = mapped_column(String, primary_key=True, index=True, sqlite_on_conflict_primary_key="IGNORE")
    pos: Mapped[str] = mapped_column(String, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)

    notes: Mapped[set[AnkiNote]] = relationship(secondary="ankinote_morpheme", back_populates="morphs")

    @property
    def status(self) -> int:
        if any(note.status == KnownStatus.KNOWN.value for note in self.notes):
            return KnownStatus.KNOWN.value
        return KnownStatus.NEW.value


class AnkiNote(Base):
    __tablename__ = "ankinotes"

    nid: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    deck: Mapped[str] = mapped_column(String, nullable=False)
    text_field: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    morphs: Mapped[set[Morpheme]] = relationship(secondary="ankinote_morpheme", back_populates="notes")


class Option(Base):
    __tablename__ = "options"

    name: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)

    # List of options:
    # - anki
