import re
import json
import urllib.request
import urllib.error

from api.core.text_analysis.spacy_wrapper import get_analyzer
from api.core.config import load_settings_from_db
from api.core.config.anki import AnkiSettings
from api.db import SessionLocal
from api.db.models.core import Morpheme, AnkiNote, AnkiNoteMorpheme, KnownStatus

from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert

from api.celery_worker import celery_app
from celery.contrib.abortable import AbortableTask

from typing import Any
from collections.abc import Iterable

import logging

logger = logging.getLogger("app_logger")


CLEANER = re.compile("<.*?>")


def cleanhtml(raw_html: str) -> str:
    cleantext = re.sub(CLEANER, "", raw_html)
    return cleantext


class AnkiError(Exception):

    def __init__(self, msg: str = "") -> None:
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return f"AnkiConnect: {self.msg}"



anki_settings: AnkiSettings = load_settings_from_db("anki")


def request(action: str, **params) -> dict[str, Any]:
    return {"action": action, "params": params, "version": 6}


def invoke(action: str, **params) -> Any:
    try:
        requestJson = json.dumps(request(action, **params)).encode("utf-8")
        response = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{anki_settings.port}", requestJson)))
        if len(response) != 2:  # noqa: PLR2004
            logger.error("AnkiConnect : response has an unexpected number of fields (%s, %s)", action, params)
            msg = f"response has an unexpected number of fields ({action = }, {params = })"
            raise AnkiError(msg)
        if "error" not in response:
            logger.error("AnkiConnect: response is missing required error field (%s, %s)", action, params)
            msg = f"response is missing required error field ({action = }, {params = })"
            raise AnkiError(msg)
        if "result" not in response:
            logger.error("AnkiConnect: response is missing required result field (%s, %s)", action, params)
            msg = f"response is missing required result field ({action = }, {params = })"
            raise AnkiError(msg)
        if response["error"] is not None:
            logger.error("AnkiConnect: %s (%s, %s)", response["error"], action, params)
            msg = f"{response["error"]} ({action = }, {params = })"
            raise AnkiError(msg)
        return response["result"]
    except (urllib.error.URLError, ConnectionResetError) as e:
        raise AnkiError("No Connection") from e


def get_media_dir() -> str:
    return invoke("getMediaDirPath")


def get_note_types() -> list[str]:
    return invoke("modelNames")


def get_note_types_fields(model_name: str) -> list[str]:
    return invoke("modelFieldNames", modelName=model_name)


def get_decks() -> list[str]:
    return invoke("deckNames")


def get_notes(deck: str = "", note_type: str = "", *, exclude_notes: Iterable[int] | None = None, extra_query: str = "") -> list[int]:
    exclude_query = f"-nid:{",".join([str(nid) for nid in exclude_notes])}" if exclude_notes else ""
    return invoke("findNotes", query=f'"deck:{deck}" "note:{note_type}" {exclude_query} {extra_query}')


def get_notes_from_query(query: str) -> list[int]:
    return invoke("findNotes", query=query)


def get_note_field(note_id: int, field: str) -> str:
    text = invoke("notesInfo", notes=[note_id])
    return cleanhtml(text[0]["fields"][field]["value"])


def get_notes_info(notes: list[int], field: str):
    result = invoke("notesInfo", notes=notes)
    for note in result:
        yield note["noteId"], cleanhtml(note["fields"][field]["value"])


def get_all_note_types_fields(names: list[str]) -> dict[str, list[str]]:
    results = invoke("findModelsByName", modelNames=names)
    fields_dict: dict[str, list[str]] = {result["name"]: [field["name"] for field in result["flds"]] for result in results}
    return fields_dict


def update_existing_notes() -> None:
    with SessionLocal() as db:
        stored_notes = db.execute(select(AnkiNote.nid)).scalars().all()

        if not stored_notes:
            return

        anki_notes = set()
        curr_notes_query = f"nid:{",".join([str(note) for note in stored_notes])}"
        # anki_notes = get_notes_from_query(curr_notes_query)

        for params in anki_settings.to_analyze:
            notes = get_notes(
                    params.deck,
                    params.note_type,
                    extra_query=curr_notes_query
                )
            anki_notes.update(notes)

        # Delete notes no longer found in Anki
        db.execute(
            delete(AnkiNote)
            .where(AnkiNote.nid.not_in(anki_notes))
        )

        # Delete corresponding rows from assosiaction table
        # db.execute(
        #     delete(AnkiNoteMorpheme)
        #     .where(AnkiNoteMorpheme.note_id.not_in(anki_notes))
        # )

        db.flush()

        # Delete morphs with no note associated to them
        db.execute(
            delete(Morpheme)
            .where(Morpheme.inflection.not_in(select(AnkiNoteMorpheme.morph_inflection)))
        )

        # Get notes that are still classified as new
        anki_notes = get_notes_from_query(f"{curr_notes_query} is:new")

        db.execute(
            update(AnkiNote)
            .where(AnkiNote.status == KnownStatus.NEW.value)
            .where(AnkiNote.nid.not_in(anki_notes))
            .values(status=KnownStatus.KNOWN.value)
        )

        db.commit()


@celery_app.task(bind=True, base=AbortableTask)
def update_morphemes_db(self) -> None:
    self.update_state(
        state="UPDATING NOTES",
        meta={
            "current_rule": -1,
            "total_rules": -1,
            "current_note": -1,
            "total_notes": -1
        }
    )
    update_existing_notes()
    analyzer = get_analyzer()
    with SessionLocal() as db:
        existing_morphs = set(db.execute(select(Morpheme.inflection)).scalars().all())
        total_rules = len(anki_settings.to_analyze) * 2
        current_rule = 0


        for params in anki_settings.to_analyze:
            msg = f"Analyzing: deck={params.deck}, note_type={params.note_type}, text_field={params.text_field}"
            logger.debug(msg)

            existing_notes = db.execute(select(AnkiNote.nid).where(AnkiNote.deck == params.deck)).scalars().all()

            for status in (KnownStatus.KNOWN, KnownStatus.NEW):
                notes = get_notes(
                    params.deck,
                    params.note_type,
                    exclude_notes=existing_notes,
                    extra_query=f"{"-" if status == KnownStatus.KNOWN else ""}is:new"
                )

                notes_count = len(notes)

                msg = f"Found {notes_count} notes."
                logger.debug(msg)

                morphemes = set()
                ankinote_morphemes = []

                current_rule += 1
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current_rule": current_rule,
                        "total_rules": total_rules,
                        "current_note": 0,
                        "total_notes": notes_count
                    }
                )

                for i, (note, text) in enumerate(get_notes_info(notes, params.text_field)):
                    print(f"{i+1}/{notes_count}, {text}")
                    if i % 50 == 0:
                        if self.is_aborted():
                            self.update_state(
                                state="CANCELLED",
                                meta={
                                    "current_rule": -1,
                                    "total_rules": -1,
                                    "current_note": -1,
                                    "total_notes": -1
                                }
                            )
                            return

                        self.update_state(
                            state="PROGRESS",
                            meta={
                                "current_rule": current_rule,
                                "total_rules": total_rules,
                                "current_note": i,
                                "total_notes": notes_count
                            }
                        )

                    db.add(AnkiNote(
                        nid=note,
                        deck=params.deck,
                        text_field=params.text_field,
                        status=status.value,
                    ))

                    note_morphs = set()
                    for morph in analyzer.parse(text, pos_exclude={"SPACE", "PUNCT", "SYM", "X"}, line_model=False):
                        if morph in note_morphs:
                            continue
                        note_morphs.add(morph)
                        ankinote_morphemes.append(AnkiNoteMorpheme(note_id=note, morph_inflection=morph.inflection))

                    morphemes.update(note_morphs)

                morphs_to_add = [
                    {"lemma": morph.lemma, "inflection": morph.inflection, "pos": morph.pos, "tag": morph.tag}
                    for morph in morphemes
                    if morph.inflection not in existing_morphs
                ]

                if morphs_to_add:
                    db.execute(
                        insert(Morpheme).on_conflict_do_nothing(),
                        [
                            {"lemma": morph.lemma, "inflection": morph.inflection, "pos": morph.pos, "tag": morph.tag}
                            for morph in morphemes
                            if morph.inflection not in existing_morphs
                        ]
                    )

                db.flush()

                db.add_all(ankinote_morphemes)

                if self.is_aborted():
                    self.update_state(
                        state="CANCELLED",
                        meta={
                            "current_rule": -1,
                            "total_rules": -1,
                            "current_note": -1,
                            "total_notes": -1
                        }
                    )
                    return

                db.commit()
                existing_morphs.update([morph.inflection for morph in morphemes])


if __name__ == "__main__":
    update_morphemes_db()
