# Implementation Plan: Beat/arc entry and exit conditions, and thread-matched selection

**Branch**: `321-arc-beat-selection` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/120-arc-beat-selection/spec.md`

## Summary

Add validated `entry`/`exit` schema for arcs and beats, and a pure selection function that
matches a live-thread set against candidates' `entry.requires_threads`, falling back to
`leads_to` only when nothing matches — the selection half of `docs/design/18-arcs-and-beats.md`
that `wyrd.session` (#309, merged) deliberately left out. Builds on `wyrd.entity`'s existing
common-schema validation and wikilink resolution; introduces no new storage, no new dependency,
and does not touch containment or the session loop themselves.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module).

**Primary Dependencies**: `engine/wyrd/entity.py` (`validate`, `resolve_wikilink`,
`ENTITY_TYPES`) for the base entity schema and wikilink resolution this feature layers
`entry`/`exit` validation on top of. No new third-party dependency.

**Storage**: N/A — this feature holds no persistent state; the live-thread set and candidate pool
are plain arguments a caller supplies (chronicle/campaign state under #300/#301 owns storage,
neither exists yet).

**Testing**: stdlib `unittest` (docs/design/27-tooling.md §6), run with `PYTHONPATH=engine`, in
`tests/engine/test_arc_selection.py`, following `test_entity.py`'s and `test_session.py`'s
existing structure.

**Target Platform**: Linux/CLI — no server or UI component; this feature adds no new platform
surface.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A — selection runs over one nesting level's candidate pool at a time
(tens of entries at most); no throughput or latency target applies.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule: thread matching
and fallback ordering are closed-form set operations, never inferred. Ruff (line length 100, rule
sets E/F/I/UP) must stay clean repo-wide. `entry`/`exit` field names must match
`docs/design/26-corpus-index.md`'s beat schema exactly (FR-011).

**Scale/Scope**: One new module covering the four user stories in spec.md; `wyrd.entity` gains no
new required fields (entry/exit stay optional), so no existing entity file is invalidated.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — original engine code implementing an already
  published design document; no source-book material involved. **Pass.**
- **No setting or system names in design/README** — this feature introduces no vocabulary beyond
  what `18-arcs-and-beats.md`/`26-corpus-index.md` already name (entry, exit, requires_threads,
  emits_threads, leads_to). **Pass.**
- **Tone is a setting property** — no tone/genre language introduced. **Pass.**
- **Deterministic over inference** (ADR 0005) — thread-set matching and fallback ordering are
  closed-form. **Pass.**
- **Rule changes apply forward only** — new capability, not a retroactive change. **Pass.**
- **Design documents describe the present** — this plan implements `18-arcs-and-beats.md` as
  written; a genuine gap found during implementation updates the design doc in place. **Pass,
  pending Phase 1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  is that artifact. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/120-arc-beat-selection/
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
├── entity.py               # existing -- base schema, validate(), resolve_wikilink() reused
└── arc_selection.py         # NEW -- entry/exit validation, thread-matched selection, leads_to
                              #        fallback

tests/engine/
├── test_entity.py          # existing
└── test_arc_selection.py    # NEW -- covers spec.md's four user stories
```

**Structure Decision**: Single-project layout (the existing `engine/` package). A new
`wyrd/arc_selection.py` module sits alongside `entity.py` and `session.py`, matching the existing
one-module-per-structural-concern pattern, rather than folding selection logic into `entity.py`
(which stays scoped to the entity file format itself, not play-time selection) or into
`session.py` (which stays scoped to containment/the session loop, not thread matching).

## Complexity Tracking

*No violations — table not needed.*
