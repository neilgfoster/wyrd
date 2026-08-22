# Tables

The ruleset in [`03-rules.md`](03-rules.md) names five kinds of table and defines none of them. This
document is where they are defined: the conventions every table satisfies, and the index of the
families themselves.

The conventions exist so that five families written at different times behave the same way. The
engine fixes **the row schema and how a result is looked up**. It does not fix the die — each family
declares its own, because a critical reads further down its table the harder the blow was, and
nothing else works that way. Rationale and the rejected alternative are in
[ADR 0008](adr/0008-tables-declare-their-own-roll.md).

**A table here means a rollable one.** A setting's lookup tables — voice, careers, gear, names —
are content addressed by key rather than by a die, and none of this applies to them
([`02-architecture.md`](02-architecture.md)).

---

## The index

Each family lives in its own file. Its roll and its uniqueness are properties of the family, stated
there and summarised here.

| Family | Roll | Uniqueness | Defined in |
|---|---|---|---|
| **Criticals** | `1d6` + points below zero | repeatable | `03a-1-criticals.md` — not yet written |
| **Aftermath** | declared by the family | repeatable | `03a-2-aftermath.md` — not yet written |
| **Transformations** | declared by the family | unique per character | `03a-3-transformations.md` — not yet written |
| **Afflictions** | declared by the family | unique per character | `03a-4-afflictions.md` — not yet written |
| **Oracles** | declared by the family | repeatable | `03a-5-oracles.md` — not yet written |

A family holds one table or several. Criticals hold one per damage type; a family with a single
table needs no variant.

The roll column says *declared by the family* wherever the ruleset has not already fixed it. Each
family settles its own when it is written, and replaces its row's last cell with a link.

---

## How a table is rolled and read

**The roll and the modifier belong to the family**, not to a row and not to the engine. A family
states both in its own file: the die it rolls and where its modifier comes from. Criticals roll
`1d6` and add the points below zero, so a harder blow reads further down the table. A family with no
modifier says so.

**Reading a result:**

1. Roll the family's die and apply its modifier.
2. Find the row whose range contains the total.
3. Apply the row's effect. Say its description.
4. Record the outcome with the table's key.

**Both ends clamp.** A total above the highest row reads the highest row; a total below the lowest
reads the lowest. Because a table's ranges are contiguous, there is no third case — nothing can fall
between two rows. Clamping is not a fallback but the intended behaviour: the modifier on a critical
is unbounded, so a hard enough blow will always run off the end of any finite table, and the top row
is already the worst thing the family has to say.

**Repeated results.** A family declares itself *repeatable* or *unique per character*. Taking the
same wound twice is ordinary, so criticals repeat. Carrying the same permanent change twice is not,
so transformations do not. When a unique family rolls a result the character already holds, roll
again.

**When a unique family runs out.** Rerolling cannot terminate once a character holds every result in
the table, so each unique family states what happens instead. For transformations the ruleset
already answers it — the character is lost, and joins the opposition
([`03-rules.md`](03-rules.md)). A family that declares itself unique must declare this too; there is
no general answer, because what exhaustion means depends on what the family tracks.

---

## The row schema

Every row in every family carries three things:

| | |
|---|---|
| **range** | the totals this row answers to |
| **effect** | the mechanical consequence, in a form that can be applied without reading the prose |
| **description** | what is said at the table |

**Effect and description are separate on purpose.** The effect is what reaches state; the
description never does. That split is what lets a setting rewrite every word of a table without
touching what it does, and it is why a rename stays presentation-only in practice rather than only
in principle.

A family may declare further fields, named in its own file, carried by every row of every table it
holds. **Severity** is the known case: a transformation consumes Taint equal to its severity
([`03-rules.md`](03-rules.md)), and afflictions work the same way. It is not a shared field. Three of
the five families have no rule that reads a severity, and a field nothing reads is how a table goes
quietly stale.

### Naming and layout

A table is addressed by a lowercase, hyphenated key: the family alone where it holds one table,
`<family>-<variant>` where it holds several. One table to a file, named for its key. Engine tables
live at `engine/tables/<key>.yaml`.

---

## What a setting may replace

A setting replaces a table's **rows** — their ranges, their effects, their descriptions — by naming
the table under `overrides.tables:` in `setting.yaml`
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)):

```yaml
overrides:
  tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}
```

A setting may **not** change the family's die, its modifier, its uniqueness, its exhaustion outcome,
or the row schema. Each of those is a mechanism rather than content, and a setting that needs a
mechanism the engine lacks files an engine gap so every setting gets it
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)). A replacement file therefore carries rows
and nothing else.

**A replacement must load.** These are checked, not trusted:

1. The key is one the engine publishes. An unknown key is a load error — the overridable set is
   closed.
2. Ranges are contiguous and do not overlap.
3. Ranges run from the family's lowest possible total upward, with the last row open at the top.
4. Every row carries range, effect and description.
5. Every row carries every extra field the family declares.
6. Every effect names a mechanic the engine knows. An effect naming something unknown is a load
   error, not a row quietly ignored.

One rule cannot be checked and stays a review obligation: **no table may carry a setting's name, a
system's name, or a term borrowed from a source system into the engine's own tables**. A setting's
tables are the setting's business; the engine's are neutral.

**Renames reach descriptions only.** A setting that renames a track renames what the descriptions
say about it. The key and the effect are what reach state, and a rename never touches either.

---

## Versioning

**A table is pinned by the versions that already exist.** A table ships with the engine or with a
setting, and `chronicle.yaml` records the version of both ([`06-state.md`](06-state.md)). Every
recorded outcome already states the engine that produced it
([`09-evolution.md`](09-evolution.md)). A table roll additionally records the key it rolled on:

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "table": "critical-slashing", ...}
```

Version plus key resolves an outcome to exactly one table, so a reader years later can always tell
which rows produced it.

**There is no per-table version.** Four things carry versions ([`06-state.md`](06-state.md)) and a
fifth would have to be bumped by hand on every row change. A version nobody bumps reliably is worse
than none, because it reads as authoritative and is not.

**Table changes apply forward.** Changing ranges, effects or numbers within an existing family is
*tuning*; adding a table or a row without disturbing existing ranges is *additive*
([`09-evolution.md`](09-evolution.md)). Neither is retroactive. A result already rolled stands as it
was rolled, and no history is recomputed.
