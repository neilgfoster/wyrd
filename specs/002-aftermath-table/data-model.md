# Data model: The Aftermath table

**Feature**: 002-aftermath-table | **Date**: 2026-08-22

What this feature adds to chronicle state, and what it only reads. Nothing here is code — the engine
does not exist yet — but each structure is what `design/06-state.md` will carry.

---

## 1. The Aftermath table itself

A member of the table families defined in `design/03a-tables.md`. It declares:

| Property | Value |
|---|---|
| key | `aftermath` |
| roll | `d100 + (5 × points below zero)` |
| lowest possible total | `6` |
| uniqueness | repeatable |
| extra row fields | none |
| exhaustion outcome | not applicable — the family is repeatable |

Rows carry the three fields the shared row schema requires and nothing more.

---

## 2. The wound record

This feature gives structure to the `wounds: []` list that `design/06-state.md` already declares on
the player character but never defines. A wound record is an entry in it.

```yaml
wounds:
  - id: the-knee-that-never-set     # kebab-case, unique on this character, stable forever
    from:
      table: aftermath              # the table key that produced it
      beat: 412                     # the beat it was rolled at
    effect:
      skill: -10                    # the mechanic it applies, from the published set below
    recurring: false                # whether it fires again at the start of every fight
    description: "the knee never set right"
```

**Fields:**

| Field | Meaning |
|---|---|
| `id` | identifies this wound for the life of the chronicle. A later rule that heals, worsens or reads a wound needs a handle on exactly one. |
| `from.table` / `from.beat` | provenance. `design/03a-tables.md` already requires a table roll to record the key it rolled on; a wound outlives the log entry, so it carries its own. |
| `effect` | the mechanical consequence, applicable without reading the prose. Names a mechanic the engine already knows. |
| `recurring` | `false` for a wound that simply applies; `true` for one that fires at the start of every fight. |
| `description` | what is said at the table. Never reaches state as a mechanic; a setting rewrites this freely. |

**`effect` is drawn from a closed set** — every mechanic named must be one the engine knows, or the
record is a load error rather than a row quietly ignored (`design/03a-tables.md`):

| `effect` | Applies |
|---|---|
| `stamina_max: -N` | permanent reduction to maximum Stamina |
| `skill: -N` | a penalty to the skill the wound bears on, applied to the *skill* and never to the roll (`design/03-rules.md` §1) |
| `dread: +N` | the existing Dread track — the wound is one other people can see |

**What the record deliberately does not carry**: no `healed` flag, no duration, no severity. Whether
a wound ever heals is R1.2's decision, and a field shaped for one answer would prejudge it. Adding a
field when a rule reads one is additive under `design/09-evolution.md`.

**Rendering**: diegetic, per `design/10-diegesis.md` — "the knee never set right", never `skill: -10`.

---

## 3. The recurring wound

A wound record with `recurring: true`. It is not a separate structure.

- **Fires**: when a fight begins, before the first roll.
- **Effect**: `skill: -10` against the character's combat skill, for that fight only.
- **Between fights**: nothing. The wound imposes no penalty when no fight is occurring.
- **Duration**: for the rest of the chronicle, unless a later rule (R1.2) says otherwise.
- **Stacking**: the family is repeatable, so a character may carry more than one. Each fires.

---

## 4. Entities this feature creates

Neither is new machinery; both are shapes `design/14-entities.md` already fixes.

**A new enemy** — a `character` entity, created when the `new-enemy` row comes up:

```yaml
type: character
role: nemesis
disposition: hostile
objective:
  wants: "…"          # required — an enemy without an objective is a note, not a character
  because: "…"
  next_step: "…"
```

The `objective` block is what makes the enemy act while the player is elsewhere, which is the whole
reason this row creates an entity rather than recording a name.

**An open loop** — a `thread` entity, created when the `taken` row comes up. Capture is a situation
the chronicle carries until it resolves; a thread is the type `design/14-entities.md` already has for
exactly that.

---

## 5. State this feature reads or updates but does not define

| Field | Where it lives | What changes |
|---|---|---|
| `dread` | player character frontmatter | `+1` on a disfigurement result |
| `stamina.max` | player character frontmatter | reduced by a wound whose effect is `stamina_max` |
| `fate.current` | player character frontmatter | decremented when spent against a death result |
| `status` | companion frontmatter | `dead` on an unsaved death result; `away` while captured |
| `trauma` | player character frontmatter | **unchanged by this feature.** `design/03-rules.md` §5 already awards 1 Trauma per critical taken; awarding more here would double-count the same blow. |

---

## 6. What is recorded

Per `design/03a-tables.md`, a table roll records the key it rolled on alongside the engine version:

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "table": "aftermath",
 "roll": 74, "modifier": 25, "total": 99, "row": "recurring-wound", "fate_spent": false}
```

`fate_spent` is recorded because a spent Fate point changes which row was applied without changing
what was rolled, and `design/03-rules.md` §3 already says that choosing *not* to spend is itself a
decision the chronicle should remember.
