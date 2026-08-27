# Phase 1 Data Model: Career graph — skill counts and succession

Careers are rows in a setting's `careers.yaml` lookup table
([`24-authoring-a-setting.md`](../../docs/design/24-authoring-a-setting.md)), not Wyrd entities
([`25-entities.md`](../../docs/design/25-entities.md); see `research.md` for why). This document
describes the shape of that row, not a schema validator (out of scope, FR-009).

## Career

| Field | Type | Required | Notes |
|---|---|---|---|
| id | string | yes | unique key within the setting's career table |
| skills | list of skill references | yes | the skills this career grants; length is setting-defined per career, not fixed across careers (research.md) |
| entry | boolean | yes | `true` marks the career as an entry point — choosable at character creation with no prerequisite |
| prerequisites | list of career identifiers | required (length ≥ 1) when `entry` is `false`; absent when `entry` is `true` | the careers a character may have **completed** (see below) to become eligible for this career — completing **any one** satisfies it (OR semantics, research.md) |

### Validity rules

- **At least one career in the setting must have `entry: true`** — already established by
  `05-character-creation.md`'s "Entry careers: at least one career marked as an entry point."
- **A career with `entry: false` must declare at least one `prerequisites` entry.** A
  single-entry list is the plain-ladder case; a multi-entry list is what lets several different
  ladders converge on the same next rung (the zigzag case, research.md) — both use the same
  field, just a different length.
- **The graph formed by `prerequisites` edges must be acyclic.** A career is unreachable, and
  therefore a setting-authoring error, only if **every** one of its `prerequisites` entries
  eventually requires the career itself — a career appearing as a prerequisite of more than one
  other career is convergence, not a cycle (research.md).
- **Every entry in `prerequisites` must name a career that exists in the same table.** A
  dangling reference is a setting-authoring error, same class as the cycle rule.

## Career completion (derived state, not a stored field)

A character's relationship to a career is not stored on the `Career` row — it is computed from
the character's own advance history inside that career, per
[`11-character-creation.md`](../../docs/design/11-character-creation.md) §3 and §5.

**A career is complete for a given character when every skill in that career's `skills` list has
been opened and raised to the career's cap.**

This derived fact feeds two existing effects, both already named in the corpus and neither
redefined here:

- the **+1 maximum Stamina** "durable toughening" bonus
  ([`11-character-creation.md`](../../docs/design/11-character-creation.md), "Why Stamina is 6")
- **eligibility for a non-entry career**: a character may choose career *B* (where *B.entry is
  false*) once **any one** career in *B.prerequisites* is complete for that character (OR
  semantics). A **specialist** keeps completing careers along one chain of successive
  prerequisites; a **generalist** completes a spread of careers across different ladders — both
  are simply different choices of *which* completed careers a character accumulates, not a
  distinction the graph itself encodes.

### State transition

```text
career not started
   │  (character opens ≥1 of the career's skills — first advance spent inside it)
   ▼
career in progress
   │  (every skill in the career's list reaches the career's cap)
   ▼
career complete  →  grants +1 max Stamina (once)
                  →  satisfies this career as one qualifying entry in `prerequisites`
                     for any career listing it
```

Nothing in this feature changes what "the career's cap" is, or how advances are spent — both
stay exactly as `05-character-creation.md` §3 already defines them.
