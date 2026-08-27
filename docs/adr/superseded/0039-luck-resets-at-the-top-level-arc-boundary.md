# ADR 0039 — Luck resets to maximum at the start of each top-level arc

**Date:** 2026-08-26
**Status:** Superseded by [ADR 0041](../0041-luck-merges-into-fortune.md)

## Context

`docs/design/03-rules.md` §1 (Luck) states that testing Luck "costs 1 Luck for the rest of the
arc, pass or fail." No document in `docs/design/` says what happens to spent Luck once that arc
ends — not per arc, not per session, not per downtime. As written, Luck reads as a one-way
depleting resource for the life of the character once first spent, which contradicts the
arc-scoped framing already in the text: scoping a cost to "the rest of the arc" only means
something if the arc's end changes the cost's standing. A resource that never comes back would
more plausibly be described as costing 1 Luck for the rest of the character's life.

This is exactly the shape of decision that earns a record: a real alternative — Luck never
restores, and is meant to be a scarce, permanently spent resource across a character's whole life
— was considered and rejected, and the question of whether Luck resets is the kind that would
plausibly be re-asked, having forgotten this reasoning, the next time someone reads `03-rules.md`
§1 in isolation.

## Decision

**Luck resets to maximum at the start of each top-level arc** — the level `docs/design/
18-campaign.md` gives a job the deeper, recursive arcs beneath it do not: each top-level arc
"should end with something altered." Restoration fires on that boundary specifically, not on
every nested arc's boundary underneath it.

`docs/design/03-rules.md` §1 is updated to state this explicitly, immediately after the existing
"costs 1 Luck for the rest of the arc, pass or fail" sentence, so a reader of that section alone
never has to infer the answer from a document it doesn't cite.

## Alternatives rejected

**Luck never restores — a one-way, whole-life resource.** Rejected: it is internally consistent
and was the honest alternative named when this gap was first raised, but it leaves the existing
"for the rest of the arc" phrasing in `03-rules.md` doing no work. If the resource never comes
back regardless, there is no reason to scope its cost to anything narrower than the character's
whole life — the sentence would need rewriting, not completing, to mean that.

**Resets at every recursive arc boundary, including nested arcs.** Rejected: arcs recurse
(`docs/design/25-entities.md`), but `18-campaign.md` is explicit that only the top-level arcs
directly under a chronicle carry the "ends with something altered" property; nested arcs beneath
them do not. Resetting Luck on every nested boundary would recover the resource far more often
than its scarcity — 40 at creation, spent one point at a time — appears designed for, and would
manufacture a second notion of "arc end" that `18-campaign.md` doesn't itself distinguish.

**Resets per session or per downtime, matching Stamina's Rally/downtime recovery cadence (ADR
0020, ADR 0021).** Rejected: `03-rules.md` already names "arc" as Luck's scoping unit in its
existing text; borrowing Stamina's cadence would contradict that wording rather than complete it.
Stamina and Luck also answer different fictional questions — Stamina is a body's condition inside
a fight, Luck is a finite favor from fortune across a whole story arc — so there is no reason to
expect them to share a recovery rhythm.

## Consequences

- `docs/design/03-rules.md` §1's "for the rest of the arc" phrasing is no longer a dangling
  implication; it names the exact boundary at which the cost lapses.
- The reset boundary is the same one `docs/design/19-campaign.md` already defines for top-level
  arcs — no new document, section, or vocabulary is introduced, and nothing in `18-campaign.md`
  itself is altered.
- A nested (sub-)arc ending, on its own, does not restore Luck. Only its enclosing top-level arc
  ending does.
- Luck's maximum (40, set at creation per `docs/design/11-character-creation.md`) is unaffected by
  this decision; only the mechanism for returning to it is newly stated.
