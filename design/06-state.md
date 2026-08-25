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

## Versioning

Four things evolve independently across a chronicle's life, so four things carry versions
([`09-evolution.md`](09-evolution.md)):

| What | Where | Why |
|---|---|---|
| **The engine** | `chronicle.yaml` | rules change |
| **The setting** | `chronicle.yaml` | content accumulates |
| **The state format** | `schema_version`, on every file | fields are added, renamed or moved |
| **The conversion rules** | `converted:`, on derived entities | a source is re-read differently |

And one thing carries provenance rather than a version: **every recorded outcome states which
engine produced it**, so an apparent inconsistency years later can be identified as drift or
as an intended change.

None of this can be retrofitted — the history you would want to describe has already
happened — so all of it exists from the first commit.

## `chronicle.yaml`

The one file that is not an entity, because it describes the chronicle rather than anything
in the world.

```yaml
schema_version: 1                 # the state format this chronicle is written in
name: <chronicle-id>

engine:
  repo: wyrd
  version: 0.4.0                  # what it runs under now
  created_under: 0.1.0            # what it began under
setting:
  repo: <setting-repo>
  version: 0.3.1
  created_under: 0.2.0

calendar: {year: 0, month: null, day: 0}
era: null
sessions: 0
danger_rating: 2

migrations:                       # append-only; never edited, never reordered
  - from:    {engine: 0.1.0}
    to:      {engine: 0.2.0}
    class:   tuning               # additive | tuning | structural | behavioural | corrective
    applied: <date>
    note:    "what changed, and that it applied forward only"

intent:                           # from the bootstrap interview; read every session
  about: null
  avoid: []
  session_length: 20
  lethality: standard
  world_acts_offstage: true

pending: null                     # set if a session stopped mid-beat
```

`created_under` matters as much as `version`: it is how a reader years later can tell whether
an early oddity was a bug or simply the rules of the time.

## Entity versioning

Every entity carries the state-format version it was written in, and derived entities also
carry the conversion rules that produced them:

```yaml
---
id: <entity-id>
type: character
schema_version: 1
converted: {rules: 2, on: <date>}   # only on entities derived from source material
---
```

This is what lets `wyrd doctor` report **which entities predate a change** and offer
re-conversion, rather than the engine silently reading old files under new assumptions
([`08-maintenance.md`](08-maintenance.md)). Re-conversion is a *structural* change: the
representation moves, the history does not.

An entity with no `schema_version` is treated as version 1 and flagged, not rejected.

## Log provenance

Every logged outcome stamps what produced it:

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "setting": "0.2.0",
 "roll": 23, "success": true, "degrees": 1, "wyrd": "none"}
```

Cheap to write, and it is what makes a decade of log falsifiable. Without it, an
inconsistency between session 40 and session 400 is unattributable.

## The player's character

A `character` entity like any other, with `role: player`. Its frontmatter carries the live
mechanical state:

```yaml
---
id: <player-character-id>
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

### Wounds

`wounds` holds the lasting marks a character is carrying. Entries are written by the Aftermath
table ([`03a-2-aftermath.md`](03a-2-aftermath.md)):

```yaml
wounds:
  - id: the-knee-that-never-set   # kebab-case, unique on this character, stable forever
    from: {table: aftermath, beat: 412}
    effect: {skill: -10}          # stamina_max | skill | dread
    bears_on: <setting-skill-id>  # which skill the penalty burdens; omitted when none
    recurring: false              # true — fires at the start of every fight
    description: "the knee never set right"
```

`effect` names a mechanic the engine knows; anything else is a load error. `id` is what a later
rule names when it needs to act on exactly one wound. A wound carries **no healing field and no
duration** — whether wounds mend is not settled, and a field shaped for one answer would prejudge
it.

`bears_on` is the skill the wound burdens, taken from the roll that caused it and named in the
setting's own vocabulary — the engine has none of its own
([`03b-the-character.md`](03b-the-character.md), [ADR 0013](adr/0013-the-engine-names-no-skill.md)).

**It is optional, and its absence is meaningful rather than missing.** A fall, a fire, a poisoning
or a wound taken while unconscious has no skill behind it. Such a wound simply carries no
`skill: -N` effect; it may still cost `stamina_max` or `dread`. An `effect` of `skill: -N` **with
no `bears_on`** is a load error: the penalty would have nothing to apply to.

Wounds render diegetically, like every other track ([`10-diegesis.md`](10-diegesis.md)): the knee
never set right, never `skill: -10`.

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
