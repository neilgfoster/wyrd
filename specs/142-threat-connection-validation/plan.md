# Implementation Plan: Every seeded Threat carries a personal connection

**Branch**: `142-threat-connection-validation` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/142-threat-connection-validation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`threat.py` gains `validate_connections(threats: list[dict]) -> list[str]`: reports every Threat
whose `connection` is absent, `None`, empty, or whitespace-only, by id, never raising.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none.

**Storage**: N/A — plain dicts/list in, plain list of strings out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library (`threat.validate_connections`), called by bootstrap-seeding
or maintenance tooling (out of scope here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A.

**Constraints**: ruff-clean repo-wide; never raises (FR-003), report-don't-raise convention.

**Scale/Scope**: one validation function. Out of scope: threat selection, connection assignment.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `connection` already named in
  docs/design/19-campaign.md. PASS.
- Deterministic over inference (ADR 0005) — a pure presence/blankness check. PASS.
- Report-don't-raise, matching #327's existing passive-validation precedent. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/142-threat-connection-validation/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/ (none)
```

### Source Code (repository root)

```text
engine/wyrd/threat.py          # gains validate_connections
tests/engine/test_threat.py    # extended: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
