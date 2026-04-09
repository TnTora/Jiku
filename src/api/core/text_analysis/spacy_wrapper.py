import spacy
from spacy.cli import download
from api.schemas.core import Morpheme

import threading

analyzer: "SpacyAnalyzer | None" = None


class SpacyAnalyzer:
    # Japanese Tokenizer is not thread-safe
    # TODO: Test creating tokenizers for each thread
    LOCK: threading.Lock = threading.Lock()

    def __init__(self, model_name:str) -> None:
        self.model_name = model_name
        self.nlp = spacy.load(model_name)

    def parse(self, text:str):
        with SpacyAnalyzer.LOCK:
            doc = self.nlp(text)
        for token in doc:
            yield Morpheme(
                lemma=token.lemma_,
                inflection=token.text,
                pos=token.pos_,
                tag=token.tag_,
            )


def get_analyzer() -> SpacyAnalyzer:
    global analyzer
    if analyzer is None:
        analyzer = SpacyAnalyzer("ja_core_news_sm")
    return analyzer

def install_model(model_name:str) -> None:
    ...

def delete_model(model_name:str) -> None:
    ...

