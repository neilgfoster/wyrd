# Wyrd — authoring a setting

Everything needed to build a new setting for Wyrd, without reading the existing ones.

A "setting" in Wyrd is closer to a **game module** than a backdrop: it supplies the world,
its content, its voice — and, where it needs to, a rules overlay. The the setting and the
the science-fiction setting are two; another source system's Wilderland would be a third and would look quite different.

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
  One paragraph. What the world is, and what its horror is made of.
```

`version` matters: a chronicle pins **both** an engine version and a setting version
([`09-evolution.md`](09-evolution.md)). Setting changes are almost always *additive* and
therefore safe, but a career being removed or renamed is structural and needs a migration
like any other.

---

## `voice.md` is the hard part

Everything else is data that can be typed in. The voice is the setting.

It should state, with examples drawn from the source material:

1. **Register** — the narrator's relationship to the world. The world's is a weary
   civil servant who has seen the paperwork. Only War's is bureaucratic doom. These are not
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
| Difficulty bands | when they apply |
| Stamina, armour dice, criticals, Aftermath | weapons, armour, critical flavour |
| Corruption, Insanity, Fate, Hope, Stress | what they are *called* and what causes them |
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
| **Rename** | Corruption becomes Shadow, or Warp-taint, or the Long Defeat. Vocabulary only |
| **Disable** | switch off Corruption entirely for a high-fantasy setting; switch off Insanity for a lighter one |

**Not permitted:**

- adding a subsystem the engine does not know about
- changing resolution, or what the Wyrd die means
- changing how state persists, how beats work, or how time passes

If a setting needs a mechanism that does not exist — a journey system, a mass-battle layer, a
Hope/Shadow balance the core lacks — **that is an engine gap and it goes in the engine**,
generalised so every setting can use it. The setting then configures it or leaves it off.

Overrides are declared in `setting.yaml`:

```yaml
overrides:
  disable: [corruption, insanity]     # a high-fantasy setting
  rename: {corruption: shadow}
  tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}
  extend: {skills: setting/rules/skills.yaml}
```

Loaded after engine defaults, exactly like a chronicle's `houserules.yaml`.

Overlays are declared in `setting.yaml` and loaded after engine defaults, exactly like
`houserules.yaml` for a chronicle.

---

## A worked example: what a One Ring setting would need

Useful because it is *not* the source line and so tests the boundary.

| Need | Where it goes |
|---|---|
| Cultures instead of careers | `careers.yaml` — the graph shape still fits |
| Hope and Shadow | **already engine** — Wyrd took this from another source system |
| Shadow Weakness from Calling | `setting/rules/` — a mapping table |
| The Fellowship phase | **already engine** |
| Journeys as a mechanic | `setting/rules/` — a real overlay, since Wyrd has no travel subsystem |
| Eagles, Wargs, the Necromancer | `creatures.yaml`, `factions.yaml` |
| "The long defeat" | **already engine** — it is the campaign model |
| The register | `voice.md`, and it would be elegiac rather than grim |

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
