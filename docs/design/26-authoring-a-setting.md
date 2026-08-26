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
│  ├─ careers.yaml    # the career graph — entry careers, and prerequisites for the rest
│  ├─ gear.yaml       # weapons, armour, prices, what is legal to carry where
│  ├─ bestiary.yaml   # adversary blocks (a lookup table) — see below
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
title: <Setting Title>
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
([`22-evolution.md`](22-evolution.md)). Setting changes are almost always *additive* and
therefore safe, but a career being removed or renamed is structural and needs a migration
like any other.

---

### Tables versus entities

Two kinds of content, and the distinction is simple:

| | Stored as | Because |
|---|---|---|
| **Lookup tables** — careers, gear, names, calendar, bestiary | `setting/*.yaml` | hundreds of rows, queried by key, never linked to individually |
| **Named things** — characters, places, organisations, arcs, beats, threads | `entities/<type>/*.md` | each is referenced, linked and can carry a chronicle overlay |

The test: *would anything ever link to it, or would a chronicle ever change it?* If yes it is
an entity. A career is a row; the guild that grants it is an entity.

### `careers.yaml`

One `careers:` list — the career graph character creation and advancement both draw skills from
([`05-character-creation.md`](05-character-creation.md)). Each entry is one career:

```yaml
careers:
  - id: guard                 # stable, kebab-case, unique
    entry: true                # choosable at character creation with no prerequisite
    skills: [blade, watch]
  - id: soldier
    entry: true
    skills: [blade, drill]
  - id: guard-captain
    entry: false
    prerequisites: [guard, soldier]  # one or more; completing ANY ONE qualifies
    skills: [blade, watch, command]
```

`id`, `entry` and `skills` are **required** on every career. `prerequisites` is required (length
at least one) exactly when `entry` is `false`, and absent when it is `true` — a career is either
an entry point or names one or more predecessors, never both and never neither.
**`prerequisites` is OR, not AND: a character is eligible once *any one* listed career is
complete for them** — a single-entry list is a plain ladder rung (`guard-captain` above could
just as well list one career); a multi-entry list is a **zigzag** convergence, letting a career
be reached from more than one ladder. This is what makes both a **specialist** (a character who
keeps climbing one ladder's successive prerequisites) and a **generalist** (a character who
completes a spread of careers across different ladders) possible over the same graph shape — the
difference is which careers a character chose to complete, not a separate mechanic. `skills`'
length is **setting-defined per career**, not fixed across the table: nothing ties two careers to
the same skill count, only the "at least two skills opened" floor advancement already enforces
([`05-character-creation.md`](05-character-creation.md) §3).

**At least one career in the table must declare `entry: true`** — a character always has
somewhere to start. Every entry in `prerequisites` must name another career **in the same
table**, and the graph those edges form **must be acyclic**: a career is unreachable, and
therefore a setting-authoring error, only if **every** one of its `prerequisites` entries
eventually requires the career itself — the same class of error as a dangling `prerequisites`
reference. (A career named in more than one other career's `prerequisites` — as `guard` and
`soldier` both are above — is convergence, not a cycle.)

A career is **complete** for a character when every skill in its `skills` list has been opened
and raised to that career's cap — the terminal state of the advance mechanics
[`05-character-creation.md`](05-character-creation.md) §3 already defines, not a new one. Two
things key off that completed state: the **+1 maximum Stamina** bonus a completed career grants,
and **eligibility for any career listing it in `prerequisites`** — a character may choose a
non-entry career once any one of its declared prerequisites is complete for them.

### `bestiary.yaml`

One `creatures:` list. Each entry is one **adversary block** — the fields the ruleset reads off an
opponent, defined once in [`06-the-adversary.md`](06-the-adversary.md):

```yaml
creatures:
  - id: the-hunter          # stable, kebab-case, unique
    name: A named antagonist
    baseline: 35            # what it tests any skill it does not list at
    stamina_max: 7
    armour: modest          # none | light | modest | heavy
    skills:
      blade: 55
      tracking: 60
    damage: 1d6             # optional; an opponent may have no attack
    damage_type: slashing   # slashing | piercing | blunt | searing
    ranged: false           # optional, defaults to false
    traits:                 # optional; effects from the closed vocabulary only
      - name: Unhurried
        effect:
          difficulty: -10
```

`id`, `name`, `baseline`, `stamina_max`, `armour` and `skills` are **required**. Run
`python3 tools/check_bestiary.py setting/bestiary.yaml` — it rejects a missing required field, a
field the engine does not define, an out-of-range value, a damage type outside the closed four, a
trait effect outside the vocabulary, and a duplicated id.

**The unrecognised-field rejection is the one worth understanding.** A trait like
`regenerates: 2`, or a field like `immune_to: fire`, is not a setting retuning the engine — it is a
setting adding a mechanism, which the hard rule below forbids. The validator is where that rule is
actually enforced rather than merely stated.

A **named antagonist** does not go here. It is a `character` entity carrying the same block
([`27-entities.md`](27-entities.md)) — a bestiary holds kinds of thing, not individuals.

### `gear.yaml`

One `gear:` list. Each entry is a **weapon** or an **armour** piece — the fields
[`03-rules.md`](03-rules.md) §2 already reads for damage, armour rank and the casual/martial
distinction:

```yaml
gear:
  - id: broadsword
    name: Broadsword
    kind: weapon
    damage: 1d8              # dice expression
    damage_type: slashing    # slashing | piercing | blunt | searing
    class: martial            # casual | martial
    price: 40
    availability: restricted # setting-defined vocabulary, e.g. common | restricted | illegal

  - id: brigandine
    name: Brigandine
    kind: armour
    rank: modest              # none | light | modest | heavy
    price: 25
    availability: restricted
```

A weapon requires `id`, `name`, `kind`, `damage`, `damage_type`, `class`, `price`,
`availability`. Armour requires `id`, `name`, `kind`, `rank`, `price`, `availability`. Both
accept an optional `notes` field for flavour only.

`availability` is a **setting-defined vocabulary** — the engine does not close this set the way
it closes armour ranks and damage types, because what is legal to carry where is a fact about the
setting, not the engine ([`03-rules.md`](03-rules.md) §2).

Run `python3 tools/check_gear.py setting/gear.yaml` — same shape as `check_bestiary.py`: it
rejects a missing required field, a field the schema does not define, an out-of-range armour
rank or damage type, a `class` outside casual/martial, and a negative price.

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
| `d100` resolution, degrees of success, the Wyrd die | **every skill name, and which skills exist** ([`04-the-character.md`](04-the-character.md)) |
| Difficulty bands | when they apply |
| Stamina, armour dice, criticals, Aftermath | weapons, armour, critical flavour |
| Taint, Trauma, Fate, Resolve, Strain | what they are *called*, what causes them, and **whether they exist at all** |
| Career graph mechanics — entries, exits, advance triggers | the graph itself |
| Beats, Rally, downtime, party tension | what downtime looks like here |
| Loyalty, and the strained/irreconcilable relations | **which Loyalties exist, what they are called, and which pairs are strained or irreconcilable** ([`16-session.md`](16-session.md)) |
| Threats, threads, elapsed time, succession | who the Threats are |
| Diegetic bands ([`23-diegesis.md`](23-diegesis.md)) | the idiom they are spoken in |
| *(nothing)* | **the tone contract** ([`01-principles.md`](01-principles.md)) |
| *(nothing)* | **the voice** |

**A setting must not need to change engine code.** If it does, that is an engine gap and
should be fixed in the engine — the whole point of the layering
([`02-architecture.md`](02-architecture.md)).

**A second setting in the same genre is not a reskin of the first.** Two worlds may share a
mechanic and mean entirely different things by it — one calls it damnation, another calls it
fatigue of the soul — and the register carrying that difference is the hardest file to write,
not the easiest.

### Rules overrides — the hard rule

> **A setting may extend, retune or disable what the engine provides.
> It may never add a mechanism the engine does not have.**

New mechanisms go in the core, for everyone. This is the rule that keeps Wyrd a single system
rather than a family of incompatible forks, and it is not negotiable.

**Permitted:**

| Override | Example |
|---|---|
| **Extend** | add careers, talents, gear, creatures, or rows to a table (append above the engine's own range, without restating it — see [`07-tables.md`](07-tables.md)). *(Skills are not extended — a setting declares its own outright; there is no engine list to add to. See [ADR 0013](../adr/0013-the-engine-names-no-skill.md).)* |
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
  extend: {skills: setting/rules/skills.yaml, oracle-prompt-npc-objective: setting/rules/tables/oracle-prompt-npc-objective-extra.yaml}
```

Loaded after engine defaults, exactly like a chronicle's `houserules.yaml`. What is
overridable is a **closed set published by the engine** — an override naming anything else is
a load error, and renames are presentation-only, never reaching state. See
[`20-tooling.md`](20-tooling.md).

What a replacement table may and may not change, and what it must satisfy to load, is in
[`07-tables.md`](07-tables.md).

Overlays are declared in `setting.yaml` and loaded after engine defaults, exactly like
`houserules.yaml` for a chronicle.

---

## Conversion rules — required for any derived setting

A setting derived from an existing system **must** carry `setting/conversion.yaml`.

Without it, on-demand conversion ([`28-arcs-and-beats.md`](28-arcs-and-beats.md)) is
improvised each time, and the same source converted twice produces different numbers. That is
non-determinism entering through the back door — precisely what
[`20-tooling.md`](20-tooling.md) exists to prevent. A conversion table makes the process
mechanical, repeatable and auditable.

```yaml
# setting/conversion.yaml
from: {system: "<source system>", edition: "<edition>"}
version: 1                      # bump on any change; converted content records which it used

# --- numbers ---
skills:
  method: direct                # direct | scale | table
  note: "source is already percentile; values are read as printed"
  # A source skill maps to one of THIS setting's skill names. There is no engine
  # skill vocabulary in between -- see docs/adr/0013.
  map: {"<source skill>": "<this setting's skill>"}
difficulty:
  map: {easy: +20, average: 0, challenging: -10, difficult: -20, hard: -30}
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
re-conversion — a **structural** change under [`22-evolution.md`](22-evolution.md), never one
that rewrites what happened in play.

### The three things conversion must never do

1. **Reproduce prose verbatim.** Read-aloud text becomes a narrative seed. A converted beat is
   a situation, not a transcription — the same reason beats are never scripts.
2. **Invent numbers it cannot derive.** Where the source gives nothing, the field stays null
   and the entity stays `status: stub`. A guessed stat is worse than an absent one.
3. **Lose provenance.** Every converted entity records the source work and pages.

## A worked example: a mythic-fantasy setting

Useful because it is unlike the settings already built, so it tests the boundary.

| Need | Where it goes |
|---|---|
| Cultures instead of careers | `careers.yaml` — the graph shape still fits |
| A hope/despair balance | **already engine** — Taint and Resolve |
| Fault Line derived from a culture rather than a Drive | **retune** — a mapping table; the mechanism already exists |
| A downtime phase | **already engine** |
| Journeys as a played mechanic | **an engine gap, since closed** — see below |
| Beasts and named powers | `bestiary.yaml`, and `organisation` entities |
| A world in decline | **the tone contract** — `victory`, `scale_drift`, `power_curve` |
| The register | `voice.md` — elegiac, where another line might be dry or brutal |

Most of it lands in data, which is the point — the exercise is meant to find what does not.

**And it found one.** A setting built around travel needs journeys *played* rather than
narrated, and at the time this example was run Wyrd had no travel subsystem: the engine assumed
travel was always summarised ([`18-campaign.md`](18-campaign.md)).

That was a **new mechanism**, so by the hard rule above no setting was permitted to add it
itself. It went into the core instead, generalised, and every setting may now configure it or
leave it off — see [`30-journeys.md`](30-journeys.md). A setting that had quietly implemented
its own would have forked the engine, and the next setting wanting journeys would have found
nothing to reuse.

This is the worked example doing its job: the value of running an unfamiliar setting through
the contract is not confirming that it fits, but discovering precisely where it does not.

---

## Checklist for a new setting

1. `setting.yaml` — identity and engine compatibility
2. `voice.md` — write this **first**, before any data. It will change what you put in the data.
3. `names.yaml` and `calendar.yaml` — cheap, and immediately make the world feel inhabited
4. `careers.yaml` — the character system; the largest single job
5. `gear.yaml`, `bestiary.yaml` — enough to run one scenario, not everything; validate with `tools/check_gear.py` and `tools/check_bestiary.py`
6. a few `organisation` entities with objectives — so the world can act while the player is absent
7. One threat and one arc — enough to play
8. Index whatever sources you have ([`24-corpus-index.md`](24-corpus-index.md))

Steps 1–5 and one scenario is a playable setting. Everything else accumulates.
