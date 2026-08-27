# Implementation Plan: Widen Resolve to counter both Taint and Trauma

**Branch**: `185-resolve-dual-threshold` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

ADR 0049 supersedes ADR 0043: Resolve's cap becomes `max(Taint, Trauma) + 3`, and Spent triggers
when Resolve falls to at or below whichever of Taint or Trauma is higher, with each axis's
zero-exemption independent. `03-rules.md` §4 restates the rule. `check_resolve.py` is extended
to verify the dual-threshold formula and both exemptions, including the Trauma-higher case ADR
0043's own verification never exercised — catching a real bug in the process (the script's first
`is_spent` draft used exact equality instead of "at or below," which would have wrongly reported
"not Spent" once Resolve descended past a threshold). A new playtest section works through a
character where Trauma is the binding threshold.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/052-resolve-recovery-mechanic/check_resolve.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: No change to Resolve's recovery cadence, spend amount, or distinction from
Fortune (FR-001–FR-003 only touch the cap/Spent formula). ADR 0043 is Accepted and merged —
superseded, not edited (FR-004).

**Scale/Scope**: One superseded ADR move + `Status:` edit, one new ADR, one
`docs/adr/superseded/README.md` index entry, one `docs/README.md` index edit,
`03-rules.md` §4's cap/Spent paragraph, one verification-script rewrite, one new playtest
section.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — the dedicated-track option was
  seriously investigated and rejected for a stated reason (resource-economy inflation). Earns the
  ADR. PASS.
- **An accepted ADR is never edited** — ADR 0043 is superseded, not amended in place. PASS.
- **Design documents rewritten in place** — `03-rules.md`'s existing cap/Spent paragraph is
  rewritten; the playtest transcript gains a new section rather than editing a prior one. PASS.
- **Deterministic over inference** — the dual-threshold formula and both exemptions are verified
  computationally, including the case ADR 0043's own script never exercised. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/064-resolve-dual-threshold/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0049-resolve-counters-both-taint-and-trauma.md      # new ADR
docs/adr/superseded/0043-...-capped-by-taint.md               # moved, Status: line only
docs/adr/superseded/README.md                                 # index entry
docs/README.md                                                # ADR index (0043 removed, 0049 added)
docs/design/03-rules.md                                       # sec4 cap/Spent paragraph
docs/design/30-playtest-transcript.md                         # new sec18
specs/052-resolve-recovery-mechanic/check_resolve.py           # dual-threshold verification
```

## Complexity Tracking

*(empty — no constitution violations)*
