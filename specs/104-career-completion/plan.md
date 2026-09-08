# Implementation Plan: Career completion grants Stamina and a Mark

**Branch**: `104-career-completion` | **Date**: 2026-09-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/104-career-completion/spec.md`

## Summary

#277 built the spend transaction and left the payout out of it deliberately: `career.py` already
answers "is this career complete", and `advancement.py` already calls it, but only to stamp a
`completed` flag on a departing career-history entry. This feature makes the completion *pay*.

The payout rides on the existing `spend_advance` transaction rather than becoming a fourth verb:
a completion is not something a character chooses, it is a consequence of the raise or open that
finished the last skill. So `advancement.py` gains a completion check after a successful skill
spend, and the character view it reads and returns gains the three fields the payout touches —
maximum Stamina, Marks, and whether *this* career-instance has already been paid.

That last field also corrects something #277 shipped: `_spend_change_career` recomputes
`career_complete(skills, career)` at the moment of departure, so a wound that lowered a skill
after the career was finished would write `completed: false` into history and silently revoke a
prerequisite the character had genuinely earned. History is never recomputed
(`docs/design/29-evolution.md`); the departure record now reads the flag the payout set.

## Technical Context

**Language/Version**: Python 3.11+ (stdlib-only)

**Primary Dependencies**: None new — `advancement.py` already depends on `career.py`

**Storage**: None written here. The verb computes a new character view; the caller persists it.
The three new view fields map onto `stamina.max` and `marks` in
`docs/design/22-state.md`'s character frontmatter, which already exist.

**Testing**: `pytest`, run under `PYTHONPATH=engine`

**Target Platform**: CLI / library, cross-platform

**Project Type**: Single project — `engine/wyrd` library plus its `wyrd` CLI

**Performance Goals**: N/A — one comparison per granted skill per spend

**Constraints**: stdlib-only; no spend may mutate its inputs; the ceiling and the starting value
are `tools/check_advancement.py`'s figures and are asserted against it, never restated by eye

**Scale/Scope**: One module changed substantively, one catalog description widened, one design
document sentence to reconcile, and tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): completion is a comparison per granted skill; the
  ceiling is a `min`. The one thing left to judgment — what the Mark *means* in the fiction — is
  the GM's, exactly as a career change's reason is. Pass.
- **No setting/system vocabulary**: "Mark" and "Stamina" are the engine's own descriptive labels,
  already in `docs/design/03-rules.md`. Test careers reuse the design document's own worked
  example. Pass.
- **Design documents describe the present**: `docs/design/03-rules.md` §6 already states this rule
  in full, so no design change is needed for the rule itself. One reconciliation *is* needed —
  §6 does not say *when* the payout fires, and the engine now answers that. See research.md R1.
- **Assert prior numbers**: SC-001 and SC-003's figures (start 6, ceiling 10, 12 instances → 12
  Marks) are `tools/check_advancement.py`'s. The tests import that module and assert agreement
  rather than hard-coding a second copy of figures that have drifted before. Pass.
- **Rule changes apply forward only**: the payout is recorded when it happens and never
  recomputed; this feature *removes* the one recompute #277 left in. Pass.
- **Capability change goes through Spec Kit**: this plan. Pass.

No violations — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/104-career-completion/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # spec quality checklist
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: the verb's shape is already contracted in
`specs/103-spend-advances/data-model.md` and this feature only widens the view it carries, which
`data-model.md` describes inline.

### Source Code (repository root)

```text
engine/
└── wyrd/
    ├── advancement.py    # + STAMINA_MAX_CEILING, completion payout inside spend_advance,
    │                     #   widened new_view/_view, departure reads the paid flag
    ├── career.py         # career_complete: a career granting nothing is not complete
    └── catalog.py        # spend-advance description names the payout
tests/engine/
├── test_advancement.py   # + payout, per-instance, ceiling, refusal-purity
└── test_career.py        # + the empty-grant career
docs/design/
└── 03-rules.md           # when the payout fires, and that it is per-instance-once
```

**Structure Decision**: No new verb and no new module. The payout has no inputs the spend does not
already have, and a `complete-career` verb would let a caller claim a completion the engine never
saw happen — the opposite of "the engine can verify an award rather than the GM being generous by
accident". `career.py` keeps owning the predicate; `advancement.py` keeps owning the currency and
now owns what the currency's completion buys.
