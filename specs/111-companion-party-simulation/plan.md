# Implementation Plan: Companion and party simulation engine support

**Branch**: `111-companion-party-simulation` | **Date**: 2026-09-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/111-companion-party-simulation/spec.md`

## Summary

Add a `wyrd.party` module implementing the person-first, two-layer companion model
(`docs/design/10-the-character.md` §4, `docs/design/16-session.md`, ADR 0034) and the
NPC-played party-simulation mechanics: companion validation, Bond-offset Tension arithmetic,
Loyalty-relation gating (undeclared / strained / irreconcilable), and a party-roster read that
returns each companion's narrative and mechanical layers together. This reuses the existing
`character` entity shape and `state.py` persistence primitive rather than inventing a new one.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module; no third-party dependency has ever been introduced there).

**Primary Dependencies**: None beyond the standard library. Reuses `wyrd.state` (entity
persistence) and `wyrd.character` (existing player-character field conventions) as the pattern to
follow for the companion record.

**Storage**: Files under the chronicle's state directory, via `state.save_entity`/`load_entity` —
the same mechanism the player character and adversaries already use. A companion is one entity
file per companion (`role: companion`); Party Tension (a single value shared by the whole party,
not per-companion) is stored on the chronicle's top-level state (`state.py`'s `default_state()`
dict), alongside other campaign-scoped counters, rather than duplicated onto every companion file.

**Testing**: `pytest`, run with `PYTHONPATH=engine`, in `tests/engine/`, following
`test_character.py`'s and `test_journey.py`'s existing structure.

**Target Platform**: Linux/CLI — the engine has no server or UI component; this feature adds no
new platform surface.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A — this is turn-scale GM tooling (at most 5 companions, Tension 0-6);
no throughput or latency target applies.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule: Tension/Bond
arithmetic and Loyalty-relation lookups are pure computation, never inferred. Ruff (line length
100, rule sets E/F/I/UP) must stay clean repo-wide.

**Scale/Scope**: Up to 5 companions per party (the design's own effective-size bound), one shared
Tension value per party.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — no source-book extraction involved; this is
  original engine code and design-doc-derived arithmetic. **Pass.**
- **No setting or system names in design/README** — this feature touches no design document
  vocabulary beyond what's already there (`companion`, `career`, `bond`, `taint`, `strain`,
  `wounds`, `loyalty`) and adds no setting-specific term. **Pass.**
- **Tone is a setting property** — no tone or genre language is introduced by this feature's
  mechanics. **Pass.**
- **Deterministic over inference** (ADR 0005) — Tension-delta computation and Loyalty-relation
  lookup are both closed-form; nothing here is inferred by an LLM or heuristic. **Pass.**
- **Rule changes apply forward only** — this feature adds new engine capability, not a change to
  an existing rule's retroactive effect; no history-recomputation concern arises. **Pass.**
- **Design documents describe the present; ADRs are not re-litigated** — this plan implements
  ADR 0034 and the existing text of `10-the-character.md`/`16-session.md` as written, and proposes
  no change to either. If implementation surfaces a genuine gap (per the issue's own Definition of
  Done), the design document is updated in place, not left stale. **Pass, pending Phase 1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  is that artifact. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/111-companion-party-simulation/
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
├── character.py         # existing — player-character shape (pattern this follows)
├── state.py              # existing — generic entity persistence (reused, not modified)
└── party.py               # NEW — companion record validation, Tension/Bond arithmetic,
                             #        Loyalty-relation gating, party-roster read

tests/engine/
├── test_character.py    # existing
└── test_party.py          # NEW — covers spec.md's four user stories
```

**Structure Decision**: Single-project layout (the existing `engine/` package). A new
`wyrd/party.py` module sits alongside `character.py` and `adversary.py` as a third domain module
built on the shared `state.py` primitive — matching the existing pattern of "one module per entity
domain, one shared persistence layer" rather than folding companion logic into `character.py`
(companions are a `character` entity, but the party-level concerns — Tension, Loyalty gating,
roster assembly — are not player-character concerns and don't belong in that module).

## Complexity Tracking

*No violations — table not needed.*
