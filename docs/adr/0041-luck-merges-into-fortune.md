# ADR 0041 — Luck merges into Fortune

**Date:** 2026-08-27
**Status:** Accepted
**Supersedes:** [ADR 0039](superseded/0039-luck-resets-at-the-top-level-arc-boundary.md), in full

## Context

`docs/design/03-rules.md` described three related player resources: **Fate** (few, permanent,
spent only to avert death — closes the Aftermath table's death rows), **Fortune** (renewable
daily, equal to the Fate score, spent to reroll, defend again, or act sooner), and **Luck** (a
percentage, tested — not spent from a pool the same way Fate or Fortune are — to dodge a
misfortune or break a tie, costing 1 from an arc-scoped pool per ADR 0039, resetting at the
top-level arc boundary).

Raised during an operator feedback round on 2026-08-27. Two problems, one soft and one hard:

**Soft — functional overlap.** Fortune and Luck occupy the same space: both are levers a player
pulls to avert an outcome they don't like. The document gave no guidance on when a player would
reach for one over the other, and no mechanical reason existed to keep them apart — they differ
in *how* they're spent (a tested percentage vs. a small integer pool) but not in *why* a player
would spend them.

**Hard — an actual naming collision.** `03-rules.md`'s engine-labels table listed "Fate" →
typical setting renames "Fate · Luck · Destiny" — offering **"Luck" as a rename for the Fate
track**. But "Luck" was *also* the engine's own formal name for the separate arc-scoped
percentage mechanic described elsewhere in the same document. The document used "Luck" as both a
suggested alias for one mechanic and the canonical name of a different one — a genuine
internal contradiction, not merely an unclear boundary.

## Decision

**Luck no longer exists as a mechanic distinct from Fortune. Fortune's existing spend list gains
two more options: dodge a misfortune, or break a tie — otherwise unchanged (renewable daily,
equal to the Fate score).**

No new mechanism, no new arc-scoped tracking, no separate percentage. What Luck used to cover is
now covered by spending an already-existing Fortune point.

Consequential fixes, all following from the merge rather than separately decided: character
creation drops its "set Luck to 40" step (Fortune's existing "equals Fate, renewed daily" step
already covers what a player has to spend); the character-fields table lists Fate and Fortune as
the paired countable resources, not Fate and Luck; and the Fate rename table's "Luck" collision
is resolved by replacing it with a genuinely distinct alternative (`Destiny`, `Providence`).

## Why

**It reuses the mechanism the engine already has, rather than choosing between two.** Fortune's
"spend to reroll, defend again, act sooner" list already reads as a small, closed set of
combat/action-adjacent averting options; "dodge a misfortune" and "break a tie" are the same
shape of choice, not a different one. Adding them to an existing list costs nothing new the way
inventing a differentiated Luck mechanic (a separate trigger, a separate refresh cadence) would
have.

**It resolves the naming collision outright**, not by picking a side. With Luck gone as a
mechanic, "Luck" is free to be nothing but a rename example for Fate again — which is exactly
what settings that want to call the death valve "Luck" (a fair, common instinct) can now do
without ambiguity.

**It simplifies the resource economy a player has to track.** `docs/design/13-diegesis.md`
already classes Fate, Fortune (and formerly Luck) as "countable" — the one class of resource that
must be rendered as a legible number, because the player is required to make a spend decision
with it. Removing one countable resource without removing any decision a player could make is a
straightforward simplification: three numbers to track becomes two, and nothing the player could
previously do becomes impossible.

## Alternatives rejected

**Keep both, sharpen the split** (e.g., Fortune spent only for the player's own action, Luck
reserved strictly for passive defense against misfortune/ties). Considered directly against the
merge. Rejected because the split would still be arbitrary — there is no in-fiction reason
"reroll my own attack" and "dodge a misfortune that just happened to me" need different resource
pools, and inventing one only to have somewhere to put Luck would be solving a problem the merge
avoids having in the first place. It also does nothing about the Fate-rename-table collision,
which needs fixing regardless of which split is chosen.

**No mechanical change, just rewrite the documentation to clarify the existing split.**
Rejected: there was no existing split worth clarifying — the two mechanics' actual trigger
conditions already overlapped in practice (see Context), so a purely editorial fix would have
been polishing a distinction that doesn't functionally exist.

## Consequences

- `docs/design/03-rules.md` loses its standalone Luck subsection; Fortune's spend list grows by
  two items; the Fate rename table no longer lists "Luck."
- `docs/design/11-character-creation.md`'s creation procedure drops one step (setting Luck to
  40) and renumbers steps 5–9 to 5–8 throughout, including every internal cross-reference to a
  step number.
- `docs/design/10-the-character.md`, `docs/design/12-the-adversary.md`,
  `docs/design/13-diegesis.md`, `docs/design/19-campaign.md` each drop their mention of Luck as a
  distinct resource, several gaining an explicit mention of Fortune in its place where the
  document already paired Fate with a second countable resource.
- `docs/design/30-playtest-transcript.md`'s worked character sheet drops its `luck:` field and
  renumbers its own steps to match.
- ADR 0039 moves to `docs/adr/superseded/`, keeping its number permanently, per the consolidation
  rule ADR 0012 established. Its own reasoning (why Luck should reset at the top-level arc
  boundary specifically) is not wrong given Luck existed — it is moot now that Luck doesn't.
- `docs/adr/0014-character-creation-is-chosen-not-rolled.md` (accepted, never edited) still
  states "Stamina 6, Luck 40, flat for everyone" as part of its own Decision — that sentence
  described the design at the time ADR 0014 was written and remains an accurate historical
  record of that decision; this ADR supersedes the Luck half of it going forward without editing
  ADR 0014's text, the same asymmetry ADR 0012 established for every other case of a decision
  moving on without the record that made it being touched.
- `specs/008-character-creation/check_creation.py` (a committed spec, itself historical record
  per CLAUDE.md) still computes and prints a "Luck — a percentage that erodes 1 per test"
  section; left unmodified, the same treatment as an accepted ADR, since it documents the
  reasoning behind a decision this ADR supersedes rather than asserting a currently-live claim.
