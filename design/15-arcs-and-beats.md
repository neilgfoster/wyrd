# Wyrd — arcs, beats, and lazy conversion

Source material in Wyrd is not a document to be read aloud. It is a **tree of arcs ending in
beats**, each with entry and exit conditions, from which stories can be rebuilt in
combinations their authors never wrote.

Entity shapes are in [`14-entities.md`](14-entities.md); this is what they are *for*.

---

## The beat

A **beat** is the atomic unit of play ([`04-session.md`](04-session.md)) and of content: one
goal, attempted, resolved, persisted.

```yaml
---
id: the-cut-page
type: beat
name: "The cut page"
status: drafted
parent: [[the-drowning-well]]        # containment: which arc it belongs to
sources: [{work: "...", pages: "34-35", licence: copyright}]

entry:
  requires_threads: [records]
  requires_state: []
  hooks: ["the player asks about the ledger"]
exit:
  emits_threads: [{tag: the-hinge, if: "the PC recalls the door"}]
  changes: ["the gap is public knowledge"]
  leads_to: [[the-tavern]]           # suggestion, never a rail

place: [[the-shrine]]
cast: [[the-caretaker]]
mode: played                         # played | summarised
danger: 2
written_for: 4                       # party size — a scaling input, never a gate
length: one-beat
---

What is true, who wants what, and what happens if nobody intervenes. Never a script.
```

## Why beats rather than adventures

Because **a published adventure is the wrong granularity for solo play.** It assumes a party,
a session length, a starting point, an ending, and that players arrive in the author's order.
None of those hold.

Broken into beats, the same material becomes reusable: a beat from the middle of one
adventure can sit inside another entirely; a six-page magazine scenario might be three beats
of which two are worth keeping; and beats recombine into stories driven by thread matching
([`05-campaign.md`](05-campaign.md)) rather than by an author's sequence.

## Selection, and why `leads_to` is only a hint

The engine picks the next beat by matching **live threads** against `entry.requires_threads`,
filtered by the deterministic predicates in [`11-corpus-index.md`](11-corpus-index.md), and
scaled to the party. `leads_to` is consulted only when nothing better is live.

Where a genuine authored sequence exists, the arc tree preserves it — an arc's children in
order *are* the original adventure, and running them in order runs it as written. So Wyrd can:

- run a published campaign exactly
- run it with substitutions where a beat does not suit this character
- assemble an original campaign from beats across many sources
- scale every beat to the party

This is what makes a decade-long chronicle possible from a finite library. Twelve adventures
is twelve stories; four hundred beats is not.

## Recursion at every level

Because arcs contain arcs ([`14-entities.md`](14-entities.md)), entry and exit conditions
exist at **every** level, not just the leaves. The engine can therefore match threads against
a whole campaign, an adventure inside it, or a single situation — and insert any of them into any
other, since they are the same shape.

A useful consequence: an arc that has never been decomposed can still be *selected*, because
its own entry/exit are enough to judge fit. Decomposition can wait until it is actually
needed.

---

## Conversion is lazy

**A setting starts as stubs, and that is the intended state.**

```yaml
---
id: the-drowned-town
type: arc
scale: adventure
status: stub
sources: [{work: "...", pages: "all", licence: copyright, path: "..."}]
tags: [town, investigation, conspiracy]
---
Stub. Not yet decomposed.
```

A stub carries **enough to be selected** — a summary, tags, a source path — and nothing more.

**Conversion happens on demand.** When the engine is planning the next stage of a chronicle
and a stub looks like the right fit, it pulls the source, decomposes *that arc* into
sub-arcs and beats, and **commits the result back to the setting repository**. The setting
deepens as it is played, and effort is only ever spent on material that gets used.

Each converted beat records the pages it came from, so provenance survives and a low-quality
extraction can be found and redone.

| Status | Meaning |
|---|---|
| `stub` | indexed, summarised, source known — selectable |
| `drafted` | decomposed, unplayed |
| `complete` | played at least once, and corrected by contact with play |

`wyrd doctor` reports the mix. **A setting that is 95% stubs is healthy**, not incomplete.
