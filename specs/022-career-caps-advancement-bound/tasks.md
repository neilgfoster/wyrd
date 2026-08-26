# Tasks: Career caps and the advancement bound

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

## Phase 1 — Computation (must precede the design doc's claims)

- [X] T001 Write `tools/check_advancement.py`: model a character completing careers
  back-to-back across a chronicle of 10+ career-instances (skills opened at 25%, raised by +5%
  per advance to the 70% cap, +1 maximum Stamina and one Mark per completion), and compute the
  Stamina sequence across completions. [FR-009, FR-010, SC-004]
- [X] T002 In the same script, find and assert the Stamina value at which a further +1 stops
  being a gain of the same order as the 16.7% (1-in-6) framing `03c-character-creation.md` used to
  fix the starting value at 6 — state this as the hard ceiling. [FR-009, SC-004]
- [X] T003 In the same script, scan the skill spread across the 10+ completions and assert no
  skill exceeds 100% and the spread stays consistent with "depth over breadth" (a character with
  many completions is not expert at everything they've touched). [FR-003, SC-004]
- [X] T004 Run the script and capture its output (the cap, the Stamina sequence, and the
  ceiling) for the design document. [SC-001, SC-004]

## Phase 2 — Design document

- [X] T005 Update `docs/design/03-rules.md` §6 in place: state the 70% career cap applied uniformly to
  every skill a career grants (FR-001, FR-002, FR-003), the illegal-advance rule (FR-004), no
  changelog language. [US1]
- [X] T006 In the same section, state the completion trigger (every granted skill at the cap,
  FR-005), the per-career-instance grant of +1 maximum Stamina and one Mark (FR-006), the
  forfeiture rule for leaving early (FR-007), and per-instance tracking so re-entering a career
  starts a fresh completion (FR-008). [US2]
- [X] T007 State the computed Stamina ceiling from T002, and cross-reference
  `03c-character-creation.md`'s starting-value reasoning rather than restating it. [US3, FR-009]
- [X] T008 Confirm the companion carve-out already in §6 ("no career graph, no Marks") is left
  intact and unambiguous against the new player-character rules just added. [FR-011]

## Phase 3 — Decision record

- [X] T009 Write `docs/adr/0032-career-cap-and-the-stamina-ceiling.md`: the flat-70%-cap
  decision (rejecting a per-skill cap table) and the computed-Stamina-ceiling decision (rejecting
  an unbounded gain), each with its rejected alternative.
- [X] T010 Add ADR 0032 to `docs/README.md`'s index.

## Phase 4 — Verification

- [X] T011 `grep` the touched files for setting/system vocabulary and tonal register; confirm
  none. [FR-012]
- [X] T012 Re-read the companion carve-out (T008) and the "harder to replace, not harder to
  kill" claim in §6 against the new text; confirm neither is contradicted.
- [X] T013 Run `python3 tools/check_docs.py` — must pass. [SC-005]
- [X] T014 Run `python3 tools/backlog.py check` — must pass. [SC-005]

## Dependencies

Phase 1 before Phase 2 (the design doc's cap and ceiling are the script's output, not a guess).
Phase 3 can run alongside Phase 2 once the load-bearing decisions are fixed. Phase 4 last.
