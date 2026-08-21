# Wyrd — chronicle maintenance

A chronicle is a growing, mostly-append store that must stay correct and cheap to load for
years. Left alone it rots in predictable ways: the entity store accumulates one-line characters, threads
pile up unresolved, the same person appears under three spellings, derived fields drift from
their sources, and the always-loaded tier quietly outgrows its budget until session start
becomes expensive.

Maintenance is therefore an engine function, not a chore.

Per [`07-tooling.md`](07-tooling.md), **almost all of this is deterministic.** Only two
operations need a model, both are Haiku-tier, and both **propose rather than apply**.

---

## The safety rule

> **Maintenance may repair derived data automatically. It may never alter the fiction
> without confirmation.**

Two tiers, and the boundary is strict:

| Tier | May run unattended | Examples |
|---|---|---|
| **Repair** | yes | recompute `career_skill`, rebuild indexes, fix conditions, rotate logs, decay thread heat, GC orphans |
| **Revision** | **no — proposes only** | merge two characters, close a thread as never-answered, demote an entity, resolve a continuity contradiction |

Anything that changes what *happened* is a proposal the player accepts or rejects. A
maintenance pass that silently rewrote history would be the worst possible failure mode for
a decade-long chronicle.

---

## `wyrd doctor` — the umbrella verb

```bash
wyrd doctor                    # report only; never writes
wyrd doctor --repair           # apply Repair-tier fixes
wyrd doctor --propose          # additionally emit Revision-tier proposals as JSON
wyrd doctor --check integrity  # run one check group
```

Exit codes: `0` clean · `1` repairable issues found · `2` revision proposals pending ·
`3` corrupt state (refuse to play).

Structured output, one entry per finding, with a stable `code` so skills can react:

```json
{"code": "ORPHAN_THREAD_REF", "severity": "repair",
 "path": "entities/thread/<id>.md",
 "detail": "hook references a character entity that does not exist",
 "fix": "drop hook | create stub"}
```

---

## Check groups

### 1. `integrity` — the state is self-consistent

- schema validation of every file
- **invariants** from [`06-state.md`](06-state.md): `career_skill` is the lowest career
  skill; `stamina.max` only grew with it; `fortune.current <= fate.max`; Spent iff
  `resolve <= taint and taint > 0`; `tension` in 0..6; transformations vs `hidden_threshold`
- **referential integrity**: every thread hook, threat connection, parent and link resolves to something that exists
- **status contradictions**: a character marked `dead` who is also `with-party`; a `lost` PC
  still holding Fortune; a resolved thread still hot
- **calendar sanity**: no event dated before the chronicle began; no threat activation in
  the future
- **version sanity**: every file carries a `schema_version` the engine understands; no entity
  claims a version newer than the engine; `migrations` is ordered and unbroken; every derived
  entity names conversion rules that exist ([`06-state.md`](06-state.md))

Everything here is Repair-tier except status contradictions, which are reported and
proposed.

### 2. `derived` — recompute what is computed

Derived fields are cached for cheap loading and must be rebuilt, not trusted:
`career_skill`, `conditions`, `fear_points`, `fortune.max`, thread `heat` after decay,
entity summary index, `viable_successor` flags.

Always safe. Always automatic.

### 3. `decay` — time passing has consequences for the store, not just the world

- **thread heat** decays on a schedule; a thread untouched for a game-year goes `cold`
- **cold threads** older than a further year are *proposed* for closure as
  `never-answered` — which is true to the setting, and is why it is a proposal not a repair
- **resolved threats** are archived out of the hot file
- **departed companions** change `status`, keeping their entity and their arc

### 4. `entities` — keep the entity store clean

- **orphans**: entities never referenced by any thread, threat, log or party member —
  reported, proposed for demotion into a `minor/` bucket rather than deletion
- **stubs**: entries with a name and nothing else — flagged for enrichment at next mention
- **duplicates**: near-identical entries — the same person under two spellings and a nickname. Detection is deterministic (normalised name distance, shared threads,
  overlapping `last_seen`); **merging is a proposal**, because two similar names may be two
  real people, and the engine cannot know.

### 5. `budget` — the always-loaded tier stays small

Session start loads the always-tier ([`06-state.md`](06-state.md)). That tier has a **budget**, and `doctor` reports against it:

| File | Target |
|---|---|
| `recap.md` | ≤ 300 words |
| open threads | ≤ 12 |
| present companions | ≤ 6 |
| whole tier | ≤ ~6k tokens |

Over budget is not an error, it is a signal that decay and compaction are overdue. The
report names the specific offender rather than saying "too big".

### 6. `logs` — rotation and archive

Session logs rotate into per-era archives (`log/archive/the-quiet-years.jsonl`), compressed
with stdlib `gzip`. Nothing is ever deleted; the raw record is the audit trail that makes
everything else safe to compact.

### 7. `continuity` — the one that needs a model

The only genuinely hard check: does the entity store contradict the log? An NPC who died in session
4 and speaks in session 9. A location described as burned and later intact. A thread marked
resolved whose resolution never appears.

This is bulk structured comparison against files that already exist, with a right answer —
squarely Haiku-tier per [`07-tooling.md`](07-tooling.md). It runs as a subagent, reads the
archive, and **emits proposals only**:

```json
{"code": "CONTINUITY_CONTRADICTION", "severity": "revision",
 "detail": "a character marked dead speaks in a later log entry",
 "candidates": ["the entity is wrong", "log is a different Otto", "he survived"]}
```

It never picks. The player does, or the GM does with the player watching.

---

## `wyrd optimise`

Separate from `doctor`, because it is about cost rather than correctness.

- **reindex** the entity summary index used for on-demand matching
- **recompact**: re-run promotion from archive to entities with current heuristics, useful
  after the compaction rules change
- **prune generated artefacts**: regenerable caches, never source
- **vacuum**: rewrite state files canonically (stable key order, consistent formatting) so
  git diffs stay legible over years — this alone makes the chronicle's history readable

Optimise is always Repair-tier: it may not change any fact.

---

## When maintenance runs

| Trigger | Runs |
|---|---|
| Every session close | `derived`, `budget` report, log rotation, compaction |
| Every session start | `integrity` (fast path); refuse to play on exit code 3 |
| End of an arc | `decay`, orphan report |
| End of an era | full `doctor --propose`, `optimise`, git tag |
| Monthly (cron) | full `doctor --propose` + `continuity`; report to the player, apply nothing |

The monthly pass is the one that suits a lab server: it can run unattended precisely
*because* Revision-tier changes only ever propose. The player comes back to a list, not a
rewritten history.

---

## Backups

The chronicle is a git repo, so history is free — but maintenance makes that explicit:

- commit after **every** beat (persist-before-narrate makes this cheap and meaningful)
- **git tag at each era boundary**, so a decade of play has navigable checkpoints
- `wyrd doctor` refuses `--repair` on a dirty working tree; every repair lands as its own
  commit with the findings in the message

That way any maintenance action is reviewable and revertible — which is the real
justification for keeping the chronicle in git rather than a database.
