# Phase 1 Data Model: Career graph — skill counts and succession

Careers are rows in a setting's `careers.yaml` lookup table
([`26-authoring-a-setting.md`](../../docs/design/26-authoring-a-setting.md)), not Wyrd entities
([`27-entities.md`](../../docs/design/27-entities.md); see `research.md` for why). This document
describes the shape of that row, not a schema validator (out of scope, FR-009).

## Career

| Field | Type | Required | Notes |
|---|---|---|---|
| identifier | string | yes | unique key within the setting's career table |
| skills | list of skill references | yes | the skills this career grants; length is setting-defined per career, not fixed across careers (research.md) |
| entry | boolean | yes | `true` marks the career as an entry point — choosable at character creation with no prerequisite |
| prerequisite | career identifier | required when `entry` is `false`; absent when `entry` is `true` | the single career a character must have **completed** (see below) to become eligible for this career |

### Validity rules

- **At least one career in the setting must have `entry: true`** — already established by
  `05-character-creation.md`'s "Entry careers: at least one career marked as an entry point."
- **A career with `entry: false` must declare exactly one `prerequisite`** — a single
  predecessor career, per the cardinality decision in `research.md`. Lists or multiple
  prerequisites are not part of this shape.
- **The graph formed by `prerequisite` edges must be acyclic.** A career reachable, directly or
  transitively, as its own prerequisite is a setting-authoring error (research.md).
- **A `prerequisite` must name a career that exists in the same table.** A dangling reference is
  a setting-authoring error, same class as the cycle rule.

## Career completion (derived state, not a stored field)

A character's relationship to a career is not stored on the `Career` row — it is computed from
the character's own advance history inside that career, per
[`05-character-creation.md`](../../docs/design/05-character-creation.md) §3 and §5.

**A career is complete for a given character when every skill in that career's `skills` list has
been opened and raised to the career's cap.**

This derived fact feeds two existing effects, both already named in the corpus and neither
redefined here:

- the **+1 maximum Stamina** "durable toughening" bonus
  ([`05-character-creation.md`](../../docs/design/05-character-creation.md), "Why Stamina is 6")
- **eligibility for a non-entry career**: a character may choose career *B* (where *B.entry is
  false*) only if *B.prerequisite* is complete for that character.

### State transition

```text
career not started
   │  (character opens ≥1 of the career's skills — first advance spent inside it)
   ▼
career in progress
   │  (every skill in the career's list reaches the career's cap)
   ▼
career complete  →  grants +1 max Stamina (once)
                  →  satisfies this career as a `prerequisite` for any career naming it
```

Nothing in this feature changes what "the career's cap" is, or how advances are spent — both
stay exactly as `05-character-creation.md` §3 already defines them.
