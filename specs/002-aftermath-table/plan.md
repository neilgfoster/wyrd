# Implementation Plan: The Aftermath table

**Branch**: `002-aftermath-table` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-aftermath-table/spec.md`

## Summary

Write `doc/design/09-aftermath.md`: the Aftermath family, declared within the conventions #15
established. It is the table `doc/design/03-rules.md` has deferred all combat death to since the ruleset
was written, and the gate on R1.2.

The approach, from [research.md](./research.md): the family rolls **`d100 + (5 × points below
zero)`**, reusing the number the ruleset already computes when a combatant drops, so a harder blow
reads further down the table. Eight rows run from *out of action only* to *death*, covering all five
outcome shapes `doc/design/03-rules.md` promises. Two things that both claim the moment a character would
die — a spent **Fate** point, and a setting's `mortality: low` — resolve through **one** mechanism:
the death rows close, and the result is re-read on the worst non-death row. The character survives
and is not better off, mechanically rather than in prose.

The distribution is **computed**, by [`check_aftermath.py`](./check_aftermath.py), not asserted. That
script has already earned its place: it rejected the first draft's `mortality` design, which made the
table structurally invalid at `mortality: low` and let a combatant dropped by 1 die at
`mortality: high`. Neither fault was visible by reading.

Alongside the new document: `doc/design/03-rules.md` loses its description of an undefined table,
`doc/design/07-tables.md`'s index row is completed, `doc/design/19-state.md` gains the wound record its
`wounds: []` field has always implied, and one ADR records the Fate/Aftermath boundary.

## Technical Context

This is a documentation feature, as 001 was. Most template fields are answered as not applicable
rather than left as placeholders.

**Language/Version**: Markdown (GitHub-flavoured), matching `design/`. One Python 3 script for
verification.

**Primary Dependencies**: None. `doc/design/07-tables.md` (#15) must be merged — it is.

**Storage**: Files in `design/`. The conventions place engine tables at `engine/tables/<key>.yaml`,
but there is no `engine/` directory in this repository yet and none is created here.

**Testing**: `specs/002-aftermath-table/check_aftermath.py` — structural checks on the ranges and an
exact computation of the distribution. Plus the grep checks in [quickstart.md](./quickstart.md).
There is no test suite in this repository; the engine does not exist. Per `CLAUDE.md` these checks
are run rather than asserted.

**Target Platform**: N/A — prose read by humans and by Claude Code at play time.

**Project Type**: Design documentation for a setting-agnostic game engine.

**Performance Goals**: N/A.

**Constraints**: The repository is intended public — nothing derived from a copyrighted source may
enter it. No setting or system name in `design/`. No tonal register baked into a row. Design
documents are rewritten in place, present tense, no changelogs.

**Scale/Scope**: One new document (~180 lines), three existing documents amended, one new ADR, one
index row, one verification script.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` holds no principles of its own; it points at `CLAUDE.md` and the
accepted ADRs. Evaluated against those:

| Gate | Status |
|---|---|
| Nothing unpublishable enters the repository | **Pass.** Every row is written from the engine's own vocabulary. No source text, no quotation, no library catalogue. The five outcome shapes come from `doc/design/03-rules.md`, not from a book. |
| No setting or system names; engine labels are descriptive English | **Pass, verified by grep** (quickstart step 4). Row keys are `out-of-action`, `lasting-wound`, `left-for-dead`, `new-enemy`, `taken`, `disfigured`, `recurring-wound`, `death` — all plain description. |
| Tone is a setting property | **Pass.** Rows state what happened, not how to feel about it. A row says a wound recurs before every fight; it does not say the character is haunted by it. The register is the setting's. |
| Anything with a correct answer is computed, not inferred | **Pass, and load-bearing.** `check_aftermath.py` computes the distribution and the range structure. It found two faults in the first draft ([research.md](./research.md) D2). |
| Rule changes apply forward only | **Pass.** The document states that a result already rolled stands, per `doc/design/22-evolution.md`. This feature adds a table; it recomputes nothing. |
| Design documents rewritten in place; ADRs never edited | **Pass.** `doc/design/03-rules.md` is rewritten where it describes this table, with no "previously" note. The new ADR is new, not an edit. |
| Capability change goes through Spec Kit, `specs/` committed | **Pass.** This is that cycle; `specs/002-aftermath-table/` is committed. |

**Complexity**: none to track. No new mechanic is introduced — Dread, the `wounds` list, `character`
and `thread` entities, the `−10` difficulty step and the Fate valve all already exist. The one thing
that could have been new machinery (a `mortality` roll modifier) was removed in favour of reusing
Fate's mechanism.

## Project Structure

### Documentation (this feature)

```
specs/002-aftermath-table/
├── spec.md                  # the requirements, with the operator's four clarifications
├── plan.md                  # this file
├── research.md              # the eight decisions and what each rejected
├── data-model.md            # the wound record, the entities, what is recorded
├── quickstart.md            # how to verify this feature is done, as commands
├── check_aftermath.py       # the distribution and range checker (FR-026, SC-003, SC-004)
├── contracts/
│   └── aftermath-table.md   # the family's declared contract, row by row
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

There is no source code. The repository is design documents and decision records; the engine has not
been written. Files touched:

```
design/
├── 03-rules.md              # AMEND  — link the table; stop describing it as undefined
├── 03a-tables.md            # AMEND  — complete the Aftermath index row
├── 03a-2-aftermath.md       # NEW    — the family
├── 06-state.md              # AMEND  — the wound record's shape
└── adr/
    └── 0009-fate-closes-the-death-rows.md   # NEW
```

**Structure Decision**: the document lives at `doc/design/09-aftermath.md`, following the index
`doc/design/07-tables.md` established in #15, which assigns `03a-1-` to criticals. Issue #16's
acceptance criteria names `03a-1-aftermath.md`; it was written before #15 merged and is stale. The
operator confirmed the index wins ([spec.md](./spec.md#clarifications)). **Issue #16 needs that line
corrected** so the board does not disagree with the merged index.

## The table, as it will be written

Roll `d100 + (5 × points below zero)`. Lowest possible total 6. Repeatable. No extra row fields.

| Range | Key | Effect |
|---|---|---|
| 6–30 | `out-of-action` | Nothing lasting. Out of action until the fight ends. |
| 31–52 | `lasting-wound` | One wound record. |
| 53–66 | `left-for-dead` | One wound record; the character wakes elsewhere, stripped of what they carried. |
| 67–78 | `new-enemy` | One wound record; a `character` entity with `role: nemesis` and an objective. |
| 79–88 | `taken` | Captured. A `thread` entity opens; a companion's `status` becomes `away`. |
| 89–98 | `disfigured` | One wound record whose effect is `dread: +1`. |
| 99–110 | `recurring-wound` | One wound record with `recurring: true` — `−10` to the combat skill at the start of every future fight. |
| 111+ | `death` | Death, unless the death rows are closed. |

Computed, across drops of 1–12: **a lasting mark 70.8%, death 22.9%**. A drop of 1 or 2 cannot reach
the death row at all. Full figures in [research.md](./research.md) D8; the script is the authority.

**Coverage of what `doc/design/03-rules.md` promises** — permanent wound (`lasting-wound`), new enemy
(`new-enemy`), capture (`taken`), a disfigurement that frightens people (`disfigured`), a wound that
recurs before every future fight (`recurring-wound`), and death at the extreme (`death`). All five
shapes plus death, each with its own row.

## Phases

**Phase 0 — research.** Complete. [research.md](./research.md) records eight decisions; D2 was found
by the script rather than by reasoning.

**Phase 1 — design.** Complete. [data-model.md](./data-model.md) fixes the wound record and the
entities; [contracts/aftermath-table.md](./contracts/aftermath-table.md) fixes the family's
declaration row by row; [quickstart.md](./quickstart.md) fixes how it is verified.

**Constitution re-check after Phase 1**: still passing. Nothing in the design added a mechanic, a
field nothing reads, or a claim that is asserted rather than computed.

**Phase 2 — tasks.** `/kord-feature-tasks` derives the task list from this plan.

## What is deliberately left out

- **Stamina recovery, and whether a lasting wound ever heals.** R1.2 of epic #1. This feature defines
  what a wound *is*; the record carries no field that prejudges healing.
- **`engine/tables/aftermath.yaml`.** No `engine/` directory exists yet.
- **The critical tables.** A sibling issue. This document states the boundary — criticals resolve
  during the fight, per damage type; Aftermath resolves after it, once per combatant who dropped — so
  the sibling has something fixed to write against.
- **What Strain does.** Discovered while designing the recurring wound ([research.md](./research.md)
  D7): `doc/design/03-rules.md` §5 says where Strain comes from and when it clears but never what it
  does. Out of scope here, and worth its own issue.
