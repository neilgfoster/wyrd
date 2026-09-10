# Implementation Plan: The Rally: recovery, advance award and commit

**Branch**: `310-the-rally` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/115-the-rally/spec.md`

## Summary

Add a `wyrd.rally` module implementing `docs/design/16-session.md`'s "The Rally -- the save
point": the fixed Strain/Stamina recovery (`docs/design/03-rules.md` §2, prior art in ADR
0020/0021), an optional advance-award hook that wires `engine/wyrd/advancement.py`'s existing
`award_advance` rather than reimplementing any award logic, and a persist/commit step that runs
exactly once, taking its actual work as an injected callable the same way `wyrd.session.run_close`
already does for close. This feature is invoked once #309's session loop (`wyrd.session`) reaches
a beat boundary; it does not itself decide when a beat has closed.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module).

**Primary Dependencies**: `engine/wyrd/advancement.py` (`award_advance`, `new_record`) for the
advance-award hook; `engine/wyrd/session.py` (#309, `run_close`'s injected-callable pattern) as
the precedent for the persist/commit step's shape. No new third-party dependency.

**Storage**: The persist/commit step's actual content depends on the chronicle state layer under
#300, which does not exist yet -- this feature guarantees the step runs exactly once, at the
right point, taking it as a caller-supplied zero-argument callable, exactly as `run_close`
already does for close. No new storage layer is introduced here.

**Testing**: stdlib `unittest` (docs/design/27-tooling.md §6), run with `PYTHONPATH=engine`, in
`tests/engine/test_rally.py`, following `test_session.py`'s and `test_advancement.py`'s existing
structure.

**Target Platform**: Linux/CLI -- no server or UI component; this feature adds no new platform
surface.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A -- one Rally computation per beat boundary; no throughput or latency
target applies.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule: recovery
amounts, capping/flooring and award legality are all closed-form, never inferred. Ruff (line
length 100, rule sets E/F/I/UP) must stay clean repo-wide. `engine/` and `tools/` must not depend
on each other (`docs/design/02-architecture.md`). Rules apply forward only
(`docs/design/29-evolution.md`) -- no recomputation of a character's history.

**Scale/Scope**: One new module (`wyrd.rally`) covering the three user stories in spec.md; no
changes to `wyrd.advancement`'s public surface (this feature calls it, unchanged) or to
`wyrd.session` (this feature is invoked by it, not vice versa).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** -- original engine code implementing an already
  published design document; no source-book material involved. **Pass.**
- **No setting or system names in design/README** -- this feature introduces no new vocabulary
  beyond what `16-session.md` already names (Rally, Strain, Stamina, advance). **Pass.**
- **Tone is a setting property** -- no tone/genre language introduced. **Pass.**
- **Deterministic over inference** (ADR 0005) -- recovery amounts, floor/cap and award legality
  are all closed-form, delegated to `advancement.award_advance`'s existing checks rather than
  reimplemented. **Pass.**
- **Rule changes apply forward only** -- new capability, not a retroactive change. **Pass.**
- **Design documents describe the present** -- this plan implements `16-session.md` and
  `03-rules.md` §2 as written; a genuine gap found during implementation updates the design doc
  in place. **Pass, pending Phase 1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** -- this plan
  is that artifact. **Pass.**
- **Reuse over invention** (CLAUDE.md) -- the advance-award hook calls
  `advancement.award_advance` directly; it does not duplicate its trigger vocabulary, session
  ceiling or refusal shapes. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/115-the-rally/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks -- not created here)
```

### Source Code (repository root)

```text
engine/wyrd/
├── advancement.py        # existing -- award_advance/new_record this feature calls, unchanged
├── session.py             # existing (#309) -- run_close's injected-callable pattern, precedent
└── rally.py                # NEW -- fixed recovery, advance-award hook, persist/commit step

tests/engine/
├── test_advancement.py   # existing
├── test_session.py         # existing
└── test_rally.py           # NEW -- covers spec.md's three user stories
```

**Structure Decision**: Single-project layout (the existing `engine/` package). A new
`wyrd/rally.py` module sits alongside `session.py` and `advancement.py` as the Rally layer,
matching the existing one-module-per-structural-concern pattern, rather than folding Rally logic
into `session.py` (which stays scoped to containment/loop-step/shape concerns) or into
`advancement.py` (which stays scoped to the advance currency itself, not the boundary that
happens to trigger it).

## Complexity Tracking

*No violations -- table not needed.*
