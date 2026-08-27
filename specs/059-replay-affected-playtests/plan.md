# Implementation Plan: Re-play playtest scenarios affected by rule changes made during the playtest epic

**Branch**: `174-replay-affected-playtests` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add §14 to `docs/design/30-playtest-transcript.md`, re-deriving the three scenarios ADR
0043/0044/0045 actually touch: §7's combat exchange (re-read against ADR 0044's virtual-roll
formula, with the critical/Aftermath rolls recomputed by reusing the original dice under new
modifiers), §8's blocked Resolve exercise (replayed with fresh rolls under ADR 0043), and §10's
Resolve recurrence and spam sequence (replayed against Kester's own character under ADR
0043/0045, not only the abstract check script). The original §7/§8/§10 text is untouched.

## Technical Context

**Language/Version**: Python 3 (scratch replay scripts, not committed as engine tooling — same
precedent as prior playtest sections' own roll-generation scripts).

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Original §7/§8/§10 text must not be edited (FR-005). No new design decision
(FR-006). §7's critical/Aftermath rolls reuse the original dice under new modifiers rather than
drawing fresh, unrelated values (FR-002).

**Scale/Scope**: One new section in `docs/design/30-playtest-transcript.md`, three small replay
scripts kept under `specs/` for reference (not committed engine tooling).

## Constitution Check

- **No ADR** — this re-applies decisions already made; no new decision, no ADR needed. PASS.
- **Design documents rewritten in place** — N/A here; this adds a new section rather than
  rewriting an existing one, consistent with how every other numbered playtest section was added.
  PASS.
- **Deterministic over inference** — every claimed outcome (which roll is now telling, what the
  critical/Aftermath bands become, how much Trauma accrues) is computed by script, not asserted.
  PASS.
- **No setting or system names** — none introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/059-replay-affected-playtests/
├── plan.md, spec.md, tasks.md
├── checklists/requirements.md
└── replay_sec7.py, replay_sec8.py, replay_sec10.py
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new sec14
```

## Complexity Tracking

*(empty — no constitution violations)*
