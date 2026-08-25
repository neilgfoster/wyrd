# Feature Specification: Opposed test resolution

**Feature Branch**: `010-opposed-tests`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #7 (R1.7), under Stage 4 (#43). Out of scope: assistance, group tests and
extended tasks (#53, the stage's other child), and the telling-blow threshold, which is combat's
(#44).

## Context

Opposed tests carry the whole weight of combat — "attacks are opposed tests" — on one sentence:

> both roll; the higher degree of success wins; ties to the defender. The acting side reads the
> Wyrd die.

It reads complete and leaves two questions unanswered, both consequential.

**What if the acting side fails?** The comparison still runs, so a missed attack could win.

**What are the degrees of a failed roll?** Degrees are `tens(skill) − tens(roll)`, negative on a
failure, and subtracting a negative inflates the margin the telling blow reads. Computed, this makes
**about three quarters of successful attacks telling blows** — doubled damage as the ordinary
result of hitting someone, entirely invisible in the prose.

## Requirements

### FR-1 — The acting side must succeed

On a failure the action fails, with no comparison. The resisting side need not roll.

### FR-2 — A failed roll has no degrees

Zero, not a negative. This is the rule that decides how often damage doubles.

### FR-3 — Ties go to the resisting side

Preserved from the original sentence.

### FR-4 — One Wyrd die per test

Only the acting side reads it, however many dice were thrown.

### FR-5 — The acting side is defined

Whoever is trying to change the situation. Where neither is, it is not an opposed test.

### FR-6 — The consequences are computed

Both candidate rules modelled across realistic skills, and the choice justified by the numbers
rather than by preference.

### FR-7 — The fight-length error is corrected

`check_creation.py` labelled hits-to-drop as "exchanges" and asserted a fight fits a twenty-minute
session on that basis. It ignores the miss rate and understates fight length three- to six-fold.
Correct it, and hand the consequence to the stage that can act on it.

## Constraints

- The degree scale from ADR 0001 is not replaced.
- No threshold belonging to combat is set here.
- Python 3.11+, stdlib only, exact arithmetic (`Fraction`).
- `check_docs.py` and `backlog.py check` stay green.

## Acceptance criteria

- [ ] `03-rules.md` states the five-part rule, with the acting side defined.
- [ ] An ADR records the decision and the rejected readings.
- [ ] `check_opposed.py` models both rules and demonstrates why one is rejected.
- [ ] The check asserts only what this feature decides.
- [ ] The telling-blow rate is reported as a finding for #44, not asserted.
- [ ] `check_creation.py`'s "exchanges" claim is corrected.
- [ ] The fight-length and telling-blow findings are recorded against #44.
