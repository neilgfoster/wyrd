# Wyrd

**A solo tabletop RPG engine for Claude Code.** One player, one character, played over text
across years.

Wyrd is **setting-agnostic**. It is its own system — percentile, simplified for narrative
play — plus the machinery a solo campaign actually needs: a world that moves while you are
away, companions the GM plays as people, consequences that outlive characters, and a
chronicle that stays correct for a decade.

Worlds live in their own **setting** repositories and are overlaid onto a chronicle. Anything
can be authored, from an original world to a conversion of a published one
([13-authoring-a-setting](design/13-authoring-a-setting.md)).

## Start a chronicle

```bash
gh repo create my-chronicle --private --template neilgfoster/wyrd-chronicle-template
cd my-chronicle && ./bootstrap
```

The bootstrap asks which setting, copies the engine and setting in at pinned versions, and
interviews you about your character and what you want the chronicle to be about. Then
`/wyrd-play` in Claude Code.

## What makes it different

- **The dice bind the GM.** Rolls happen in code, before narration, and the result stands.
  Without this, solo play becomes wish-fulfilment.
- **One roll, three answers.** `d100` gives success, magnitude, and *what else happened* —
  on genuinely independent axes ([ADR 0001](design/adr/0001-resolution.md)).
- **The world does not wait.** Threats and characters act on their own objectives; you hear
  about it late, partially, and sometimes wrong.
- **Adventures are beats**, not scripts — recombinable into campaigns their authors never
  wrote ([15-arcs-and-beats](design/15-arcs-and-beats.md)).
- **Tone is the setting's, not the engine's.** A setting declares whether prophecy is
  forbidden or central, whether victory is mitigation or triumph, how flat the power curve
  runs — and the engine holds that line against its own drift.
- **Settings and chronicles are Obsidian vaults.** The graph view is the world.
- **The past is a fact.** Rules change forward; history is never recomputed
  ([09-evolution](design/09-evolution.md)).

## The repositories

| Repo | Holds | Visibility |
|---|---|---|
| **wyrd** *(here)* | the engine — rules, CLI, GM contract, design | intended public |
| **wyrd-setting-\<name\>** | one setting: world, content, overrides, corpus | private where its sources are |
| **wyrd-chronicle-template** | clone this to start playing | template |
| **wyrd-chronicle-\<name\>** | one per chronicle | yours |

Known settings are listed in [settings.yaml](settings.yaml). A chronicle pins **an engine
version and a setting version**, both copied in, so nothing breaks when upstream moves — and
two chronicles never share a repository, so they can be played in parallel without
interfering.

## Contributing

Ground rules are in [CLAUDE.md](CLAUDE.md) — decision records, the setting-agnostic rule,
and what may not enter this repository.

Open work is tracked as GitHub issues rather than in a file. Epics live in this repo and may
have children in any `wyrd-*` repository; the board spans them all.

## Read in this order

| Doc | |
|---|---|
| [01-principles](design/01-principles.md) | Seven engine principles, the tone contract, the GM contract |
| [02-architecture](design/02-architecture.md) | The four repositories; code versus prose |
| [03-rules](design/03-rules.md) | The ruleset |
| [03b-the-character](design/03b-the-character.md) | What a character is made of, and on what scale |
| [03c-character-creation](design/03c-character-creation.md) | Turning a setting's options into a playable character |
| [03d-the-adversary](design/03d-the-adversary.md) | What an opponent is made of, and which rule reads each field |
| [03a-tables](design/03a-tables.md) | Table conventions, and the index of the table families |
| [03a-1-criticals](design/03a-1-criticals.md) | The Criticals family — the four damage types, and one table for each |
| [03a-2-aftermath](design/03a-2-aftermath.md) | The Aftermath family — what happens to a combatant who drops |
| [03a-3-transformations](design/03a-3-transformations.md) | The Transformations family — Taint thresholds, the hidden count, Dread |
| [03a-4-afflictions](design/03a-4-afflictions.md) | The Afflictions family — the Trauma test, the table, the sawtooth cadence |
| [03e-playtest-transcript](design/03e-playtest-transcript.md) | A hand-run character creation and combat exchange against the R1 specification |
| [04-session](design/04-session.md) | Beats, Rally points, downtime, and the party |
| [05-campaign](design/05-campaign.md) | Threats, threads, elapsed time, succession |
| [06-state](design/06-state.md) | Chronicle state — which is entities |
| [07-tooling](design/07-tooling.md) | Deterministic-over-inference, stdlib Python, model tiering |
| [08-maintenance](design/08-maintenance.md) | Keeping a decade-long chronicle correct and cheap |
| [09-evolution](design/09-evolution.md) | How the engine changes without rewriting history |
| [10-diegesis](design/10-diegesis.md) | Knowing your character without reading their statistics |
| [11-corpus-index](design/11-corpus-index.md) | Finding the right passage in a large library |
| [12-parallel-chronicles](design/12-parallel-chronicles.md) | Running more than one chronicle at once |
| [13-authoring-a-setting](design/13-authoring-a-setting.md) | Everything needed to build a setting |
| [14-entities](design/14-entities.md) | The world mesh — ten types, two relations, overlays |
| [15-arcs-and-beats](design/15-arcs-and-beats.md) | Beats, recombination, lazy conversion |
| [16-chronicle-bootstrap](design/16-chronicle-bootstrap.md) | Cloning and seeding a chronicle |
| [17-journeys](design/17-journeys.md) | The travel subsystem — legs, hazards, and when it's inert |
| [adr/](design/adr/) | Decision records — indexed in [design/README.md](design/README.md) |

Two more trees, reachable from here so nothing in the repo is orphaned:

| | |
|---|---|
| [specs/](specs/) | One directory per change that added or altered a capability — spec, plan, tasks |
| [tools/](tools/) | Repository tooling: `backlog.py` for what to work on next, `check_docs.py` for this page's own integrity |

## The core idea in one paragraph

A solo chronicle fails in two ways: the world stops being real, or the record stops being
true. Wyrd defends against both. The world stays real because everyone in it wants something
and pursues it whether or not you are watching, and because the dice are rolled in code
before anything is narrated. The record stays true because state is written before prose,
history is never recomputed when rules change, and nothing significant happens that the
saved state cannot account for. What kind of story that produces is the setting's business,
not the engine's.

## Build order

1. **Skeleton** — state schema (with version pinning, migrations and provenance stamping
   from the first commit — see [09-evolution](design/09-evolution.md)), atomic writes,
   validation, and the CLI's dice and track verbs. Prove one fight and one track threshold
   round-trip through a save, then freeze it as the first golden chronicle.
2. **Ruleset** — combat, criticals, Aftermath, the tracks, Fate, Fear.
3. **One setting** — enough to run a single arc, no more.
4. **One arc, three sessions.** Play it. This is the real test.
5. **Memory tiers and compaction** — driven by what actually broke in step 4.
6. **Campaign layer** — threats, threads, elapsed time, arc selection.
7. **A second setting** in a different genre, to prove the layer boundary holds.

## Status

**Design in consolidation; no implementation yet.**

The ruleset has been playtested by hand — dice by script, arithmetic by hand, no engine —
which corrected the resolution mechanic three times in its first two rolls and is why the
design says what it does. Chronicles live in their own repositories.

The design was built by topic rather than in dependency order, and the recurring result was a
mechanic referenced before it was defined. The **design programme** is working through it in
thirteen stages, each finished before the next depends on it; the character model is the stage
most of the others wait on. Open work is tracked on the board — see
[CLAUDE.md](CLAUDE.md#the-backlog-has-an-order) — and `python3 tools/backlog.py next` names the
next thing to do.
