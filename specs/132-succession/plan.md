# Implementation Plan: Succession: successor selection and inheritance

**Branch**: `132-succession` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/132-succession/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/succession.py` module, matching the epic's existing division of labour
(plain dicts/lists in, plain dicts out, no I/O): `rank_candidates` (fixed six-category priority
order, stable, closed vocabulary), `propose_successors` (top three), `inherit` (the
inherited/excluded field table exactly, holdings only when explicitly passed), and
`record_predecessor` (the three post-succession outcomes).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package. No import of `threat.py`/
`thread.py` — this module reads whichever already-shaped fields a caller's predecessor dict
carries (spec.md's Assumptions), the same decoupling `holding.py` (#337) established.

**Storage**: N/A — plain dicts/lists in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called at a character-end session-orchestration point (out
of scope here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of dict/list operations over a small candidate set.

**Constraints**: ruff-clean repo-wide; the entanglement vocabulary is closed (six members,
FR-001/FR-002), matching ADR 0026's established closed-vocabulary convention for adversary
traits.

**Scale/Scope**: candidate ranking/proposal, inheritance computation, predecessor-state
recording. Out of scope: entity-store-wide candidate discovery, assigning entanglement labels
during play, the at-the-table offer/decline interaction.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `entanglement`, `wronged`, `investigating`,
  `bystander`, `rival`, `found_evidence`, `companion` are all direct, engine-neutral slugs of
  docs/design/19-campaign.md's own prose categories, none borrowed from a source system. PASS.
- Closed vocabulary for entanglement (FR-002), matching ADR 0026's precedent. PASS.
- Deterministic over inference (ADR 0005) — ranking, inheritance, and predecessor-state
  recording are all pure, deterministic transforms of caller-supplied data. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/132-succession/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (none — internal engine module, no external contract)
└── tasks.md             # Phase 2 output (kord-feature-tasks, not this command)
```

### Source Code (repository root)

```text
engine/wyrd/
└── succession.py          # NEW: rank_candidates, propose_successors, inherit, record_predecessor

tests/engine/
└── test_succession.py      # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
