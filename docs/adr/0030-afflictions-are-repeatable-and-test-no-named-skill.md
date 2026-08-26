# ADR 0030 — Afflictions are repeatable, and the Trauma test names no skill

**Date:** 2026-08-26
**Status:** Accepted

## Context

`03-rules.md` §5 said afflictions occur on a failed test past 6 Trauma without stating the table's
contents, its uniqueness, or what the test is rolled against. Two decisions had to be made that
were not forced by the section's own text alone, and each had a real alternative a future pass
could plausibly re-propose:

1. **Whether the affliction family is unique per character or repeatable.**
   [`07-tables.md`](../design/07-tables.md) defaults every table family to unique per character unless
   carrying the same result twice is genuinely ordinary for that family.
2. **What the Trauma test at 6+ is rolled against.** The engine names no skill
   ([ADR 0013](0013-the-engine-names-no-skill.md)), so a test firing repeatedly across a
   chronicle needed either a fixed target (inventing a new mechanic) or a stated convention for
   choosing one from the fiction each time.

## Decision

**Afflictions are a repeatable family**, not unique per character. §5 states the alternative
explicitly is not the intent: "the track sawtooths, so a character can break many times across
years" reads as the same fracture recurring, and forcing uniqueness would additionally require an
exhaustion clause this track has no natural cap to justify — unlike the transformation table's
hidden threshold ([`10-transformations.md`](../design/10-transformations.md)), nothing in §5 bounds
how many times a character can break this way.

**The Trauma test names no fixed skill.** It is an ordinary [`03-rules.md`](../design/03-rules.md) §1
test, and the GM picks the skill each time to fit whatever is actually straining the character in
that scene — the same shape as Exposure's "resist with a test" in §4, which already establishes
this pattern for a mental/moral pressure with no fixed mechanic of its own.

## Alternatives considered and rejected

**A unique-per-character affliction table**, matching the transformation table's default. Rejected
because it collides directly with §5's own stated design (recurring breaks across a long
chronicle) and because it would require inventing an exhaustion rule with no textual basis — the
transformation table's exhaustion works because a hard cap (the hidden threshold) already exists
for an unrelated reason; nothing analogous exists for Trauma.

**A new named skill for the Trauma test** (a universal "Willpower," "Resolve check," or similar).
Rejected as exactly the borrowed-vocabulary problem `CLAUDE.md` and [ADR 0013](0013-the-engine-names-no-skill.md)
already rule out for this engine: no other mental/moral test in the ruleset works this way, and a
character in one chronicle resists despair differently than a character in another — the test
should draw on whatever the fiction actually establishes as relevant, not a stat every character
is presumed to have.

**A flat, fixed target number instead of a skill.** Considered as a lighter-weight alternative to
either of the above (e.g., always test at 50%, no skill involved). Rejected because
[`tools/check_affliction.py`](../../tools/check_affliction.py) shows the sawtooth's long-run
cadence is *independent of the test's skill value* below 5/6 — the floor and the drop are both 6,
which cancels the skill dependence exactly. A fixed target would have bought nothing a
fiction-chosen skill does not already give for free, while removing the table's one remaining
point of characterisation (which skill a given character leans on under pressure).

## Consequences

- [`11-afflictions.md`](../design/11-afflictions.md) declares the family repeatable and the roll
  `1d12`, no modifier, no severity field.
- The sawtooth cadence computed in `tools/check_affliction.py` — exactly 1 Affliction per 6
  Trauma-adding events, for any test skill below ~83% — is a consequence of the floor and drop
  both being 6, not of this decision directly; it is recorded here because it is what confirmed the
  fixed-target alternative bought nothing.
- A setting may still narrow which skills are plausible for this test in its own text (a
  presentation choice), but the engine itself commits to none, matching every other
  fiction-resolved test in the ruleset.
