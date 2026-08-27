# Implementation Plan: Fix the Strain-threshold check so a success cannot erase a Trauma crossing

**Branch**: `178-strain-threshold-catchup-fix` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

ADR 0045's crossing check compared a failed invocation's own before/after Strain — a delta
scoped to one roll — which let a success permanently erase a boundary crossing for every failure
after it. ADR 0047 supersedes ADR 0045: the check now reads the character's current, cumulative
Strain directly on a failure (`gained = (strain - 1) // max_stamina`), needing no separate
bookkeeping, since Strain is only ever reduced at the moment it is charged. `03-rules.md` and
`09-systems-of-power.md` restate the rule; `check_spam_brake.py` re-verifies every existing
property plus a new direct demonstration that the corrected check strictly out-charges the
superseded one on the exact sequences that found the bug. A new §16 in
`docs/design/30-playtest-transcript.md` states the corrected §10/§14/§15 figures with real
seeded rolls (same seeds), without editing the originals.

## Technical Context

**Language/Version**: Python 3 (verification script only; no engine code).

**Testing**: `python3 specs/057-systems-of-power-spam-brake/check_spam_brake.py`,
`python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: ADR 0045 is Accepted and merged — must be superseded, not edited (FR-004). The
corrected check must never give less Trauma than the superseded one on any sequence (FR-006). No
change to failure-only gating, the modulus, or the disabled-track note (unchanged from ADR 0045).

**Scale/Scope**: One superseded ADR move + `Status:` edit, one new ADR, one
`docs/adr/superseded/README.md` index entry, one `docs/README.md` index edit, two design-doc
rule restatements, one verification script rewrite, one new playtest-transcript section.

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — a separate "already charged"
  counter alongside Strain was implemented first and found subtly wrong; the simpler cumulative
  form is the adopted one. Earns the ADR. PASS.
- **An accepted ADR is never edited** — ADR 0045 is superseded, not amended in place, per this
  repo's own rule; 0045 moves to `docs/adr/superseded/` with only its `Status:` line changed.
  PASS.
- **Design documents rewritten in place** — `03-rules.md`/`09-systems-of-power.md` restate the
  rule in place; the playtest transcript's original sections are left untouched, with a new
  section stating the correction, matching the precedent §14 already set. PASS.
- **Deterministic over inference** — the fix is verified against the exact sequences that
  exposed the bug, showing the corrected check strictly out-charges the superseded one, not
  merely asserted to fix it. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/061-strain-threshold-catchup-fix/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0047-strain-threshold-crossing-checks-cumulative-strain.md      # new ADR
docs/adr/superseded/0045-...-costs-trauma.md                             # moved, Status: line only
docs/adr/superseded/README.md                                            # index entry
docs/README.md                                                           # ADR index (0045 removed, 0047 added)
docs/design/03-rules.md                                                  # sec5 bullet restated
docs/design/09-systems-of-power.md                                       # cost section restated
docs/design/30-playtest-transcript.md                                    # new sec16
specs/057-systems-of-power-spam-brake/check_spam_brake.py                # corrected logic + new checks
```

## Complexity Tracking

*(empty — no constitution violations)*
