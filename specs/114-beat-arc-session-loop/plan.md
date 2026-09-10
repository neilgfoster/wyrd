# Implementation Plan: Beat/arc structure and the session loop

**Branch**: `309-beat-arc-session-loop` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/114-beat-arc-session-loop/spec.md`

## Summary

Add a `wyrd.session` module implementing `docs/design/16-session.md`'s beat/arc structure and
session loop, on top of the entity file format (`wyrd.entity`, #296/closed) which already gives
arc/beat containment (`arc` is in `RECURSIVE_TYPES`, `beat` is not) and cycle detection. This
feature adds what `entity.py` deliberately leaves out: an explicit rejection of a beat given
children (containment gives the *shape*, not the *enforcement*); per-narration `mode`
(`played`/`summarised`) recorded independently of the beat's stored definition; the six-step
session loop (load, orient, recap, beat, repeat, close) as checkable state transitions; the
`pending:` mid-beat marker; and session-shape classification kept out of player-facing strings.
The Rally mechanic and the Downtime phase's own steps are explicitly out of scope (#310, #311).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module).

**Primary Dependencies**: `engine/wyrd/entity.py` (`ENTITY_TYPES`, `RECURSIVE_TYPES`, `validate`,
`children_of`, `check_containment`, `resolve_entity`) for arc/beat data and containment;
`engine/wyrd/state.py` for entity file I/O reuse. No new third-party dependency.

**Storage**: Session-loop and pending-marker state lives in per-chronicle state (the same
mechanism `state.py`'s chronicle-level `schema_version`/`last_roll` fields already use), not a new
storage layer.

**Testing**: stdlib `unittest` (docs/design/27-tooling.md §6: "stdlib unittest, no pytest"), run with `PYTHONPATH=engine`, in `tests/engine/test_session.py`, following
`test_entity.py`'s and `test_party.py`'s existing structure.

**Target Platform**: Linux/CLI — no server or UI component; this feature adds no new platform
surface.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A — one session loop, low tens of beats at most; no throughput or
latency target applies.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule: containment
enforcement, mode recording, loop-step ordering and shape classification are all closed-form,
never inferred. Ruff (line length 100, rule sets E/F/I/UP) must stay clean repo-wide. `engine/`
and `tools/` must not depend on each other (`docs/design/02-architecture.md`).

**Scale/Scope**: One new module (`wyrd.session`) covering the five user stories in spec.md;
no changes to `wyrd.entity` or `wyrd.party` required, since both already expose what this feature
needs (containment primitives; Bond/Tension are untouched).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — original engine code implementing an already
  published design document; no source-book material involved. **Pass.**
- **No setting or system names in design/README** — this feature introduces no new vocabulary
  beyond what `16-session.md` already names (beat, arc, Rally is out of scope here, session
  shapes). **Pass.**
- **Tone is a setting property** — no tone/genre language introduced. **Pass.**
- **Deterministic over inference** (ADR 0005) — containment enforcement, mode recording, loop
  ordering and shape classification are closed-form. **Pass.**
- **Rule changes apply forward only** — new capability, not a retroactive change. **Pass.**
- **Design documents describe the present** — this plan implements `16-session.md` as written; a
  genuine gap found during implementation updates the design doc in place. **Pass, pending Phase
  1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  is that artifact. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/114-beat-arc-session-loop/
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
├── entity.py             # existing -- containment primitives this feature builds on
├── state.py              # existing -- entity file I/O reuse
└── session.py             # NEW -- containment enforcement, mode recording, session loop,
                             #        pending marker, shape classification

tests/engine/
├── test_entity.py        # existing
└── test_session.py         # NEW -- covers spec.md's five user stories
```

**Structure Decision**: Single-project layout (the existing `engine/` package). A new
`wyrd/session.py` module sits alongside `entity.py` and `party.py` as the session-structure layer,
matching the existing one-module-per-structural-concern pattern, rather than folding session-loop
logic into `entity.py` (which stays scoped to the entity file format itself, not play-time
sequencing).

## Complexity Tracking

*No violations — table not needed.*
