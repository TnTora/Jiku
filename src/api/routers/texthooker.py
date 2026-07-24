from fastapi import APIRouter, status, Depends, HTTPException

from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.schemas.texthooker import LineCreate, LineResponse, LastSessionResponse, PresetRename, PresetCreate, PresetInfo, PresetUpdate

from api.db import get_db

from sqlalchemy import select, delete, distinct, func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from api.db.models.texthooker import Line, LineLineToken, LineToken, Preset
from api.db.models.core import AnkiNoteMorpheme, AnkiNote, Morpheme

from typing import Annotated

import re

router = APIRouter()

#-------------------------------------------------------------------------------
# utility functions to add whitespace to the new line in order to make
# reconstructing text input in the frontend easier after tokenization with spacy

def increase_whitespace(match: re.Match) -> str:
    return " " + match.group(0)

def correct_line_whitespace(line: str) -> str:
    return re.sub(r"(?<!\s) \s*", increase_whitespace, line)

#-------------------------------------------------------------------------------

@router.get("/last_session", response_model=LastSessionResponse)
def last_session(
    db: Annotated[Session, Depends(get_db)],
    preset: str | None,
):
    preset = preset or "Default"
    lines = db.execute(
        select(Line).where(Line.preset == preset).order_by(Line.date_added)
    ).scalars().all()

    #TODO: Add filter for preset name
    status_result = db.execute(
        select(Morpheme.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, Morpheme.inflection == AnkiNoteMorpheme.morph_inflection)
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .where(Morpheme.lemma.in_(select(LineToken.lemma).distinct()))
        .group_by(Morpheme.lemma)
    )

    status_map = {lemma: status for lemma, status in status_result}  # noqa: C416

    return {"lines": lines, "status_map": status_map}

@router.post(
    "/new_line",
    response_model=LineResponse,
    status_code=status.HTTP_201_CREATED
)
def add_new_line(line: LineCreate, db: Annotated[Session, Depends(get_db)]):
    new_line = Line(text=line.text, preset=line.preset)
    db.add(new_line)
    db.flush()
    db.refresh(new_line)

    analyzer = get_analyzer()
    tokens = []
    llts = []

    for i, tok in enumerate(analyzer.parse(correct_line_whitespace(line.text), line_model=True, skip_brackets=False)):
        tokens.append({
            "lemma": tok.lemma,
            "inflection": tok.inflection,
            "pos": tok.pos,
            "tag": tok.tag,
        })

        llts.append({
            "line_id":new_line.id,
            "token_inflection":tok.inflection,
            "order_ref":i,
        })

    db.execute(
        insert(LineToken).on_conflict_do_nothing(),
        tokens,
    )
    db.flush()

    db.execute(
        insert(LineLineToken).on_conflict_do_nothing(),
        llts,
    )

    db.commit()

    status_result = db.execute(
        select(LineToken.lemma, func.max(AnkiNote.status))
        .join(AnkiNoteMorpheme, (LineToken.inflection == AnkiNoteMorpheme.morph_inflection) & (LineToken.inflection.in_({tok["inflection"] for tok in tokens})))
        .join(AnkiNote, AnkiNote.nid == AnkiNoteMorpheme.note_id)
        .group_by(LineToken.lemma)
    )

    status_map = {lemma: status for lemma, status in status_result}  # noqa: C416

    return {"id": new_line.id, "text": new_line.text, "date_added": new_line.date_added, "tokens": tokens, "line_status_map": status_map}


@router.delete("/line/{id}")
def delete_line(id: int, db: Annotated[Session, Depends(get_db)]):  # noqa: A002
    line = db.execute(select(Line).where(Line.id == id)).scalar()

    if line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")

    db.delete(line)
    db.flush()

    db.execute(
        delete(LineToken).where(LineToken.inflection.not_in(select(distinct(LineLineToken.token_inflection))))
    )

    db.commit()


@router.delete("/clear_lines/{preset}")
def clear_lines(preset:str, db: Annotated[Session, Depends(get_db)]):
    db.execute(
        delete(Line)
        .where(Line.preset == preset)
    )
    db.flush()
    db.execute(
        delete(LineToken)
        .where(LineToken.inflection.not_in(select(LineLineToken.token_inflection)))
    )
    # db.execute(delete(LineLineToken))
    db.commit()


@router.get("/presets", response_model=list[str])
def get_presets(db:Annotated[Session, Depends(get_db)]):
    presets = db.execute(
        select(Preset.name)
    ).scalars().all()

    if not presets:
        default_preset = Preset(
            name="Default",
            ws_url="ws://localhost:6677"
        )
        db.add(default_preset)
        db.commit()
        return ["Default"]

    return presets


@router.get("/presets_info", response_model=list[PresetInfo])
def get_presets_info(db:Annotated[Session, Depends(get_db)]):
    presets = db.execute(
        select(Preset)
    ).scalars().all()

    if not presets:
        default_preset = Preset(
            name="Default",
            ws_url="ws://localhost:6677"
        )
        db.add(default_preset)
        db.commit()
        return [default_preset]

    return presets


@router.get("/preset_info/{name}", response_model=list[PresetInfo])
def get_preset_info(name: str, db:Annotated[Session, Depends(get_db)]):
    preset = db.execute(
        select(Preset).where(Preset.name == name)
    ).scalar()

    if not preset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    return preset


@router.put("/update_preset")
def update_preset(data: PresetUpdate, db:Annotated[Session, Depends(get_db)]):
    preset = db.execute(
        select(Preset).where(Preset.name==data.name)
    ).scalar()

    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    preset.ws_url = data.ws_url
    db.commit()


@router.post("/add_preset")
def add_preset(data: PresetCreate, db:Annotated[Session, Depends(get_db)]):
    preset = db.execute(
        select(Preset).where(Preset.name==data.name)
    ).scalar()

    if preset:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{data.name} preset already exists")

    new_preset = Preset(
        name=data.name,
        ws_url=data.ws_url
    )
    db.add(new_preset)
    db.commit()


@router.put("/rename_preset")
def rename_preset(data: PresetRename, db:Annotated[Session, Depends(get_db)]):
    preset = db.execute(
        select(Preset).where(Preset.name==data.old_name)
    ).scalar()

    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    preset.name = data.new_name

    db.execute(
        update(Line)
        .where(Line.preset == data.old_name)
        .values(preset=data.new_name)
    )
    db.commit()


@router.delete("/delete_preset/{name}")
def delete_preset(name: str, db:Annotated[Session, Depends(get_db)]):
    preset = db.execute(
        select(Preset).where(Preset.name==name)
    ).scalar()

    if preset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")

    db.delete(preset)
    db.commit()

#TODO: @router.put("/update_line") or patch
