---

description: "Task list for 001-table-conventions"
---

# Tasks: Table conventions and the tables index

**Input**: Design documents from `/specs/001-table-conventions/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/table-file.md, quickstart.md

**Tests**: No automated tests. This repository has no test suite — the engine does not exist yet
(`doc/design/20-tooling.md` describes it as future work). Verification is the mechanical grep-and-read
pass in [quickstart.md](./quickstart.md), which Phase 6 executes. Per `CLAUDE.md`, those checks are
run rather than asserted.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Design documentation at `design/`, decision records at `doc/adr/`. No source tree is touched —
`engine/` does not exist and is not created here (`tables.py` is R4 of epic #1, out of scope).

---

## Phase 1: Setup

**Purpose**: Establish the file and its place in the design set before any content goes in.

- [x] T001 Create `doc/design/07-tables.md` with its title, a one-paragraph statement of what the
      document is for, and its section headings only — no content yet. Sections: how a table is
      rolled and read; the row schema; the override contract; the index; versioning. Present tense,
      no changelog (`doc/README.md`).

**Checkpoint**: The document exists and its shape is fixed, so the three stories below fill
independent sections rather than negotiating structure.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The family set has to be agreed and consistent before an index of it can be written.
Getting this wrong makes every later task index the wrong thing.

**⚠️ CRITICAL**: No user story work begins until T002 and T003 are done.

- [x] T002 Correct the stale family list at `doc/design/20-tooling.md:84`: it reads "criticals,
      aftermath, transformations, oracles" and omits afflictions, which `doc/design/02-architecture.md:91`
      includes and `doc/design/03-rules.md:229` requires. Add afflictions so the two lists match
      (research.md R10, FR-015). This is fault class 3 — both documents read as coherent alone.
- [x] T003 Confirm by reading `doc/design/02-architecture.md:91`, the corrected `doc/design/20-tooling.md:84`
      and every table reference in `doc/design/03-rules.md` that the family set is exactly five:
      criticals, aftermath, transformations, afflictions, oracles. Record nothing; this gates T004
      and SC-002/SC-005.

**Checkpoint**: The family set is settled and consistent across the design set.

---

## Phase 3: User Story 1 — An author writes a new table family (Priority: P1) 🎯 MVP

**Goal**: A sibling author can write their family's file without inventing any structural decision.

**Independent test**: Give the document to a reader who has seen none of the sibling issues; they
can state the row fields and why a total can never fall off either end, without guessing (SC-001).

- [x] T004 Write the **index** section of `doc/design/07-tables.md`: one row per family, each with its
      name, its roll, its uniqueness, and its own `design/03a-N-*.md` file. Those files do not exist
      yet, so name each as plain text marked *not yet written* rather than as a link — a link to a
      missing file is a broken link, and the sibling turns it into a live one when it lands.
      Structure it so adding a sixth family is one new row and touches no other line (FR-012,
      SC-003).
- [x] T005 Write the **how a table is rolled and read** section: that the die and the modifier are
      family properties declared in the family's own file, not engine-wide (FR-002, research.md R1);
      why there is no out-of-range case at all — contiguity, a floor at the family's lowest total,
      and an open-topped last row, all required at load (FR-003, R2);
      the reroll rule for a unique-per-character family and the exhaustion outcome when no unheld
      result remains (FR-004, FR-004a, R5).
- [x] T006 Write the **row schema** section: `range`, `effect`, `description` on every row, and what
      each is for (FR-005, R3). State that `effect` reaches state and `description` does not, and
      that this split is what makes the override contract and renames work. State that a family may
      declare additional fields, and that severity is one such — carried by transformations and
      afflictions, not shared (FR-006, FR-007, R4).
- [x] T007 Write the **naming and file layout** paragraph: keys are lowercase and hyphenated,
      `<family>` or `<family>-<variant>`, one table per file, engine tables at
      `engine/tables/<key>.yaml`. Consistent with the `critical-slashing` example already published
      at `doc/design/26-authoring-a-setting.md:157`, which is the only existing evidence of either
      convention (FR-008, R6).
- [x] T008 Review T005–T007 against the plan's implementation note 2: no plausible table content.
      Any illustrative row uses placeholders, or is omitted. A plausible row reads as authoritative,
      is not, and pre-empts the sibling whose job it is (FR-014).

**Checkpoint**: A sibling author has everything they need. This alone is a viable deliverable.

---

## Phase 4: User Story 2 — A setting author replaces a table (Priority: P2)

**Goal**: A setting author can tell whether a proposed override is legal and where their file goes.

**Independent test**: From this document alone, determine the legality of an override and name the
file path the replacement must live at.

- [x] T009 Write the **override contract** section of `doc/design/07-tables.md`: a setting replaces a
      table's rows via `overrides.tables:`, and may not change the family's roll, modifier,
      uniqueness, exhaustion outcome or row schema — each of those is a mechanism, and a setting
      needing a new mechanism files an engine gap (FR-009, R8,
      `doc/design/26-authoring-a-setting.md`).
- [x] T010 State the load-time requirements on an overriding table, as the numbered list in
      contracts/table-file.md: published key, contiguous non-overlapping ranges spanning the
      rollable minimum, all required fields present, every `effect` naming a known mechanic. Each is
      a load error, not a warning (FR-011, ADR 0005). Mark explicitly which single rule — no setting
      or system vocabulary — is a review obligation rather than a load check, since a script cannot
      settle it.
- [x] T011 State that renames reach `description` only, never `key` or `effect`, and that this is
      why the row schema separates them (FR-010, ADR 0004).
- [x] T012 [P] Amend `doc/design/26-authoring-a-setting.md` near line 157 to link the
      `overrides.tables:` example to the contract in `doc/design/07-tables.md`, so the one published
      example stops being the only statement of a contract it does not state (FR-015, R10).

**Checkpoint**: The override contract is complete and the document that presumed it now points at
it.

---

## Phase 5: User Story 3 — A chronicle replays years later (Priority: P3)

**Goal**: A recorded table outcome stays interpretable after the table changes, and is never
recomputed.

**Independent test**: Given a recorded outcome from an earlier version, a reader can identify the
table that produced it and confirm it will not be recomputed.

- [x] T013 Write the **versioning** section of `doc/design/07-tables.md`: a table is pinned by the
      version stamps that already exist — engine and setting versions in `chronicle.yaml`, the
      engine stamped on every outcome (`doc/design/22-evolution.md:105`) — plus the table key recorded
      with the outcome. State explicitly that no per-table version is introduced, and why: a version
      nobody bumps reliably reads as authoritative and is not (FR-013, R7).
- [x] T014 State that a table change is *tuning* when it alters ranges, effects or numbers within an
      existing family and *additive* when it adds a table or row without changing existing ranges;
      that both are forward-only; and that recorded outcomes stand unchanged (FR-013a,
      `doc/design/22-evolution.md:37`).

**Checkpoint**: All five sections of the document are written.

---

## Phase 6: Cross-cutting — links, record, verification

**Purpose**: Make the document reachable, record the decision, and verify mechanically rather than
by assertion.

- [x] T015 [P] Amend `doc/design/02-architecture.md:91` to link the `tables/` bullet to
      `doc/design/07-tables.md` (FR-015, R10).
- [x] T016 [P] Amend `doc/design/20-tooling.md:84` to link the `tables.py` line to
      `doc/design/07-tables.md` — the conventions are what that module will implement (FR-015, R10).
- [x] T017 [P] Amend `doc/design/03-rules.md` at each of lines 115, 123, 205 and 229 to link the named
      table to `doc/design/07-tables.md`, so every table reference in the ruleset resolves (FR-015,
      SC-005, R10).
- [x] T018 Write `doc/adr/0008-tables-declare-their-own-roll.md`: dated, accepted, recording that
      the engine fixes the row schema and lookup rule while each family declares its own roll, and
      that the rejected alternative was one universal table format rolled the same way across every
      family. It earns a record on `doc/README.md`'s two-part test — a workable smaller engine
      was rejected, and "why does every table roll differently?" is the first question a reader asks
      (research.md R9).
- [x] T019 Add the ADR 0008 row to the index in `doc/README.md` (FR-017).
- [x] T020 Run every mechanical check in [quickstart.md](./quickstart.md) §1, §3, §4, §6, §7 and
      report the actual output. Do not assert a pass — `CLAUDE.md`: where a claim can be checked by
      a script, check it.
- [x] T021 Read `doc/design/07-tables.md` against `doc/design/02-architecture.md`,
      `doc/design/20-tooling.md`, `doc/design/22-evolution.md` and `doc/design/26-authoring-a-setting.md` for
      contradictions (quickstart §8, SC-006, FR-015). This is fault class 3 — grep does not find it,
      because both documents read as coherent alone.
- [x] T022 Read the added prose for the two faults a wordlist misses: a mechanic name carrying genre,
      and a tonal register baked into a convention or an example (quickstart §7, FR-016,
      `CLAUDE.md` fault classes 2 and 5).
- [x] T023 Confirm the index is genuinely append-only (quickstart §5, SC-003): the families are
      enumerated in exactly one place in `doc/design/07-tables.md`. If prose elsewhere in the document
      lists them a second time, remove it — it will go stale the first time a sibling lands.

---

## Dependencies

```text
T001
 └── T002, T003  (Foundational — must both complete before any story)
       ├── US1: T004 → T005 → T006 → T007 → T008
       ├── US2: T009 → T010 → T011,  T012 [P]
       └── US3: T013 → T014
             └── T015 [P], T016 [P], T017 [P], T018 → T019
                   └── T020 → T021 → T022 → T023
```

- US1, US2 and US3 all write into `doc/design/07-tables.md`, so their tasks are **not** parallel with
  each other despite being independent stories. Only the tasks touching other files (T012, T015,
  T016, T017) carry `[P]`.
- T019 depends on T018 — the index row needs the record to exist.
- Phase 6's verification tasks (T020–T023) depend on everything, by design.

## Independent delivery

US1 alone is a viable increment: it unblocks the four sibling children, which is the whole reason
issue #15 is the gate. US2 and US3 complete the contract but no sibling is waiting on them.
