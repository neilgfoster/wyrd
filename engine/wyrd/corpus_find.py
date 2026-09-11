"""Corpus index retrieval: the query layer over the five indexes (#357).

docs/design/26-corpus-index.md, "Retrieval": five indexes exist to answer a question by its
shape (#354's `documents.json`/`nouns.json`, #355's `terms.json`/`tables.json`, #356's
`scenarios.json`) -- this module is the `wyrd find ...` layer that actually queries them. "Every
result returns doc + offset, so the next step is always a bounded read of the surrounding
passage rather than loading a whole book into context. That bounded read is the point."

Five pure functions, no I/O, and deliberately no import of #354/#355/#356 -- this module reads
the dict/list shapes those modules already produce, the same decoupling `holding.py` (#337)
established toward `threat.py`: a query layer over a shape, not a hard dependency on the
producer.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def find_noun(nouns_index: dict, name: str) -> list[dict]:
    """Every occurrence of `name`, flattened to one `{"doc", "offset"}` entry per offset
    (FR-001). `[]` for an unmatched name or an empty index (FR-006)."""
    return [
        {"doc": posting["doc"], "offset": offset}
        for posting in nouns_index.get(name, [])
        for offset in posting["offsets"]
    ]


def find_rule(terms_index: dict, term: str) -> list[dict]:
    """Every posting for `term`, `definition`-ranked entries first, stable otherwise (FR-002)."""
    postings = terms_index.get(term.lower(), [])
    return sorted(postings, key=lambda posting: posting["rank"] != "definition")


def find_table(
    tables_index: list[dict], dice: str | None = None, about: str | None = None
) -> list[dict]:
    """Filter `tables_index` by `dice` (exact) and/or `about` (case-insensitive substring of
    `caption`) (FR-003). A `None` caption never matches a non-`None` `about`."""
    results = tables_index
    if dice is not None:
        results = [record for record in results if record["dice"] == dice]
    if about is not None:
        needle = about.lower()
        results = [
            record
            for record in results
            if record.get("caption") is not None and needle in record["caption"].lower()
        ]
    return list(results)


def find_scenario(scenarios_index: list[dict], **filters) -> list[dict]:
    """Filter `scenarios_index` by exact match on each `filters` key against the record's own
    field (FR-004). `setting_in`, if given, checks membership in the record's `settings` list
    instead of an exact-match field."""
    setting_in = filters.pop("setting_in", None)
    results = scenarios_index
    for key, value in filters.items():
        results = [record for record in results if record.get(key) == value]
    if setting_in is not None:
        results = [record for record in results if setting_in in record.get("settings", [])]
    return list(results)


def find_doc(
    documents_index: list[dict], work: str | None = None, issue: str | None = None
) -> list[dict]:
    """Filter `documents_index` by `work` (matched against `system`) and `issue` (matched
    against `edition`), returning `{"doc": id}` -- no offset (FR-005)."""
    results = documents_index
    if work is not None:
        results = [record for record in results if record["system"] == work]
    if issue is not None:
        results = [record for record in results if record["edition"] == issue]
    return [{"doc": record["id"]} for record in results]
