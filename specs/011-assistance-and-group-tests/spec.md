# Feature Specification: Assistance, group tests and extended tasks

**Feature Branch**: `011-assistance-and-group-tests`

**Created**: 2026-08-25

**Status**: Clarified

**Input**: GitHub issue #53 (R1.8), under Stage 4 (#43). Out of scope: opposed tests, completed by
#7 in `specs/010-opposed-tests`; the telling-blow threshold, which is combat's (#44).

## Context

**Assistance, group tests and extended tasks return zero matches across every design document.**
The core roll, the difficulty ladder, the declaration bonuses, the Wyrd die and the opposed test
are all specified. The shapes that sit between them are not.

This matters more here than in a table game. The player runs one character and the GM runs the
whole rest of the party, so almost every non-trivial action has companions in it: someone holds the
rope, someone else keeps watch, and the party crosses the ford together. **The most-used part of
the system after the core roll is the part that does not exist**, and in its absence each session
invents it again — which is the fault class the design programme exists to close.

Two pressures shape every answer below.

**Stacking.** Assistance is the one shape with an arithmetic failure mode. If each willing
companion adds to the skill, a party of four turns a Hard test into a formality, and the difficulty
ladder stops meaning anything. The size of that failure is a computation, not an opinion.

**Roll count.** A group of five rolling five times contradicts *only roll when it is dramatic*, and
costs five lines of prose for one beat. Sessions happen on a phone.

## Clarifications

### Session 2026-08-25

- **Q: Extended and prolonged tasks — build the mechanic, or reject it in an ADR?**
  A: Build an accumulating mechanic. Repeated tests accumulate degrees toward a target.
- **Q: What should a helper grant on an assisted test?**
  A: The helper's own skill sets the bonus, on a scale, capped.

## Requirements

### FR-1 — Assistance is specified

Who may help, what help must consist of, and what it grants. A helper must be **able to do the
task** and must contribute something **specific**; generic encouragement is not assistance.

### FR-2 — Assistance does not stack

Additional helpers beyond the one who is actually helping do not add to the number. Extra hands
change the fiction — and may change the *difficulty* the GM sets — but they do not accumulate a
bonus.

### FR-3 — The helper's own skill sets the size of the bonus

A master's hand is worth more than a novice's. The bonus is derived from the helper's own skill in
the relevant skill, on a stated scale, and is capped. The scale and the cap are chosen by
computation, not by preference.

### FR-3a — The bound is computed

The chosen rule is demonstrated not to trivialise a difficult test at realistic party sizes
(2–5 characters) and realistic skills, by computing the success rate under the chosen rule and
under naive stacking, rather than asserting the difference.

### FR-4 — Group tests are specified

The engine states which of the three shapes it uses — everyone rolls, one rolls with modifiers,
or the party rolls as a unit — and does not leave the choice to the table.

### FR-5 — A group test is one roll

Whatever the shape, a group action resolves in a single test. The party's composition is expressed
in the *skill tested* and the modifiers to it, never in the number of dice thrown.

### FR-6 — Extended tasks accumulate toward a target

A long task is specified as a mechanic, not rejected. Repeated tests accumulate degrees of success
toward a stated target; the task completes when the target is reached. The specification must state
the target scale, what one interval of work costs in fiction and time, what a failed interval does,
and when an extended task is called for at all rather than a single test.

### FR-6a — An extended task stays cheap in prose

*Only roll when it is dramatic* still binds. The rule must say what makes an interval worth a roll,
so a long task is a handful of beats rather than a roll per hour.

### FR-7 — The Wyrd die survives every added shape

One test, one omen, read from the units digit of the natural roll, unmodified and unrerolled — in
assisted, group and extended tests alike. No shape may introduce a second omen or a rerolled one.

### FR-8 — The three axes stay independent

Every shape modifies the **skill**, never the roll — the property that keeps success, degrees and
the Wyrd die independent (ADR 0001).

### FR-9 — The design documents are updated, not merely the spec

`design/03-rules.md` carries the rules as the engine's description; the ADR carries the rejected
alternatives. The spec is not left as the only record.

## Constraints

- Setting-agnostic: no setting or system name in `design/` or `README.md`; engine labels are
  descriptive English.
- The core roll, the difficulty ladder and the degree scale from ADR 0001 are not replaced.
- No threshold belonging to combat is set here.
- Python 3.11+, stdlib only, exact arithmetic (`Fraction`) for any computation.
- `check_docs.py` and `backlog.py check` stay green.

## Assumptions

- **Helpers do not roll.** A second roll would raise a second Wyrd die and a second failure, which
  FR-5 and FR-7 both forbid. Assistance resolves as a modifier to the acting character's skill.
- **Still one helper.** FR-2 stands: the helper's skill sets *how large* the bonus is, not how many
  bonuses there are. Extra hands remain fiction and difficulty, never arithmetic.
- **An extended task's intervals are separate tests.** Each interval is one test with its own
  natural roll and therefore its own Wyrd die — which is consistent with FR-7, not an exception to
  it. FR-5's single-roll rule governs a *group* test, not the interval count of a long task.
- Realistic party size is 2–5 including the player's character; realistic tested skills run roughly
  25–65%.

## Acceptance criteria

- [ ] `03-rules.md` specifies assistance: eligibility, what help must consist of, what it grants,
      and what extra helpers do instead of stacking.
- [ ] `03-rules.md` specifies group tests, naming the shape used and the skill tested.
- [ ] `03-rules.md` specifies extended tasks: the target scale, the interval, what a failed
      interval costs, and when a long task earns the mechanic at all.
- [ ] An ADR records the assistance and group-test decisions and the rejected alternatives.
- [ ] A check script computes assisted success rates under the chosen rule and under naive
      stacking, across party sizes 2–5 and realistic skills, and demonstrates the difficulty ladder
      still bites.
- [ ] The check asserts only what this feature decides; anything it reveals about combat is
      reported as a finding for #44, not asserted.
- [ ] Every added shape states, or visibly preserves, the natural-roll rule.
- [ ] `check_docs.py` and `backlog.py check` pass.
