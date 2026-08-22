# Data Model: Table conventions and the tables index

**Feature**: `001-table-conventions` | **Date**: 2026-08-22

Phase 1 output. This describes the shape the conventions define. It is not a schema for
`tables.py` — that is R4 of epic #1 and out of scope (FR-014). What follows is the contract a
sibling's table file must satisfy and that a future implementation will validate.

---

## Family

A named category of outcome the rules roll for. Five exist.

| Field | Required | Notes |
|---|---|---|
| `family` | yes | lowercase, single word — `critical`, `aftermath`, `transformation`, `affliction`, `oracle` |
| `roll` | yes | the die expression, e.g. `1d6` |
| `modifier` | yes | where the modifier comes from, in words the engine can resolve; `none` where the family has none |
| `uniqueness` | yes | `unique-per-character` or `repeatable` (R5) |
| `exhausted` | only when `uniqueness: unique-per-character` | what happens when the character holds every result (FR-004a) |
| `extra_fields` | no | family-specific row fields beyond the shared three, each named and described |

A family may hold one table or several. Where it holds several, each is a variant addressed by its
own key.

## Table

One rollable list. Addressed by a key, held in its own file (R6).

| Field | Required | Notes |
|---|---|---|
| `key` | yes | `<family>` or `<family>-<variant>`, lowercase and hyphenated |
| `family` | yes | the family this table belongs to; supplies the roll, modifier and uniqueness |
| `rows` | yes | ordered, contiguous, non-overlapping |

**Invariants**, all checkable rather than asserted (ADR 0005):

1. `key` is one the engine publishes.
2. Row ranges are contiguous and non-overlapping.
3. Ranges span from the family's rollable minimum upward; the highest row is open at the top by
   virtue of clamping (R2).
4. Every row carries the shared fields plus every field the family declares in `extra_fields`.
5. Every `effect` names a mechanic the engine knows.

## Row

| Field | Required | Reaches state | Notes |
|---|---|---|---|
| `range` | yes | no | the rolled values this row answers to |
| `effect` | yes | **yes** | the mechanical consequence, applicable without reading the prose |
| `description` | yes | no | the words said at the table; a setting replaces these freely |

Plus whatever the family declares. `severity` is the known example, carried by transformations and
afflictions and by nothing else (R4).

The `effect`/`description` split is the load-bearing one: `effect` is what reaches state and is
never renamed; `description` is presentation and a setting may say it however it likes. This is what
makes renames presentation-only in practice rather than only in principle (FR-010, R8).

## Recorded outcome

What a roll on a table leaves in the log. Extends the provenance shape already in
`design/09-evolution.md:105` — one new field, no new version (R7).

| Field | Source |
|---|---|
| `engine` | already recorded on every outcome |
| `table` | **new** — the table key that was rolled on |
| `roll`, `modifier`, `result` | the roll as it fell and the row it read |

Resolving an outcome to the exact table that produced it is `engine` version plus `table` key, or
setting version plus `table` key where the table was overridden. Both versions are already in
`chronicle.yaml`.

## Override

A setting's declaration replacing a table's rows.

| Field | Notes |
|---|---|
| key | the published table key being replaced |
| path | the setting-relative file holding the replacement rows |

May replace: rows — ranges, effects, descriptions.

May not replace: the family's `roll`, `modifier`, `uniqueness`, `exhausted`, the row schema, or the
set of published keys. Each of these is a mechanism, and a setting that needs a new mechanism files
an engine gap (`design/13-authoring-a-setting.md`).

## Relationships

```text
Family (5)
  └── Table (1..n)   addressed by key, one file each
        └── Row (1..n)   contiguous ranges
              └── effect ──> reaches state
                  description ──> presentation only, setting-replaceable

Override ──replaces──> Table.rows   (never Family)
Recorded outcome ──references──> Table.key + engine/setting version
```

## State transitions

None. Tables are pure data read at load and rolled on; they hold no state of their own. The only
lifecycle is versioning, and that is forward-only: a changed table applies to future rolls and never
recomputes a recorded outcome (`design/09-evolution.md`, R7).
