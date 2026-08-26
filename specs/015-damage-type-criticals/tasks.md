# Tasks: The damage-type critical tables

**Feature**: 015-damage-type-criticals | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_criticals.py` — model the damage scale from the merged numbers and assert agreement with what #13 computed: 1.56 through modest armour, 4.5 hits to drop, and the weapon/armour band those figures used (FR-013).
- [x] T002 Compute the distribution of **points below zero** across the weapon band, all four armour ranks, the telling blow, and remaining Stamina 1–7 — not at a midpoint (FR-007).
- [x] T003 Compute the largest modifier the rules can produce at all, and how far out on the tail it lives, so the open top is a stated property (FR-003, FR-007).
- [x] T004 Draw each table's ranges from that distribution, and assert for every table: contiguous, non-overlapping, first row at 2, last row open at the top, every total from 2 past the extreme on exactly one row (FR-003).
- [x] T005 Compute what each table weighs — nothing lasting / a lasting mark / mortal — at the modifiers that actually occur, and assert the four differ mechanically rather than in prose (FR-002, FR-007).
- [x] T006 Compute death odds composed through both tables (a mortal critical fixes Aftermath at `death`), read against Aftermath's published 23% (FR-008, FR-013).
- [x] T007 Assert every effect any row names is in the closed set the engine already knows, and that no row charges Trauma (FR-005, FR-009).
- [x] T008 Assert every figure the new document publishes, so drift fails loudly rather than reading as authoritative (FR-013).

## The playtest

- [x] T009 `worked-criticals.md` — play a fight by hand: a character and a companion, blows of different damage types at real Stamina, each critical resolved through its table and then through Aftermath, including one mortal blow and one Fate point spent.
- [x] T010 Fold back what the play found, as rules rather than notes. The worked fight may change the rows.

## The rules

- [x] T011 `doc/design/08-criticals.md` — the family: key, die, modifier, lowest possible total, uniqueness, extra fields, and why each is what it is (FR-003, FR-004, FR-006).
- [x] T012 The four damage types, with the rationale for the set and how a setting renames one it has no fiction for (FR-001, FR-010).
- [x] T013 The four tables, one per type, rows of range / key / effect / description (FR-002, FR-004, FR-005).
- [x] T014 When a critical is rolled, and the boundary with Aftermath stated from this side (FR-008).
- [x] T015 The mortal blow: what it marks, how Aftermath reads it, and that Fate and `mortality: low` still answer it unchanged (FR-008).
- [x] T016 What this table does not touch — Trauma, Stamina recovery — so neither is charged twice (FR-009).
- [x] T017 What a setting may replace and may not, with the override example (FR-010).
- [x] T018 `doc/design/07-tables.md` — the Criticals index row gains its link and its stated uniqueness (FR-011).
- [x] T019 `doc/design/03-rules.md` §2 — the critical rule points at the new file and names the four types (FR-011).
- [x] T020 `doc/design/09-aftermath.md` — the criticals/Aftermath boundary table gains the mortal blow, and the death-row section gains its mirror (FR-008, FR-011).
- [x] T021 `doc/design/26-authoring-a-setting.md` — the override example verified against the published keys (FR-011).
- [x] T022 Write every section in place, present tense, no changelog and no "previously we…" note.

## The record

- [x] T023 ADR — the damage-type enumeration: four wound shapes, and the rejected alternatives (a weapon taxonomy, an element taxonomy, three physical types with no fourth, a single undifferentiated critical table) (FR-012).
- [x] T024 ADR — the mortal blow: a critical never kills during the fight, and the rejected alternatives (criticals that kill outright, criticals that never kill, a bonus to the Aftermath total) (FR-008, FR-012).
- [x] T025 Add both ADR rows to the index in `doc/README.md`, and link the new design document from the hub (FR-011).

## The gates

- [x] T026 Confirm nothing added introduces a new die, a new track, a new modifier, or an effect outside the closed set.
- [x] T027 `python3 specs/015-damage-type-criticals/check_criticals.py` — green.
- [x] T028 `python3 tools/check_docs.py` — reachability, dead links, ADR index, link policy.
- [x] T029 `python3 tools/backlog.py check` — the order is still whole.
- [x] T030 Grep `design/` for setting and system vocabulary, and read the four touched documents against each other for the two-descriptions fault (FR-014, SC-006).
