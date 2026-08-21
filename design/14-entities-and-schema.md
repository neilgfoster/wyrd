# Wyrd — entities and the world mesh

Every fact Wyrd knows about a world is an **entity**. Entities are markdown files with YAML
frontmatter: the frontmatter is the schema, the body is the prose. That makes them
machine-parseable, human-editable, diff-friendly, and — because they link with `[[wikilinks]]`
— a working **Obsidian vault**.

Setting and chronicle repositories are both vaults. Open either in Obsidian and the graph
view *is* the world.

---

## The entity types

| Type | What it is |
|---|---|
| `character` | a person — NPC, nemesis, companion, or the PC |
| `location` | anywhere with a name |
| `faction` | an organisation with objectives |
| `item` | a thing that matters |
| `creature` | a stat block, not a person |
| `beat` | the atomic unit of play ([`15-adventures-as-beats.md`](15-adventures-as-beats.md)) |
| `scenario` | a situation made of beats |
| `adventure` | a published or authored sequence |
| `campaign` | an arc across adventures |
| `threat` | a campaign-length antagonist with an Imminence |
| `tracker` | a named clock — a countdown, a meter, a state machine |
| `lore` | background with no other home |

Nothing else. A new type is an engine change, not a setting one.

## The common schema

Every entity, of every type, in every setting:

```yaml
---
id: hallam-weissbruck          # unique within the repo, kebab-case, stable forever
type: character
name: Hallam Weissbruck
aliases: ["the ledger man"]
setting: wfrp2e                # which setting repo owns this
tags: [altdorf, nobility, cult]
status: stub                   # stub | drafted | complete
sources:                       # where it came from, always
  - {work: "White Dwarf 98", pages: "34-39", licence: copyright}
links: [[altdorf]], [[the-meisters]]
---
```

`status: stub` matters — most of a setting starts as stubs
([`15-adventures-as-beats.md`](15-adventures-as-beats.md)).

`sources.licence` matters too: `copyright` entities never leave a private repo.

## Type-specific schema

Each type adds a small, fixed block. Characters, being the richest:

```yaml
role: nemesis                  # nemesis | ally | companion | bystander | authority | quarry
archetype: mastermind          # nemesis archetypes, after WFRP 3e:
                               # fallen-ally | gloryhound | heretic | mastermind | warlord
disposition: hostile           # ally | wary | hostile | hunting | unaware
objective:
  wants: "the debt written off before the reckoning"
  because: "her brother signed it and she witnessed it"
  next_step: "find out whether Wendel remembers the tavern"
  blocked_by: "cannot be seen taking an interest in the record house"
  escalates_to: "burn the outbuilding as a distraction"
  timeline: "before Marktag"
stats: {ws: 41, t: 35, w: 12}  # read as printed — ADR 0002
appears_in: [[the-drowning-well]]
```

**Nemeses are first-class.** WFRP 3e's guidance is the model: a Nemesis is *"every bit as
detailed and developed as the PCs are — with their own distinct personality traits,
abilities, resources, motives, and goals."* They get objectives that advance whether or not
the player is present, exactly like Threats.

The five archetypes are worth keeping because they are *behavioural*, not thematic — they
tell the GM how the character acts when unobserved. The Mastermind uses minions and has
contingencies; the Warlord commands loyalty and fights; the Fallen Ally knows you.

## Trackers

A `tracker` is any named, persistent countable thing — a Threat's Imminence, a scenario
clock, a faction's strength, a town's suspicion of you, days until the boat.

```yaml
type: tracker
kind: clock                    # clock | meter | state
value: 3
max: 8
advances_on: ["a week passes", "the PC is seen at the shrine"]
fires:
  4: "the Overseer sends word ahead"
  8: "the reckoning happens without you"
```

Making trackers a first-class entity rather than a field means the world can carry
**arbitrarily many** without schema changes, and every one is visible in the vault.

---

## The chronicle overlay — how the world changes

**Setting entities are immutable within a chronicle.** A chronicle never edits its setting;
it writes an **overlay**.

```
wyrd-chronicle-x/
├─ setting/        # copied at bootstrap, read-only thereafter
└─ overlay/        # what this chronicle has changed
   └─ character/hallam-weissbruck.md
```

An overlay file carries only the delta:

```yaml
---
id: hallam-weissbruck
overlay_of: wfrp2e
---
knows_pc: "believes Wendel cut the page himself"
disposition: hunting           # was: unaware
memories:
  - {when: "2512 Pflugzeit 1", what: "saw Wendel leaving the shrine at night"}
state: alive
```

This is what makes "a setting character gains memories of the PC" and "a location is
destroyed" work without corrupting the setting. Resolution at load is
`setting entity + overlay = effective entity`, and the overlay alone is the answer to
*"what has this player done to this world?"*

It also means the same setting can host many chronicles, each with a different history, and
a setting update can be pulled into a chronicle without discarding what happened
([`09-evolution.md`](09-evolution.md)).

## Why frontmatter, not a database

- Obsidian reads it natively; the graph view is free world visualisation
- git diffs are legible, so a chronicle's history is readable years later
- `grep` works
- no dependency, per [`07-tooling.md`](07-tooling.md)
- a human can fix a file by hand at 3am, which a database does not allow

The cost is that referential integrity must be checked rather than enforced — which is what
`wyrd doctor` already does ([`08-maintenance.md`](08-maintenance.md)).
