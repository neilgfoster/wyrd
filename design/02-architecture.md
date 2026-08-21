# Wyrd — architecture

How the pieces separate, and what is code versus prose.

## Four repositories

Wyrd is four kinds of thing with four different lifecycles, so it is four repositories.

| Repo | Holds | Changes |
|---|---|---|
| **`wyrd`** | the engine — rules, CLI, GM contract, design | when a rule changes |
| **`wyrd-<setting>`** | one setting: world, content, indexes, corpus | when content is added |
| **`wyrd-chronicle-template`** | cloned to start a chronicle | rarely |
| **`wyrd-chronicle-<name>`** | one per chronicle — its state and entities | every beat |

There is one setting repository **per setting**, not per genre. A chronicle **references** an
engine version and a setting version; a setting declares a minimum engine version. Nothing
references a chronicle.

This is what makes parallel play safe: two chronicles never share a repository, so two live
sessions cannot race on a commit
([`12-parallel-chronicles.md`](12-parallel-chronicles.md)). It also means many
chronicles and many characters can coexist — several in the same setting, at different points
in its history, without interfering.

### Why settings are separate from the engine

Because they change for different reasons and at different rates. The engine changes when a
rule changes — rarely, deliberately, with a migration
([`09-evolution.md`](09-evolution.md)). A setting only accumulates: another arc indexed,
another organisation written up, another career added. Mixing them makes both histories
unreadable, and makes it impossible to say which version of *what* a chronicle is pinned to.

It also keeps the engine genuinely setting-agnostic rather than
setting-agnostic-in-principle. **If a rule cannot be written without naming a god, it is not
an engine rule.**

### The corpus lives with its setting

Extracted text from source material is committed to the setting repo it belongs to, alongside
the indexes over it ([`11-corpus-index.md`](11-corpus-index.md)). Setting repos are **private
where their sources are copyrighted**.

The engine repo holds **no corpus, no source text and no source digests**, because it is
intended to become public and nothing unpublishable may enter it. Research notes live
separately and privately.

A source usable by two settings is indexed **in both**, because the same adventure adapted for
two different worlds produces two different adaptations, not one shared record.

## Inside each repository

```
wyrd/                          # the engine
├─ engine/                     # rules, tables, the CLI
├─ design/                     # how and why
├─ settings.yaml               # the catalogue of known settings
└─ tools/

wyrd-<setting>/
├─ setting.yaml                # identity, engine compatibility, tone, overrides
├─ setting/                    # lookup tables: voice, careers, gear, names, calendar
│  └─ rules/                   # overrides only
├─ entities/                   # character · place · organisation · arc · beat ·
│                              # creature · item · tracker · thread · lore
├─ index/                      # documents · nouns · terms · tables · arcs
└─ corpus/                     # extracted source text

wyrd-chronicle-<name>/
├─ chronicle.yaml              # pins engine and setting versions; calendar; intent
├─ engine/                     # copied at bootstrap. Read-only.
├─ setting/                    # copied at bootstrap. Read-only.
├─ overlay/                    # deltas to setting entities
├─ entities/                   # entities this chronicle created, including the player character
├─ log/
└─ recap.md
```

Which files are tables and which are entities is decided by one test
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)): *would anything link to it, or
would a chronicle change it?*

### What the engine holds

- `rules/` — resolution, combat, the tracks, fate, fear, advancement
- `tables/` — criticals, aftermath, transformations, afflictions, oracles
- `contract.md` — the GM contract from [`01-principles.md`](01-principles.md), in the form
  loaded every session
- `settings.yaml` — the catalogue of known settings

Setting-neutral throughout. **A rule that names a god belongs in a setting, not here.**

### What a setting holds

Content, in the two forms distinguished in
[`13-authoring-a-setting.md`](13-authoring-a-setting.md):

- **Lookup tables** (`setting/*.yaml`) — voice, careers, gear, names, calendar, bestiary.
  Rows queried by key.
- **Entities** (`entities/**/*.md`) — every named thing, in the ten types
  ([`14-entities.md`](14-entities.md)). Arcs and beats live here, so scenarios and campaigns
  are entities like everything else.
- **Overrides** (`setting/rules/`) — extend, retune, rename or disable. Never a new mechanism.
- **Index and corpus** — [`11-corpus-index.md`](11-corpus-index.md).

### What a chronicle holds

Its pinned copies of engine and setting, an `overlay/` of what it has changed about that
setting, the entities it has created itself, its log, and its recap
([`06-state.md`](06-state.md)).

## Memory tiers

By session 40 the log is far larger than any context window. Three tiers:

1. **Always loaded** — `chronicle.yaml`, the player character, present companions, hot
   threads, `recap.md`, plus the engine contract. Chosen by **query, not manifest**. Target: a few thousand tokens.
2. **On demand** — any other entity, fetched by id or name when a scene needs them.
3. **Archival** — `log/`. Rarely read; exists so the history is recoverable and auditable.

**Compaction** runs at session end: what mattered is promoted into the entity store and the recap
is regenerated. This is the step that makes multi-year play possible, and it must be
mechanical, not optional.

## Code versus prose

**A small deterministic CLI** (`wyrd`) does the things the GM must not be trusted to do
freehand:

```
wyrd roll <skill> [--difficulty N]     # d100 + Wyrd die; full structured result
wyrd damage <target> <expr>            # applies damage, stamina, criticals
wyrd track <id> taint +1               # mutates a track, fires thresholds
wyrd advance-time <days>               # calendar, threat activation, expected-value events
wyrd threat-check                      # per-threat activation roll
wyrd save / wyrd load / wyrd validate  # atomic writes, schema validation
wyrd recap                             # regenerate recap.md from state
wyrd doctor [--repair|--propose]       # chronicle health: integrity, decay, budget
wyrd optimise                          # reindex, recompact, canonicalise
```

Maintenance is a first-class engine function, not a chore — see
[`08-maintenance.md`](08-maintenance.md).

Everything else is **skills** — prompt-level instructions the GM follows:

```
/wyrd-play              # resume the chronicle and run a beat
/wyrd-bootstrap         # complete a cloned template: character, intent, opening situation
/wyrd-character         # inspect or advance the player character
/wyrd-downtime          # run a downtime phase (see 04-session.md)
/wyrd-end-session       # compaction, recap regeneration, commit
```

The dice roller being external code is not pedantry. It is the thing that makes the world
feel indifferent to the player, and it is the only defence against principle 1 eroding
quietly over a long campaign.

Engineering ground rules for all of this — deterministic-over-inference, stdlib-only Python,
the MCP-shaped tool catalog, and model tiering — are in [`07-tooling.md`](07-tooling.md).

## Deployment

Wyrd runs wherever Claude Code runs — a laptop, or an always-on machine reached from a phone.
A chronicle is a git repository and needs no service, no database and no network at play
time; source material is fetched only when converting content
([`15-arcs-and-beats.md`](15-arcs-and-beats.md)).

Sessions are stateless with respect to the model: everything needed to resume is on disk.
