# Implementation Plan: Playtest minor-tier systems-of-power spam, the typical caster-in-an-encounter case

**Branch**: `176-minor-tier-spam-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add §15 to `docs/design/30-playtest-transcript.md`: Kester spams `minor`-tier `ember-craft`
across a 26-attempt sequence (real seeded rolls, seed `20260850`), directly comparable to §10/
§14's `major`-tier sequence. Result: only 29% of failures cross ADR 0045's Trauma threshold (vs.
near-100% at major tier), confirming the threshold behaves as intended at a realistic tier — the
major-tier near-certainty is a disclosed, tier-specific property, not a general flaw. No new
design decision.

## Technical Context

**Language/Version**: Python 3 (scratch replay script, not committed engine tooling).

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: No new design decision (FR-004). Crossing rate stated as a fraction of real
failures, not asserted from arithmetic (FR-002).

**Scale/Scope**: One new section in `docs/design/30-playtest-transcript.md`, one replay script
kept under `specs/` for reference.

## Constitution Check

- **No ADR** — this is a confirmatory playtest pass, not a new decision. PASS.
- **Deterministic over inference** — the crossing rate is computed from a real seeded sequence,
  not asserted from the strain_cost/maximum-Stamina arithmetic alone. PASS.
- **No setting or system names** — none introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/060-minor-tier-spam-playtest/
├── plan.md, spec.md, tasks.md
├── checklists/requirements.md
└── replay_minor_spam.py
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new sec15
```

## Complexity Tracking

*(empty — no constitution violations)*
