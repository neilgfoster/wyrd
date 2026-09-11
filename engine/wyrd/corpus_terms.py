"""Curated term and structural table indexes: terms.json and tables.json (#355).

docs/design/26-corpus-index.md: two more of the five corpus indexes, both deterministic and
built once at ingest. `terms.json` is a small, curated mechanical vocabulary mapped to postings,
ranked by whether a hit looks like a definition or a passing mention -- "what are the Fear
rules?" is a lookup, not a grep through every mention. `tables.json` detects dice tables by
shape alone (runs of number/range-prefixed lines) -- "the most reusable content in the entire
library and the most annoying to find."

Like #354's `corpus_document.py`, this tooling never fetches, stores, or reads source material
itself (CLAUDE.md) -- a setting repo supplies already-extracted text as a plain string; every
function here is pure, no I/O.

Both heuristics are documented, cheap, stdlib-only proxies rather than a layout-aware parser
(research.md) -- matching `corpus_document.py`'s own `ocr_confidence` convention:

- "Near a heading" (terms) is a short, punctuation-final-free line within 2 lines before the
  occurrence.
- A table row is a leading number/range key followed by descriptive text; a *run* of 2+ such
  lines is a table (a single stray row-shaped line is not).
- Dice type is inferred purely from the run's own key values, not from nearby dice notation.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import re

CURATED_TERMS = frozenset(
    {"fear", "terror", "taint", "transformation", "critical", "career exit", "trauma", "fate"}
)

_HEADING_WINDOW = 2
_HEADING_MAX_LENGTH = 60
_ROW_PATTERN = re.compile(r"^\s*(\d{1,3})(?:-(\d{1,3}))?\s+\S")
_TWO_DIGIT_D66 = re.compile(r"^[1-6][1-6]$")


def _line_offsets(text: str) -> list[tuple[int, str]]:
    """`[(start_offset, line), ...]` for every line in `text` (newline-split, offsets preserved)."""
    lines = text.split("\n")
    offsets = []
    pos = 0
    for line in lines:
        offsets.append((pos, line))
        pos += len(line) + 1  # +1 for the stripped '\n'
    return offsets


def _is_heading_like(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    return len(stripped) < _HEADING_MAX_LENGTH and not stripped.endswith((".", "!", "?"))


def build_terms_index(text: str, doc: str, setting: str) -> dict:
    """Map every case-insensitive occurrence of a `CURATED_TERMS` entry to its posting,
    ranked `definition` when near a heading-like line, `mention` otherwise (FR-001, FR-002,
    FR-003, FR-007)."""
    lines = _line_offsets(text)
    index: dict[str, list[dict]] = {}
    for line_idx, (start, line) in enumerate(lines):
        for term in CURATED_TERMS:
            for match in re.finditer(re.escape(term), line, re.IGNORECASE):
                window = lines[max(0, line_idx - _HEADING_WINDOW) : line_idx]
                rank = (
                    "definition"
                    if any(_is_heading_like(candidate) for _, candidate in window)
                    else "mention"
                )
                index.setdefault(term, []).append(
                    {
                        "doc": doc,
                        "setting": setting,
                        "offset": start + match.start(),
                        "rank": rank,
                    }
                )
    return index


def _infer_dice(keys: list[tuple[int, int | None]]) -> str | None:
    """`keys` is `[(first, second_or_None), ...]` for a run's matched row keys (FR-006)."""
    if all(second is None and _TWO_DIGIT_D66.match(str(first)) for first, second in keys):
        if max(first for first, _ in keys) == 66:
            return "d66"
    endpoints = [second if second is not None else first for first, second in keys]
    top = max(endpoints)
    if top <= 6:
        return "d6"
    if top <= 10:
        return "d10"
    if top <= 100:
        return "d100"
    return None


def build_tables_index(text: str, doc: str, setting: str) -> list[dict]:
    """Detect runs of 2+ consecutive row-shaped lines as tables (FR-004, FR-005, FR-006,
    FR-007)."""
    lines = _line_offsets(text)
    tables = []
    run_start: int | None = None
    run_keys: list[tuple[int, int | None]] = []

    def _close_run(end_idx: int) -> None:
        nonlocal run_start
        if run_start is not None and len(run_keys) >= 2:
            caption = None
            for _, candidate in reversed(lines[:run_start]):
                if candidate.strip():
                    caption = candidate.strip()
                    break
            tables.append(
                {
                    "doc": doc,
                    "setting": setting,
                    "offset": lines[run_start][0],
                    "dice": _infer_dice(run_keys),
                    "row_count": len(run_keys),
                    "caption": caption,
                }
            )
        run_start = None
        run_keys.clear()

    for idx, (_, line) in enumerate(lines):
        match = _ROW_PATTERN.match(line)
        if match:
            if run_start is None:
                run_start = idx
            first = int(match.group(1))
            second = int(match.group(2)) if match.group(2) else None
            run_keys.append((first, second))
        else:
            _close_run(idx)
    _close_run(len(lines))

    return tables
