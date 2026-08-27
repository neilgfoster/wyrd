# Implementation Plan: Decide whether reroll resources may stack unbounded on one roll

**Branch**: `167-reroll-stacking-deliberate` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Resolve #167: Fortune, Resolve, and the Bargain may all be spent against the same original failed
roll, with no engine-imposed cap — a deliberate decision (ADR 0046), not a silent gap. `03-rules.md`
§3 and §4 both state this explicitly, cross-referencing each other and the new ADR. No new
verification script — #153's own seven-trial playtest record (one trial failed even after the
full stack was spent) already serves as the evidence this decision relies on.

## Technical Context

**Language/Version**: N/A — documentation-only decision, no script.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Must not change how Fortune, Resolve, or the Bargain work individually (FR-004).
Must reference #153's existing evidence rather than re-deriving it (FR-003).

**Scale/Scope**: One new ADR, two `03-rules.md` cross-referencing statements (§3, §4), one
playtest-transcript resolution note plus a §13 synthesis-table update, `docs/README.md`'s ADR
index entry.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — a per-test cap on reroll
  resources is workable and was seriously weighed. Earns an ADR even though the status quo is
  kept, per the issue's own Definition of Done. PASS.
- **Design documents rewritten in place** — `03-rules.md`'s existing Fortune/Bargain prose gains
  the new statement in place, not appended as a changelog note. PASS.
- **No setting or system names** — none introduced. PASS.
- **Deterministic over inference** — the decision cites #153's own already-computed seven-trial
  evidence rather than asserting a new claim without support. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/058-reroll-stacking-deliberate/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0046-reroll-resources-stack-unbounded-on-one-roll.md   # new ADR
docs/README.md                                                    # ADR index entry
docs/design/03-rules.md                                           # sec3, sec4 statements
docs/design/30-playtest-transcript.md                             # sec12 resolution note, sec13 status update
```

## Complexity Tracking

*(empty — no constitution violations)*
