# Implementation Plan: Downtime phase, including Mend

**Branch**: `311-downtime-mend` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/116-downtime-mend/spec.md`

## Summary

Add `engine/wyrd/downtime.py`: a pure-function module mirroring `rally.py`'s and `session.py`'s
existing shape. It provides a Downtime period's own loop state (Destination → Upkeep → Advances →
Undertaking → Rest), the Upkeep trade (Standing -1 vs. coin -= Standing, away from home only),
the exactly-one-undertaking gate, unconditional Stamina rest, calendar-advance exposure, and
Mend's own wound-stepping logic reusing `character.py`'s existing wound shape and
`WOUND_EFFECT_KEYS` unchanged.

## Technical Context

**Language/Version**: Python 3.11, stdlib only (matches every sibling module in `engine/wyrd/`)

**Primary Dependencies**: None beyond the standard library; reuses `wyrd.character` (wound
validation/shape) and `wyrd.economy` (Standing/coin primitives) as data, not by re-implementing
their logic.

**Storage**: N/A — pure functions over caller-supplied dicts, exactly as `rally.py`/`session.py`/
`economy.py` already do. Persistence is out of scope (chronicle state layer, #300, does not exist
yet) — this module follows the injected-callable pattern `session.run_close`/`rally.apply_rally`
already established for a not-yet-existing commit step.

**Testing**: `pytest`, `PYTHONPATH=engine`, matching every existing `tests/test_*.py` in this repo.

**Target Platform**: Library code, no platform dependency.

**Project Type**: Single library module added to `engine/wyrd/`.

**Performance Goals**: N/A — no performance-sensitive path; Downtime happens once per session at
most.

**Constraints**: ruff-clean (E/F/I/UP, line length 100); `check_recovery.py`'s published figures
(0.61 wound records, 0.62 downtimes of Mend) must be diffed before/after if touched, per CLAUDE.md
and the spec's SC-004. A recurring wound must be provably un-mendable (tested, not just
documented).

**Scale/Scope**: One new module (~150-200 lines), plus one test module. No changes to
`character.py`'s wound schema.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — feature is pure engine mechanics derived
  from this repo's own design docs and ADRs; no external source text is copied. PASS.
- **No setting or system names** — `downtime.py`'s vocabulary (Destination, Upkeep, Advances,
  Undertaking, Rest, Mend) is exactly the engine's own labels from `docs/design/16-session.md`,
  not borrowed from any source system. PASS.
- **Tone is a setting property** — no narrative tone is baked into this module; it returns data,
  never prose. PASS.
- **Deterministic over inference** — Mend's ladder and the recurring-wound exemption are fixed,
  checkable rules (ADR 0021); no probability claim is introduced by this feature, so no new check
  script beyond re-running the existing `check_recovery.py` diff is needed. PASS.
- **Rule changes apply forward only; history never recomputed** — Mend marks a wound `closed`
  rather than deleting it, matching ADR 0021 and `docs/design/29-evolution.md` directly. PASS.
- **Design documents describe the present; ADRs are never edited** — this feature implements
  ADR 0021 and `docs/design/16-session.md` as already written; it proposes no design change and
  therefore no new ADR (no rejected alternative is being decided here — the design already
  settled Mend's ladder). PASS.
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  itself satisfies that gate.

No violations. Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/116-downtime-mend/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks, not this command)
```

### Source Code (repository root)

```text
engine/wyrd/
└── downtime.py           # New: Downtime loop state, Upkeep, undertaking gate, Rest, Mend

tests/
└── test_downtime.py      # New: unit tests for every function above
```

**Structure Decision**: Single library module added alongside `engine/wyrd/rally.py` and
`engine/wyrd/session.py`, which this feature's Downtime loop state directly mirrors in shape (a
`new_*_state`/`advance_*` pair). No new top-level directory, no contracts/ subdirectory — this is
an internal library with no external wire format; its "contract" is its Python function
signatures, documented in data-model.md instead.

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
