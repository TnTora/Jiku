from fastapi import APIRouter, status
from api.core.text_analysis.utils import Morpheme
from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.schemas.texthooker import LineCreate, LineResponse, LastSessionResponse

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
mock_session_lines = [list(analyzer.parse(line)) for line in test_lines]


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

    for tok in analyzer.parse(line.text):
        tokens.append(tok)
        if tok.inflection in mock_session_map:
            status_map[tok.inflection] = mock_session_map[tok.inflection]

    mock_session_lines.append(tokens)
    return {"tokens": tokens, "status_map": status_map}

# @router.put("/update_line") or patch
# @router.delete("/delete_line")
