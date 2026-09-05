# Phase 1 Data Model: Spend advances — raise, open, change career

## Constants

| Name | Value | Module | Source |
|---|---|---|---|
| `SPENDS` | `("raise", "open", "change_career")` | `advancement` | docs/design/03-rules.md §6 spending table |
| `ADVANCE_COST` | `1` | `advancement` | same table — every row costs 1 |
| `SKILL_OPEN_VALUE` | `25` | `rules` (existing) | reused, not redefined |
| `SKILL_ADVANCE_STEP` | `5` | `rules` (existing) | reused, not redefined |

`SPENDS` is closed the same way `advancement.TRIGGERS` is: a setting renames a spend, it never
adds a fourth.

## The career table

A setting's `careers.yaml` list, passed in by the caller (docs/design/24-authoring-a-setting.md):

```yaml
- id: guard
  entry: true
  skills: {blade: 70, watch: 70}
- id: guard-captain
  entry: false
  prerequisites: [guard, soldier]   # OR — completing any one qualifies
  skills: {blade: 70, watch: 70, command: 70}
```

`skills` is a mapping of skill to that career's cap, the shape `effective_cap` already reads.
(The design document writes the grant as a list because it states one cap per career; the engine's
career dict has always carried the cap per skill, and this feature does not change that.)

## The character view a spend takes and returns

```yaml
career: <career-id>
career_history: [{career: <id>, completed: true}]
skills: {blade: 35}
advances_unspent: 2
```

Four fields — a subset of the player character (docs/design/22-state.md), not a new entity. The
feature never reads or writes a file; the caller persists what it returns.

`career_history` entry shape is fixed here: `career` (the id left) and `completed` (whether every
skill that career granted stood at its cap at departure). Entries are appended, never rewritten —
a career entered twice appears twice.

## `career.is_entry(career)`

`True` when `career["entry"]` is true. An entry career declares no `prerequisites`.

## `career.career_complete(skills, career)`

`True` when every skill in `career["skills"]` is present in `skills` at or above that career's cap
for it. Ancestry is not consulted: completion is a property of the career's own grant list.

## `career.find_career(career_id, careers)`

The career dict with that id, or `None`. Used to refuse an unknown target by name (FR-007).

## `career.change_career_legality(target, careers, career_history)`

Returns `{"legal": True}`, or `{"legal": False, "refusal": <key>, "error": "<prose>"}`.

| `refusal` | When |
|---|---|
| `unknown_career` | no career in `careers` has that id |
| `prerequisites_unmet` | the target is non-entry and no id in its `prerequisites` appears in `career_history` with `completed: true` |

An entry career is always legal — no history can make it unreachable
(docs/design/03-rules.md §6, "abandoning a career path entirely and starting over from a fresh
entry point is always legal").

## `advancement.spend_advance(spend, view, career, careers=None, ancestry=None, skill=None, target=None)`

Returns a new view on success; never mutates its arguments.

**Success**: `{"spent": True, "spend": <key>, "view": {...}}` with `advances_unspent` reduced by
`ADVANCE_COST` and exactly one of `skills` / (`career` + `career_history`) changed.

**Refusal**: `{"spent": False, "refusal": <key>, "error": "<prose>", "view": <unchanged>}`

| `refusal` | When |
|---|---|
| `unknown_spend` | `spend` is not one of the three |
| `no_advance` | `advances_unspent` is below `ADVANCE_COST` |
| `not_granted` | raise/open: the current career (widened by ancestry) does not grant the skill |
| `not_open` | raise: the skill is not held |
| `at_cap` | raise: `held + 5` would exceed the grant's cap |
| `already_open` | open: the skill is already held |
| `unknown_career` | change: no such career in the table |
| `prerequisites_unmet` | change: the target is non-entry and no prerequisite is complete |

Checked in that order. `unknown_spend` first because it is a caller bug rather than a play-time
answer; `no_advance` next because an unaffordable spend is unaffordable whichever action was named
(research.md), and the remainder in the order the action's own rules read.

## Verb and CLI surface

| Verb | CLI | Arguments |
|---|---|---|
| `spend_advance` | `wyrd spend-advance` | `--spend`, `--view-json`, `--career-json`, `--careers-json`, `--ancestry-json`, `--skill`, `--target` |

The record is passed in as flags, not read from a state file, matching every other verb in
`client.py`: the engine computes, the caller persists.
