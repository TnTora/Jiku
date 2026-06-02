import re
from collections.abc import Iterator
from pathlib import Path

import ebooklib
import tinycss2

# from spacy_wrapper import get_analyzer
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
from ebooklib import epub
from dataclasses import dataclass, field
from tinycss2.ast import IdentToken, QualifiedRule, AtRule

from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.db.models.core import Morpheme

from api.core.config import config_path
from sqlalchemy.orm import Session
from api.db import SessionLocal
from api.db.models.books import (
    Book,
    Section,
    TocItem,
    CreatorBook,
    Creator,
    BookToken,
    BookTokenCount,
    LastPosition,
)

from sqlalchemy import select, insert

from typing import Any


@dataclass
class BookStats:
    total_char: int = 0
    total_tokens: int = 0
    tokens_count: dict[str, dict[str, Any]] = field(default_factory=dict)


def store_tokens_count(book_id:int, tokens_count: dict[str, dict[str, Any]], db: Session) -> None:
    existing = db.execute(
        select(BookToken.inflection).where(BookToken.inflection.in_(tokens_count))
    )
    db.execute(
        insert(BookToken),
        [
            {
                "lemma": v["morph"].lemma,
                "inflection": v["morph"].inflection,
                "pos": v["morph"].pos,
                "tag": v["morph"].tag,
            }
            for key, v in tokens_count.items() if key not in existing
        ]
    )

    db.execute(
        insert(BookTokenCount),
        [
            {
                "book_id": book_id,
                "morph_inflection": v["morph"].inflection,
                "count": v["count"],
            }
            for v in tokens_count.values()
        ]
    )


def process_ebub(filepath: Path, db: Session) -> Book:
    book = epub.read_epub(filepath)
    spine: list[str] = [section_name for section_name, linear in book.spine if linear]


    processed_book = Book(
        title=book.get_metadata("DC", "title")[0][0],
        raw_metadata=book.metadata,
        stylesheets=[],
        spine=spine,
        thumb=None,
        original_file=filepath.name,
        static_url="http://127.0.0.1:8000/static/books",
        total_char=0,
        total_tokens=0,
    )

    db.add(processed_book)
    db.flush()
    db.refresh(processed_book)

    book_id = processed_book.id

    last_pos = LastPosition(book_id=book_id, section=spine[0])
    db.add(last_pos)

    base_path = config_path / Path(f"books/{book_id}/")
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "stylesheets").mkdir(parents=True, exist_ok=True)
    (base_path / "content").mkdir(parents=True, exist_ok=True)
    (base_path / "images").mkdir(parents=True, exist_ok=True)


    for creator_data in book.get_metadata("DC", "creator"):
        creator = db.execute(
            select(Creator).where(Creator.name == creator_data[0])
        ).scalars().one_or_none()

        if creator is None:
            creator = Creator(name=creator_data[0])

            db.add(creator)
            db.flush()
            db.refresh(creator)

        db.add(CreatorBook(
            book_id=book_id,
            creator_id=creator.id,
        ))

    stats = BookStats()

    stylesheets:set[str] = set()

    cover = None

    documents_id_dict = {}

    for img in book.get_items_of_type(ebooklib.ITEM_COVER):
        cover = Path(img.get_name()).name
        (base_path / "images" / Path(img.get_name()).name).write_bytes(img.get_content())

    for img in book.get_items_of_type(ebooklib.ITEM_IMAGE):
        (base_path / "images" / Path(img.get_name()).name).write_bytes(img.get_content())

    for stylesheet in book.get_items_of_type(ebooklib.ITEM_STYLE):
        filename = Path(stylesheet.get_name()).name
        process_stylesheet(base_path / "stylesheets" / filename, stylesheet.get_content())

    for idref in spine:
        doc = book.get_item_with_id(idref)
        filename = Path(doc.get_name()).name
        print(filename)

        section: Section = process_html_content(
            base_path / "content" / filename,
            doc.content,
            book_id,
            stats
        )

        section.key = doc.id

        documents_id_dict[Path(doc.get_name()).stem] = doc.id

        try:
            section.number = spine.index(section.key)
        except ValueError:
            section.number = -1

        stylesheets.update(section.stylesheets)

        db.add(section)

    store_tokens_count(book_id, stats.tokens_count, db)

    toc: list[TocItem] = []

    def process_toc(toc_items: list) -> None:
        for item in toc_items:
            if isinstance(item, tuple):
                href_path = Path(item[0].href)
                anchor_match = re.search(r"(?<=#).+",href_path.suffix)
                anchor = anchor_match.group() if anchor_match else None

                toc.append(
                    TocItem(
                        book_id=book_id,
                        title=item[0].title,
                        section=documents_id_dict[href_path.stem],
                        anchor_id=anchor,
                        number=len(toc)
                    )
                )

                process_toc(item[1])

            else:
                href_path = Path(item.href)
                anchor_match = re.search(r"(?<=#).+",href_path.suffix)
                anchor = anchor_match.group() if anchor_match else None
                toc.append(
                    TocItem(
                        book_id=book_id,
                        title=item.title,
                        section=documents_id_dict[href_path.stem],
                        anchor_id=anchor,
                        number=len(toc)
                    )
                )


    process_toc(book.toc)

    processed_book.stylesheets = list(stylesheets)
    processed_book.thumb = cover
    processed_book.total_char = stats.total_char
    processed_book.total_tokens = stats.total_tokens

    db.add_all(toc)
    db.commit()

    return processed_book


def process_stylesheet(filepath: Path, content: bytes):
    print(filepath)
    rules, _ = tinycss2.parse_stylesheet_bytes(content)

    temp_prelude = tinycss2.parse_stylesheet("#jiku-book-container .jiku-book-body.jiku-book-html{}")[0].prelude
    # book_container_class = temp_prelude[:3]
    new_body_class = temp_prelude[3:5]
    new_html_class = temp_prelude[5:7]

    to_delete = []
    exclude_at_rules = {"media", "supports", "layer", "scope", "container", "starting-style"}
    rules_new = []

    for j, rule in enumerate(rules):
        if isinstance(rule, QualifiedRule):
            for i, tok in enumerate(rule.prelude):
                if isinstance(tok, IdentToken):
                    if tok.lower_value == "html":
                        rule.prelude[i:i+1] = new_html_class
                    elif tok.lower_value == "body":
                        rule.prelude[i:i+1] = new_body_class

        elif isinstance(rule, AtRule) and rule.lower_at_keyword not in exclude_at_rules:
            to_delete.append(j)
            rules_new.append(rule)

    for i in reversed(to_delete):
        rules.pop(i)

    book_container_rule = tinycss2.parse_stylesheet("#jiku-book-container{}")[0]
    book_container_rule.content = rules
    rules_new.append(book_container_rule)

    filepath.write_text(tinycss2.serialize(rules_new))


def process_html_content(filepath: Path, content: bytes, book_id: int, stats: BookStats) -> Section:
    soup = BeautifulSoup(content, "html.parser")

    if soup.head:
        section_stylesheets = [Path(link["href"]).name for link in soup.head.select("link[rel='stylesheet']")]  # ty:ignore[invalid-argument-type]
        soup.head.decompose()
    else:
        section_stylesheets = []

    html_tag = soup.html
    if html_tag is not None:
        html_tag.attrs = {key: val for key, val in html_tag.attrs.items() if key in {"class", "id"}}

        if html_tag.has_attr("class"):
            html_tag["class"].append("jiku-book-html")  # ty:ignore[unresolved-attribute]
        else:
            html_tag["class"] = ["jiku-book-html"]  # ty:ignore[invalid-assignment]

        html_tag.name = "div"

    body_tag = soup.body
    if body_tag is not None:
        if body_tag.has_attr("class"):
            body_tag["class"].append("jiku-book-body")  # ty:ignore[unresolved-attribute]
        else:
            body_tag["class"] = ["jiku-book-body"]  # ty:ignore[invalid-assignment]

        body_tag.name = "div"

    for child in soup.children:
        if not isinstance(child, Tag):
            child.decompose()

    for img in soup.find_all("img", src=True):
        filename = Path(img["src"]).name  # ty:ignore[invalid-argument-type]
        img["src"] = f"http://127.0.0.1:8000/static/books/{book_id}/images/{filename}"

    for image in soup.find_all("image"):
        if "href" in image.attrs:
            filename = Path(image["href"]).name  # ty:ignore[invalid-argument-type]
            image["href"] = f"http://127.0.0.1:8000/static/books/{book_id}/images/{filename}"
        elif "xlink:href" in image.attrs:
            filename = Path(image["xlink:href"]).name  # ty:ignore[invalid-argument-type]
            del image["xlink:href"]
            image["href"] = f"http://127.0.0.1:8000/static/books/{book_id}/images/{filename}"



    section = Section(
        book_id=book_id,
        key=filepath.stem,
        number=-1,
        stylesheets = section_stylesheets,
        filename=filepath.name,
        start_ch=stats.total_char+1,
        start_tok=stats.total_tokens+1,
    )

    content_tokenization(soup, stats)

    filepath.write_text(str(soup))

    return section


@dataclass
class TokenizationContext:
    tokens: Iterator[Morpheme]
    curr_token: Morpheme = field(init=False)
    tokens_exhausted: bool = field(init=False)
    partial_match_end_idx: int
    stats: BookStats
    p_tag: Tag
    new_content: list[str] = field(default_factory=list)
    open_tags: list[Tag] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.next_token()

    def next_token(self) -> Morpheme | None:
        next_token_v = next(self.tokens, None)

        if next_token_v is None:
            self.tokens_exhausted = True
            return None

        self.curr_token = next_token_v
        self.tokens_exhausted = False

        if self.curr_token.inflection.lower() in self.stats.tokens_count:
            self.stats.tokens_count[self.curr_token.inflection.lower()]["count"] += 1
        else:
            self.stats.tokens_count[self.curr_token.inflection.lower()] = {
                "morph": self.curr_token,
                "count": 1
            }

        return next_token_v


def content_tokenization(soup: BeautifulSoup, stats: BookStats):
    analyzer = get_analyzer()

    p_tags = soup.find_all("p")
    for p_tag in p_tags:
        p_text = p_tag.get_text()

        if not p_text:
            continue

        tokens = analyzer.parse(p_text, pos_exclude={"SPACE", "PUNCT", "SYM", "X"}, line_model=False)
        # print("p_tag", p_tag.prettify(), "\n")
        start_ch = stats.total_char

        tokenization_context = TokenizationContext(
            tokens = tokens,
            new_content = [],
            partial_match_end_idx = 0,
            stats = stats,
            p_tag = p_tag,
        )

        handle_html_node(p_tag, tokenization_context)

        new_tag = BeautifulSoup("".join(x for x in tokenization_context.new_content if x), "html.parser").p

        assert new_tag is not None  # noqa: S101

        if stats.total_char > start_ch:
            new_tag["data-char-start"] = start_ch  # ty:ignore[invalid-assignment]

        p_tag.replace_with(new_tag)
        # print("new_tag", new_tag.prettify(), "\n")



def handle_html_node(node: PageElement, context: TokenizationContext) -> None:
    # print("node", node)
    # print("handle", context.new_content)
    if context.tokens_exhausted:
        context.new_content.append(str(node))
        return

    if not isinstance(node, NavigableString):
        if not node.get_text():
            context.new_content.append(str(node))
            return

        if not isinstance(node, Tag):
            return

        if node.name == "ruby":
            handle_ruby(node, context)
            return

        open_tag = re.search(r"<.*?>", str(node)).group()  # ty:ignore[unresolved-attribute]
        context.new_content.append(open_tag)
        context.open_tags.append(node)

        for child in node.children:
            handle_html_node(child, context)

        if context.open_tags and context.open_tags[-1] is node:
            context.new_content.append(f"</{node.name}>")
            context.open_tags.pop()

    else:
        handle_nav_string(node, context)


def handle_nav_string(node: NavigableString, context: TokenizationContext) -> bool:
        i = 0
        starting_token = context.curr_token
        if context.partial_match_end_idx > 0:
            idx_increment = min(len(node), len(context.curr_token.inflection)-context.partial_match_end_idx)
            if node.startswith(context.curr_token.inflection[context.partial_match_end_idx:context.partial_match_end_idx+idx_increment]):
                context.new_content.append(node[:idx_increment])
                context.partial_match_end_idx += idx_increment
                if context.partial_match_end_idx == len(context.curr_token.inflection):
                    if node.parent is context.p_tag or node.parent.name == "ruby":  # ty:ignore[unresolved-attribute]
                        context.new_content.append("</span>")
                    else:
                        context.new_content.append(f"</{node.parent.name}>")  # ty:ignore[unresolved-attribute]
                        context.new_content.append("</span>")
                        if len(node) > idx_increment:
                            open_tag = re.search(r"<.*?>", str(node.parent)).group()  # ty:ignore[unresolved-attribute]
                            context.new_content.append(open_tag)
                        else:
                            context.open_tags.pop()
                    # context.curr_token = next(context.tokens, None)
                    context.next_token()
                    context.partial_match_end_idx = 0
                    i = idx_increment
                    if context.tokens_exhausted:
                        context.new_content.append(node[i:])
                        return True
                else:
                    return False
        # print(f"{i = }")
        while i < len(node):
            # print(f"{i = }", context.new_content)
            curr_text = node[i:]
            match_idx = curr_text.find(context.curr_token.inflection)
            # print(f"{curr_text = }, {match_idx = }, {curr_text[:match_idx] = }")
            if match_idx < 0:
                for end in range(len(context.curr_token.inflection)-1, 0, -1):
                    if curr_text.endswith(context.curr_token.inflection[:end]):
                        context.partial_match_end_idx = end
                        context.stats.total_tokens += 1
                        context.stats.total_char += len(context.curr_token.inflection)

                        unmatched_text = curr_text[:-end]
                        if unmatched_text:
                            context.new_content.append(unmatched_text)

                        if node.parent is context.p_tag or node.parent.name == "ruby":  # ty:ignore[unresolved-attribute]
                            context.new_content.append(f'<span class="tok-{context.curr_token.lemma} status-underline" data-tok={context.stats.total_tokens}>')
                            context.new_content.append(context.curr_token.inflection[:end])
                        else:
                            open_tag = re.search(r"<.*?>", str(node.parent)).group()  # ty:ignore[unresolved-attribute]

                            if not unmatched_text:
                                context.new_content.pop()
                                close_tag = ""
                            else:
                                close_tag = f"</{node.parent.name}>" # ty:ignore[unresolved-attribute]

                            context.new_content.append(f'{close_tag}<span class="tok-{context.curr_token.lemma} status-underline" data-tok={context.stats.total_tokens}>')
                            context.new_content.append(f"{open_tag}{context.curr_token.inflection[:end]}")
                        return False
                context.new_content.append(curr_text)
                return False

            context.new_content.append(curr_text[:match_idx])

            context.stats.total_tokens += 1
            context.stats.total_char += len(context.curr_token.inflection)
            context.new_content.append(
                f'<span class="tok-{context.curr_token.lemma} status-underline" data-tok={context.stats.total_tokens}>{context.curr_token.inflection}</span>'
            )

            i += match_idx + len(context.curr_token.inflection)
            # context.curr_token = next(context.tokens, None)
            context.next_token()

            if context.tokens_exhausted:
                context.new_content.append(node[i:])
                return True

        return context.curr_token != starting_token


def handle_ruby(node: Tag, context: TokenizationContext):
    open_tag_idx = -1

    rt: list[str] = []

    for child in node.children:
        if isinstance(child, Tag) and child.name in {"rt", "rp"}:
            continue

        starting_token = context.curr_token
        mid_token = context.partial_match_end_idx > 0

        if open_tag_idx < 0:
            open_tag_idx = len(context.new_content)
            context.new_content.append("<ruby>")

        if isinstance(child.next_sibling, Tag) and child.next_sibling.name == "rt":
            rt.append(child.next_sibling.get_text())

        handle_html_node(child, context)

        if starting_token != context.curr_token:
            if mid_token:
                context.new_content.insert(-1, f"<rt>{"".join(rt)}</rt>")
                context.new_content.insert(-1, "</ruby>")
            else:
                context.new_content.append(f"<rt>{"".join(rt)}</rt>")
                context.new_content.append("</ruby>")

            rt = []
            open_tag_idx = -1
            mid_token = False

    if open_tag_idx >= 0:
        if not mid_token:
            context.new_content.pop(open_tag_idx)
            for i in range(open_tag_idx, len(context.new_content)):
                if "data-tok" in context.new_content[i]:
                    context.new_content.insert(i+1, "<ruby>")
        context.new_content.append(f"<rt>{"".join(rt)}</rt></ruby>")




if __name__ == "__main__":
    # from pydantic import RootModel
    # Books = RootModel[list[Book]]
    with SessionLocal() as db:
        books = []
        for i, test_book in enumerate(Path("test_epubs").iterdir()):
            print(i, test_book)
            # book = process_ebub(test_book, i+1)
            try:
                book = process_ebub(test_book, db)
                books.append(book)
            except Exception as e:  # noqa: BLE001
                print(e)

    # Path("test_epub.json").write_text(Books(books).model_dump_json(indent=2))

