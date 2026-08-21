# Wyrd — authoring a setting

Everything needed to build a new setting for Wyrd, without reading the existing ones.

A "setting" in Wyrd is closer to a **game module** than a backdrop: it supplies the world,
its content, its voice — and, where it needs to, a rules overlay. The the setting and the
a science-fiction setting are two; a mythic-fantasy one would be a third and would look quite different.

---

## What a setting repository contains

```
wyrd-<name>/
├─ setting.yaml       # identity, engine compatibility, version
├─ setting/
│  ├─ voice.md        # THE most important file. See below.
│  ├─ careers.yaml    # the career graph — nodes with entries and exits
│  ├─ gear.yaml       # weapons, armour, prices, what is legal to carry where
│  ├─ creatures.yaml  # stat blocks
│  ├─ factions.yaml   # with objectives (see 06-state)
│  ├─ deities.yaml    # or creeds, or powers, or nothing
│  ├─ names.yaml      # given / family / place, by culture
│  ├─ conversion.yaml # REQUIRED if derived from another system — see below
│  ├─ calendar.yaml   # months, festivals, celestial cycles
│  └─ rules/          # OPTIONAL overlay — only where the engine is insufficient
├─ scenarios/
└─ index/             # corpus indexes over this setting's sources
```

### `setting.yaml`

```yaml
name: <setting-id>
title: The the setting
line: fantasy
requires_engine: ">=0.1.0"
version: 0.3.0
description: >
  One paragraph. What the world is, and what it is about.

tone:                       # the tone contract — see 01-principles.md
  prophecy: forbidden       # forbidden | rare | central
  victory: mitigation       # mitigation | mixed | triumph
  power_curve: flat         # flat | moderate | heroic
  scope: personal           # personal | regional | world
  scale_drift: suppressed   # suppressed | allowed
  mortality: high           # low | standard | high
  register: "one line naming the voice"
```

**The tone contract is the setting's most load-bearing declaration after `voice.md`.** The
engine will hold whatever line it draws — refusing to invent a destiny under
`prophecy: forbidden`, and building one under `prophecy: central`. Getting it wrong produces
a technically correct chronicle that feels like the wrong game.

`version` matters: a chronicle pins **both** an engine version and a setting version
([`09-evolution.md`](09-evolution.md)). Setting changes are almost always *additive* and
therefore safe, but a career being removed or renamed is structural and needs a migration
like any other.

---

## `voice.md` is the hard part

Everything else is data that can be typed in. The voice is the setting.

It should state, with examples drawn from the source material:

1. **Register** — the narrator's relationship to the world. The world's is a weary
   civil servant who has seen the paperwork; another's is bureaucratic doom. These are not
   interchangeable.
2. **What institutions look like** — named, mundane, and administratively real, or vast and
   incomprehensible. This is where most of the tone actually lives.
3. **How danger is stated** — as an occupational hazard, or as prophecy, or as liturgy.
4. **What a critical failure looks like here.** Concretely.
5. **Vocabulary** — the words that belong and the words that do not. A the setting scene does
   not contain the word "cosmic".
6. **What the joke is, and who it is on.** Some settings are dry; some have no humour at all.
   Getting this wrong is the fastest way to break immersion.

A good `voice.md` is three pages of examples and one page of rules. It is read at the start
of every session and it does more work than any other file in the repository.

---

## The engine/setting contract

The engine guarantees, and a setting may rely on:

| Engine provides | Setting supplies |
|---|---|
| `d100` resolution, SL, the Wyrd die | skill names |
| Diffisecty bands | when they apply |
| Stamina, armour dice, criticals, Aftermath | weapons, armour, critical flavour |
| Taint, Trauma, Fate, Resolve, Strain | what they are *called* and what causes them |
| Career graph mechanics — entries, exits, advance triggers | the graph itself |
| Beats, Rally, Fellowship phases, party tension | what downtime looks like here |
| Threats, threads, elapsed time, succession | who the Threats are |
| Diegetic bands ([`10-diegesis.md`](10-diegesis.md)) | the idiom they are spoken in |

**A setting must not need to change engine code.** If it does, that is an engine gap and
should be fixed in the engine — the whole point of the layering
([`02-architecture.md`](02-architecture.md)).

### Rules overrides — the hard rule

> **A setting may extend, retune or disable what the engine provides.
> It may never add a mechanism the engine does not have.**

New mechanisms go in the core, for everyone. This is the rule that keeps Wyrd a single system
rather than a family of incompatible forks, and it is not negotiable.

**Permitted:**

| Override | Example |
|---|---|
| **Extend** | add setting-specific skills, careers, talents, gear, creatures |
| **Retune** | replace a table with one that has more setting feel; change exposure tiers; alter starting Fate |
| **Rename** | Taint becomes Shadow, or Warp-taint, or Sin. Vocabulary only |
| **Disable** | switch off Taint entirely for a high-fantasy setting; switch off Trauma for a lighter one |

**Not permitted:**

- adding a subsystem the engine does not know about
- changing resolution, or what the Wyrd die means
- changing how state persists, how beats work, or how time passes

If a setting needs a mechanism that does not exist — a journey system, a mass-battle layer, a
Resolve/Shadow balance the core lacks — **that is an engine gap and it goes in the engine**,
generalised so every setting can use it. The setting then configures it or leaves it off.

Overrides are declared in `setting.yaml`:

```yaml
overrides:
  disable: [taint, trauma]     # a high-fantasy setting
  rename: {taint: shadow}
  tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}
  extend: {skills: setting/rules/skills.yaml}
```

Loaded after engine defaults, exactly like a chronicle's `houserules.yaml`.

Overlays are declared in `setting.yaml` and loaded after engine defaults, exactly like
`houserules.yaml` for a chronicle.

---

## Conversion rules — required for any derived setting

A setting derived from an existing system **must** carry `setting/conversion.yaml`.

Without it, on-demand conversion ([`15-arcs-and-beats.md`](15-arcs-and-beats.md)) is
improvised each time, and the same source converted twice produces different numbers. That is
non-determinism entering through the back door — precisely what
[`07-tooling.md`](07-tooling.md) exists to prevent. A conversion table makes the process
mechanical, repeatable and auditable.

```yaml
# setting/conversion.yaml
from: {system: "<source system>", edition: "<edition>"}
version: 1                      # bump on any change; converted content records which it used

# --- numbers ---
skills:
  method: direct                # direct | scale | table
  note: "source is already percentile; values are read as printed"
characteristics:
  map: {combat: weapon-skill, ranged: ballistic-skill, physical: strength}
diffisecty:
  map: {easy: +20, average: 0, challenging: -10, diffisect: -20, hard: -30}
damage:
  method: direct
  wounds_to_stamina: direct
armour:
  method: table
  map: {1: light, 2: light, 3: modest, 4: modest, 5: heavy}
danger:
  derive_from: "the source's stated party level or recommended party"
  formula: "danger = ceil(source_level / 2)"

# --- vocabulary ---
rename: {taint: taint, trauma: shock}

# --- structure ---
arcs:
  chapter: arc(scale=adventure)
  encounter: beat
  read_aloud: "narrative seed — never reproduced verbatim"

# --- deliberately dropped ---
drop: [talents, hit-locations, vehicles, initiative-order, facing]
drop_note: >
  Dropped mechanics are recorded on the converted entity as prose, not lost silently.
  A creature with a Frenzy talent is described as frenzied.

# --- cannot be converted automatically ---
manual: [setting-specific-subsystems, published-maps]
```

### Conversion is versioned

Every converted entity records the conversion version that produced it:

```yaml
converted: {rules: 1, on: 2026-08-21}
```

So when a conversion rule changes, `wyrd doctor` reports which entities predate it and offers
re-conversion — a **structural** change under [`09-evolution.md`](09-evolution.md), never one
that rewrites what happened in play.

### The three things conversion must never do

1. **Reproduce prose verbatim.** Read-aloud text becomes a narrative seed. A converted beat is
   a situation, not a transcription — the same reason beats are never scripts.
2. **Invent numbers it cannot derive.** Where the source gives nothing, the field stays null
   and the entity stays `status: stub`. A guessed stat is worse than an absent one.
3. **Lose provenance.** Every converted entity records the source work and pages.

## A worked example: a mythic-fantasy setting

Useful because it is *not* the source line and so tests the boundary.

| Need | Where it goes |
|---|---|
| Cultures instead of careers | `careers.yaml` — the graph shape still fits |
| A hope/despair balance | **already engine** — Taint and Resolve |
| Shadow Weakness from Calling | `setting/rules/` — a mapping table |
| The Fellowship phase | **already engine** |
| Journeys as a mechanic | `setting/rules/` — a real overlay, since Wyrd has no travel subsystem |
| Eagles, Wargs, the Necromancer | `creatures.yaml`, `factions.yaml` |
| "A losing struggle" | **already engine** — it is the campaign model |
| The register | `voice.md` — elegiac, where another line might be dry or brutal |

Most of it lands in data. The one genuine overlay is journeys — which tells you something
useful: **Wyrd's engine currently assumes travel is narrated, not played.** That is a defensible
choice for text play, and a setting that disagrees can add it.

---

## Checklist for a new setting

1. `setting.yaml` — identity and engine compatibility
2. `voice.md` — write this **first**, before any data. It will change what you put in the data.
3. `names.yaml` and `calendar.yaml` — cheap, and immediately make the world feel inhabited
4. `careers.yaml` — the character system; the largest single job
5. `gear.yaml`, `creatures.yaml` — enough to run one scenario, not everything
6. `factions.yaml` with objectives — so the world can act while the player is absent
7. One Threat Pack and one scenario — enough to play
8. Index whatever sources you have ([`11-corpus-index.md`](11-corpus-index.md))

Steps 1–5 and one scenario is a playable setting. Everything else accumulates.
