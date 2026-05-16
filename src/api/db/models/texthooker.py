from __future__ import annotations

from api.db import Base

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class LineLineToken(Base):
    __tablename__ = "line_linetokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_ref: Mapped[int] = mapped_column(Integer, nullable=False)
    line_id: Mapped[int] = mapped_column(ForeignKey("lines.id"), nullable=False)
    token_inflection: Mapped[str] = mapped_column(ForeignKey("linetokens.inflection"), nullable=False)


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    tokens: Mapped[list[LineToken]] = relationship(
        secondary="line_linetokens",
        order_by=LineLineToken.order_ref,
        back_populates="lines"
    )


class LineToken(Base):
    __tablename__ = "linetokens"

    lemma: Mapped[str] = mapped_column(String, nullable=False, index=True)
    inflection: Mapped[str] = mapped_column(String, primary_key=True, index=True, sqlite_on_conflict_primary_key="IGNORE")
    pos: Mapped[str] = mapped_column(String, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)

    lines: Mapped[list[Line]] = relationship(secondary="line_linetokens", back_populates="tokens")
