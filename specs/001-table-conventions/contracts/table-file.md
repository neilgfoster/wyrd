# Contract: a table file

**Feature**: `001-table-conventions` | **Date**: 2026-08-22

The interface this feature exposes is a file format — what a sibling author writes and what a
setting author replaces. This is the contract `design/03a-tables.md` publishes. It is not an
implementation of a parser; `tables.py` is R4 of epic #1 (FR-014).

The example below uses a family that already exists in `design/03-rules.md` and deliberately
invents no content: the rows are placeholders showing shape, not a table anyone should ship.

## Shape

```yaml
key: critical-slashing
family: critical

roll: 1d6
modifier: points below zero
uniqueness: repeatable

rows:
  - range: [1, 2]
    effect: <a mechanic the engine knows>
    description: <what is said at the table>
  - range: [3, 4]
    effect: <a mechanic the engine knows>
    description: <what is said at the table>
  - range: [5, null]          # null means open at the top: every higher total reads this row
    effect: <a mechanic the engine knows>
    description: <what is said at the table>
```

A family carrying an extra field declares it, and every row in every table of that family supplies
it:

```yaml
family: transformation
uniqueness: unique-per-character
exhausted: <what happens when the character holds every result>
extra_fields:
  severity: <how much Taint this result consumes>
```

## Rules a table file must satisfy

| # | Rule | Failure |
|---|---|---|
| 1 | `key` is a table key the engine publishes | load error |
| 2 | Ranges are contiguous and non-overlapping | load error |
| 3 | Ranges span the family's rollable minimum upward; the last is open at the top | load error |
| 4 | Every row carries `range`, `effect`, `description` | load error |
| 5 | Every row carries every field the family declares in `extra_fields` | load error |
| 6 | Every `effect` names a mechanic the engine knows | load error |
| 7 | No setting name, system name, or borrowed term appears anywhere in the file | review, not load |

Rules 1–6 are mechanical and are therefore checked, not asserted (ADR 0005). Rule 7 is the one a
script cannot settle, so it stays a review obligation.

## Reading a result

1. Roll the family's `roll`.
2. Add the family's `modifier`.
3. Find the row whose `range` contains the total. There is always exactly one: the ranges are
   contiguous, they start at the family's lowest possible total, and the last is open at the top.
4. If the family is `unique-per-character` and the character already holds this result, roll again.
   If no result remains that they lack, apply the family's `exhausted` outcome.
5. Apply `effect`. Say `description`.
6. Record the outcome with the table's `key` alongside the engine version already stamped on it.

## The override contract

A setting replaces a named table's rows:

```yaml
overrides:
  tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}
```

The replacement file carries `rows:` and nothing else — `roll`, `modifier`, `uniqueness`,
`exhausted` and `extra_fields` belong to the family and come from the engine. A replacement that
sets any of them is a load error, because changing one is changing a mechanism, and a setting that
needs a new mechanism files an engine gap instead (`design/13-authoring-a-setting.md`).

Rules 1–6 apply to a replacement exactly as to an engine table. A setting cannot ship a table with a
gap in it.

Renames reach `description` and nothing else. `key` and `effect` are what reach state, and a rename
never touches them (ADR 0004).
