# Roadmap

Design is complete; nothing is implemented. This is the order to build in.

## 1. Skeleton

The `TOOLS` catalog and `describe`, the state layer with atomic writes and invariant
validation, and three verbs: `roll`, `damage`, `track`.

Version pinning, `migrations[]` and provenance stamping exist **from the first commit** —
they cannot be retrofitted, because the history they would describe has already happened
([`design/09-evolution.md`](design/09-evolution.md)).

Prove one fight and one track threshold round-trip through a save, then freeze it as the
**first golden chronicle**.

## 2. Ruleset

Combat, criticals, Aftermath, the tracks, Fate, Fear. Pure functions in `rules.py`, pure data
in `tables.py`, tested without fixtures ([`design/07-tooling.md`](design/07-tooling.md)).

## 3. One setting, minimally

Enough to run a single arc — voice, a career graph, some gear, a handful of entities. Not a
complete world ([`design/13-authoring-a-setting.md`](design/13-authoring-a-setting.md)).

## 4. Play it

One arc, three sessions. **This is the real test**, and the first playtest already showed why:
it corrected the resolution mechanic three times inside two rolls, none of which was visible
on paper.

## 5. Memory tiers and compaction

Driven by what actually broke in step 4, not by what was predicted in step 1.

## 6. Campaign layer

Threats, threads, elapsed time, arc selection against live threads.

## 7. A second setting

In a different genre, to prove the layer boundary holds rather than assuming it.

---

## Known engine gaps

Recorded so they are not rediscovered:

- **No journey subsystem.** A setting whose story is travel needs journeys *played* rather
  than summarised. Per the hard rule this belongs in the core, generalised, and never in a
  setting ([`design/13-authoring-a-setting.md`](design/13-authoring-a-setting.md)).
- **Companions may want two layers** — a rich narrative one and a deliberately thin
  mechanical one — rather than the single layer described today
  ([`design/04-session.md`](design/04-session.md)).
- **The party track runs one way.** Tension rises toward a break; there is no positive
  counterpart a functioning party can spend.
- **Taint has magnitude but only a nominal direction.** Fault Line names the path; nothing
  yet makes the direction mechanically distinct.

Each is a change to the engine, and each wants deciding rather than assuming.
