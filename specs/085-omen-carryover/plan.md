# Implementation Plan: Omen carryover

**Branch**: `238-omen-carryover` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/085-omen-carryover/spec.md`

## Summary

Extends `engine/wyrd/resolution.py` (#235, #236, #237) with per-actor pending-Omen tracking,
threaded through a new shared `_stage_requests` helper that both `propose_batch` and `reroll` now
call instead of looping over `_stage_request` directly. `_stage_request` gains an
`extra_depends_on` parameter so the Omen-consumption edge composes with (but doesn't replace) the
existing cascade `depends_on` machinery. `reroll` is extended to collect *every* top-level
request within a rerolled step's downstream set (not only the named step's own request) — needed
because an Omen-consumption edge can now pull a different request into that set — and re-stages
all of them together via the same `_stage_requests` helper, so `reroll` itself needs no
Omen-specific logic.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/resolution.py`.

**Storage**: unchanged — `pending_omen` is already part of the character schema
(`engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS`); this feature is the first to read/write
it.

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: Reading `pending_omen` must never itself constitute a write; only a staged
`pending_omen` mutation, applied on `commit`, changes what's on disk.

**Scale/Scope**: the two named worked-example shapes (spec.md SC-001–SC-004) — no change to
which mechanics exist, only how their requests within one call see each other's Omens.

## Constitution Check

- No setting/system names — `pending_omen`, Fair/Ill Omen are the engine's own existing
  vocabulary (`docs/design/03-rules.md` §1, already in the character schema).
- Deterministic over inference — every worked example is freshly computed with a disclosed seed
  (`research.md`), never asserted.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: implements what `docs/design/31-action-resolution.md` (design already landed,
  #193) and ADR 0042 already specify.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/085-omen-carryover/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
engine/wyrd/
└── resolution.py      # extended: _read_wyrd_omen, _stage_requests (shared, replaces the
                        # bare loop/single call propose_batch and reroll used before),
                        # _stage_request gains extra_depends_on

tests/engine/
└── test_resolution.py  # extended with Omen-carryover test classes; two existing tests
                         # updated for a now-correctly-staged pending_omen mutation their
                         # own already-seeded scenarios happen to trigger
```

**Structure Decision**: No new files — additive to #235/#236/#237's existing structure.

## Complexity Tracking

*No violations — table omitted.*
