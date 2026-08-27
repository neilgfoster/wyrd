# Implementation Plan: Systems-of-power costs paid only on a failed invocation

**Branch**: `180-cost-paid-only-on-failure` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

ADR 0048: both `strain_cost` and `resolve_cost` are now paid only when an invocation fails — the
engine's only win-or-lose exception is removed, matching Strain's own generic failure-driven
definition (`03-rules.md` §5), and `resolve_cost` follows `strain_cost` rather than the two
fields diverging. `09-systems-of-power.md`'s Resolution section, Trauma-threshold paragraph, and
both worked examples are updated (also fixing an unrelated pre-existing "Strain drops" wording
bug found while editing the same sentence). `check_spam_brake.py` is rewritten for failure-only
accrual, re-verifying every existing property plus a new direct comparison against the
superseded win-or-lose rule on the exact sequences already on record. A new playtest section
replays the major/minor-tier spam sequences, the "ordinary use" worked example, and the
Resolve-recurrence check under the corrected timing.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/057-systems-of-power-spam-brake/check_spam_brake.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Does not touch ADR 0036's schema or ADR 0047's crossing-check logic — only cost
timing changes (FR-001–FR-003). `resolve_cost` must follow `strain_cost`'s timing exactly
(FR-002). Every affected scenario re-derived with real rolls (FR-006).

**Scale/Scope**: One new ADR, one `docs/README.md` index entry, `09-systems-of-power.md`'s
Resolution section + Trauma-threshold paragraph + both worked examples, one verification-script
rewrite, one new playtest-transcript section.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — keeping win-or-lose, or
  splitting Strain/Resolve timing, are both workable and considered. Earns the ADR. PASS.
- **Design documents rewritten in place** — `09-systems-of-power.md` is edited in place; the
  playtest transcript's prior sections are left untouched, with a new section stating the
  correction, matching the precedent §14/§16 already set. PASS.
- **Deterministic over inference** — the change's impact is verified against the exact sequences
  already on record, not asserted (FR-006, SC-003). PASS.
- **No setting or system names** — none introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/062-cost-paid-only-on-failure/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0048-system-of-power-costs-paid-only-on-failure.md   # new ADR
docs/README.md                                                  # ADR index entry
docs/design/09-systems-of-power.md                              # Resolution, Trauma paragraph, worked examples
docs/design/30-playtest-transcript.md                            # new sec17
specs/057-systems-of-power-spam-brake/check_spam_brake.py        # failure-only accrual + new checks
```

## Complexity Tracking

*(empty — no constitution violations)*
