# Contract: the Aftermath family

**Feature**: 002-aftermath-table | **Date**: 2026-08-22

What `docs/design/06-aftermath.md` must declare, in the form `docs/design/04-tables.md` requires of every
family. This is the checkable surface: a table file that fails any clause here does not load.

---

## Family declaration

| Clause | Value | Source |
|---|---|---|
| **key** | `aftermath` | lowercase, hyphenated; the family holds one table, so the key is the family name |
| **die** | `d100` | declared by the family (`03a-tables.md`) |
| **modifier** | `+ (5 × points below zero)` | the number `03-rules.md` §2 already computes for the critical |
| **lowest possible total** | `6` | `1` (lowest die face) `+ 5 × 1` (a critical means at least 1 point below zero) |
| **highest total** | unbounded | the modifier is unbounded, so the last row is open at the top |
| **uniqueness** | repeatable | taking the same mark twice is ordinary |
| **exhaustion outcome** | not applicable | only a unique family needs one |
| **extra row fields** | none | no rule reads a severity for this family |

---

## When it is rolled

| Clause | Rule |
|---|---|
| **Trigger** | a combatant went below 0 Stamina during a fight and is *out of action* |
| **Timing** | **after** the fight ends. Never during it — that is the whole content of "death is deferred" |
| **Frequency** | once per combatant who dropped, however many times they dropped in that fight |
| **Order** | if several combatants dropped, they are resolved in any order; no result depends on another |
| **Who rolls** | every combatant who dropped — player character and companion alike, same table, same modifier, same rows |

---

## Rows

Contiguous from 6, non-overlapping, last row open at the top. Every row carries range, effect and
description; the descriptions below are the engine's defaults and a setting may replace every word.

| Range | Key | Effect (what reaches state) |
|---|---|---|
| 6–30 | `out-of-action` | nothing lasting |
| 31–52 | `lasting-wound` | one wound record |
| 53–66 | `left-for-dead` | one wound record; character wakes elsewhere, without what they carried |
| 67–78 | `new-enemy` | one wound record; one `character` entity, `role: nemesis`, with an `objective` |
| 79–88 | `taken` | captured; one `thread` entity; a companion's `status` becomes `away` |
| 89–98 | `disfigured` | one wound record with effect `dread: +1` |
| 99–110 | `recurring-wound` | one wound record with `recurring: true`, effect `skill: -10` |
| 111+ | `death` | death |

**Every effect names a mechanic the engine already knows** — the `wounds` list, the Dread track,
`character` and `thread` entities, companion `status` values, and the `−10` skill step from
`03-rules.md` §1. An effect naming anything else is a load error, not a row quietly ignored.

---

## Closing the death rows

Two things close the death rows. Both use **one** mechanism, and it is deterministic — no second
roll, no GM judgement.

```
if the row is `death` and the death rows are closed for this character:
    apply the worst non-death row instead   # `recurring-wound`
```

| Closed by | Condition |
|---|---|
| **A spent Fate point** | the character has Fate and the player spends it. For a companion: the player character is **present and able to act** and spends their own (`03-rules.md` §3). |
| **`mortality: low`** | the setting's tone contract. The death rows are closed for everyone, always. |

**Fate may only be spent against a `death` result.** It does not improve any other row, and it is
never spent at a distance. Declining to spend is a decision the chronicle records.

---

## Invariants

Checked by [`../check_aftermath.py`](../check_aftermath.py):

1. Ranges are contiguous, non-overlapping, and start at `6`.
2. The last row is open at the top.
3. Every total the roll can produce lands on exactly one row.
4. A lasting mark is the common outcome and death the uncommon one, across drops of 1–12 — the claim
   `03-rules.md` already makes.
5. A combatant dropped by 1 or 2 cannot reach the death row, at any `mortality`.
6. At `mortality: low` no death result survives application.

Not checkable, and a review obligation instead: **no row carries a setting's name, a system's name,
a term borrowed from a source system, or a tonal register.**

---

## What a setting may replace

The rows — ranges, effects, descriptions — via `overrides.tables:` in `setting.yaml`:

```yaml
overrides:
  tables: {aftermath: setting/rules/tables/aftermath.yaml}
```

A setting may **not** change the die, the modifier, the uniqueness, or the row schema. It may not
change how the death rows close, because that is the mechanism Fate depends on. `mortality` is the
knob a setting has for lethality, and it is already part of the tone contract.
