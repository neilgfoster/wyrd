# Implementation Plan: Award advances against the four session triggers

**Branch**: `102-advance-award-triggers` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/102-advance-award-triggers/spec.md`

## Summary

A new stdlib-only module, `engine/wyrd/advancement.py`, holding the award side of the advance
economy: the closed four-trigger vocabulary, the one-of-each-per-session rule, the 3-per-session
ceiling, and the session reset that carries the unspent balance forward. No dice are rolled, so
this does not enter `resolution.py`'s propose/commit staging pipeline at all — it is a validator
in the same shape as `career.validate_allocation`, surfaced through `verbs.py`, `catalog.py` and
`client.py` the way `validate-allocation` already is.

## Technical Context

**Language/Version**: Python 3.11+ (stdlib-only)

**Primary Dependencies**: None new — one new module plus the existing `verbs.py`/`catalog.py`/
`client.py` surface

**Storage**: None written by this feature. It computes a new award record from a given one; the
caller persists it. `advances_unspent` already exists in the character shape
(docs/design/22-state.md).

**Testing**: `pytest`, run under `PYTHONPATH=engine`

**Target Platform**: CLI / library, cross-platform

**Project Type**: Single project — `engine/wyrd` library plus its `wyrd` CLI

**Performance Goals**: N/A — membership and count checks on a four-element vocabulary

**Constraints**: stdlib-only; no XP total may be stored or derived (FR-007); the engine never
judges whether the fiction met a trigger (FR-008)

**Scale/Scope**: One new module, two verbs, their catalog and CLI entries, and their tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): every rule here is a membership test or a count
  against a fixed constant. The judgment this feature deliberately does *not* make — whether the
  fiction met the trigger — is the GM's, supplied as the caller's claim. Pass.
- **No setting/system vocabulary**: Learned, Drove, Practised and Endured are the design
  document's own descriptive English, not borrowed from any source system. Pass.
- **Design documents describe the present**: `docs/design/03-rules.md` §6 already states this
  rule in full; the engine is catching up to it, so no design document changes. Pass.
- **Capability change goes through Spec Kit**: this plan. Pass.
- **Rule changes apply forward only**: nothing recomputes a past award. Pass.

No violations — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/102-advance-award-triggers/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: the two verbs' request/response shapes are small enough to describe
inline in `data-model.md`.

### Source Code (repository root)

```text
engine/
├── wyrd/
│   ├── advancement.py    # NEW -- triggers, ceiling, award_advance, begin_session
│   ├── verbs.py          # award_advance / begin_session passthroughs
│   ├── catalog.py        # TOOLS entries for award-advance and begin-session
│   └── client.py         # CLI subparsers for both
└── tests/
    └── test_advancement.py  # NEW
```

**Structure Decision**: A new module rather than an extension of `career.py`. `career.py` is
creation-time allocation against a career's grants; this is session-time award against triggers.
They meet only in #277, where a spend is validated against both — and putting the award rules in
`career.py` now would mean moving them then.
