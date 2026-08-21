# Wyrd — architecture

How the pieces separate, and what is code versus prose.

## Four repositories

Wyrd is four kinds of thing with four different lifecycles, so it is four repositories.

| Repo | Holds | Changes |
|---|---|---|
| **`wyrd`** | the engine — rules, CLI, GM contract, design, mechanics research | when the game changes |
| **`wyrd-<setting>`** | the setting, fantasy scenarios, fantasy corpus indexes | when content is added |
| **`wyrd-<sf-setting>`** | the science-fiction setting setting, the science-fiction line scenarios, the science-fiction line corpus indexes | when content is added |
| **`wyrd-chronicle-*`** | one per chronicle — the save, its codex, its threads | every beat |

A chronicle **references** an engine version and a setting version; a setting references a
minimum engine version. Nothing references a chronicle.

This is what makes parallel play safe: two chronicles never share a repository, so two live
sessions cannot race on a commit
([`12-settings-and-parallel-play.md`](12-settings-and-parallel-play.md)). It also means many
chronicles and many characters can coexist — several in the same setting, at different points
in its history, without interfering.

### Why the settings are separate from the engine

Because they change for different reasons and at different rates. The engine changes when a
rule changes — rarely, deliberately, with a migration
([`09-evolution.md`](09-evolution.md)). A setting accumulates: another scenario indexed,
another faction written up, another career added. Mixing them makes both histories
unreadable, and makes it impossible to say which version of *what* a chronicle is pinned to.

It also keeps the engine repository genuinely setting-agnostic rather than
setting-agnostic-in-principle. If a rule cannot be written without naming a god, it is not
an engine rule.

### The source corpus lives in the setting repos

Extracted text from the PDF library is committed to the relevant setting repo, alongside the
indexes over it. Setting repos are **private and must stay private** — the corpus is derived
from copyrighted books.

This is the reason the engine repo holds no corpus and no source digests: it is intended to
become **public**, so nothing that cannot be published may enter it. Research notes live in
the private `wyrd-research`.

Also committed, per setting, are the **indexes** —
[`11-corpus-index.md`](11-corpus-index.md) — which are small, are metadata rather than
content, and are the part with real value. The master catalogue of source material
([`library.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library.md)) stays in the engine repo, since it maps
the raw material both settings draw from.

Cross-setting sources are indexed **in both** settings, because a Deadlands adventure adapted
for the starting region and the same adventure adapted for a hive world are two different
adaptations, not one shared record.

## Inside each repository

```
wyrd/
├─ engine/          # ruleset + GM contract. Setting- and scenario-agnostic.
├─ design/          # how and why
├─ reference/       # mechanics research across systems
└─ tools/

wyrd-<setting>/
├─ setting/         # voice, careers, gear, factions, deities, names, calendar
├─ scenarios/       # situations and Threat Packs
└─ index/           # documents, nouns, terms, tables, scenarios

wyrd-chronicle-<name>/
├─ chronicle.yaml   # pins engine_version AND setting_version
├─ pc.yaml, party.yaml, threats.yaml, threads.yaml
├─ codex/
├─ log/
└─ recap.md
```

### wyrd — the engine

- `rules/` — resolution, combat, taint, trauma, fate, fear, advancement
- `tables/` — criticals, injuries, transformations, miscasts, oracles
- `contract.md` — the GM contract from [`01-principles.md`](01-principles.md), in the form
  loaded every session

Setting-neutral. A rule that names a god belongs in `settings/`, not here.

### wyrd-<setting> — a setting

A setting is **data plus a voice document**.

```
wyrd-<setting>/setting/
├─ voice.md          # register, vocabulary, what a critical failure looks like here
├─ careers.yaml      # the career tree (the chassis system careers, the setting-named)
├─ gear.yaml         # weapons, armour, prices, what is legal to carry where
├─ factions.yaml     # sects, guilds, watch, nobility — with agendas
├─ deities.yaml
├─ names.yaml        # given/family/place name tables
└─ calendar.yaml     # months, festivals, the ill moon cycle
```

The the science-fiction line setting is the same shape with different data and one extra rules overlay
(psychic powers reskinned from magic; see [`03-rules.md`](03-rules.md)).

### scenarios — inside each setting repo

Two kinds, and the distinction matters:

- **Threat** — a campaign-length antagonist with an Imminence rating that acts on its own
  schedule. Format taken from a sandbox source system. See [`05-campaign.md`](05-campaign.md).
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

### wyrd-chronicle-<name>

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
wyrd roll <skill> [--diffisecty N]     # 3d6 + Wyrd die, returns full structured result
wyrd damage <target> <expr>            # applies damage, stamina, criticals
wyrd track <pc> taint +1          # mutates tracks, fires thresholds
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
[`library.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library.md)).

Sessions are stateless with respect to Claude: everything needed to resume is on disk.
