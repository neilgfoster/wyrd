# Implementation Plan: Specify the attack → damage → armour → critical chain through propose/commit

**Branch**: `200-combat-chain-propose-commit` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Restate `31-action-resolution.md`'s "Cascading resolution" section to name two trigger shapes
(mutation-crosses-threshold; roll-outcome-calls-for-a-further-roll), both staging identically.
Add "The combat resolution chain" specifying the attack/damage/armour/critical mapping, and a
worked example reusing the real rolls already verified in §7/§14 of the playtest transcript.
Remove `wyrd damage` from `02-architecture.md`'s CLI sketch (superseded by `propose`) and update
its known-follow-up note to reference the still-outstanding generic-tracker case only.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Must not touch Aftermath's own deferred-consequence status (FR unchanged from
#194). Worked example reuses already-verified rolls (SC-003), not fresh dice.

**Scale/Scope**: `docs/design/31-action-resolution.md`'s Cascading resolution section (restated)
and a new subsection; `docs/design/02-architecture.md`'s CLI sketch and known-follow-up note.

## Constitution Check

- **No ADR** — generalises ADR 0050's/#194's already-accepted reasoning; no new decision. PASS.
- **Design documents rewritten in place** — the existing section is restated, not appended with
  a changelog note. PASS.
- **Deterministic over inference** — the worked example reuses figures already verified twice,
  not fresh unverified arithmetic. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/071-combat-chain-propose-commit/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/31-action-resolution.md   # Cascading resolution restated; new combat-chain subsection
docs/design/02-architecture.md        # wyrd damage removed; known-follow-up note updated
```

## Complexity Tracking

*(empty — no constitution violations)*
