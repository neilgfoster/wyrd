# Implementation Plan: Resolve recovers at a Rally, capped by Taint

**Branch**: `052-resolve-recovery-mechanic` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Fix `docs/design/03-rules.md` §4 to state Resolve's gain trigger (+1 at a Rally, full at
downtime, matching ADR 0020's existing rate), cap (current Taint plus 3), and spend (1 Resolve
for a +20 reroll bonus, distinct from Fortune's plain reroll). Record the decision as ADR 0043,
including a naive first-draft cap formula (exactly equal to Taint) that was found broken during
design and corrected before merge. Verify with `check_resolve.py`, proving the corrected formula
leaves real spendable headroom at every Taint above 0 and confirming the rejected naive version
actually fails, rather than trusting either claim unchecked.

## Technical Context

**Language/Version**: Python 3.11+ stdlib for the verification script; the rule itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 specs/052-resolve-recovery-mechanic/check_resolve.py`, `python3 -m pytest -q`.

**Constraints**: The cap formula must leave real headroom above Taint at every value (FR-002).
Taint 0's exemption from Spent must be stated explicitly, not left to the formula (FR-003). The
verification script must positively demonstrate the rejected naive alternative's failure mode,
not merely check the chosen formula (FR-004).

**Scale/Scope**: One new ADR (~85 lines), one revised paragraph in `docs/design/03-rules.md` §4,
one new ~70-line verification script.

## Constitution Check

- **Nothing unpublishable** — pure rules fix plus a verification script. PASS.
- **No setting or system names** — none introduced. PASS.
- **Decisions are recorded** — two real alternatives rejected (Taint-linked gain instead of
  Rally/downtime; a naive cap=Taint formula; a plain-reroll spend matching Fortune's); ADR 0043
  records all three. PASS.
- **Design documents rewritten in place** — §4's Resolve bullet is corrected in place, no
  changelog note. PASS.
- **Deterministic over inference** — the cap formula's correctness, and the naive alternative's
  actual failure, are both computed rather than asserted. PASS.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/052-resolve-recovery-mechanic/
├── plan.md, spec.md, tasks.md, check_resolve.py
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0043-resolve-recovers-at-a-rally-capped-by-taint.md   # new
docs/README.md                                                 # ADR index entry added
docs/design/03-rules.md                                        # sec4's Resolve bullet corrected
```

## Complexity Tracking

*(empty — no constitution violations)*
