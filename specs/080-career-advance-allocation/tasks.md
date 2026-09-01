# Tasks: Career graph and advance allocation

**Input**: Design documents from `/specs/080-career-advance-allocation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, same rationale as #221-#229.

**Organization**: A single cohesive function (`validate_allocation`) — no independently
shippable sub-stories; US1 (the career shape) is only meaningful as an input to US2's validator.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Adds `engine/wyrd/career.py` (new file); extends `catalog.py`/`verbs.py`/`client.py`.

---

## Phase 1: Setup

None needed beyond what #221-#229 already provide.

---

## Phase 2: Tests (write first, confirm they fail)

- [ ] T001 Create `tests/engine/test_career.py`: each of the four worked spreads from
      docs/design/11-character-creation.md section 3 (open 2 everything-into-one → 55%/25%;
      open 2 split evenly → 40%/40%; open 3 → 35%/35%/30%; open 4 → 30%×4) is accepted with
      exactly the documented percentages (SC-001)
- [ ] T002 Add to `tests/engine/test_career.py`: total != 8 is rejected naming the total
      (Acceptance Scenario 2); fewer than 2 skills opened is rejected (Scenario 3); raising past
      a skill's cap is rejected naming the skill and cap (Scenario 4); acting on a skill outside
      the career∪ancestry union is rejected naming the skill (Scenario 5); opening an
      already-open skill is rejected (Scenario 7); raising a not-yet-open skill is rejected
      (Scenario 8) — eight distinct rejection cases total across this task and T001's positive
      cases (SC-002)
- [ ] T003 Add to `tests/engine/test_career.py`: an ancestry-granted skill (not in the career) is
      accepted, widening eligibility without adding to the 8-action budget, and its resulting
      percentage is correct (Scenario 6, SC-003); a skill present in both career and ancestry
      with different caps resolves to the higher cap (research.md's Assumption)
- [ ] T004 [P] Add to `tests/engine/test_verbs.py`: `verbs.validate_allocation(...)` returns the
      documented shape for both an accepted and a rejected allocation
- [ ] T005 [P] Add to `tests/engine/test_client.py`: `describe --name validate-allocation`
      matches contracts/cli.md; a valid and an invalid allocation both return the documented
      JSON shape via the CLI, exit 0 either way; malformed `--actions-json` is a non-zero exit
      (not a caller-input validation case, per contracts/cli.md)

---

## Phase 3: Implementation

- [ ] T006 Create `engine/wyrd/career.py`: `effective_cap(skill, career, ancestry=None) -> int |
      None` (the higher of the career's and ancestry's cap for `skill`, `None` if in neither)
- [ ] T007 Implement `validate_allocation(actions: list[dict], career: dict, ancestry: dict |
      None = None) -> dict` in `career.py`: check total count == 8 first (FR-004), then distinct
      `open` count >= 2 (FR-005), then replay actions in order tracking each skill's current
      value and open/closed state, applying FR-006 through FR-009 per action using
      `rules.SKILL_OPEN_VALUE`/`rules.SKILL_ADVANCE_STEP` — return `{"valid": True, "skills":
      {...}}` on success or `{"valid": False, "error": "..."}` naming the first rule violated —
      depends on T006
- [ ] T008 [P] Add `validate-allocation` to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md
- [ ] T009 [P] Implement the `validate_allocation` verb wrapper in `engine/wyrd/verbs.py`
- [ ] T010 [P] Add the `validate-allocation` subcommand to `engine/wyrd/client.py`:
      `--career-json` required, `--ancestry-json` optional, `--actions-json` required, each
      parsed as JSON; a `json.JSONDecodeError` on any of them is an uncaught, non-zero-exit
      failure (not wrapped into a structured error), per contracts/cli.md's exit-code note
- [ ] T011 Add a `to_text` case for `validate-allocation` results in `engine/wyrd/render.py`

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes.

---

## Phase 4: Polish

- [ ] T012 Run every step of `specs/080-career-advance-allocation/quickstart.md` by hand and
      confirm
- [ ] T013 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/`, fix anything flagged

---

## Dependencies & Execution Order

- Phase 2's T001-T003 build the same file sequentially (each adds to `test_career.py`); T004/T005
  are independent of that chain and of each other.
- Phase 3: T006 before T007 (T007 calls T006). T008-T011 depend on T007 existing to wire up, but
  are independent of each other once it does.
- Phase 4 depends on Phase 3.

## Implementation Strategy

Single increment — one function, tested against every documented case before wiring the CLI
around it.
