# ADR 0005 — Anything with a correct answer is computed, not inferred

**Status:** accepted 2026-08-20

## Context

Wyrd is run by a language model. The model could plausibly do everything: roll dice, track
state, apply thresholds, decide what a result means.

## Decision

**If a script can do it, a script does it.** The model is reserved for judgement
([`../20-tooling.md`](../design/20-tooling.md)).

The test, in order: does it have a single correct answer given the state? Could the player
catch the GM getting it wrong? Must it hold across years and context resets? Is it
arithmetic, lookup, validation or bookkeeping? Any yes means code.

And a rule that follows: **the model narrates from tool output and never recomputes it.** If
the tool and the prose disagree, the tool is right and the prose is a bug.

## Alternatives rejected

**Letting the model hold the rules.** It works, for a session. Over a chronicle running
years it does not, and the failure is not that the model gets things *wrong* — it is that it
gets them **inconsistently right**. Drift accumulates in the direction of whatever makes the
current scene better, and over years drift is indistinguishable from cheating.

The dice are the acute case. A model that rolls its own dice will, eventually and without
intending to, roll the result the story wants. That is why the dice tool is non-negotiable:
it is the only defence against principle 1 eroding quietly.

**A middle position** — code for dice, model for everything else. Rejected because the
boundary has to be drawn by a property, not by a list. A list gets extended in the direction
of convenience.

## Consequences

- The engine is a CLI with structured output, and skills are prompt-level instructions.
- This decision later ruled out adopting a detailed source system wholesale
  ([0002](0002-source-material.md)): a hundred special-case abilities are a hundred
  judgements per session, which is the same drift by another route.
- It also set the model tiering: no model for arithmetic, a small one for mechanical language
  work with a right answer, the capable one only for the fiction.
- It constrains settings too. A setting supplies data and declarations, never code, so
  "a setting cannot add a mechanism" is enforceable rather than merely requested.
