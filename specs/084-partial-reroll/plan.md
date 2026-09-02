# Implementation Plan: Partial reroll

**Branch**: `237-partial-reroll` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/084-partial-reroll/spec.md`

## Summary

Extends `engine/wyrd/resolution.py` (#235, #236) with `propose_batch` (several independent
top-level requests in one proposal — needed by this feature's own worked example, and a thin
`propose` now delegates to it as a single-request call) and `reroll(proposal_id, step, resource)`.
Each top-level step records its own originating `request` (actor/mechanic/skill/target/
difficulty/tier/dice) as `inputs`, so `reroll` can re-invoke the same staging logic
`propose_batch` already uses, under the resource's modifier, after computing and discarding the
downstream set from `depends_on`. A shared `_stage_request` helper factors the staging logic out
of both `propose_batch` and `reroll` so the two never diverge.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/resolution.py` (#235, #236).

**Storage**: unchanged — proposals stay process-local/in-memory; `reroll` never writes; `commit`
still writes via the existing atomic entity-file path, now per-entity-group (already generalized
in #236).

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: `reroll` must never mutate a step outside the downstream set, and must never
invalidate the proposal id.

**Scale/Scope**: top-level-request reroll only (spec.md Assumptions) — no internal-step reroll,
no Omen-carryover interaction.

## Constitution Check

- No setting/system names — `reroll`, `resolve`/`fortune`/`bargain` are the engine's own closed
  vocabulary, matching `docs/design/03-rules.md` §§3-4 and `31-action-resolution.md`.
- Deterministic over inference — every worked example is freshly computed with a disclosed seed
  (`research.md`), never asserted.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: this feature implements what `docs/design/31-action-resolution.md` (design already
  landed, #193) already specifies.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/084-partial-reroll/
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
└── resolution.py      # extended: propose_batch, _stage_request (shared), reroll,
                        # _downstream_set, _renumber_and_merge, RESOURCE_MODIFIERS/COSTS

tests/engine/
└── test_resolution.py  # extended with reroll test classes
```

**Structure Decision**: No new files beyond continuing to extend `resolution.py` and its test
module — additive to #235/#236's existing structure.

## Complexity Tracking

*No violations — table omitted.*
