from __future__ import annotations

from api.db import Base

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    start_ch: Mapped[int] = mapped_column(Integer, nullable=False)
    start_tok: Mapped[int] = mapped_column(Integer, nullable=False)

    stylesheets: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class BookMark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    section: Mapped[str] = mapped_column(String, nullable=False)

    ch_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tok_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)


class TocItem(Base):
    __tablename__ = "tocitems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)

    title: Mapped[str] = mapped_column(String, nullable=False)
    section: Mapped[str] = mapped_column(String, nullable=False)
    anchor_id: Mapped[str | None] = mapped_column(String, nullable=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)


class BookToken(Base):
    __tablename__ = "bookstokens"

    lemma: Mapped[str] = mapped_column(String, nullable=False)
    inflection: Mapped[str] = mapped_column(String, primary_key=True, index=True, sqlite_on_conflict_primary_key="IGNORE")
    pos: Mapped[str] = mapped_column(String, nullable=True)
    tag: Mapped[str] = mapped_column(String, nullable=True)


class BookTokenCount(Base):
    __tablename__ = "booktokencount"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    morph_inflection: Mapped[str] = mapped_column(ForeignKey("bookstokens.inflection"), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)


class CreatorBook(Base):
    __tablename__ = "creators_books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), nullable=False)


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    books: Mapped[list[Book]] = relationship(
        secondary="creators_books",
        back_populates="creators_"
    )


class LastPosition(Base):
    __tablename__ = "lastpositions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)

    section: Mapped[str] = mapped_column(String, nullable=False)
    ch_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tok_pos: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String, nullable=False)

    original_file: Mapped[str] = mapped_column(String, nullable=False)
    thumb: Mapped[str | None] = mapped_column(String, nullable=True)
    static_url: Mapped[str] = mapped_column(String, nullable=False)

    total_char: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)

    spine: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    raw_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    stylesheets: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    sections: Mapped[dict[str, Section]] = relationship(
        collection_class=attribute_keyed_dict("key"),
        cascade="all, delete"
    )
    toc: Mapped[list[TocItem]] = relationship(order_by=TocItem.number)
    bookmarks: Mapped[list[BookMark]] = relationship(order_by=BookMark.tok_pos)

    creators_: Mapped[list[Creator]] = relationship(
        secondary="creators_books",
        back_populates="books"
    )

    last_pos: Mapped[LastPosition] = relationship(cascade="all, delete")

    # tokens_count: dict[str, int] = {}

    @property
    def creators(self) -> list[str]:
        print(f"{self.creators_ = }")
        return [creator.name for creator in self.creators_]
