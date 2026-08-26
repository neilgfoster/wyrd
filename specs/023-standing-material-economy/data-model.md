# Data model: Standing and the material economy

Design-only feature — no runtime data store. This document specifies the entities the design
documents define and the schema the validator checks, not a persisted model.

## Standing (design entity, not a file schema)

| Field | Meaning |
|---|---|
| Standing | a small, open-ended count on the character. Starts at a value set during character
  creation (setting- or table-dependent, like other tracks); rises and falls through play,
  primarily through Upkeep and social consequence. Rendered diegetically, never as a raw number,
  per `design/10-diegesis.md`. |

No file schema — Standing lives on the character sheet the way Stamina and the other tracks do,
already covered by `design/03b-the-character.md`'s existing character-state conventions.

## Coin (design entity, not a file schema)

| Field | Meaning |
|---|---|
| Coin | a small numeric count the character can state a total for. Spent at Upkeep (as an
  alternative to losing Standing) and against prices in a setting's `gear.yaml`. No itemized
  transaction history. |

## Gear entry (`gear.yaml`, validated by `tools/check_gear.py`)

Two entry kinds, `weapon` and `armour`, sharing a `kind` discriminator field.

### Weapon

| Field | Required | Type / closed set | Notes |
|---|---|---|---|
| `id` | yes | string | unique within the file |
| `name` | yes | string | |
| `kind` | yes | `weapon` | discriminator |
| `damage` | yes | dice expression (e.g. `1d6`) | rolled on a successful attack, `03-rules.md` §2 |
| `damage_type` | yes | one of `slashing`, `piercing`, `blunt`, `searing` | closed four, ADR 0022 |
| `class` | yes | one of `casual`, `martial` | martial carries the Standing consequence |
| `price` | yes | non-negative number | in the setting's stated currency |
| `availability` | yes | string, setting-defined vocabulary (e.g. `common`, `restricted`,
  `illegal`) | legality/availability; the closed set is declared per setting, not by the engine |
| `notes` | no | string | flavour only, no mechanical effect |

### Armour

| Field | Required | Type / closed set | Notes |
|---|---|---|---|
| `id` | yes | string | unique within the file |
| `name` | yes | string | |
| `kind` | yes | `armour` | discriminator |
| `rank` | yes | one of `none`, `light`, `modest`, `heavy` | `03-rules.md` §2's existing four |
| `price` | yes | non-negative number | |
| `availability` | yes | string, setting-defined vocabulary | as above |
| `notes` | no | string | |

## Validation rules (`tools/check_gear.py`)

1. Every entry declares all required fields for its `kind`.
2. No entry declares a field outside the union of both kinds' fields (an unrecognised field is
   rejected, not ignored — mirrors `check_bestiary.py`).
3. `damage_type` (weapons) is one of the closed four.
4. `rank` (armour) is one of the closed four.
5. `class` (weapons) is exactly `casual` or `martial`.
6. `price` is a non-negative number on every entry.
7. Every failure is reported, naming the entry and field — not just the first.
