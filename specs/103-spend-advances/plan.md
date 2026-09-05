# Implementation Plan: Spend advances — raise, open, change career

**Branch**: `103-spend-advances` | **Date**: 2026-09-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/103-spend-advances/spec.md`

## Summary

The spend side of the advance economy, split across the two modules that already own its halves:
the **career-graph rules** (is a career an entry career, is a career complete for a character,
which prerequisites does a change satisfy) land in `engine/wyrd/career.py`, next to
`effective_cap` and the creation-time allocation validator that already reads a career's grants;
the **spend transaction** (take one advance, apply one of three actions, return a new character
view or a refusal) lands in `engine/wyrd/advancement.py`, next to the award side that mints the
currency this consumes. No dice are rolled, so this stays out of `resolution.py`'s propose/commit
staging, and is surfaced through `verbs.py`/`catalog.py`/`client.py` exactly as `award-advance`
is.

Issue #277 says the career-graph rules are "already in `engine/wyrd/career.py`". They are not —
`career.py` today holds `effective_cap` and `validate_allocation` only; the graph is specified in
`docs/design/24-authoring-a-setting.md` and `specs/035-career-graph/` but never implemented. This
plan writes them there, which is what the issue's instruction amounts to: one copy, in that
module.

## Technical Context

**Language/Version**: Python 3.11+ (stdlib-only)

**Primary Dependencies**: None new — `advancement.py` gains a dependency on `career.py`, the
direction `career.py`'s own docstring already anticipates

**Storage**: None written by this feature. It computes a new character view from a given one; the
caller persists it, matching `award_advance`.

**Testing**: `pytest`, run under `PYTHONPATH=engine`

**Target Platform**: CLI / library, cross-platform

**Project Type**: Single project — `engine/wyrd` library plus its `wyrd` CLI

**Performance Goals**: N/A — membership tests over a setting's career table

**Constraints**: stdlib-only; no spend may mutate its inputs (FR-012); the engine never judges the
fictional reason for a career change (FR-011); one copy of the career-graph rules (#277)

**Scale/Scope**: Two modules touched, one verb added, its catalog and CLI entries, and tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): every rule is a membership test, an arithmetic
  comparison against a cap, or a set intersection against a history. The one judgment deliberately
  left out — whether the fiction justifies a career change — is the GM's, exactly as the award
  side leaves the trigger's fiction to them. Pass.
- **No setting/system vocabulary**: careers named in tests are the design document's own worked
  example (guard, soldier, guard-captain), already public in
  `docs/design/24-authoring-a-setting.md`. Pass.
- **Design documents describe the present**: `docs/design/03-rules.md` §6 and
  `docs/design/24-authoring-a-setting.md` already state these rules in full; the engine is
  catching up, so no design document changes. Pass.
- **Capability change goes through Spec Kit**: this plan. Pass.
- **Rule changes apply forward only**: nothing recomputes a past spend. Pass.
- **Assert prior numbers**: SC-001's "9 advances from 25% to 70%" is the figure
  `tools/check_advancement.py` already publishes; the tests assert agreement with it rather than
  restating it by eye. Pass.

No violations — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/103-spend-advances/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: the verb's request/response shape is small enough to describe inline in
`data-model.md`.

### Source Code (repository root)

```text
engine/
└── wyrd/
    ├── career.py         # + is_entry, career_complete, career_by_id, change_career_legality
    ├── advancement.py    # + SPENDS, spend_advance
    ├── verbs.py          # spend_advance passthrough
    ├── catalog.py        # TOOLS entry for spend-advance
    └── client.py         # CLI subparser for spend-advance
tests/engine/
├── test_career.py        # + graph rules
└── test_advancement.py   # + the three spends and their refusals
```

**Structure Decision**: The split follows what each module's inputs already are. `career.py` reads
a career (and now a career table) and answers questions about it; it holds no character balance
and gains none. `advancement.py` holds the currency and now spends it, calling `career.py` for
every legality question rather than reimplementing a cap or a prerequisite check — the single
copy #277 asks for.
