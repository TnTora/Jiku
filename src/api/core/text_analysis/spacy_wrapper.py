from collections.abc import Iterable, Iterator
import spacy
from spacy.cli import download
from api.schemas.core import Morpheme

import threading

analyzer: "SpacyAnalyzer | None" = None


class SpacyAnalyzer:
    # Japanese Tokenizer is not thread-safe
    # TODO: Test creating tokenizers for each thread
    LOCK: threading.Lock = threading.Lock()

    def __init__(self, model_name: str, blank: bool = False) -> None:
        self.model_name = model_name
        if blank:
            self.nlp = spacy.blank(model_name)
        else:
            self.nlp = spacy.load(model_name)

    def _parse(self, text:str) -> Iterator[Morpheme]:
        with SpacyAnalyzer.LOCK:
            doc = self.nlp(text)
        for token in doc:
            yield Morpheme(
                lemma=token.lemma_,
                inflection=token.text,
                pos=token.pos_,
                tag=token.tag_,
            )

    def _filtered_parse(self, text: str, pos_exclude: Iterable[str]) -> Iterator[Morpheme]:
        with SpacyAnalyzer.LOCK:
            doc = self.nlp(text)
        for token in doc:

            if token.pos_ in pos_exclude:
                continue

            yield Morpheme(
                lemma=token.lemma_,
                inflection=token.text,
                pos=token.pos_,
                tag=token.tag_,
            )

    def parse(self, text: str, pos_exclude: Iterable[str] | None = None) -> Iterator[Morpheme]:
        if pos_exclude is None:
            return self._parse(text)
        return self._filtered_parse(text, pos_exclude)



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

