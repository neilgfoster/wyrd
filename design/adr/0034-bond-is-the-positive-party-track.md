# ADR 0034 — Bond is the positive party track; no standalone Cohesion track is added

**Date:** 2026-08-26
**Status:** Accepted

## Context

`04-session.md` measures **Party Tension**, 0-6, rising toward a break, and nothing a
functioning party earns for behaving well beyond Tension's own slow decay. Epic #2 recorded this
as a gap: a mechanical asymmetry, in an engine whose whole subject is a long relationship with a
small group of people, where things going badly is expressed and things going well is not.

Meanwhile `04-session.md` already carries **Bond** (-3..+3, per companion, toward the player
character): it modifies Tension gain, whether a companion follows into danger, and whether they
tell the truth — described in prose as "the closest thing Wyrd has to a relationship score," but
never spelled out as a concrete mechanical effect a GM could point to and say "this is what a
well-run party has bought."

Two shapes were available to close the gap, and they produce genuinely different engines: give
Bond a stated positive effect, or add a second track that answers the same underlying question
("is this party working") from the opposite direction.

## Decision

**Bond is completed as the positive party track. No new track is added.**

Bond now has a stated mechanical effect on Tension gain: an event that raises Tension and names a
specific companion adds 1 point per point that companion's Bond sits *below* 0, and 1 point
*fewer* (floored at 0) per point their Bond sits *above* 0. A companion at Bond +3 contributes
nothing to Tension from events naming them; a companion at Bond -3 contributes up to 4. This is
not a new number to track — Bond already exists and is already read at the moment Tension would
rise; the change is stating what that existing read does, not adding a mechanism.

## Alternatives considered

**A standalone 0-6 "Cohesion" track, rising on the axis Tension falls, alongside it.** Rejected.
Both tracks would answer the same fictional question from the same set of inputs (shared meals
kept, promises honoured, beats spent on a companion's problem), which means every future rule
touching one would need to state whether it also touches the other — a reconciliation burden this
design doesn't need, and the exact two-documents-describing-one-thing-differently fault
`CLAUDE.md` names as recurring. It would also strand Bond as a second, unfinished relationship
number sitting next to a purpose-built one, rather than resolving what Bond was already gesturing
at.

**Leaving the asymmetry as deliberate, recording only this ADR, no mechanical change.**
Considered, because a genuinely one-directional track is a legitimate design (some engines
deliberately track only what threatens the table, not what sustains it). Rejected here because
Bond's own text was already halfway to being the answer — "modifies Tension gain... whether they
follow into danger, and whether they tell you the truth" is a relationship mechanism with no
stated positive payoff, which reads as an omission rather than a considered choice once compared
against the issue's framing. Declining to finish it would leave the gap open under a different
name.

## Consequences

- `04-session.md`'s companion section states the two-layer split (narrative / mechanical) and
  Bond's completed Tension-offset rule together, since the rule is the payoff of tracking Bond on
  the mechanical layer at all.
- No new field appears on the companion record. `tools/check_companion_layers.py` asserts the
  mechanical layer stays at exactly five fields (`career`, `bond`, `taint`, `strain`, `wounds`),
  so a future PR that tries to add a Cohesion-style field alongside Bond fails the check rather
  than drifting in unnoticed.
- A companion at Bond -3 remains, as `04-session.md` already says, "more interesting than one who
  left" — this ADR does not change that framing, only completes what the number in front of it
  does.
