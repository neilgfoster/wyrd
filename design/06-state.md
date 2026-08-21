# Wyrd — chronicle state

**State is entities.** There is no second storage model: the character, their companions,
the threads, the trackers and the world are all entity files with YAML frontmatter, exactly
as defined in [`14-entities.md`](14-entities.md).

What differs is not *format* but **where a file lives** and **when it is loaded**.

---

## Where things live

```
chronicle/
├─ chronicle.yaml     # the only non-entity file: pins, calendar, era, intent
├─ engine/            # copied at bootstrap. Read-only.
├─ setting/           # copied at bootstrap. Read-only.
├─ overlay/           # deltas to setting entities — what this chronicle changed
├─ entities/          # entities this chronicle created
├─ log/
└─ recap.md           # regenerated at session close
```

An **effective entity** is `setting/<id>` + `overlay/<id>`, or `entities/<id>` if the
chronicle invented it. Nothing else needs resolving.

## `chronicle.yaml`

The one file that is not an entity, because it describes the chronicle rather than anything
in the world.

```yaml
name: <chronicle-id>
engine:  {repo: wyrd, version: 0.4.0}
setting: {repo: <setting-repo>, version: 0.3.1}
calendar: {year: 0, month: null, day: 0}
era: null
sessions: 0
danger_rating: 2
migrations: []
intent:                      # from the bootstrap interview; read every session
  about: null
  avoid: []
  session_length: 20
  lethality: standard
  world_acts_offstage: true
pending: null                # set if a session stopped mid-beat
```

## The player's character

A `character` entity like any other, with `role: player`. Its frontmatter carries the live
mechanical state:

```yaml
---
id: <pc-id>
type: character
role: player
career: <career-id>
career_history: []
skills: {}                   # name -> percentage
stamina: {current: 0, max: 0}
luck: {current: 0, max: 0}
fate: {current: 0, max: 0}
fortune: {current: 0}
resolve: {current: 0, max: 0}
taint: 0
trauma: 0
strain: 0
hidden_threshold: null       # SECRET — set at first Transformation, never rendered
fault_line: null
transformations: []
afflictions: []
dread: 0
reputation: {score: 0, label: null}
drives: []
misfortune: null
wounds: []
holdings: []
allegiances: []
marks: []
advances_unspent: 0
---
```

`hidden_threshold` is written once and **never shown to the player**. Any render for the
player must strip it ([`10-diegesis.md`](10-diegesis.md)).

## Companions

`character` entities with `role: companion` and a `status`. There is no `party.yaml` — the
party is *a query*: characters with `role: companion` and `status: with-party`.

Their mechanical layer is deliberately thin ([`04-session.md`](04-session.md)) — presence,
bond, and a competence or two. No hidden threshold, no Fate, no career graph.

```yaml
role: companion
status: with-party           # with-party | away | dead | lost | departed
bond: 0                      # -3..+3, toward the player
```

Party tension is a `tracker`.

## Threads

A `thread` is an entity — an open loop the chronicle is carrying.

```yaml
---
id: <thread-id>
type: thread
status: open                 # open | resolved | cold | never-answered
heat: 3                      # 0-5; rises when touched, decays when ignored
hooks: []                    # matched against arc and beat entry conditions
opened: {year: 0, month: null}
links: []
---
```

Threads are the substrate campaign selection runs on
([`05-campaign.md`](05-campaign.md)). There is no `threads.yaml`; the live set is a query on
`status: open` ordered by heat.

## Threats

**A threat is not a type.** It is an aspect attached to a `character`, `organisation` or
`place`, because a campaign-length antagonist may be a person, a conspiracy or a poisoned
valley ([`14-entities.md`](14-entities.md)).

```yaml
threat:
  imminence: 3
  clues_found: []
  activations: 0
  connection: "why this touches the player"
  known_to_player: none      # none | rumoured | partial | understood
  effects: {}                # what happens when it activates
```

The active set is a query: entities with a `threat` block and `imminence > 0`.

## `recap.md`

Regenerated at every session close, always loaded, ~200 words: where and when you are, the
three hottest threads, what changed while you were away, the state of your body and mind in
one sentence, and who is with you.

## Load policy

Formats are identical; only *when* differs
([`02-architecture.md`](02-architecture.md)).

| Tier | What | How chosen |
|---|---|---|
| **Always** | `chronicle.yaml`, the player character, companions with `status: with-party`, threads with `heat ≥ 3`, `recap.md`, the GM contract | query, not a manifest |
| **On demand** | every other entity | fetched by id or by grep |
| **Archival** | `log/` | rarely read; the audit trail that makes compaction safe |

Choosing by query rather than a manifest means the tier can never drift out of date.

## Invariants

Enforced on every write, and tested directly:

- an entity's `id` is unique and stable; `parent` never forms a cycle
- every `[[link]]`, `parent` and `overlay_of` resolves
- `fortune.current ≤ fate.max`
- a character is **Spent** iff `resolve.current ≤ taint` and `taint > 0`
- `trauma ≥ 6` triggers a test on every further gain
- `transformations` count > `hidden_threshold` → `status: lost`
- a tracker's `value` stays within `0..max`; reaching `max` fires and resets
- **no write may be skipped because narration already happened** — persist precedes narrate

## Interrupted sessions

If a session stops mid-beat:

```yaml
pending:
  beat: <beat-id>
  awaiting: "what the player was about to decide"
  rolled: null
```

Cleared at the next Rally. Its presence means the next session resumes exactly rather than
recapping vaguely.
