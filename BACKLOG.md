# Backlog

Open work, by kind. Items keep their identifier for life so commits and decision records can
reference them; closed items move to the bottom rather than being deleted.

**Status:** `open` · `next` (queued for the current phase) · `blocked` · `done`

---

## Engine gaps — `G`

Things a setting will need that the core does not yet provide. Per
[`design/13-authoring-a-setting.md`](design/13-authoring-a-setting.md) these are **always**
engine work, never setting work.

| id | | status |
|---|---|---|
| **G1** | **Journeys.** A setting whose story is travel needs journeys *played* rather than summarised. The engine assumes travel is narrated. Needs a generalised travel subsystem every setting can configure or leave off. | open |
| **G2** | **Companions may want two layers** — a rich narrative one and a deliberately thin mechanical one — rather than the single layer described in [`04-session`](design/04-session.md). | open |
| **G3** | **The party track runs one way.** Tension rises toward a break; there is no positive counterpart a functioning party can spend. | open |
| **G4** | **Taint has magnitude but only a nominal direction.** Fault Line names the path; nothing yet makes the direction mechanically distinct. | open |

## Build — `B`

The implementation sequence. Each depends on the one before.

| id | | status |
|---|---|---|
| **B1** | **Skeleton** — `TOOLS` catalog, `describe`, state layer with atomic writes and invariant validation, and `roll` / `damage` / `track`. Version pinning, `migrations[]` and provenance stamping from the first commit ([0006](design/adr/0006-state-is-entities.md), [`09-evolution`](design/09-evolution.md)). Ends by freezing the first golden chronicle. | next |
| **B2** | **Ruleset** — combat, criticals, Aftermath, the tracks, Fate, Fear. Pure functions, pure tables, tested without fixtures. | open |
| **B3** | **One setting, minimally** — enough to run a single arc. Not a complete world. | open |
| **B4** | **Play it.** One arc, three sessions. The real test: the first playtest corrected the resolution mechanic three times inside two rolls, none of it visible on paper. | open |
| **B5** | **Memory tiers and compaction** — driven by what broke in B4, not by what was predicted in B1. | open |
| **B6** | **Campaign layer** — threats, threads, elapsed time, arc selection against live threads. | open |
| **B7** | **A second setting** in a different genre, to prove the layer boundary holds rather than assuming it. | open |

## Defects — `D`

| id | | status |
|---|---|---|
| **D1** | **Corpus slug collision.** The extraction pipeline derives an output name from the source path truncated to 120 characters; 13 slugs collide across 70 paths and the resumability check then skips the later ones. 57 documents were never fetched, silently. Fix by hashing the full path. Pipeline is resumable, so only the missing are re-fetched. | open |
| **D2** | **Five unreadable source PDFs** — `pdfinfo` cannot open them at all. Probably corrupt in the collection rather than a pipeline fault; needs confirming. | open |
| **D3** | **Five transient download failures** during extraction. A re-run picks them up. | open |

## Settings — `S`

Onboarding is: create the repo, declare `setting.yaml` including its tone contract, write
`voice.md` **first**, then populate only what a chronicle actually needs
([`design/13-authoring-a-setting`](design/13-authoring-a-setting.md)).

| id | | status |
|---|---|---|
| **S1** | Eight settings are catalogued in [`settings.yaml`](settings.yaml) and all are stubs. **None should be populated until the engine exists** and a person has decided what belongs in each. | blocked on B4 |
| **S2** | Structured extractions are parked in the research repo — careers with their entry/exit graph, register notes. Inputs to a future setting, not a setting. | blocked on S1 |

## Research — `R`

| id | | status |
|---|---|---|
| **R1** | Review the extracted corpus and build a setting from it — **after** the engine is built. 443 documents, 80.5 M characters, in the private research repo. | blocked on B4 |
| **R2** | Build the deterministic corpus indexes — `documents`, `nouns`, `terms`, `tables` — then the `arcs` index ([`design/11-corpus-index`](design/11-corpus-index.md)). | blocked on D1 |

## Housekeeping — `H`

| id | | status |
|---|---|---|
| **H1** | Two superseded repositories need deleting; `gh` lacks the scope (`gh auth refresh -h github.com -s delete_repo`). | open |
| **H2** | Confirm the licensing position before the engine repository is made public. | open |

---

## Closed

*(nothing yet)*
