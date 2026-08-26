# Implementation Plan: The affliction table

**Branch**: `020-affliction-table` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Define `doc/design/11-afflictions.md` as the affliction table family required by
`03a-tables.md`'s conventions: the test fired on every Trauma point past 6, a table of behaviour
rows large enough to survive a chronicle measured in years, the repeat-draw rule, the (already
settled) restatement that Taint thresholds never produce an Affliction, and the sawtooth cadence
computed at the accrual rates §5 already states. Update `03-rules.md` §5 and `03a-tables.md`'s
index in place, and record the repeatable-family and test-shape decisions as an ADR.

## The load-bearing decisions

**The Trauma test is an ordinary §1 skill test, skill chosen by the GM to fit the specific strain
— the same shape as Exposure's "resist with a test" (§4), not a new mechanic.** The engine names
no skill ([ADR 0013](../../doc/adr/0013-the-engine-names-no-skill.md)); inventing a universal
"Willpower" here would be exactly the kind of borrowed vocabulary `CLAUDE.md` rules out, and §4
already establishes the pattern of a fiction-chosen skill resisting a mental/moral pressure. Only
pass/fail matters — degrees are not read, matching how the transformation table's roll reads no
Wyrd die either.

**Afflictions are repeatable, not unique per character.** `03a-tables.md`'s default is unique
per family, but its own carve-out is explicit: a family is unique only where carrying the same
result twice is *not* ordinary, and §5 states the opposite for this track — "the track sawtooths,
so a character can break many times across years," which reads as the same fracture recurring, not
only new ones accumulating. Declaring the family unique would additionally force an exhaustion rule
for a track with no natural cap (unlike the transformation table's hidden threshold), for a
guarantee nothing in the source material requires. See the ADR for the rejected alternative.

**A twelve-row `1d12` table, no modifier.** Large enough that a chronicle computing several
Afflictions a year (see the cadence below) does not see the same row twice in a row often, small
enough that every row still earns real design attention rather than being padding. Twelve rows
covering distinct behaviour-shapes (compulsion, withdrawal, delusion, dependency, aggression,
dissociation, and so on) rather than one row per possible severity gradient, since — unlike
Transformations — this family carries no severity field: §5 already fixes the track's cost at a
flat 6 Trauma per Affliction, so a row has nothing left to charge for.

**The sawtooth cadence is computed, not asserted, across a spread of accrual and skill
assumptions**, because neither is fixed by the rules as written — `tools/check_affliction.py`
scans a range of Trauma-generating events per session (criticals taken, Terror tests failed) and a
range of representative test skills, and reports expected sessions between Afflictions at each
combination, flagged if any combination gives an implausible cadence.

## Structure

- `doc/design/11-afflictions.md` — new. The test, the table, repeat draws, the Taint/Trauma
  restatement, the cadence.
- `doc/design/03-rules.md` §5 — rewritten in place to name the test and point at the new document.
- `doc/design/07-tables.md` — index row updated from "not yet written" to the real file, roll, and
  link.
- `README.md` — hub row added for reachability, matching the transformation table's precedent.
- `doc/adr/00XX-*.md` — records the repeatable-family and fiction-chosen-test decisions and
  their rejected alternatives.
- `doc/README.md` — ADR index updated.
- `tools/check_affliction.py` — computes the sawtooth cadence across the assumption spread;
  asserts it stays within a plausible band or reports the finding explicitly if not.

## No engine code

Design-only, matching the shape of every table-family issue so far (#15, #17, #18): there is no
`engine/` implementation of tables yet for this repo to extend. The deliverable is the design
document, its computation script, and the ADR.

## Verification

- `python3 tools/check_affliction.py` — passes, prints the computed cadence table.
- `python3 tools/check_docs.py` — reachability, links, ADR index, link policy.
- `python3 tools/backlog.py check` — unaffected by this change; run to confirm no drift introduced.
- `grep` across `design/` for setting/system vocabulary — no unexpected match in changed files.

## Complexity tracking

None. No constitution violations; no new dependencies; no code beyond a single stdlib script.
