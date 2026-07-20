from __future__ import annotations

from api.db import Base

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class LineLineToken(Base):
    __tablename__ = "line_linetokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_ref: Mapped[int] = mapped_column(Integer, nullable=False)
    line_id: Mapped[int] = mapped_column(ForeignKey("lines.id", ondelete="CASCADE"), nullable=False)
    token_inflection: Mapped[str] = mapped_column(ForeignKey("linetokens.inflection"), nullable=False)

    line: Mapped[Line] = relationship(back_populates="tokens_association")
    token: Mapped[LineToken] = relationship(back_populates="lines_association")


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    preset: Mapped[str] = mapped_column(String, nullable=False, default="Default")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date_added: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    tokens_association: Mapped[list[LineLineToken]] = relationship(
        order_by=LineLineToken.order_ref,
        back_populates="line",
        cascade="all, delete"
    )

    @property
    def tokens(self) -> list[LineToken]:
        return [a.token for a in self.tokens_association]


class LineToken(Base):
    __tablename__ = "linetokens"

    lemma: Mapped[str] = mapped_column(String, nullable=False, index=True)
    inflection: Mapped[str] = mapped_column(String, primary_key=True, index=True, sqlite_on_conflict_primary_key="IGNORE")
    pos: Mapped[str] = mapped_column(String, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)

    lines_association: Mapped[list[LineLineToken]] = relationship(back_populates="token")


class Preset(Base):
    __tablename__ = "presets"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    ws_url: Mapped[str] = mapped_column(String, nullable=False)
