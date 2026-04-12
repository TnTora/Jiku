from fastapi import APIRouter, status
from api.core.text_analysis.utils import Morpheme
from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.schemas.texthooker import LineCreate, LineResponse, LastSessionResponse

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

analyzer = get_analyzer()
mock_session_lines = [{"id": i, "tokens": list(analyzer.parse(line))} for i, line in enumerate(test_lines)]

#-------------------------------------------------------------------------------
# utility functions to add whitespace to the new line in order to make
# reconstructing text input in the frontend easier after tokenization with spacy

def increase_whitespace(match: re.Match) -> str:
    return " " + match.group(0)

def correct_line_whitespace(line: str) -> str:
    return re.sub(r"(?<!\s) \s*", increase_whitespace, line)

#-------------------------------------------------------------------------------

@router.get("/last_session", response_model=LastSessionResponse)
def last_session():
    return {"lines": mock_session_lines, "status_map": mock_session_map}

@router.post(
    "/new_line",
    response_model=LineResponse,
    status_code=status.HTTP_201_CREATED
)
def add_new_line(line: LineCreate):
    analyzer = get_analyzer()
    tokens = []
    status_map = {}

    for tok in analyzer.parse(correct_line_whitespace(line.text)):
        tokens.append(tok)
        if tok.inflection in mock_session_map:
            status_map[tok.inflection] = mock_session_map[tok.inflection]

    tmp_id = mock_session_lines[-1]["id"]+1 if mock_session_lines else 1
    mock_session_lines.append({"id": tmp_id, "tokens": tokens})
    return {"id": tmp_id, "tokens": tokens, "status_map": status_map}

# @router.put("/update_line") or patch
# @router.delete("/delete_line")
# @router.delete("/clear_lines")
