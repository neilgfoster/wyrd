# Implementation Plan: Assistance, group tests and extended tasks

**Branch**: `011-assistance-and-group-tests` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Add three missing shapes of test to `03-rules.md` §1, record the decisions as one ADR, and compute
the two numbers that decide whether any of it works.

## The load-bearing decisions

**Assistance is one helper, and the helper's own skill sets the size.** The stacking failure is
closed by FR-2 rather than by arithmetic: extra hands never add. What is left is a scale — some
fraction of the helper's skill — and it has two competing duties. It must be **worth asking for**,
or nobody will help and the rule is dead text. It must **never turn a rung of the difficulty ladder
into the rung above it**, or the ladder stops meaning anything. The smallest ladder step is 10 and
the largest 20, so the ceiling is +20 and the interesting question is the divisor.

**An extended task's target is a degree count, and the target scale is a computation.** Degrees are
`tens(skill) − tens(roll)`, so a character at 45% clears roughly one degree per interval once
failures are counted in. A target of 10 is therefore *ten rolls* — the design's own "only roll when
it is dramatic" turned into a chore. The target scale must be derived from expected degrees per
interval at realistic skills, not chosen because 5/10/20 looks tidy.

## What the check script has to settle

`check_assistance.py`, stdlib only, exact arithmetic:

1. **The assistance divisor.** Model helper bonus as `skill // n` capped at 20, for the candidate
   divisors, across actor skills 25–65 and every rung of the difficulty ladder. Report the lift at
   each rung and reject any divisor that lifts a rung to or past the rung above it.
2. **Naive stacking, for contrast.** The same table with a flat bonus per helper at party sizes
   2–5, showing what FR-2 is buying.
3. **Expected degrees per interval**, at realistic skills, and from it the number of intervals each
   candidate target implies. The target scale is whatever keeps a long task to a handful of beats.

Anything the script reveals about combat is **reported, not asserted** — that is #44's to act on.

## The shapes, as planned

**Assistance.** One helper, who must be able to do the task and must contribute something specific.
Helpers do not roll. The bonus derives from the helper's own skill, capped at +20. Extra hands are
fiction, and may move the GM's difficulty; they are never arithmetic.

**Group tests.** Two named shapes, one roll each — the "one rolls with modifiers" answer to FR-4:

- *A led action*, where the party achieves one thing together: the most capable acts, and
  assistance applies normally.
- *A test everyone must clear*, where each member must get past: the **least capable** member's
  skill is tested, with the most capable assisting.

Which shape applies is a question about the fiction — must everyone succeed, or must the thing get
done — and the rule says so rather than leaving it to the table.

**Extended tasks.** A long task accumulates degrees toward a target. One test per interval named by
the fiction. A success adds its degrees, minimum 1, so a success never stalls the work. A failed
interval is spent and gains nothing. The Wyrd die is read per interval as normal — each interval is
an ordinary test, which is why FR-7 survives untouched.

## Steps

1. `check_assistance.py` — settle the divisor and the target scale; assert only what this feature owns.
2. `03-rules.md` §1 — assistance, group tests, extended tasks, each preserving the natural-roll rule.
3. ADR 0017 — the three decisions and the rejected alternatives (flat bonus, diminishing stack,
   everyone-rolls, and no-extended-tasks-at-all).
4. `check_docs.py` and `backlog.py check` green; findings for #44 recorded on the issue.

## Risks

**Extended tasks are the shape most likely to be wrong on paper.** The engine has been playtested
once, and this is a mechanic whose cost only shows up over several sessions. The mitigation is the
interval rule: if an interval is not worth a beat of prose, it is not worth a roll, and the task was
a single test all along.

**"Least capable" needs a judgement per group test** — whose skill, and does the character with no
relevant skill at all sit at the untrained 10%. The rule must answer that explicitly or it will be
answered differently each session.
