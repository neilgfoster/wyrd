# Wyrd

**A solo tabletop RPG engine for Claude Code.** One player, one character, played over text
across years.

Wyrd is **setting-agnostic**. It is its own system — percentile resolution descended from
percentile, simplified for narrative play — plus the machinery a solo campaign actually needs:
a world that moves while you are away, companions the GM plays as people, taint you
choose, consequences that outlive characters, and a chronicle that stays correct for a
decade.

Settings live in their own repositories and are overlaid onto a chronicle. the fantasy line
settings exist for several published worlds; anything else can be authored
([13-authoring-a-setting](design/13-authoring-a-setting.md)).

## Start a chronicle

```bash
gh repo create my-chronicle --private --template neilgfoster/wyrd-chronicle-template
cd my-chronicle && ./bootstrap
```

Then `/wyrd-play` in Claude Code.

## The repositories

| Repo | Holds | Public |
|---|---|---|
| **wyrd** *(here)* | the engine — rules, CLI, GM contract, design | intended |
| **wyrd-\<setting\>** | a setting: world, adventures, overrides, corpus | private where copyrighted |
| **wyrd-chronicle-template** | clone this to start playing | yes |
| **wyrd-chronicle-\<name\>** | one per chronicle | yours |
| **wyrd-research** | source mining notes | never |

Settings are catalogued in [settings.yaml](settings.yaml). A chronicle pins **an engine
version and a setting version**, both copied in, so nothing breaks when upstream moves.

## What makes it different

- **The dice bind the GM.** Rolls happen in code, before narration, and the result stands.
- **Power stays flat.** What grows over years is what you know and what it cost.
- **The world does not wait.** Threats advance on their own calendar; you hear late.
- **Adventures are beats**, not scripts — recombinable into campaigns their authors never
  wrote ([15-arcs-and-beats](design/15-arcs-and-beats.md)).
- **Settings and chronicles are Obsidian vaults.** The graph view is the world.
- **The past is a fact.** Rules change forward; history is never recomputed
  ([09-evolution](design/09-evolution.md)).

## Read in this order

**Design** — what Wyrd is:

| Doc | |
|---|---|
| [01-principles](design/01-principles.md) | The seven constraints and the GM contract |
| [02-architecture](design/02-architecture.md) | Engine / settings / scenarios / chronicles; code vs prose |
| [03-rules](design/03-rules.md) | The ruleset |
| [04-session](design/04-session.md) | Beats, Rally points, downtime, and the NPC party |
| [05-campaign](design/05-campaign.md) | Threats, threads, elapsed time, a losing struggle |
| [06-state](design/06-state.md) | The save schema |
| [07-tooling](design/07-tooling.md) | Deterministic-over-inference, stdlib Python, model tiering |
| [08-maintenance](design/08-maintenance.md) | Keeping a decade-long chronicle correct and cheap |
| [09-evolution](design/09-evolution.md) | How the engine changes without rewriting history |
| [10-diegesis](design/10-diegesis.md) | Knowing your character without reading their statistics |
| [11-corpus-index](design/11-corpus-index.md) | Finding the right passage in a library of 3,841 PDFs |
| [12-settings-and-parallel-play](design/12-settings-and-parallel-play.md) | Two settings, and running two chronicles at once |
| [13-authoring-a-setting](design/13-authoring-a-setting.md) | Everything needed to build a new setting |
| [14-entities](design/14-entities.md) | The world mesh — entities, overlays, Obsidian |
| [15-arcs-and-beats](design/15-arcs-and-beats.md) | Beats, the campaign matrix, lazy conversion |
| [16-chronicle-bootstrap](design/16-chronicle-bootstrap.md) | Cloning and seeding a chronicle |
| [adr/](design/adr/) | Decision records — resolution, source compatibility |

**Research** — the source mining that informed it — lives in the private
`wyrd-research` repo, because it quotes copyrighted RPG material directly.

## The core idea in one paragraph

the source line's register is that you are a labourer, not a chosen one. Wyrd enforces that
mechanically: power stays flat while danger scales, victory is usually mitigation, the world
darkens whether or not you attend, and the things that break are the people beside you.
Taint is a bargain you may choose to make. Death is deferred and usually survivable at
a price. What accumulates over years is not strength but knowledge, reputation, obligations,
and loss.

## Build order

1. **Skeleton** — save schema (including `engine_version`, `migrations[]` and provenance
   stamping from the first commit — see [09-evolution](design/09-evolution.md)), atomic
   writes, validation, and the `wyrd` CLI's dice and track verbs. Prove one fight and one
   taint gain round-trip through a save, then freeze it as the first golden chronicle.
2. **Ruleset** — combat, criticals, the Aftermath table, Taint/Trauma/Fate/Fear.
3. **the setting** — one setting, because you know instantly whether the voice is right.
4. **One scenario, three sessions.** Play it. This is the real test.
5. **Memory tiers and compaction** — driven by what actually broke in step 4.
6. **Campaign layer** — Threats, threads, elapsed time, scenario selection.
7. **Second setting (the science-fiction line)** to prove the layer boundary holds.

## Status

Design and research complete. No implementation yet.

A hand-run playtest is under way in [`playtest/`](playtest/) — no engine, dice by script,
state by hand. It has already corrected the resolution mechanic twice; see
[playtest/README](playtest/README.md).
