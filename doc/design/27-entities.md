# Wyrd — entities

Every fact Wyrd knows about a world is an **entity**: a markdown file with YAML frontmatter.
The frontmatter is the schema, the body is the prose. That makes entities machine-parseable,
human-editable, diff-legible, and — because they link with `[[wikilinks]]` — a working
Obsidian vault. Setting and chronicle repositories are both vaults, and the graph view is
the world.

---

## Two relations, and everything follows

Wyrd has exactly two structural relations. Almost all of the model is these two applied to
different things.

**Containment — a tree.** A thing is *part of* another thing.

```
region → city → district → building → room
order  → chapter → cell
campaign → adventure → situation
```

**Connection — a graph.** A thing *leads to* another thing, under conditions.

```
the great road → the city gate
the ledger room → the tavern
```

Containment is strict and acyclic. Connection is free and may loop. A `wyrd doctor` check
enforces the first and reports oddities in the second
([`21-maintenance.md`](21-maintenance.md)).

Any entity may use either. Three types are **recursive containers**: `place`, `organisation`
and `arc`. They behave identically; only their contents differ.

## The ten types

| Type | Recursive | What it is |
|---|---|---|
| `character` | — | a person: the player, a companion, a nemesis, a bystander |
| `place` | **yes** | anywhere with a name, at any scale |
| `organisation` | **yes** | any body of people, at any scale |
| `arc` | **yes** | any unit of story larger than a beat |
| `beat` | leaf | the atomic unit of play |
| `creature` | — | a stat block — a kind of thing, not an individual. What it carries is the adversary block ([`06-the-adversary.md`](06-the-adversary.md)) |
| `item` | — | a thing that matters |
| `tracker` | — | a named clock, meter or state |
| `thread` | — | an open loop the chronicle is carrying |
| `lore` | — | background with no other home |

Nothing else. **A new type is an engine change, never a setting one.**

Entity *files* are the only storage; there is no second model for chronicle state
([`19-state.md`](19-state.md)).

Note what is *not* a type. A **nemesis** is a `character` with `role: nemesis`, and it carries an
adversary block alongside the person layer — the same block a `creature` is, so one set of rules
reads one set of fields whichever it is fighting
([`06-the-adversary.md`](06-the-adversary.md)). A **threat**
is an aspect attached to a character, organisation or place — because a campaign-length
antagonist may be a person, a conspiracy, or a blighted valley, and forcing a choice would
lose information. A **faction** is an `organisation`.

## The common schema

Every entity, of every type, in every setting:

```yaml
---
id: the-old-quarter            # unique in the repo, kebab-case, stable forever
type: place
name: The Old Quarter
aliases: []
setting: <setting-id>
status: stub                   # stub | drafted | complete
tags: []
sources:
  - {work: "...", pages: "...", licence: copyright}
parent: [[the-river-city]]     # containment — at most one
links: []                      # free association; anything else
---
```

`parent` is the only containment field. Children are found by reverse lookup, so a tree can
never disagree with itself.

`status: stub` is normal and healthy — most of a setting starts as stubs
([`28-arcs-and-beats.md`](28-arcs-and-beats.md)).

`sources.licence` decides distribution: anything marked `copyright` never leaves a private
repository.

## Places

```yaml
type: place
scale: district                # world | region | settlement | district | building | room
parent: [[the-river-city]]
connections:
  - {to: [[the-great-road]], via: "the west gate", cost: "half a day",
     requires: "the gate is open"}
  - {to: [[the-undercroft]], via: "a stair behind the shrine", hidden: true}
danger: 2
```

**Connections are conditional and directional**, which is what makes a world navigable
rather than merely catalogued. A road *leads to* a city; the city is entered *from* the road;
its districts are contained *within* it. Recursion gives depth for free: describe a city
once, then add districts when a chronicle needs them, then a building inside a district when
a beat needs that.

`hidden: true` connections are known to the engine and not to the player until discovered —
so a place can have a secret way in that exists before anyone finds it.

## Organisations

Identical shape, different contents.

```yaml
type: organisation
scale: cell                    # institution | order | chapter | cell
parent: [[the-northern-order]]
objective: {...}               # organisations act — see below
members: [[hallam]], [[the-caretaker]]
reach: district
```

Characters point at organisations through `allegiances`, so one person can belong to several
at different depths — an institution publicly and a cell secretly, which is most of what
makes a conspiracy work.

## Arcs — story is recursive too

This replaces the fixed campaign/adventure/scenario/episode ladder, which was arbitrary and
did not survive contact with real material.

```yaml
type: arc
scale: adventure               # LABEL ONLY: campaign | adventure | scenario | situation
parent: [[the-long-winter]]
entry:
  requires_threads: [rural, records]
  requires_state: []
  hooks: ["the player asks about the ledger"]
exit:
  emits_threads: [{tag: financier-escaped, if: "they are not caught"}]
  changes: ["the gap in the ledger is public knowledge"]
  leads_to: [[the-tavern]]     # suggestion, never a rail
place: [[the-river-city]]
cast: [[the-caretaker]]
```

`scale` is a **human-readable label, not a structural constraint**. An arc contains arcs
and beats to whatever depth the material warrants. Published material does not fit a fixed
ladder: some "adventures" are a single situation, some campaigns nest three deep, some scenarios
contain sub-scenarios. Recursion means never having to decide whether something is an
adventure or a scenario — it is an arc, at some scale.

The payoff is recombination: **any arc can be inserted into any arc**, because they are the
same shape. Entry and exit conditions exist at every level, so thread-matching works at any
granularity — pull in a whole campaign, or one situation out of it.

## Trackers

Any named, persistent countable thing: a threat's imminence, a clock, an organisation's
strength, a settlement's suspicion of you, days until the boat.

```yaml
type: tracker
kind: clock                    # clock | meter | state
value: 3
max: 8
advances_on: ["a week passes", "the player character is seen at the shrine"]
fires: {4: "word is sent ahead", 8: "it happens without you"}
```

A first-class type rather than a field, so a world may carry arbitrarily many without schema
changes, and every one is visible in the vault.

## Characters

```yaml
type: character
role: nemesis                  # nemesis | ally | companion | bystander | authority | quarry
archetype: mastermind          # fallen-ally | gloryhound | heretic | mastermind | warlord
disposition: hostile           # ally | wary | hostile | hunting | unaware
allegiances: [[the-cell]]
based_at: [[the-old-quarter]]
objective:
  wants: "the debt written off before the reckoning"
  because: "her brother signed it and she witnessed it"
  next_step: "find out whether the player character remembers that night"
  blocked_by: "cannot be seen taking an interest"
  escalates_to: "arson, as a distraction"
  timeline: "before the boat arrives"
stats: {}                      # as printed by the source, where one exists
```

**Objectives are what make the world act while the player is absent.** `next_step` advances
on its own; it is what the engine consults before deciding how anyone reacts. The archetypes
are *behavioural* rather than thematic — they say how a character acts unobserved.

---

## The chronicle overlay

**Setting entities are immutable within a chronicle.** A chronicle never edits its setting;
it writes an overlay.

```
chronicle/
├─ setting/    # copied at bootstrap, read-only thereafter
└─ overlay/    # what this chronicle has changed
```

An overlay carries only the delta:

```yaml
---
id: <entity-id>
overlay_of: <setting-id>
---
disposition: hunting           # was: unaware
knows_pc: "what they now believe about the player"
memories:
  - {when: "<date>", what: "<what they witnessed>"}
state: alive
role: nemesis                  # was: bystander
threat:                        # acquired in play — see 18-campaign.md
  imminence: 2
  connection: "the player left them for dead"
```

An overlay is also how an entity is **promoted**: a bystander the player wronged becomes a
nemesis with a `threat` block, without the setting ever changing. The setting keeps the
person it described; this chronicle records what they became.

Resolution at load is `setting entity + overlay = effective entity`. The overlay alone
answers *"what has this player done to this world?"* — and it is why one setting can host
many chronicles with different histories, and why a setting update can be pulled in without
discarding what happened ([`22-evolution.md`](22-evolution.md)).

## Why frontmatter rather than a database

Obsidian reads it natively and the graph view is free visualisation. `git diff` stays legible,
so a chronicle's history is readable years later. `grep` works. No dependency
([`20-tooling.md`](20-tooling.md)). And a person can repair a file by hand at three in the
morning, which a database does not allow.

The cost is that referential integrity is checked rather than enforced — which is what
`wyrd doctor` is for.
