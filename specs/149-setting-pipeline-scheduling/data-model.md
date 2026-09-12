# Phase 1 Data Model: Setting build pipeline — scheduled execution and web augmentation policy

## Entity: Provenance record

Attached by a setting repository's own tooling to any derived fact (a Pass 0 catalogue entry, a
corpus index posting, or any other artifact this pipeline produces) to record where that fact
came from.

| Field | Type | Required | Notes |
|---|---|---|---|
| `origin` | `"library"` \| `"public"` | yes | Closed two-value vocabulary — same pattern as `AUTHORITY_TIERS` (`setting_pass0.py`) and `WORLD_BUILDING_CATEGORIES` (`corpus_pipeline.py`). |
| `reference` | `str` or `None` | conditionally | **Required, non-empty** when `origin == "public"` — must name a specific, checkable source (e.g. a title, edition/printing, and locator, or a stable citation — never a bare URL alone, per research.md Decision 3). **Must be `None`** when `origin == "library"` — a library-sourced fact's provenance is the setting's own `documents.json` record it was extracted from; a second reference would duplicate that pointer. |

**Validation rules** (enforced by `build_provenance_record`, `engine/wyrd/corpus_provenance.py`):

- `origin` not in `{"library", "public"}` → `ValueError` naming the invalid value.
- `origin == "public"` and `reference` is `None` or empty/whitespace-only → `ValueError` (FR-005,
  FR-007; SC-003's "zero derived facts carry an unattributed 'public' tag").
- `origin == "library"` and `reference` is not `None` → `ValueError` (keeps the two origins
  structurally distinct rather than allowing an unused field to carry inconsistent data).

**State transitions**: none — a provenance record is immutable once built. A derived fact whose
provenance changes (a public source is later found to have a private-library equivalent, say) is
recorded as a new record replacing the old one by the caller, not mutated in place; this module
has no notion of "editing" a provenance record.

**Relationships**: A provenance record is always attached to exactly one derived fact, by the
caller — this module does not model the derived fact itself (a Pass 0 catalogue entry, a corpus
posting, or anything else), matching every sibling `corpus_*` builder's own "pure record, no
ownership graph" shape.

## Entity: Public-augmentation policy (documentation, not code)

Not a runtime data shape — a stated rule, recorded in `docs/design/26-corpus-index.md`'s extended
"Build and maintenance" section (see plan.md's Project Structure). Its content is fixed by
research.md Decision 3: a public source is in-bounds only when it carries independently checkable
provenance not contingent on the private library (public-domain text, openly published errata/SRD
material, broadly attested common knowledge); "found on the open internet" alone is explicitly
out of bounds.

## Entity: Scheduled-run design (documentation, not code)

Not a runtime data shape — the design recorded in the same doc section, fixed by research.md
Decisions 1–2: GitHub Actions' `schedule` trigger, defined and run inside the setting repository
itself, covering Pass 0's catalogue/gap-survey/idempotence pass and the four deterministic corpus
indexes; the scenario index's model call stays on its existing lazy, on-first-need path and is
excluded from the scheduled run.
