# Tasks: The crowd rule

**Input**: Design documents from `specs/089-the-crowd-rule/`
**Prerequisites**: plan.md

## Phase 1: Qualification and ease

- [ ] **T001** Implement `is_crowd_member(opponent_max_stamina, opponent_armoured,
      character_skill, opponent_skill)` in `combat.py` (FR-001).
- [ ] **T002** [P] Implement `crowd_ease(body_count)`: +10 per body beyond the first, capped at
      +20 (FR-005).

## Phase 2: Body-count tracking

- [ ] **T003** Implement `register_crowd(crowd, body_count, *, state_path=...)` and
      `crowd_body_count(crowd, *, state_path=...)`, nesting a `crowds` dict in the chronicle's
      `combat` scene (FR-002 depends on this).
- [ ] **T004** Implement `clear_crowd_member(actor, crowd, *, state_path=...)`: requires `actor`
      currently engaged with `crowd`; decrements the crowd's body count by exactly one; no roll,
      no `acted` mutation; raises on a non-engaged actor or an already-empty crowd (FR-002,
      FR-003).

## Phase 3: Crowd attacks

- [ ] **T005** Implement `crowd_attack(crowd, target, skill, weapon_dice, armour_dice, *,
      seed=None, state_path=...)`: reads the crowd's current body count, computes
      `crowd_ease`, stages exactly one `combat-attack` request via `resolution.propose_batch`
      with that ease as `declaration_bonus` (FR-004, FR-005).
- [ ] **T006** Implement `crowd_parting_blow(crowd, actor, skill, weapon_dice, armour_dice, *,
      seed=None, state_path=...)`: same shape as `crowd_attack`, crowd attacking the departing
      actor (FR-006).

## Phase 4: Tests

- [ ] **T007** [P] `tests/engine/test_combat.py`: `is_crowd_member` at each boundary (Stamina 1
      vs. 2, armoured vs. not, skill gap 19 vs. 20) (SC-001).
- [ ] **T008** [P] Test: `crowd_ease` at body counts 1, 2, 3, and 3+ (SC-003's ease values).
- [ ] **T009** [P] Test: a multi-round `clear_crowd_member` sequence against a registered crowd
      ends at the expected remaining count, with `acted` never touched (SC-002).
- [ ] **T010** [P] Test: `clear_crowd_member` raises when the actor is not engaged with the
      crowd, and when the crowd is already at zero (FR-003).
- [ ] **T011** [P] Test: `crowd_attack` at 1, 2, and 3-or-more remaining bodies each resolve as
      exactly one `combat-attack` step, with `effective_pct` differing by the expected ease
      (SC-003).
- [ ] **T012** [P] Test: `crowd_parting_blow` resolves as exactly one `combat-attack` step
      regardless of remaining body count (SC-004).

## Phase 5: Polish

- [ ] **T013** `ruff check . && ruff format --check . && python3 -m pytest -q` clean.
- [ ] **T014** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

T001/T002 independent. T003 before T004. T003 before T005/T006. Tests (T007-T012) after their
respective implementation tasks. Polish (T013-T014) last.
