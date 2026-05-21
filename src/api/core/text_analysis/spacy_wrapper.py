from typing import Literal, overload
from collections.abc import Iterable, Iterator
import spacy
# from spacy.cli import download
from api.db.models.core import Morpheme
from api.db.models.texthooker import LineToken

import re

import threading

analyzer: "SpacyAnalyzer | None" = None


punc_sym_regex = re.compile(r"[^\w\s]+")

class SpacyAnalyzer:
    # Japanese Tokenizer is not thread-safe
    # TODO: Test creating tokenizers for each thread
    LOCK: threading.Lock = threading.Lock()

    def __init__(self, model_name: str, *, blank: bool = False) -> None:
        self.model_name = model_name
        if blank:
            self.nlp = spacy.blank(model_name)
        else:
            self.nlp = spacy.load(model_name)

    def _parse(self, text:str, model: type[Morpheme] | type[LineToken] = Morpheme) -> Iterator[Morpheme | LineToken]:
        with SpacyAnalyzer.LOCK:
            doc = self.nlp(text)
        for token in doc:
            yield model(
                lemma=token.lemma_,
                inflection=token.text,
                pos=token.pos_,
                tag=token.tag_,
            )

    def _filtered_parse(self, text: str, pos_exclude: Iterable[str], model: type[Morpheme] | type[LineToken] = Morpheme) -> Iterator[Morpheme | LineToken]:
        with SpacyAnalyzer.LOCK:
            doc = self.nlp(text)
        for token in doc:

            if token.pos_ in pos_exclude:
                continue

            if punc_sym_regex.match(token.text) and token.pos_ not in ("PUNCT", "SYM"):
                if any(pos in pos_exclude for pos in ("PUNCT", "SYM")):
                    continue
                token.pos_ = "N/A"
                token.tag_ = "N/A"

            yield model(
                lemma=token.lemma_,
                inflection=token.text,
                pos=token.pos_,
                tag=token.tag_,
            )

    @overload
    def parse(self, text: str, pos_exclude: Iterable[str] | None = None, *, line_model:  Literal[False]) -> Iterator[Morpheme]:
        ...

    @overload
    def parse(self, text: str, pos_exclude: Iterable[str] | None = None, *, line_model:  Literal[True]) -> Iterator[LineToken]:
        ...

    def parse(self, text: str, pos_exclude: Iterable[str] | None = None, *, line_model: bool = False) -> Iterator[Morpheme | LineToken]:
        model = LineToken if line_model else Morpheme
        if pos_exclude is None:
            return self._parse(text, model)
        return self._filtered_parse(text, pos_exclude, model)



def get_analyzer() -> SpacyAnalyzer:
    global analyzer
    if analyzer is None:
        # analyzer = SpacyAnalyzer("ja_core_news_sm")
        # pretrained ja model failing at punctuation and sym, more testing needed
        analyzer = SpacyAnalyzer("ja", blank=True)
    return analyzer

def install_model(model_name:str) -> None:
    ...

def delete_model(model_name:str) -> None:
    ...

