# Implementation Plan: Elapsed time and the advance-time command

**Branch**: `130-advance-time` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/130-advance-time/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/advance_time.py` module: `advance_calendar` (pure day/year arithmetic,
365-day years) and `advance_time` (the combined operation `close_downtime`'s own scope note
deferred to "elsewhere" -- computes each Threat's expected-value activation count over the span
and resolves that many effects-table rolls via `threat.resolve_effects`, seeded for
reproducibility via `rules.roll_d100`).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: `wyrd.threat` (`resolve_effects`), `wyrd.rules` (`roll_d100`, for
seeded, reproducible dice).

**Storage**: N/A — plain dicts/lists in, plain dicts out; no `chronicle.yaml` I/O (caller
persists the returned calendar via `state.save_chronicle`, matching `chronicle.py`/`era.py`'s
existing convention).

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by `close_downtime`'s caller (#311) and by
`journey.resolve_leg`'s summarised-leg path (#287) — both currently defer to "elsewhere".

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of arithmetic operations and seeded rolls per Threat per
elapsed span.

**Constraints**: ruff-clean repo-wide; advancing time stays the only calendar-forward path
(FR-005) — no second mechanism introduced.

**Scale/Scope**: calendar arithmetic and per-Threat expected-value activation/effects
resolution. Out of scope: CLI wiring (no precedent exists for any chronicle-level operation, per
spec.md's Assumptions), entity-store-wide active-Threat scanning (caller's job, matching every
sibling module).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `calendar`, `elapsed`, `imminence`, `activation` are
  all existing engine-neutral terms already in docs/design/19-campaign.md/22-state.md. PASS.
- Deterministic over inference (ADR 0005) — the expected-value formula is a pure arithmetic
  computation; the only randomness (effects-table rolls) is seeded and reproducible (FR-004).
  PASS.
- No second calendar-advance mechanism introduced (FR-005, docs/design/19-campaign.md's explicit
  "closing the session advances nothing" statement). PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/130-advance-time/
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
└── advance_time.py        # NEW: advance_calendar, expected_activation_count, advance_time

tests/engine/
└── test_advance_time.py    # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
