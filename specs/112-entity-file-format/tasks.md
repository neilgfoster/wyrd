# Tasks: Entity file format engine support

**Input**: Design documents from `/specs/112-entity-file-format/`

## Phase 1: Setup

- [ ] T001 Create `engine/wyrd/entity.py` with the module docstring (mirroring `state.py`'s style)
      naming the design doc it implements: `docs/design/25-entities.md`, and noting it reuses
      `state.parse_entity`/`dump_entity`/`save_entity`/`load_entity` for file-level I/O.
- [ ] T002 Create `tests/engine/test_entity.py` with the `PYTHONPATH=engine` import pattern used by
      `tests/engine/test_state.py`.

## Phase 2: Foundational

- [ ] T003 In `engine/wyrd/entity.py`, define module constants `ENTITY_TYPES`,
      `RECURSIVE_TYPES`, `STATUSES` per `data-model.md` and `contracts/entity_module.md`.
- [ ] T004 In `engine/wyrd/entity.py`, define the common-schema required-field set (`id`, `type`,
      `name`, `setting`, `status`) and the type-specific additional-field tables from
      `data-model.md`'s "The ten types" section, as module-level data structures driving
      validation rather than a long if/elif chain.

## Phase 3: User Story 1 - Read and write an entity of any of the ten types (P1)

**Goal**: `validate`/`load` accept a well-formed entity of each of the ten types and reject a
malformed one, per FR-001/FR-002/FR-003/FR-010.

**Independent Test**: For each of the ten types, construct a minimal valid entity, write it via
`state.save_entity`, read it back via `entity.load`, and confirm the round trip reproduces the
same data.

- [ ] T005 [P] [US1] Write `test_validate_accepts_minimal_entity_of_each_type` in
      `tests/engine/test_entity.py`, parametrized over all ten types (data-model.md's common
      schema plus each type's minimal shape).
- [ ] T006 [P] [US1] Write `test_validate_rejects_missing_common_field` and
      `test_validate_rejects_unknown_type` in `tests/engine/test_entity.py`.
- [ ] T007 [US1] Implement `validate(frontmatter: dict) -> dict` in `engine/wyrd/entity.py` per
      `contracts/entity_module.md`, checking the common schema and delegating to each type's
      additional-field table from T004.
- [ ] T008 [P] [US1] Write `test_validate_rejects_invalid_status` and
      `test_validate_rejects_type_specific_enum_violation` (e.g. `character.disposition` outside
      its five values) in `tests/engine/test_entity.py`.
- [ ] T009 [US1] Extend `validate` (T007) to cover type-specific enum fields
      (`character.disposition`/`role`, `place.scale`, `organisation.scale`, `tracker.kind`) per
      `data-model.md`.
- [ ] T010 [P] [US1] Write `test_load_round_trips_each_type` in `tests/engine/test_entity.py`:
      write a minimal entity of each type to a temp path via `state.save_entity`, then confirm
      `entity.load` returns the same frontmatter.
- [ ] T011 [US1] Implement `load(path) -> dict` in `engine/wyrd/entity.py` per
      `contracts/entity_module.md`, calling `state.load_entity` then `validate`, raising
      `state.StateError` naming the file on either failure.

**Checkpoint**: A single entity file of any of the ten types can be written, read back, and
validated end-to-end.

## Phase 4: User Story 2 - Containment resolves without disagreement (P1)

**Goal**: `children_of`/`check_containment` resolve the `parent` tree by reverse lookup and reject
cycles, per FR-005/FR-006.

**Independent Test**: Load a set of entities forming a small tree via `parent`; ask for a given
entity's children and confirm the reverse-lookup result matches the tree by hand. Introduce a
`parent` cycle and confirm it is rejected.

- [ ] T012 [P] [US2] Write `test_resolve_wikilink_strips_brackets_and_passes_through_plain_ids`
      in `tests/engine/test_entity.py`.
- [ ] T013 [US2] Implement `resolve_wikilink(value: str) -> str` in `engine/wyrd/entity.py` per
      `contracts/entity_module.md`.
- [ ] T014 [P] [US2] Write `test_children_of_returns_direct_children_only` in
      `tests/engine/test_entity.py` (three-entity chain A/B/C from quickstart.md).
- [ ] T015 [US2] Implement `children_of(entity_id: str, entities: dict[str, dict]) -> list[str]`
      in `engine/wyrd/entity.py` per `contracts/entity_module.md`, using `resolve_wikilink` on
      each entity's `parent`.
- [ ] T016 [P] [US2] Write `test_check_containment_accepts_rootless_entity` and
      `test_check_containment_rejects_cycle` in `tests/engine/test_entity.py`
      (research.md's cycle-detection approach).
- [ ] T017 [US2] Implement `check_containment(entities: dict[str, dict]) -> dict` in
      `engine/wyrd/entity.py` per `contracts/entity_module.md` and `research.md`'s decision
      (visited-set walk per entity).

**Checkpoint**: Containment resolves correctly and a cycle is rejected without looping forever,
independent of connection-graph or validation-detail work in other phases.

## Phase 5: User Story 3 - Connections are read as a free, conditional, directional graph (P2)

**Goal**: A `hidden: true` connection is preserved and distinguishable; a connection loop is
accepted (not rejected, unlike containment), per FR-007/FR-008/FR-009.

**Independent Test**: Load a place with three connections, one of them `hidden: true`; confirm
all three are present in the loaded data and the hidden one is flagged distinctly.

- [ ] T018 [P] [US3] Write `test_validate_accepts_place_with_connections` and
      `test_validate_preserves_hidden_flag_distinctly` in `tests/engine/test_entity.py`
      (quickstart.md's harbour example).
- [ ] T019 [US3] Extend `validate` (T007/T009) to check each `place.connections` entry's shape
      (`to` required, `via`/`cost`/`requires`/`hidden` optional) per `data-model.md`'s Connection
      table — connections are never acyclicity-checked, only shape-checked.
- [ ] T020 [P] [US3] Write `test_validate_accepts_connection_loop` in `tests/engine/test_entity.py`
      (A connects to B, B connects to A) confirming no rejection, unlike `check_containment`.
- [ ] T021 [P] [US3] Write `test_unresolved_references_reports_absent_target` in
      `tests/engine/test_entity.py` (a `connections[].to` and a `parent` each pointing at an id
      absent from the loaded set).
- [ ] T022 [US3] Implement `unresolved_references(entities: dict[str, dict]) -> list[dict]` in
      `engine/wyrd/entity.py` per `contracts/entity_module.md`, covering `parent`, `links`,
      `connections[].to`, `allegiances`, `cast`, `members`, `based_at`.
- [ ] T023 [P] [US3] Write `test_load_set_loads_and_validates_every_file` in
      `tests/engine/test_entity.py` (a small set of entity files in a temp directory).
- [ ] T024 [US3] Implement `load_set(paths) -> dict[str, dict]` in `engine/wyrd/entity.py` per
      `contracts/entity_module.md`.

**Checkpoint**: All three user stories pass independently; `quickstart.md`'s examples now all run.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T025 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` and fix any
      finding in the new files.
- [ ] T026 Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_entity.py -q` and confirm
      all tests pass; then run the full suite (`PYTHONPATH=engine python3 -m pytest -q`) to
      confirm no regression elsewhere.
- [ ] T027 Review `docs/design/25-entities.md` against the implemented behavior; update it in
      place only if implementation surfaced a genuine gap — otherwise make no design-document
      change.
- [ ] T028 Run `python3 tools/check_docs.py` if any design document was touched in T027.

## Dependencies

- Phase 1 (Setup) and Phase 2 (Foundational) block every user-story phase.
- User Story 1 (Phase 3) has no dependency on any other story — it only needs the module
  constants and field tables from Phase 2.
- User Story 2 (Phase 4) depends on `validate`/`load` existing (Phase 3) only insofar as its own
  tests build entities via the same minimal shapes; `resolve_wikilink`/`children_of`/
  `check_containment` themselves have no functional dependency on Phase 3's implementation.
- User Story 3 (Phase 5) extends `validate` (T007/T009 from Phase 3) with connection-shape
  checking, and its `unresolved_references`/`load_set` build on `resolve_wikilink` (Phase 4,
  T013) — so Phase 5 follows both Phase 3 and Phase 4.
- Phase 6 (Polish) runs last, after every story phase.

**Suggested MVP scope**: User Story 1 alone (Phases 1-3) — a validated, round-tripping entity of
each type is the minimum viable slice; containment and connections build on it existing.

## Parallel execution examples

- Within Phase 3: T005, T006, T008, T010 can be written in parallel (different test functions,
  same file, no shared state) before T007/T009/T011 are implemented.
- Within Phase 4: T012 and T014 can be written in parallel; T016 can be written in parallel with
  both, before T013/T015/T017 are implemented.
- Within Phase 5: T018, T020, T021, T023 can all be written in parallel before T019/T022/T024 are
  implemented.

## Implementation strategy

Build incrementally in phase order: Setup → Foundational → User Story 1 (MVP: a validated,
round-tripping entity of each type) → User Story 2 (containment, which only needs Story 1's shapes
for its own test fixtures) → User Story 3 (connections and cross-entity reference resolution,
which extends Story 1's `validate` and uses Story 2's `resolve_wikilink`) → Polish. Each
user-story checkpoint is a working, testable increment; the loop may stop and report after any
checkpoint if time-boxed.
