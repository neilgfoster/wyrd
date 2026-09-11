"""Corpus index retrieval: the query layer over the five indexes (#357), setting-scoped (#364).

docs/design/26-corpus-index.md, "Retrieval": five indexes exist to answer a question by its
shape (#354's `documents.json`/`nouns.json`, #355's `terms.json`/`tables.json`, #356's
`scenarios.json`) -- this module is the `wyrd find ...` layer that actually queries them. "Every
result returns doc + offset, so the next step is always a bounded read of the surrounding
passage rather than loading a whole book into context. That bounded read is the point."

Every function requires a `setting` argument, filtered before any other criterion
(docs/design/21-parallel-chronicles.md: "the corpus is queried with the setting as a filter,
never unfiltered" -- a GM-contract MUST). Omitting it is a `TypeError`, not a silently-unscoped
query -- the strongest structural enforcement Python offers for "this is never optional"
(research.md). A record/posting carrying no `setting`/`settings` field at all never matches any
query, regardless of the value passed.

Five pure functions, no I/O, and deliberately no import of #354/#355/#356 -- this module reads
the dict/list shapes those modules already produce, the same decoupling `holding.py` (#337)
established toward `threat.py`: a query layer over a shape, not a hard dependency on the
producer.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def find_noun(nouns_index: dict, setting: str, name: str) -> list[dict]:
    """Every occurrence of `name` within `setting`, flattened to one `{"doc", "offset"}` entry
    per offset (FR-001). `[]` for an unmatched name, a non-matching setting, or an empty
    index."""
    return [
        {"doc": posting["doc"], "offset": offset}
        for posting in nouns_index.get(name, [])
        if posting.get("setting") == setting
        for offset in posting["offsets"]
    ]


def find_rule(terms_index: dict, setting: str, term: str) -> list[dict]:
    """Every posting for `term` within `setting`, `definition`-ranked entries first, stable
    otherwise (FR-001)."""
    postings = [
        posting
        for posting in terms_index.get(term.lower(), [])
        if posting.get("setting") == setting
    ]
    return sorted(postings, key=lambda posting: posting["rank"] != "definition")


def find_table(
    tables_index: list[dict], setting: str, dice: str | None = None, about: str | None = None
) -> list[dict]:
    """Filter `tables_index` to `setting`, then by `dice` (exact) and/or `about`
    (case-insensitive substring of `caption`) (FR-001). A `None` caption never matches a
    non-`None` `about`."""
    results = [record for record in tables_index if record.get("setting") == setting]
    if dice is not None:
        results = [record for record in results if record["dice"] == dice]
    if about is not None:
        needle = about.lower()
        results = [
            record
            for record in results
            if record.get("caption") is not None and needle in record["caption"].lower()
        ]
    return results


def find_scenario(scenarios_index: list[dict], setting: str, **filters) -> list[dict]:
    """Filter `scenarios_index` to records whose `settings` list contains `setting` (FR-002),
    then by exact match on each remaining `filters` key against the record's own field."""
    results = [record for record in scenarios_index if setting in record.get("settings", [])]
    for key, value in filters.items():
        results = [record for record in results if record.get(key) == value]
    return results


def find_doc(
    documents_index: list[dict], setting: str, work: str | None = None, issue: str | None = None
) -> list[dict]:
    """Filter `documents_index` to `setting`, then by `work` (matched against `system`) and
    `issue` (matched against `edition`), returning `{"doc": id}` -- no offset (FR-001)."""
    results = [record for record in documents_index if record.get("setting") == setting]
    if work is not None:
        results = [record for record in results if record["system"] == work]
    if issue is not None:
        results = [record for record in results if record["edition"] == issue]
    return [{"doc": record["id"]} for record in results]
