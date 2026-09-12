"""Provenance records for derived facts: library-sourced vs. public-sourced (#102).

`docs/design/26-corpus-index.md`'s "Scheduled execution" and "Public augmentation" subsections
state the policy this module implements the data shape for: a public source may supplement a
setting's private library only when it carries independently checkable provenance of its own, and
every derived fact produced this way must record where it came from -- `library` (the setting's
own already-extracted, already-catalogued material) or `public` (a specific, named, checkable
external source), never an unattributed "public" tag.

Like every sibling `corpus_*` module, this is a **pure, no-I/O** slice: it never fetches, reads,
or otherwise touches any source material itself (CLAUDE.md's "no tooling that fetches source
material"). A setting repository's own tooling builds the record with data it already has --
whether a fact came from its own extracted library or from a public source it has already
identified and cited -- and attaches the returned `dict` to whatever record that fact lives on
(a Pass 0 catalogue entry, a corpus index posting, or any other derived artefact).

Python 3.11+, standard library only.
"""

from __future__ import annotations

# The closed, two-value origin vocabulary (specs/149-setting-pipeline-scheduling/data-model.md) --
# the same closed-vocabulary pattern as AUTHORITY_TIERS (tools/setting_pass0.py) and
# WORLD_BUILDING_CATEGORIES (corpus_pipeline.py).
ORIGINS = frozenset({"library", "public"})


def build_provenance_record(*, origin: str, reference: str | None = None) -> dict:
    """A provenance record for one derived fact (FR-005, FR-007).

    `origin` must be one of `ORIGINS`. `reference` must be a non-empty, non-whitespace-only
    string naming a specific, checkable source when `origin` is `"public"` (docs/design/26-
    corpus-index.md's public-augmentation policy: a bare "public" tag with no traceable
    reference is never valid), and must be omitted (`None`) when `origin` is `"library"` -- a
    library-sourced fact's provenance is the setting's own `documents.json` record it was
    already extracted from, so a second reference would only duplicate that pointer.

    Raises `ValueError`, naming the offending value or condition, for:
      - an `origin` outside `ORIGINS`;
      - `origin == "public"` with a missing or blank `reference`;
      - `origin == "library"` with a `reference` supplied.
    """
    if origin not in ORIGINS:
        raise ValueError(f"origin {origin!r} is not one of {sorted(ORIGINS)}")

    if origin == "public":
        if reference is None or not reference.strip():
            raise ValueError("reference is required and must be non-empty when origin is 'public'")
    elif reference is not None:
        raise ValueError("reference must be None when origin is 'library'")

    return {"origin": origin, "reference": reference}
