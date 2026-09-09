# Tasks: Companion and party simulation engine support

**Input**: Design documents from `/specs/111-companion-party-simulation/`

## Phase 1: Setup

- [ ] T001 Create `engine/wyrd/party.py` with the module docstring (mirroring `character.py`'s
      style) naming the design docs it implements: `docs/design/10-the-character.md` §4,
      `docs/design/16-session.md`, ADR 0034.
- [ ] T002 Create `tests/engine/test_party.py` with the `PYTHONPATH=engine` import pattern used by
      `tests/engine/test_character.py`.

## Phase 2: Foundational

- [ ] T003 In `engine/wyrd/party.py`, define `MECHANICAL_FIELDS = {"career", "bond", "taint",
      "strain", "wounds"}` and `NARRATIVE_FIELDS = {"objective", "flaw", "secret", "arc"}` as
      module constants (data-model.md's Companion section), matching
      `tools/check_companion_layers.py`'s `EXPECTED_MECHANICAL`/`EXPECTED_NARRATIVE`.

## Phase 3: User Story 1 - Bring a companion into the party (P1)

**Goal**: Represent and validate a companion record with both layers, per FR-001/FR-002.

**Independent Test**: `validate_companion` accepts a well-formed record and rejects one with a
missing or extra mechanical field.

- [ ] T004 [P] [US1] Write `test_validate_companion_accepts_well_formed_record` in
      `tests/engine/test_party.py` (data-model.md's Companion example).
- [ ] T005 [P] [US1] Write `test_validate_companion_rejects_missing_field` and
      `test_validate_companion_rejects_extra_field` in `tests/engine/test_party.py`.
- [ ] T006 [US1] Implement `validate_companion(companion: dict) -> dict` in `engine/wyrd/party.py`
      per `contracts/party_module.md`, checking the mechanical layer against `MECHANICAL_FIELDS`
      exactly (no missing, no extra) and that `bond` is an integer in `[-3, 3]`.
- [ ] T007 [US1] Write `test_validate_companion_rejects_out_of_range_bond` in
      `tests/engine/test_party.py` and confirm it passes against T006.

**Checkpoint**: Companion records can be created and validated end-to-end.

## Phase 4: User Story 2 - Tension and Bond interact the way the rule specifies (P1)

**Goal**: Bond-offset Tension arithmetic and the 6-break-and-reset rule, per FR-003/FR-004/FR-005.

**Independent Test**: `tension_delta` reproduces the design document's worked table; `apply_tension`
resolves a break at/above 6 and resets to 0.

- [ ] T008 [P] [US2] Write `test_tension_delta_matches_design_table` in
      `tests/engine/test_party.py`, parametrized over the four worked values from
      `docs/design/16-session.md` (bond +3→0, +1→0, 0→1, -2→3 for a base-1 event).
- [ ] T009 [P] [US2] Write `test_tension_delta_unaffected_when_no_companion_named` in
      `tests/engine/test_party.py` (`bond=None`).
- [ ] T010 [US2] Implement `tension_delta(base_delta: int, *, bond: int | None,
      strained_pairing: bool) -> int` in `engine/wyrd/party.py` per `contracts/party_module.md`.
- [ ] T011 [P] [US2] Write `test_apply_tension_breaks_and_resets_at_six` and
      `test_apply_tension_does_not_go_negative` in `tests/engine/test_party.py`.
- [ ] T012 [US2] Implement `apply_tension(current: int, delta: int) -> dict` in
      `engine/wyrd/party.py` per `contracts/party_module.md`.
- [ ] T013 [US2] Write `test_downtime_and_beat_spend_reduce_tension_floored_at_zero` in
      `tests/engine/test_party.py` and implement `apply_tension_decrement(current: int) -> int` in
      `engine/wyrd/party.py` (FR-006: -1, floored at 0).

**Checkpoint**: Tension/Bond arithmetic is independently correct and testable without any party
assembly or Loyalty logic.

## Phase 5: User Story 3 - Loyalty gates who can join, and strain doubles Tension gain (P2)

**Goal**: Loyalty-relation lookup, join gating, and the strained-doubling/irreconcilable-break
rules, per FR-007 through FR-011.

**Independent Test**: `loyalty_relation` and `can_join` behave per data-model.md's Loyalty
relation table and State transitions sections.

- [ ] T014 [P] [US3] Write `test_loyalty_relation_defaults_to_undeclared` and
      `test_loyalty_relation_is_symmetric` in `tests/engine/test_party.py`.
- [ ] T015 [US3] Implement `loyalty_relation(a: str, b: str, relations: dict[tuple[str, str],
      str]) -> str` in `engine/wyrd/party.py` per `contracts/party_module.md`.
- [ ] T016 [P] [US3] Write `test_can_join_refuses_irreconcilable_pairing_and_names_it` in
      `tests/engine/test_party.py`.
- [ ] T017 [P] [US3] Write `test_can_join_refuses_when_party_full` in `tests/engine/test_party.py`
      (party_size == 5, per data-model.md's bound).
- [ ] T018 [P] [US3] Write `test_can_join_allows_strained_and_undeclared_pairings` in
      `tests/engine/test_party.py`.
- [ ] T019 [US3] Implement `can_join(candidate_loyalty: str, party_loyalties: list[str], relations:
      dict[tuple[str, str], str], party_size: int) -> dict` in `engine/wyrd/party.py` per
      `contracts/party_module.md`.
- [ ] T020 [US3] Update `tension_delta`'s `strained_pairing` handling (already parametrized in
      T010) to double `base_delta` before any Bond offset (FR-009), and add
      `test_tension_delta_doubles_under_strained_pairing` in `tests/engine/test_party.py`.
- [ ] T021 [US3] Write `test_loyalty_change_to_irreconcilable_breaks_tension_immediately` in
      `tests/engine/test_party.py` and implement `recheck_loyalty_change(party_loyalties:
      list[str], relations: dict[tuple[str, str], str]) -> bool` in `engine/wyrd/party.py`
      (returns whether an irreconcilable pairing now exists, per FR-010 — the caller applies the
      immediate break via `apply_tension`).

**Checkpoint**: Party assembly is gated correctly and Tension's strained-doubling and
Loyalty-change-break rules hold.

## Phase 6: User Story 4 - The GM plays the whole rest of the party (P2)

**Goal**: Surface each companion's recorded narrative layer alongside its mechanical layer for the
GM, without generating or altering any narrative content, per FR-012/FR-013.

**Independent Test**: `roster` returns both layers unchanged for every companion passed in.

- [ ] T022 [P] [US4] Write `test_roster_returns_both_layers_unchanged` in
      `tests/engine/test_party.py` for a single companion.
- [ ] T023 [P] [US4] Write `test_roster_handles_full_five_companion_party` in
      `tests/engine/test_party.py`.
- [ ] T024 [US4] Implement `roster(companions: list[dict]) -> list[dict]` in
      `engine/wyrd/party.py` per `contracts/party_module.md` — a pure pass-through/reshape, no
      content generation.

**Checkpoint**: All four user stories pass independently; `quickstart.md`'s examples now all run.

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T025 Run `python3 tools/check_companion_layers.py` and confirm it still passes unchanged
      (this feature must not alter the closed five-field mechanical layer).
- [ ] T026 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` and fix any
      finding in the new files.
- [ ] T027 Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_party.py -q` and confirm all
      tests pass; then run the full suite (`PYTHONPATH=engine python3 -m pytest -q`) to confirm no
      regression elsewhere.
- [ ] T028 Review `docs/design/10-the-character.md` §4 and `docs/design/16-session.md` against the
      implemented behavior; update either in place only if implementation surfaced a genuine gap
      (per the issue's Definition of Done) — otherwise make no design-document change.
- [ ] T029 Run `python3 tools/check_docs.py` if any design document was touched in T028.

## Dependencies

- Phase 1 (Setup) and Phase 2 (Foundational) block every user-story phase.
- User Story 1 (Phase 3) has no dependency on any other story — it only needs the module
  constants from Phase 2.
- User Story 2 (Phase 4) has no dependency on User Story 1's validation logic — it only needs the
  module file to exist (Phase 1).
- User Story 3 (Phase 5) depends on User Story 2's `tension_delta` (T020 modifies it), so Phase 4
  completes before Phase 5.
- User Story 4 (Phase 6) has no dependency on Stories 2/3 — it only needs companion records
  shaped per User Story 1, so it may run in parallel with Phases 4-5 once Phase 3 completes.
- Phase 7 (Polish) runs last, after every story phase.

**Suggested MVP scope**: User Story 1 alone (Phases 1-3) — a validated companion record is the
minimum viable slice; every later story builds on it existing.

## Parallel execution examples

- Within Phase 3: T004 and T005 can run in parallel (different test functions, same file, no
  shared state) before T006 is implemented.
- Within Phase 4: T008/T009 (Tension-delta tests) and T011 (apply_tension tests) can be written in
  parallel; T010 and T012 are separate functions and can be implemented in parallel once their
  tests exist.
- Within Phase 5: T014, T016, T017, T018 can all be written in parallel before T015/T019 are
  implemented.
- Phase 6 (User Story 4) can be worked in parallel with Phase 5 (User Story 3) once Phase 3 is
  done, since neither touches the other's functions.

## Implementation strategy

Build incrementally in phase order: Setup → Foundational → User Story 1 (MVP: a validated
companion record) → User Story 2 (Tension/Bond arithmetic, independently useful for anyone driving
Tension by hand) → User Story 3 (Loyalty gating, which extends Story 2's Tension function) → User
Story 4 (roster read, a thin layer over Story 1's records) → Polish. Each user-story checkpoint is
a working, testable increment; the loop may stop and report after any checkpoint if time-boxed.
