# Implementation Plan: Chronicle state invariants: passive validation and active cascades

**Branch**: `124-chronicle-state-invariants` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/124-chronicle-state-invariants/spec.md`

## Summary

`commit()` in `engine/wyrd/resolution.py` currently applies a proposal's staged mutations with no
validation at all. This feature adds one validation pass, run once across the whole proposal
immediately before any mutation is applied, enforcing the four passive rules
`docs/design/22-state.md` § Invariants states (duplicate id, unresolved reference/cycle,
`fortune.current ≤ fate.max`, tracker `0..max`) — rejecting the entire proposal, with nothing
written, on any violation. It also adds a small `is_spent()` accessor computing Spent at read
time (ADR 0049), and a regression test proving the three cascades already implemented in
`resolution.py` (taint→Transformation, trauma→test→Affliction, transformation-count→lost)
continue to stage correctly once the new passive checks sit in front of `commit`.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only (repo-wide constraint, `CLAUDE.md`)

**Primary Dependencies**: none new — reuses `engine/wyrd/entity.py` (`check_containment`,
`unresolved_references`, `resolve_wikilink`) and `engine/wyrd/resolution.py`'s existing
`_get_nested`/`_apply_mutation` machinery

**Storage**: entity files under a chronicle directory (YAML frontmatter), via `state.py`/
`character.py`'s existing load/save — no schema change

**Testing**: pytest, run as `PYTHONPATH=engine python3 -m pytest -q` (existing repo convention)

**Target Platform**: Linux CLI (`wyrd` command), no new platform surface

**Project Type**: single library/CLI (`engine/wyrd/`)

**Performance Goals**: N/A — validation is a bounded pass over one proposal's mutations plus a
lookup against the chronicle's entity set already loaded elsewhere; no new I/O beyond what
`commit` already performs

**Constraints**: must not alter the existing atomic-per-entity-file guarantee `commit()`'s
docstring already states; must not touch `wyrd track`'s immediate-write path (out of scope, FR-010)
or the pending/transaction lifecycle (out of scope, FR-011)

**Scale/Scope**: one chronicle's worth of entities per commit call — no scale concern

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): every passive rule in this feature is a computed
  check (id set membership, reference resolution, numeric comparison, range check) — no inference
  anywhere. PASS.
- **No setting/system names, tone stays out of mechanics** (`CLAUDE.md`): this feature touches no
  prose the player sees and introduces no new vocabulary beyond terms `22-state.md` already uses
  (`fortune`, `fate`, `taint`, `trauma`, `tracker`, `Spent`). PASS.
- **Rule changes apply forward only** (`09-evolution.md`): this feature enforces invariants going
  forward on new commits; it does not touch or recompute any already-committed entity file. PASS.
- **Nothing unpublishable** (`CLAUDE.md`): no source text, no setting content — pure engine
  mechanism. PASS.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/124-chronicle-state-invariants/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
└── tasks.md              # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
engine/wyrd/
├── entity.py         # existing: check_containment, unresolved_references, resolve_wikilink (reused, not duplicated)
├── resolution.py      # commit() gains a validation pass; new is_spent() accessor added here
└── state.py           # unchanged — load/save of entities and chronicle.yaml

tests/engine/
└── test_resolution.py  # new tests: passive-check rejections, cascade regression, is_spent()
```

**Structure Decision**: single existing project (`engine/wyrd/`), no new module — this feature is
additive functions inside `resolution.py`, calling into `entity.py`'s already-existing checks. No
new top-level package, no new test directory.

## Complexity Tracking

*No violations — table omitted.*
