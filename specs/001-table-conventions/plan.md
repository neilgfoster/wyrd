# Implementation Plan: Table conventions and the tables index

**Branch**: `001-table-conventions` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-table-conventions/spec.md`

## Summary

Create `design/03a-tables.md`: the engine's table index and the shared conventions every table
family must satisfy. It settles five structural questions once — the roll, the out-of-range
behaviour, the row schema, the override contract, and versioning — so that issue #15's four sibling
children produce one coherent system rather than four independently-reasonable ones.

The approach, from [research.md](./research.md): the engine fixes the **row schema and the lookup
rule**; each **family declares its own roll**. That split is what lets criticals keep the
`1d6 + points below zero` the ruleset already commits to while an oracle rolls something else
entirely, without the index becoming five unrelated documents. Everything else is chosen to add
nothing new — the override contract is the one `design/13-authoring-a-setting.md` already draws, and
the version pin reuses the four versions `design/06-state.md` already defines rather than
introducing a fifth.

Alongside the new document, four existing design documents gain links to it and one stale list is
corrected (`design/07-tooling.md:84` omits afflictions). One ADR records the decision that a real
alternative — a single universal table format — was rejected.

## Technical Context

This is a documentation feature. Most of the template's fields are not applicable and are answered
as such rather than left as placeholders.

**Language/Version**: Markdown (GitHub-flavoured), matching the existing `design/` set.

**Primary Dependencies**: None. The document describes a contract that `tables.py` will later
implement; no code is written here.

**Storage**: Files in `design/`. The conventions describe YAML table files at
`engine/tables/<key>.yaml`, but no such file is created by this feature.

**Testing**: Manual and grep-based, per [quickstart.md](./quickstart.md). There is no test suite in
this repository yet — the engine does not exist. The mechanical checks in the quickstart are the
verification, and per `CLAUDE.md` they are run rather than asserted.

**Target Platform**: N/A — prose read by humans and by Claude Code at play time.

**Project Type**: Design documentation for a setting-agnostic game engine.

**Performance Goals**: N/A.

**Constraints**: The repository is intended public — nothing derived from a copyrighted source may
enter it. No setting or system name may appear in `design/`. Design documents are rewritten in
place, present tense, with no changelogs.

**Scale/Scope**: One new document (~150 lines), four existing documents amended by a link or a list
correction, one new ADR, one index row.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is an **unfilled Spec Kit template** — every principle is still a
`[PRINCIPLE_N_NAME]` placeholder. It carries no governance. The effective constitution for this
repository is `CLAUDE.md` plus the accepted ADRs, and the gate is evaluated against those.

| Gate | Source | Status |
|---|---|---|
| Nothing unpublishable enters this repo | `CLAUDE.md` | **Pass** — no source material is read or quoted; the conventions are derived from the repo's own documents |
| No setting or system names in `design/` | `CLAUDE.md` | **Pass** — verified by grep at implementation, quickstart §7; illustrative rows are deliberate placeholders |
| Engine labels are descriptive English | `CLAUDE.md` | **Pass** — `family`, `range`, `effect`, `description`, `severity` are all plain English; none is borrowed |
| Tone is a setting property | `CLAUDE.md`, ADR 0004 | **Pass** — the `effect`/`description` split exists precisely so register lives in the replaceable half |
| Deterministic over inference | `CLAUDE.md`, ADR 0005 | **Pass** — six of the seven table-file rules are mechanical and stated as load errors; the seventh is explicitly marked as review, not load |
| Design documents describe the present | `CLAUDE.md`, `design/README.md` | **Pass** — no changelog, no "previously we…"; the `07-tooling.md` list is corrected in place |
| ADRs are never edited | `CLAUDE.md` | **Pass** — one new ADR, no existing one touched |
| Capability changes go through Spec Kit, `specs/` committed | `CLAUDE.md` | **Pass** — this cycle; `specs/001-table-conventions/` is committed |
| Rules changes are forward-only | ADR-adjacent, `design/09-evolution.md` | **Pass** — R7 states a table change is tuning or additive, never retroactive |

**Re-check after Phase 1**: unchanged, all pass. The Phase 1 artifacts introduce no mechanism beyond
what Phase 0 settled; the one genuine addition — the `table` key on a recorded outcome — extends the
provenance shape `design/09-evolution.md:105` already defines rather than creating a new one.

**Note on the constitution file itself**: filling it in is real work but is not this feature's
scope, and inventing principles here would be exactly the "stale but plausible specification" fault
`CLAUDE.md` warns about. Flagged for the operator rather than silently done.

## Project Structure

### Documentation (this feature)

```text
specs/001-table-conventions/
├── plan.md                      # This file
├── spec.md                      # Feature specification
├── research.md                  # Phase 0 — the ten decisions, with rejected alternatives
├── data-model.md                # Phase 1 — family, table, row, override, recorded outcome
├── contracts/
│   └── table-file.md            # Phase 1 — the file format a sibling writes
├── quickstart.md                # Phase 1 — how to verify the document, mechanically
├── checklists/
│   └── requirements.md          # Spec quality checklist
└── tasks.md                     # Phase 2 output (kord-feature-tasks — not created here)
```

### Repository (what this feature changes)

```text
design/
├── 03a-tables.md                # NEW — the conventions and the index
├── 02-architecture.md           # amended — link tables/ to the conventions
├── 03-rules.md                  # amended — link each named table to its family
├── 07-tooling.md                # amended — link, and correct the family list (afflictions omitted)
├── 13-authoring-a-setting.md    # amended — link the overrides.tables: example to its contract
├── README.md                    # amended — one index row for the new ADR
└── adr/
    └── 0008-tables-declare-their-own-roll.md   # NEW
```

**Structure Decision**: The new document is `design/03a-tables.md`, sitting between `03-rules.md`
and `04-session.md` because it is an annexe to the ruleset rather than a peer of it — the ruleset
names the tables, the annexe defines them. Each sibling family will land as `design/03a-N-*.md`
under the same prefix, per issue #15's stated deviation from epic #6's "one new file" deliverable.
`03a-tables.md` indexes those files; it does not contain them, so epic #6's acceptance criteria hold
while the four siblings stay independently reviewable.

No source tree is touched. `engine/` does not exist yet and is not created — `tables.py` is R4 of
epic #1, gated behind this epic.

## Implementation notes

Three things are easy to get wrong here and are worth stating before tasks are generated:

1. **The index must be genuinely append-only.** SC-003 is the test: adding a sibling family is one
   row and touches no other line. If the document ends up with prose that enumerates the families a
   second time, that prose will go stale the first time a sibling lands — fault class 4, and tables
   are where it hides. Enumerate the families in exactly one place.

2. **Do not write table content.** The temptation while writing conventions is to illustrate them
   with a plausible critical row. A plausible row reads as authoritative and is not, and it
   pre-empts the sibling whose job it is. The contract's example rows use angle-bracket placeholders
   for this reason; the design document should do the same or omit rows entirely.

3. **`design/07-tooling.md:84` is a real stale list, not a typo.** It omits afflictions while
   `design/02-architecture.md:91` includes them and `design/03-rules.md:229` requires them. Correct
   it in place as part of this change — leaving two documents disagreeing about the family set while
   publishing an index of the family set would be the exact fault this feature exists to prevent.

## Complexity Tracking

No Constitution Check violations. Nothing to justify.
