---

description: "Implementation plan for the affliction table and Trauma-test cascade"
---

# Implementation Plan: Affliction table and Trauma-test cascade

**Branch**: `099-affliction-table` | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/099-affliction-table/spec.md`

## Summary

Add a `trauma`-crossing cascade to `engine/wyrd/resolution.py`, mirroring the existing
`taint`-crossing cascade (`_cascade_from_mutation` / `_stage_transformation_chain`), plus the
affliction table itself. Where Taint crossing a multiple-of-3 threshold stages a Transformation
directly, Trauma crossing past 6 stages an ordinary pass/fail **test** first (`trauma-test`), and
only a *failed* test stages a further `1d12` roll against the new repeatable `AFFLICTION_TABLE`
(`_stage_affliction_roll`), whose row effect is applied via the existing mutation vocabulary,
along with a flat `-6 trauma` mutation (docs/design/03-rules.md section 5: "take an Affliction
and lose 6 Trauma"). The test's skill is threaded through as an already-decided input on the
request that produced the Trauma-gaining mutation, the same way Exposure's `tier` is
caller-supplied. A new `terror` top-level mechanic (docs/design/03-rules.md section 5's own
"failed Terror test") is added as the cascade's public entry point, mirroring `exposure`'s role
for Taint -- the only Trauma-gain source this feature wires up.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Storage**: N/A -- pure functions over in-memory proposal state, following the existing
propose/commit/discard shape (docs/design/31-action-resolution.md).

**Testing**: stdlib `unittest` (docs/design/27-tooling.md section 6), `tests/engine/test_resolution.py` (existing file, extended).

**Target Platform**: the engine library (`engine/wyrd/`).

**Project Type**: single project (this repo's engine).

**Performance Goals**: N/A -- at most a handful of staged steps per cascade, same order of
magnitude as the existing transformation cascade.

**Constraints**: stdlib-only; no severity/consumption step for the affliction table (unlike
Transformation, docs/design/08-afflictions.md "No severity field"); a duplicate affliction row
is applied, never re-rolled (repeatable family, contrast with Transformation's unique-per-
character re-roll); the floor (Trauma == 6 exactly) stages no test.

**Scale/Scope**: one new public mechanic (`terror`), one new cascade trigger, one new internal
step mechanic (`trauma-test`), one new table constant (`AFFLICTION_TABLE`), and the roll-and-
apply step it stages (`_stage_affliction_roll`) in the existing `resolution.py` module, plus
tests.

## Constitution Check

- No new setting/system vocabulary -- `trauma-test` and `affliction` are the design document's
  own descriptive names (docs/design/08-afflictions.md "The roll": key `affliction`).
- Reuses the existing cascading-resolution mechanism (docs/design/31-action-resolution.md,
  specs/083-cascading-resolution) rather than inventing a second cascade shape; the affliction
  table's rows reuse the existing points-modifier/difficulty-ladder mutation vocabulary rather
  than a new mutation kind.
- The Trauma test's skill remains an already-decided caller input (docs/design/08-afflictions.md
  "the engine names no skill", ADR 0013) -- this feature does not choose it, matching how
  `exposure`'s `tier` and the transformation cascade's Fault Line bias are already handled as
  caller-decided inputs.
- No new ADR needed: docs/design/07-transformations.md's "Body, never mind" section and
  docs/design/08-afflictions.md already settled the Taint/Trauma split and this table's shape;
  this feature implements what those documents already decided, and rejects no alternative they
  didn't already weigh.

## Project Structure

### Documentation (this feature)

```
specs/099-affliction-table/
|-- spec.md
|-- plan.md
`-- tasks.md
```

### Source Code (repository root)

```
engine/wyrd/resolution.py       # + AFFLICTION_TABLE, TRAUMA_FLOOR, _stage_affliction_roll,
                                 #   a trauma-test entry in _MECHANICS (resolve/mutate), and a
                                 #   trauma-crossing branch in _cascade_from_mutation
tests/engine/test_resolution.py # + tests for the above
```

**Structure Decision**: extends the existing `resolution.py` module rather than a new one --
Trauma/Affliction is the direct sibling of the Taint/Transformation cascade already implemented
there (`_cascade_from_mutation`, `_stage_transformation_chain`, `TRANSFORMATION_SEVERITIES`), and
splitting one cascade mechanism's second instance into a separate file would fragment one concept
across modules for no reason, the same judgment #098's plan already made for `adversary.py`.

## Complexity Tracking

No constitution violation to justify -- table omitted.
