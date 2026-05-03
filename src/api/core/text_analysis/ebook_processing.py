import re
from collections.abc import Iterator
from datetime import datetime
from os import getenv
from pathlib import Path

import ebooklib
import tinycss2

# from spacy_wrapper import get_analyzer
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
from ebooklib import epub
from pydantic import BaseModel, ConfigDict, Field
from tinycss2.ast import IdentToken, LiteralToken, QualifiedRule

from api.schemas.books import (
    Book,
    BookMetadata,
    Section,
    BookStats,
    TocItem,


)

from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.schemas.core import Morpheme

config_base = getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"
config_path.mkdir(parents=True, exist_ok=True)


def process_ebub(filepath: Path, book_id) -> Book:
    book = epub.read_epub(filepath)
    base_path = config_path / Path(f"books/{book_id}/")
    base_path.mkdir(parents=True, exist_ok=True)
    (base_path / "stylesheets").mkdir(parents=True, exist_ok=True)
    (base_path / "content").mkdir(parents=True, exist_ok=True)
    (base_path / "images").mkdir(parents=True, exist_ok=True)

    sections: dict[str, Section] = {}
    spine: list[str] = [section_name for section_name, linear in book.spine if linear]
    toc: list[TocItem] = [TocItem(title=link.title, section=Path(link.href).stem) for link in book.toc]
    stats = BookStats()

    stylesheets = set()

    for stylesheet in book.get_items_of_type(ebooklib.ITEM_STYLE):
        filename = Path(stylesheet.get_name()).name
        process_stylesheet(base_path / "stylesheets" / filename, stylesheet.get_content())

    section_number = 0

    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        filename = Path(doc.get_name()).name
        print(filename)

        section: Section = process_html_content(base_path / "content" / filename, doc.content, book_id, stats)
        spine_key = Path(doc.get_name()).stem
        sections[spine_key] = section

        if spine_key in spine:
            section.number = section_number
            section_number += 1

        stylesheets.update(section.stylesheets)

    metadata = BookMetadata(
        title=book.get_metadata("DC", "title")[0][0],
        raw=book.metadata
    )

    processed_book = Book(
        id=book_id,
        sections=sections,
        stylesheets=list(stylesheets),
        spine=spine,
        toc=toc,
        metadata=metadata,
        original_file=filepath.name,
        # static_url="jiku://",
        static_url="http://127.0.0.1:8000/static/books",
        stats=stats
    )

    return processed_book


def process_stylesheet(filepath: Path, content: bytes):
    print(filepath)
    rules, _ = tinycss2.parse_stylesheet_bytes(content)

    temp_prelude = tinycss2.parse_stylesheet(".jiku-book-container .jiku-book-body.jiku-book-html{}")[0].prelude
    book_container_class = temp_prelude[:3]
    new_body_class = temp_prelude[3:5]
    new_html_class = temp_prelude[5:7]

    for rule in rules:
        if isinstance(rule, QualifiedRule):
            for i, tok in enumerate(rule.prelude):
                if isinstance(tok, IdentToken):
                    if tok.lower_value == "html":
                        rule.prelude[i:i+1] = new_html_class
                    elif tok.lower_value == "body":
                        rule.prelude[i:i+1] = new_body_class
                elif isinstance(tok, LiteralToken) and tok.value == ",":
                    rule.prelude[i+1:i+1] = book_container_class
            rule.prelude[0:0] = book_container_class

    filepath.write_text(tinycss2.serialize(rules))



def process_html_content(filepath: Path, content: bytes, book_id: int, stats: BookStats) -> Section:
    soup = BeautifulSoup(content, "html.parser")
    section_stylesheets = [Path(link["href"]).name for link in soup.find_all("link")]

    if soup.head:
        soup.head.decompose()

    html_tag = soup.html
    if html_tag is not None:
        html_tag.attrs = {key: val for key, val in html_tag.attrs.items() if key in {"class", "id"}}

        if html_tag.has_attr("class"):
            html_tag["class"].append("jiku-book-html")
        else:
            html_tag["class"] = ["jiku-book-html"]

        html_tag.name = "div"

    body_tag = soup.body
    if body_tag is not None:
        if body_tag.has_attr("class"):
            body_tag["class"].append("jiku-book-body")
        else:
            body_tag["class"] = ["jiku-book-body"]

        body_tag.name = "div"

    for child in soup.children:
        if not isinstance(child, Tag):
            child.decompose()

    for img in soup.find_all("img", src=True):
        filename = Path(img["src"]).name
        # img["src"] = f"jiku://books/{book_id}/images/{filename}"
        img["src"] = f"http://127.0.0.1:8000/static/books/{book_id}/images/{filename}"


    section = Section(
        key=filepath.stem,
        stylesheets = section_stylesheets,
        filename=filepath.name,
        start_ch=stats.total_char+1,
        start_tok=stats.total_tokens+1,
    )

    content_tokenization(soup, stats)

    filepath.write_text(str(soup))

    return section


class TokenizationContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    tokens: Iterator[Morpheme]
    new_content: list[str] = []
    curr_token: Morpheme | None
    partial_match_end_idx: int
    stats: BookStats
    p_tag: Tag


def content_tokenization(soup: BeautifulSoup, stats: BookStats):
    analyzer = get_analyzer()

    p_tags = soup.find_all("p")
    for p_tag in p_tags:
        p_text = p_tag.get_text()

        if not p_text:
            continue

        tokens = analyzer.parse(p_text, pos_exclude={"SPACE", "PUNCT", "NUM", "SYM", "X"})
        # print(f"{tokens}, {type(tokens)}")
        # print(p_tag, "\n")
        start_ch = stats.total_char
        # original_attrs = p_tag.attrs

        tokenization_context = TokenizationContext(
            tokens = tokens,
            new_content = [],
            curr_token = next(tokens, None),
            partial_match_end_idx = 0,
            stats = stats,
            p_tag = p_tag,
        )

        handle_html_node(p_tag, tokenization_context)

        new_tag = BeautifulSoup("".join(x for x in tokenization_context.new_content if x), "html.parser").p

        # new_tag.attrs = original_attrs
        if stats.total_char > start_ch:
            new_tag["data-char-start"] = start_ch

        p_tag.replace_with(new_tag)
        # print("new_tag", new_tag.prettify(), "\n")



def handle_html_node(node: PageElement, context: TokenizationContext) -> None:
    # print("node", node)
    # print("handle", context.new_content)
    if context.curr_token is None:
        context.new_content.append(str(node))
        return

    if not isinstance(node, NavigableString):
        if not node.get_text():
            context.new_content.append(str(node))
            return

        if node.name == "ruby":
            handle_ruby(node, context)
            return

        open_tag = re.search(r"<.*?>", str(node)).group()
        context.new_content.append(open_tag)

        for child in node.children:
            handle_html_node(child, context)

        context.new_content.append(f"</{node.name}>")

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
                    if node.parent is context.p_tag or node.parent.name == "ruby":
                        context.new_content.append("</span>")
                    else:
                        open_tag = re.search(r"<.*?>", str(node.parent)).group()
                        context.new_content.append(f"</{node.name}></span>{open_tag}")
                    context.curr_token = next(context.tokens, None)
                    context.partial_match_end_idx = 0
                    i = idx_increment
                    if context.curr_token is None:
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
                        context.new_content.append(curr_text[:-end])
                        if node.parent is context.p_tag or node.parent.name == "ruby":
                            context.new_content.append(f'<span class="tok-{context.curr_token.lemma} status-underline" data-tok={context.stats.total_tokens}>')
                            context.new_content.append(context.curr_token.inflection[:end])
                        else:
                            open_tag = re.search(r"<.*?>", str(node.parent)).group()
                            context.new_content.append(f'</{node.parent.name}><span class="tok-{context.curr_token.lemma} status-underline" data-tok={context.stats.total_tokens}>')
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
            context.curr_token = next(context.tokens, None)

            if context.curr_token is None:
                context.new_content.append(node[i:])
                return True

        return context.curr_token != starting_token


def handle_ruby(node: Tag, context: TokenizationContext):
    open_tag_idx = -1

    rt: list[str] = []

    for child in node.children:
        if isinstance(child, NavigableString):
            if open_tag_idx < 0:
                open_tag_idx = len(context.new_content)
                context.new_content.append("<ruby>")

            if child.next_sibling and child.next_sibling.name == "rt":
                rt.append(child.next_sibling.get_text())

            completed_token = handle_nav_string(child, context)

            if completed_token:
                context.new_content.append(f"<rt>{"".join(rt)}</rt>")
                rt = []
                context.new_content.append("</ruby>")
                open_tag_idx = -1

    if open_tag_idx >= 0:
        context.new_content.pop(open_tag_idx)
        for i in range(open_tag_idx, len(context.new_content)):
            if "data-tok" in context.new_content[i]:
                context.new_content.insert(i+1, "<ruby>")
        context.new_content.append(f"<rt>{"".join(rt)}</rt></ruby>")




if __name__ == "__main__":
    book = process_ebub(Path("test.epub"), 1)
    print(book.model_dump_json(indent=2))
    Path("test_epub.json").write_text(book.model_dump_json(indent=2))
