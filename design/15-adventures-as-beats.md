# Wyrd — adventures as beats

An adventure in Wyrd is not a document to be read aloud. It is a **set of beats with entry
and exit conditions**, from which campaigns can be rebuilt in combinations their authors
never wrote.

---

## The unit

A **beat** is the atomic unit of play ([`04-session.md`](04-session.md)): one goal,
attempted, resolved, persisted. It is also the atomic unit of *content*.

```yaml
---
id: the-cut-page
type: beat
name: "The cut page"
setting: wfrp2e
status: drafted
scenario: [[the-drowning-well]]
adventure: [[the-drowning-well]]
campaign: null
sources:
  - {work: "White Dwarf 98", pages: "34-35", licence: copyright}

# --- placement in the mesh ---
entry:
  requires_threads: [rural, records]      # what must be live for this to be reachable
  requires_state: []                      # e.g. "pc has the ledger"
  hooks: ["the player asks about the ledger", "Brida raises it"]
exit:
  emits_threads:
    - {tag: the-hinge, if: "the PC recalls the door"}
    - {tag: brida-suspicious, if: "the PC handles her badly"}
  changes: ["the ledger's gap is now public knowledge"]
  leads_to: [[the-drowned-cat]]           # SUGGESTION, never a requirement

# --- running it ---
scale: village
threat: 2
party_written_for: 4
length: one-beat
mode: scene                               # scene | story
cast: [[brida-voss]]
place: [[hemmelfurt-shrine]]
tone: [investigation]
---

What is true, who wants what, and what happens if nobody intervenes. Never a script.
```

## Why beats rather than adventures

Because **a published adventure is the wrong granularity for a solo chronicle.** It assumes
a party, a session length, a starting point and an ending, and it assumes the players arrive
in the order the author wrote.

Broken into beats, the same material becomes reusable:

- a beat from *Shadows Over Bögenhafen* can sit in the middle of something else entirely
- a six-page *White Dwarf* adventure might be three beats, two of which are worth keeping
- beats recombine into campaigns **the author never wrote**, driven by thread matching
  ([`05-campaign.md`](05-campaign.md))

`leads_to` is a *suggestion*, not a rail. Wyrd selects the next beat by matching live threads
against `entry.requires_threads`, and only falls back to the author's sequence when nothing
better is live. Where a genuine authored chain exists — *The Enemy Within* — the `campaign`
field preserves it and the sequence can be run as written.

## The campaign matrix

Given a corpus of beats, a campaign is a **path through them**. The engine can therefore:

- rebuild a published campaign exactly (follow `campaign` and `leads_to`)
- rebuild it with substitutions where a beat doesn't fit this character
- assemble an entirely original campaign from beats across many sources
- scale every beat to the party via `party_written_for`
  ([`11-corpus-index.md`](11-corpus-index.md))

This is the mechanism that makes a decade-long chronicle possible from a finite library.
Twelve adventures is twelve stories; two hundred beats is far more.

---

## Conversion is lazy

**A setting starts as stubs.** Wyrd does not need — and should not attempt — to convert the
whole library up front.

```yaml
---
id: shadows-over-bogenhafen
type: adventure
status: stub
setting: wfrp2e
sources:
  - {work: "WFRP 1e — Shadows Over Bögenhafen", pages: "all", licence: copyright,
     path: "Warhammer Fantasy Roleplay/01 - .../04 - Shadows Over Bögenhafen.pdf"}
summary: "Bögenhafen, a merchant town, a fire, and a cult of Slaanesh beneath it."
tags: [town, investigation, cult, enemy-within]
---
Stub. Not yet converted to beats.
```

A stub carries **enough to be selected** — summary, tags, source path — and nothing more.

**Conversion happens on demand.** When Wyrd is planning the next stage of a campaign and a
stub looks like the right fit, it pulls the source, converts *that adventure* into beats, and
**commits the result back to the setting repo**. The setting deepens as it is played, and
effort is only ever spent on material that gets used.

This also keeps the corpus honest: a beat file records exactly which pages it came from, so
its provenance survives.

## Statuses

| Status | Meaning |
|---|---|
| `stub` | indexed, summarised, source known. Selectable. |
| `drafted` | converted to beats, unplayed |
| `complete` | played at least once, and corrected by contact with play |

`wyrd doctor` reports the mix, and a setting that is 95% stubs is perfectly healthy.
