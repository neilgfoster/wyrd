# Wyrd

Claude Code as a tabletop RPG games master, for grim low-fantasy solo play.

**One player, one character.** Claude runs the world, the story, and the entire rest of the
party as NPCs. Text only — no maps, no grids. Sessions of twenty minutes from a phone,
across a chronicle meant to run years.

Setting is Warhammer Fantasy first (the Reikland), 40k later on the same engine. The
ruleset is *Warlock!* as a chassis with the Warhammer dials fitted: Corruption, Insanity,
Fate, Fear.

## Read in this order

**Design** — what Wyrd is:

| Doc | |
|---|---|
| [01-principles](design/01-principles.md) | The seven constraints and the GM contract |
| [02-architecture](design/02-architecture.md) | Engine / settings / scenarios / chronicles; code vs prose |
| [03-rules](design/03-rules.md) | The ruleset |
| [04-session](design/04-session.md) | Beats, Rally points, downtime, and the NPC party |
| [05-campaign](design/05-campaign.md) | Threats, threads, elapsed time, the long defeat |
| [06-state](design/06-state.md) | The save schema |
| [07-tooling](design/07-tooling.md) | Deterministic-over-inference, stdlib Python, model tiering |
| [08-maintenance](design/08-maintenance.md) | Keeping a decade-long chronicle correct and cheap |
| [09-evolution](design/09-evolution.md) | How the engine changes without rewriting history |
| [10-diegesis](design/10-diegesis.md) | Knowing your character without reading their statistics |
| [adr/](design/adr/) | Decision records — resolution mechanic, 2e compatibility |

**Reference** — where it came from:

| Doc | |
|---|---|
| [library](reference/library.md) | The source collection: 112 systems, 3,841 PDFs |
| [library-triage](reference/library-triage.md) | Which of them are worth reading |
| [warlock-rules](reference/warlock-rules.md) | The base system |
| [wfrp-mechanics](reference/wfrp-mechanics.md) | Fate, Insanity, Corruption, Fear |
| [wfrp3-concepts](reference/wfrp3-concepts.md) | Session structure, party tension |
| [tor-concepts](reference/tor-concepts.md) | Hope/Shadow, the year cycle, the long defeat |
| [dice-design](reference/dice-design.md) | The resolution mechanic and why |
| [systems-mined](reference/systems-mined.md) | Threat Packs, injuries, scaling |
| [scenarios](reference/scenarios.md) | Runnable material, biased to short-form |

## The core idea in one paragraph

Warhammer's register is that you are a rat-catcher, not a chosen one. Wyrd enforces that
mechanically: power stays flat while danger scales, victory is usually mitigation, the world
darkens whether or not you attend, and the things that break are the people beside you.
Corruption is a bargain you may choose to make. Death is deferred and usually survivable at
a price. What accumulates over years is not strength but knowledge, reputation, obligations,
and loss.

## Build order

1. **Skeleton** — save schema (including `engine_version`, `migrations[]` and provenance
   stamping from the first commit — see [09-evolution](design/09-evolution.md)), atomic
   writes, validation, and the `wyrd` CLI's dice and track verbs. Prove one fight and one
   corruption gain round-trip through a save, then freeze it as the first golden chronicle.
2. **Ruleset** — combat, criticals, the Aftermath table, Corruption/Insanity/Fate/Fear.
3. **Reikland** — one setting, because you know instantly whether the voice is right.
4. **One scenario, three sessions.** Play it. This is the real test.
5. **Memory tiers and compaction** — driven by what actually broke in step 4.
6. **Campaign layer** — Threats, threads, elapsed time, scenario selection.
7. **Second setting (40k)** to prove the layer boundary holds.

## Status

Design and research complete. No implementation yet.

A hand-run playtest is under way in [`playtest/`](playtest/) — no engine, dice by script,
state by hand. It has already corrected the resolution mechanic twice; see
[playtest/README](playtest/README.md).
