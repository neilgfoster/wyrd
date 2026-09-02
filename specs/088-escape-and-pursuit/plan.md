# Implementation Plan: Escape and pursuit

**Branch**: `088-escape-and-pursuit` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/088-escape-and-pursuit/spec.md`

## Summary

Adds `escape_scene` to `engine/wyrd/combat.py` (#243/#244): converts a pursuer count to the
Challenging→Very Hard difficulty ladder rung, resolves it as a `rules.group_test` in the
"least_capable" mode (the party is only as fast as its slowest member), and interprets the
result — success clears the chronicle's `combat` scene entirely, failure leaves it untouched
(the fight resumes exactly where it was). A zero-pursuer count skips the roll and clears the
scene unconditionally. Difficulty is converted to `group_test`'s `opponent` parameter via the
same `50 - DIFFICULTY_BONUSES[difficulty]` identity `resolution.propose`'s own difficulty
handling already uses, so `effective_pct` comes out identical to a direct skill+difficulty
test.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/combat.py` (#243/#244) and
calls the existing `rules.group_test`/`rules.select_group_skill` (specs/078) unchanged.

**Storage**: chronicle-level state, the same `combat` key #243 established; a successful escape
removes that key entirely (the scene is over).

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: `escape_scene` never reimplements `group_test`'s selection or roll; it only
supplies the difficulty-derived `opponent` value and interprets `success`. A failed escape must
change nothing about `engaged`/`acted` state beyond what the roll itself specifies (nothing —
the fight simply resumes as it was).

**Scale/Scope**: exactly spec.md's two user stories (escape with pursuers, no-pursuer case). No
crowd rule (#4/#246).

## Constitution Check

- No setting/system names — `escape_scene`, Challenging/Difficult/Hard/Very Hard are the
  engine's own vocabulary, matching `docs/design/03-rules.md` §1's difficulty ladder and §2
  directly.
- Deterministic over inference — the pursuer→difficulty ladder is a fixed table, and the
  difficulty→`opponent` conversion is the same identity `resolution.propose` already uses, not
  a newly-invented formula.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: implements what `docs/design/03-rules.md` §2 already specifies (the pursuit-count
  ladder and its failure consequence), reusing `group_test` exactly as #212's own scope note
  requires — not a new decision.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/088-escape-and-pursuit/
├── plan.md              # This file
├── tasks.md             # Phase 2 output
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
engine/wyrd/
├── combat.py             # + escape_difficulty, escape_scene
└── rules.py               # unchanged, reused as-is (group_test, select_group_skill)

tests/engine/
└── test_combat.py         # + escape-and-pursuit tests
```

**Structure Decision**: extends the existing single-project `engine/wyrd/` layout; no new
modules. `escape_scene` lives in `combat.py` alongside `close`/`break_off`, since it is the
scene-level counterpart to those two (docs/design/03-rules.md §2 treats them as one section).

## Complexity Tracking

No constitution violations — table not needed.
