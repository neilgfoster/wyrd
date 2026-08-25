# Implementation Plan: Opposed test resolution

**Branch**: `010-opposed-tests` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Replace one sentence in `03-rules.md` §1 with a five-part rule, record it as ADR 0016, and compute
the consequence that made the original dangerous.

## The load-bearing decision

**A failed roll has no degrees.** Everything else in the rule is tidying; this is the one that
changes play. Degrees go negative on a failure, and the margin is a *difference* of degrees, so a
badly-failed defence would hand the attacker an enormous margin.

Modelled across realistic skills, that reading makes about **three quarters** of successful attacks
telling blows. Zeroing a failed roll roughly halves it. Neither number is visible by reading the
prose, which is the argument for `check_opposed.py` existing at all.

## What this deliberately does not decide

The telling-blow threshold. Section 2 sets it at a win by 3+ degrees, and under the corrected rule
that is impossible at starting skills and the majority of hits at practised ones. That curve is
almost certainly wrong, and it is **combat's number** (#44). This feature makes the margin honest
enough to judge it; it does not judge it.

## A correction to merged work

`check_creation.py` asserted "an armoured fight resolves in 4.50 exchanges" and used it to justify
starting Stamina against the session-length requirement. **That is hits-to-drop.** Converting hits to
exchanges needs the hit probability this feature computes, and the real figure is 11–28 exchanges.

The claim is corrected to report rather than assert, because creation cannot fix it — Stamina is not
the lever on fight length, the hit rate is. Both facts are recorded against #44.

Left as an assertion it would be a merged, passing check making a false claim, which is the fault
class this whole programme exists to remove.

## Steps

1. `check_opposed.py` — model both rules; assert only what this feature owns.
2. `03-rules.md` — the five-part rule and the acting-side definition.
3. ADR 0016.
4. Correct `check_creation.py`; record both findings on #44.

## Risks

**The acting/resisting asymmetry needs a judgement per test.** Usually obvious — an attacker attacks
— and genuinely ambiguous for a race, which the rule handles by saying that is not an opposed test.
