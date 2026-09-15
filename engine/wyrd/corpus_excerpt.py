"""Corpus excerpt retrieval: the bounded read after a doc+offset query (#397).

`docs/design/26-corpus-index.md`, "Retrieval": "Every result returns doc + offset, so the next
step is always a bounded read of the surrounding passage rather than loading a whole book into
context. That bounded read is the point." `corpus_find.py` (#357) built the coordinate-lookup
half of that promise; this module is the read itself.

Deliberately a **separate** module from `corpus_find.py`, not an addition to it --
`corpus_find.py`'s own docstring states it is "deliberately no I/O." Resolving a `documents.json`
record's `path` field to an actual file on disk and reading it is I/O by definition, so it lives
here instead, leaving `corpus_find.py` untouched and still importable with zero filesystem access.

The path-derivation rule below (`setting_dir / "corpus" / <path with suffix changed to .txt>`) is
reimplemented from `tools/setting_build.py`'s own `corpus_text_path`, not imported from it --
`engine/` never imports from `tools/` (the reverse of this repo's existing dependency direction,
grep-verified against every `engine/wyrd/*.py` file). Both copies express the same one-line rule
that `documents.json`'s `path` field (a `library/`-relative path, `corpus_document.py`) already
commits every setting repo to.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_WINDOW = 400


def _corpus_text_path(setting_dir: Path, record_path: str) -> Path:
    """Where a document's extracted text lives: the same relative path under
    `setting_dir / "corpus"` as its `library/`-relative `path` field, suffix changed to `.txt`
    (mirrors `tools/setting_build.py`'s `corpus_text_path`, research.md)."""
    return setting_dir / "corpus" / Path(record_path).with_suffix(".txt")


def read_excerpt(
    documents_index: list[dict],
    setting: str,
    setting_dir: Path,
    doc: str,
    offset: int,
    window: int = DEFAULT_WINDOW,
) -> str | None:
    """The corpus text surrounding `offset` in document `doc`, `window` characters either side
    (FR-001, FR-003).

    Requires `setting` and only resolves a record belonging to it -- never across settings, the
    same rule every `corpus_find.py` function already follows (FR-002). Returns `None`, never
    raises, for every failure mode FR-004 names: an unknown `doc` id, a `doc` that belongs to a
    different setting, a missing or unreadable corpus text file, a negative `offset`, or an
    `offset` at or past the end of the document's text. Deterministic (FR-005): the same inputs
    always read the same file and slice the same range.
    """
    record = next(
        (r for r in documents_index if r.get("id") == doc and r.get("setting") == setting),
        None,
    )
    if record is None:
        return None

    text_path = _corpus_text_path(setting_dir, record["path"])
    try:
        text = text_path.read_text(encoding="utf-8")
    except OSError:
        return None

    if offset < 0 or offset >= len(text):
        return None

    return text[max(0, offset - window) : offset + window]
