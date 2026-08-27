# Implementation Plan: Brake on spamming a failing system-of-power invocation

**Branch**: `163-systems-of-power-spam-brake` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Resolve #163 (and, by the same decision, #172): a failed system-of-power invocation that pushes
accumulated Strain past a multiple of the character's maximum Stamina costs 1 Trauma per multiple
crossed, with Strain carrying forward at its remainder. Only a failed invocation is checked — a
success crossing the same multiple costs nothing extra. ADR 0045 records this as the second
design tried within the same decision: a first same-power-failure-streak draft was re-playtested
and found defeated outright by rotating between two known systems of power (#172); the max-Stamina
design is immune to that exploit by construction, since it never reads which power failed.
`03-rules.md` §5 and `09-systems-of-power.md` state the rule, including explicit graceful
degradation when a setting has disabled Strain and/or Trauma. `check_spam_brake.py` verifies the
spam outcome across the realistic maximum-Stamina range, the rotation-immunity property, and
failure-gating against a naive any-outcome variant.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/057-systems-of-power-spam-brake/check_spam_brake.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, `python3 -m pytest -q`.

**Constraints**: No new dice mechanic or power-specific consequence table (ADR 0036) — the rule
reuses Trauma's existing gain-trigger list and its own sawtooth shape. Must be immune to the
rotation exploit that defeated the first design (FR-006), and failure-gated, not volume-gated
(FR-002, FR-007), both verified computationally.

**Scale/Scope**: One ADR (rewritten in place within this same PR, since it had not yet merged —
not a supersession of a landed decision), one `03-rules.md` §5 bullet, one
`09-systems-of-power.md` section (cost rule + disabled-track note), one verification script, one
playtest-transcript note, `docs/README.md`'s ADR index entry.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — the same-power-streak design, a
  flat engine-wide threshold, an any-outcome trigger, and a disabled-track fallback are all
  workable and were each considered in turn. Earns an ADR. PASS.
- **Design documents rewritten in place** — `03-rules.md`/`09-systems-of-power.md` are edited in
  place. The ADR file itself is edited in place too, since PR #171 (which introduced it) had not
  merged when the design changed — this is drafting, not amending an Accepted decision. PASS.
- **Deterministic over inference** — the rule's effect, its failure-gating, and its
  rotation-immunity are all verified by direct computation, not asserted. PASS.
- **No setting or system names** — none introduced. PASS.
- **One configurable power mechanism (ADR 0036)** — no new dice roll, no new table; reuses
  Trauma's existing gain-trigger list and sawtooth shape, and explicitly declines to invent a
  fallback consequence for a disabled track. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/057-systems-of-power-spam-brake/
├── plan.md, spec.md, tasks.md
├── checklists/requirements.md
└── check_spam_brake.py
```

### Repository changes

```text
docs/adr/0045-failed-invocation-crossing-max-stamina-in-strain-costs-trauma.md   # ADR (rewritten in place, pre-merge)
docs/README.md                                                                    # ADR index entry
docs/design/03-rules.md                                                           # sec5 Trauma-gain bullet
docs/design/09-systems-of-power.md                                                # cost section + disabled-track note
docs/design/30-playtest-transcript.md                                             # sec10 resolution note
```

## Complexity Tracking

*(empty — no constitution violations)*
