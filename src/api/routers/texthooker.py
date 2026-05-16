from fastapi import APIRouter, status, Depends

from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.schemas.texthooker import LineCreate, LineResponse, LastSessionResponse

from api.db import get_db

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from api.db.models.texthooker import Line, LineLineToken, LineToken
from api.db.models.core import AnkiNoteMorpheme, AnkiNote

from typing import Annotated

import re

router = APIRouter()

morphemes = []

mock_session_map = {
    "無償": "known",
    "で": "known",
    "こと": "known",
    "宝泉": "known",
    "くん": "known",
    "は": "known",
    "に": "known",
    "ない": "known",
}

line1 = ["無償", "で", "手助け", "する", "こと", "を", "宝泉", "くん", "は", "絶対", "に", "認め","ない", "です", "。"]
test_lines = [
    "無償で手助けすることを宝泉くんは絶対に認めないです。",
    "どうして？ 彼には何のデメリットもないはずよ。",
    "それでも　やはり宝泉くんは認めないと思います。"
]

# analyzer = get_analyzer()
# mock_session_lines = [{"id": i, "text": line, "tokens": list(analyzer.parse(line, line_model=True))} for i, line in enumerate(test_lines)]

#-------------------------------------------------------------------------------
# utility functions to add whitespace to the new line in order to make
# reconstructing text input in the frontend easier after tokenization with spacy

def increase_whitespace(match: re.Match) -> str:
    return " " + match.group(0)

def correct_line_whitespace(line: str) -> str:
    return re.sub(r"(?<!\s) \s*", increase_whitespace, line)

#-------------------------------------------------------------------------------

@router.get("/last_session", response_model=LastSessionResponse)
def last_session(db: Annotated[Session, Depends(get_db)]):
    lines = db.execute(
        select(Line)
    ).scalars().all()

    status_result = db.execute(
        select(LineToken.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, LineToken.inflection == AnkiNoteMorpheme.morph_inflection)
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .group_by(LineToken.lemma)
    )

    status_map = {lemma: status for lemma, status in status_result}  # noqa: C416

    return {"lines": lines, "status_map": status_map}

@router.post(
    "/new_line",
    response_model=LineResponse,
    status_code=status.HTTP_201_CREATED
)
def add_new_line(line: LineCreate, db: Annotated[Session, Depends(get_db)]):
    new_line = Line(text=line.text)
    db.add(new_line)
    db.flush()
    db.refresh(new_line)

    analyzer = get_analyzer()
    tokens = []
    status_map = {}

    for i, tok in enumerate(analyzer.parse(correct_line_whitespace(line.text), line_model=True)):
        tokens.append(tok)

        db.add(LineLineToken(
            line_id=new_line.id,
            token_inflection=tok.inflection,
            order_ref=i,
        ))

        if tok.inflection in mock_session_map:
            status_map[tok.inflection] = mock_session_map[tok.inflection]

    db.add_all(tokens)
    db.commit()

    status_result = db.execute(
        select(LineToken.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, LineToken.inflection == AnkiNoteMorpheme.morph_inflection and LineToken.inflection.in_(set(tok.inflection for tok in tokens)))
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .group_by(LineToken.lemma)
    )

    status_map = {lemma: status for lemma, status in status_result}  # noqa: C416

    return {"id": new_line.id, "text": new_line.text, "tokens": tokens, "status_map": status_map}

# @router.put("/update_line") or patch
# @router.delete("/delete_line")
# @router.delete("/clear_lines")
