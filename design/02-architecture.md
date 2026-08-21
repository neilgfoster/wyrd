# Wyrd — architecture

How the pieces separate, and what is code versus prose.

## The four layers

```
wyrd/
├─ engine/          # ruleset + GM contract. Setting- and scenario-agnostic.
├─ settings/        # reikland/ , imperium/ — tone, factions, careers, gear, names
├─ scenarios/       # situations and arcs. Threat Packs, one-shots.
└─ corpus/          # extracted text and indexes over the source library

chronicles/
├─ reikland-01/     # each its own git repo — see 12-settings-and-parallel-play.md
└─ imperium-01/
```

**Chronicles live outside the engine repo.** They are data with a different lifecycle, and
separate repos are what make two live chronicles safe to run in parallel.

Keeping these separable is the whole design: any scenario × any compatible setting × one
engine. A **chronicle** pins all three plus accumulated state.

### engine/

- `rules/` — resolution, combat, corruption, insanity, fate, fear, advancement
- `tables/` — criticals, injuries, mutations, miscasts, oracles
- `contract.md` — the GM contract from [`01-principles.md`](01-principles.md), in the form
  loaded every session

Setting-neutral. A rule that names Sigmar belongs in `settings/`, not here.

### settings/

A setting is **data plus a voice document**.

```
settings/reikland/
├─ voice.md          # register, vocabulary, what a critical failure looks like here
├─ careers.yaml      # the career tree (Warlock careers, Reikland-named)
├─ gear.yaml         # weapons, armour, prices, what is legal to carry where
├─ factions.yaml     # cults, guilds, watch, nobility — with agendas
├─ deities.yaml
├─ names.yaml        # given/family/place name tables
└─ calendar.yaml     # months, festivals, Morrslieb cycle
```

The 40k setting is the same shape with different data and one extra rules overlay
(psychic powers reskinned from magic; see [`03-rules.md`](03-rules.md)).

### scenarios/

Two kinds, and the distinction matters:

- **Threat** — a campaign-length antagonist with an Imminence rating that acts on its own
  schedule. Format taken from Beyond the Wall. See [`05-campaign.md`](05-campaign.md).
- **Situation** — a one-shot to three-session scenario. A place, people with agendas, a
  clock, and a cost. **Never a script.**

```
scenarios/the-drowning-well/
├─ scenario.yaml     # metadata: threat rating T, settings it fits, hooks, threads emitted
├─ situation.md      # what is true, who wants what, what happens if nobody intervenes
├─ cast.yaml         # NPCs with agendas
└─ clock.yaml        # what advances, and what fires at each step
```

Every scenario declares `source:` — where it came from and what was changed. Partly honesty,
partly so adapted material is distinguishable from original three years in.

### chronicles/ *(separate repos)*

```
chronicles/<name>/
├─ chronicle.yaml    # setting, engine version, calendar date, era
├─ pc.yaml           # the player's character — full state
├─ party.yaml        # companions
├─ threats.yaml      # active Threats and their Imminence
├─ threads.yaml      # open threads (see 05-campaign.md)
├─ codex/            # one file per NPC, location, faction — loaded on demand
├─ log/              # session transcripts, archival
└─ recap.md          # regenerated at each session end; the always-loaded summary
```

Git-committed after every session. That gives free undo and a free campaign history.

## Memory tiers

By session 40 the log is far larger than any context window. Three tiers:

1. **Always loaded** — `chronicle.yaml`, `pc.yaml`, `party.yaml`, `recap.md`, active
   `threads.yaml`, plus the engine contract. Target: a few thousand tokens.
2. **On demand** — `codex/` entries, fetched by name when a scene needs them. Claude greps.
3. **Archival** — `log/`. Rarely read; exists so the history is recoverable and auditable.

**Compaction** runs at session end: what mattered is promoted into the codex and the recap
is regenerated. This is the step that makes multi-year play possible, and it must be
mechanical, not optional.

## Code versus prose

**A small deterministic CLI** (`wyrd`) does the things Claude must not be trusted to do
freehand:

```
wyrd roll <skill> [--difficulty N]     # 3d6 + Wyrd die, returns full structured result
wyrd damage <target> <expr>            # applies damage, stamina, criticals
wyrd track <pc> corruption +1          # mutates tracks, fires thresholds
wyrd advance-time <days>               # calendar, Threat activation, expected-value events
wyrd threat-check                      # weekly d12 per Threat
wyrd save / wyrd load / wyrd validate  # atomic writes, schema validation
wyrd recap                             # regenerate recap.md from state
wyrd doctor [--repair|--propose]       # chronicle health: integrity, decay, budget
wyrd optimise                          # reindex, recompact, canonicalise
```

Maintenance is a first-class engine function, not a chore — see
[`08-maintenance.md`](08-maintenance.md).

Everything else is **skills** — prompt-level instructions Claude follows:

```
/wyrd-play              # resume the chronicle and run a beat
/wyrd-new-chronicle     # setting choice, character creation, opening situation
/wyrd-character         # inspect or advance the PC
/wyrd-fellowship        # run a downtime phase (see 04-session.md)
/wyrd-end-session       # compaction, recap regeneration, commit
```

The dice roller being external code is not pedantry. It is the thing that makes the world
feel indifferent to the player, and it is the only defence against constraint 1 eroding
quietly over a long campaign.

Engineering ground rules for all of this — deterministic-over-inference, stdlib-only Python,
the MCP-shaped tool catalog, and model tiering — are in [`07-tooling.md`](07-tooling.md).

## Deployment

Runs on the lab server, reached from a phone via remote control. The chronicle is a git
repo; the library is read on demand from OneDrive (see
[`../reference/library.md`](../reference/library.md)).

Sessions are stateless with respect to Claude: everything needed to resume is on disk.
