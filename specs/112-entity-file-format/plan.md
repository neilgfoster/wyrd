# Implementation Plan: Entity file format engine support

**Branch**: `112-entity-file-format` | **Date**: 2026-09-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/112-entity-file-format/spec.md`

## Summary

Add a `wyrd.entity` module implementing `docs/design/25-entities.md`'s file format: the common
frontmatter schema shared by all ten entity types, per-type field validation, containment
resolution (`parent` tree, acyclic, children by reverse lookup) and connection-graph loading
(free, directional, conditional, may loop, `hidden` preserved). This is the foundational data
model the rest of epic #219 (arcs/beats, session, campaign, state, parallel chronicles) builds on,
and follows the restricted-YAML-subset reader/writer pattern already used by `state.py` and
`tools/check_bestiary.py` rather than adding a third-party YAML dependency.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module).

**Primary Dependencies**: None beyond the standard library. `engine/wyrd/state.py` already exposes
`parse_entity`/`dump_entity`/`save_entity`/`load_entity` — the frontmatter/body split and atomic
file I/O for an entity file — added ahead of schedule for the player-character and companion
records. This feature reuses those functions directly for file I/O and adds the layer `state.py`
does not have: the common-schema and per-type validation, containment resolution, and connection-
graph loading across a *set* of entity files (`state.py`'s functions operate on one file at a
time).

**Storage**: Entity files on disk, one file per entity (markdown + YAML frontmatter). This
feature's read/write path is agnostic to *where* the files live (setting repo vs. chronicle
overlay); that split is a dependent feature (#306, chronicle overlay resolution).

**Testing**: `pytest`, run with `PYTHONPATH=engine`, in `tests/engine/`, following
`test_party.py`'s and `test_journey.py`'s existing structure.

**Target Platform**: Linux/CLI — no server or UI component; this feature adds no new platform
surface.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A — entity sets are read from a chronicle/setting repository on disk, at
a scale of hundreds to low thousands of files; no throughput or latency target applies.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule: schema
validation, cycle detection and wikilink resolution are pure computation, never inferred. Ruff
(line length 100, rule sets E/F/I/UP) must stay clean repo-wide. `engine/` and `tools/` must not
depend on each other (`docs/design/02-architecture.md`), so this module does not import
`tools/check_bestiary.py`, even though it follows the same reader pattern.

**Scale/Scope**: Ten closed entity types; the common schema plus each type's own additional
fields, per `docs/design/25-entities.md`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — no source-book extraction involved; this is
  original engine code implementing an already-published design document. **Pass.**
- **No setting or system names in design/README** — this feature adds no new design-document
  vocabulary; it implements the ten types and field names `25-entities.md` already names.
  **Pass.**
- **Tone is a setting property** — no tone or genre language is introduced by this feature.
  **Pass.**
- **Deterministic over inference** (ADR 0005) — schema validation, cycle detection, and wikilink
  resolution are all closed-form; nothing here is inferred by an LLM or heuristic. **Pass.**
- **Rule changes apply forward only** — this feature adds new engine capability, not a change to
  an existing rule's retroactive effect. **Pass.**
- **Design documents describe the present; ADRs are not re-litigated** — this plan implements
  `25-entities.md` as written. If implementation surfaces a genuine gap, the design document is
  updated in place, not left stale. **Pass, pending Phase 1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  is that artifact. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/112-entity-file-format/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks — not created here)
```

### Source Code (repository root)

```text
engine/wyrd/
├── state.py             # existing — restricted-YAML-subset pattern this follows
├── character.py         # existing — a character entity's player-facing fields (consumer)
├── party.py             # existing — companion character records (consumer)
└── entity.py             # NEW — common schema, ten-type validation, containment,
                            #        connection-graph loading

tests/engine/
├── test_state.py        # existing
└── test_entity.py         # NEW — covers spec.md's three user stories
```

**Structure Decision**: Single-project layout (the existing `engine/` package). A new
`wyrd/entity.py` module sits alongside `state.py` as the entity-format layer other domain modules
(`character.py`, `party.py`, and future arc/beat, campaign, and parallel-chronicle modules) build
on — matching the existing pattern of one module per structural concern, built on a shared
restricted-YAML reading approach, rather than folding entity-format parsing into `state.py` itself
(which stays scoped to chronicle-level `schema_version`/`last_roll` state, not the entity schema).

## Complexity Tracking

*No violations — table not needed.*
