"""Bibliographic and concordance indexes: documents.json and nouns.json (#354).

docs/design/26-corpus-index.md: of the five corpus indexes, these two are deterministic and
built once at ingest. `documents.json` is one record per extracted source -- id, path, system,
edition, type, page count, extraction method, and an OCR-confidence estimate. `nouns.json` is
the concordance: every proper noun mapped to where it appears, which is "what makes a long
chronicle work" -- a name a GM half-remembers is findable by its canonical mention rather than
re-read from scratch.

This tooling never fetches, stores, or reads source material itself (CLAUDE.md) -- a setting
repo supplies already-extracted text as a plain string; every function here is pure, no I/O.

Two things worth being explicit about (research.md):

- `ocr_confidence` is a stdlib-only word-shape heuristic, not a real dictionary-word ratio --
  no word list ships with this repo (no third-party dependency, per this codebase's stdlib-only
  convention), so this is the closest deterministic proxy available.
- The concordance's sentence-boundary detection is a plain `.`/`!`/`?`-plus-whitespace rule, not
  a full NLP sentence splitter -- matching the design document's own "deterministic" and
  "one pass" framing for these indexes.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import re

_WORD_TOKEN = re.compile(r"\S+")
_PLAUSIBLE_WORD = re.compile(r"^[A-Za-z]{2,20}$")
_IMPLAUSIBLE_RUN = re.compile(r"([bcdfghjklmnpqrstvwxyz])\1{2,}|([aeiou])\2{2,}", re.IGNORECASE)

# A small, fixed stop list of common English words -- not exhaustive (research.md).
_STOP_WORDS = frozenset(
    {
        "the", "a", "an", "and", "but", "or", "nor", "for", "yet", "so",
        "when", "where", "while", "if", "then", "than", "that", "this",
        "these", "those", "it", "its", "he", "she", "they", "we", "you",
        "i", "his", "her", "their", "our", "your", "my", "there", "here",
        "what", "who", "whom", "which", "as", "at", "by", "in", "of",
        "on", "to", "with", "from", "into", "onto", "after", "before",
    }
)  # fmt: skip

_SENTENCE_BOUNDARY = re.compile(r"[.!?]\s+")


def ocr_confidence(text: str) -> float:
    """The fraction of `text`'s tokens matching a plausible-word shape (FR-002).

    `0.0` for empty text. A token counts as plausible when it is purely alphabetic, 2-20
    characters, and has no implausible consonant/vowel run (3+ of the same letter-class in a
    row) -- a cheap, stdlib-only proxy for "looks like a real word" (research.md).
    """
    tokens = _WORD_TOKEN.findall(text)
    if not tokens:
        return 0.0
    plausible = sum(
        1 for token in tokens if _PLAUSIBLE_WORD.match(token) and not _IMPLAUSIBLE_RUN.search(token)
    )
    return plausible / len(tokens)


def build_document_record(
    *,
    id: str,
    path: str,
    system: str,
    edition: str,
    document_type: str,
    page_count: int,
    extraction_method: str,
    text: str,
    setting: str,
) -> dict:
    """A bibliographic record for one extracted source (FR-001, FR-006)."""
    return {
        "id": id,
        "path": path,
        "system": system,
        "edition": edition,
        "document_type": document_type,
        "page_count": page_count,
        "extraction_method": extraction_method,
        "ocr_confidence": ocr_confidence(text),
        "setting": setting,
    }


def _sentence_initial_positions(text: str) -> set[int]:
    """Character offsets where a new sentence begins: position 0, and every position right
    after a `.`/`!`/`?`-plus-whitespace boundary (research.md)."""
    positions = {0}
    for match in _SENTENCE_BOUNDARY.finditer(text):
        positions.add(match.end())
    return positions


def build_concordance(text: str, doc: str, setting: str) -> dict:
    """Map every capitalised, non-sentence-initial, non-stop-listed token to its occurrences
    in `text` (FR-003, FR-004, FR-005, FR-006)."""
    sentence_starts = _sentence_initial_positions(text)
    concordance: dict[str, dict] = {}
    for match in _WORD_TOKEN.finditer(text):
        token = match.group().strip(".,;:!?\"'()")
        if not token or not token[0].isupper():
            continue
        if token.lower() in _STOP_WORDS:
            continue
        if match.start() in sentence_starts:
            continue
        entry = concordance.setdefault(
            token, {"doc": doc, "setting": setting, "count": 0, "offsets": []}
        )
        entry["count"] += 1
        entry["offsets"].append(match.start())
    return {name: [entry] for name, entry in concordance.items()}


def merge_concordances(entries: list[dict]) -> dict:
    """Merge multiple single-document `build_concordance` outputs, keeping each document's own
    postings separate under the same name key (never summed across documents)."""
    merged: dict[str, list[dict]] = {}
    for concordance in entries:
        for name, postings in concordance.items():
            merged.setdefault(name, []).extend(postings)
    return merged
