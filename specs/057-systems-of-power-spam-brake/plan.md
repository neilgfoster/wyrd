# Implementation Plan: Brake on spamming a failing system-of-power invocation

**Branch**: `163-systems-of-power-spam-brake` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Resolve #163: a failed system-of-power invocation immediately following another failed invocation
of the *same* system of power, in the same scene, now costs 1 Trauma in addition to its stated
Strain/Resolve cost (ADR 0045). The first failure of a scene is free; a success or a failure of a
different power resets the streak. `03-rules.md` §5 gains the Trauma-gain bullet;
`09-systems-of-power.md`'s cost section states and cross-references it.
`check_spam_brake.py` re-runs a comparable spam sequence to #151's playtest and confirms the rule
produces real Trauma (crossing the Affliction threshold) on spam while leaving ordinary play
(one isolated failure among successes) untouched.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/057-systems-of-power-spam-brake/check_spam_brake.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, `python3 -m pytest -q`.

**Constraints**: No new dice mechanic or power-specific consequence table (ADR 0036) — the rule
reuses Trauma's existing gain-trigger list. The fix must be shown to change the outcome (FR-004)
and not fire on ordinary play (FR-005), both verified computationally.

**Scale/Scope**: One new ADR, one `03-rules.md` §5 bullet, one `09-systems-of-power.md` paragraph,
one new verification script, one playtest-transcript note, `docs/README.md`'s ADR index entry.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — a Strain cap/threshold and an
  escalating retry cost are both workable, and were presented as options before this direction was
  chosen. Earns an ADR. PASS.
- **Design documents rewritten in place** — `03-rules.md`/`09-systems-of-power.md` are edited
  in place, not appended with a changelog note. PASS.
- **Deterministic over inference** — the rule's effect is verified by a seeded replay, not
  asserted. PASS.
- **No setting or system names** — none introduced. PASS.
- **One configurable power mechanism (ADR 0036)** — no new dice roll, no new table; reuses
  Trauma's existing gain-trigger list. PASS.

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
docs/adr/0045-repeated-failed-invocations-cost-trauma.md   # new ADR
docs/README.md                                              # ADR index entry
docs/design/03-rules.md                                     # sec5 Trauma-gain bullet
docs/design/09-systems-of-power.md                          # cost section paragraph
docs/design/30-playtest-transcript.md                       # sec10 resolution note, sec13 status update
```

## Complexity Tracking

*(empty — no constitution violations)*
