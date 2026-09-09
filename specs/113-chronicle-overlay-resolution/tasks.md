# Tasks: Chronicle overlay resolution

**Input**: Design documents from `/specs/113-chronicle-overlay-resolution/`

## Phase 1: Setup

- [x] T001 In `engine/wyrd/entity.py`, extend the module docstring to note it now also resolves
      `chronicle/setting/` + `chronicle/overlay/` into effective entities, per
      `docs/design/25-entities.md`'s "chronicle overlay" section.

## Phase 2: Foundational

- [x] T002 In `engine/wyrd/entity.py`, define the overlay-only bookkeeping field set (`id`,
      `overlay_of`) that `resolve_entity` (T005) excludes from a merged effective entity's
      frontmatter, per `data-model.md`.

## Phase 3: User Story 1 - Setting entity with no overlay resolves unchanged (P1)

**Goal**: `resolve_entity` returns the setting entity unchanged when no overlay targets it, per
FR-004.

**Independent Test**: Resolve an entity id present in `setting_entities` with an empty/unrelated
`overlays` mapping and confirm the result is identical to the setting entity.

- [x] T003 [P] [US1] Write `test_resolve_entity_with_no_overlay_returns_setting_unchanged` in
      `tests/engine/test_entity.py`, per `quickstart.md`'s User Story 1 example.
- [x] T004 [P] [US1] Write `test_resolve_entity_unknown_id_raises` in `tests/engine/test_entity.py`
      (resolving an id absent from `setting_entities` at all is a caller error, distinct from
      FR-008's dangling-overlay case).
- [x] T005 [US1] Implement `resolve_entity(entity_id: str, setting_entities: dict[str, dict],
      overlays: dict[str, dict], setting_bodies: dict[str, str] | None = None,
      overlay_bodies: dict[str, str] | None = None) -> dict` in `engine/wyrd/entity.py`: with no
      overlay for `entity_id`, return the setting entity's frontmatter unchanged (a shallow copy,
      not the same dict object, so a caller cannot mutate the stored setting entity through the
      result).

**Checkpoint**: Untouched entities resolve as pure pass-throughs.

## Phase 4: User Story 2 - Overlay changes one field (P1)

**Goal**: `resolve_entity` merges overlay fields over the setting entity, overlay taking
precedence, per FR-002/FR-003/FR-006/FR-007/FR-009.

**Independent Test**: Resolve an entity with an overlay changing one field; confirm that field is
overridden and every other field (and the body) matches the setting entity.

- [x] T006 [P] [US2] Write `test_resolve_entity_overlay_overrides_one_field` and
      `test_resolve_entity_overlay_overrides_multiple_fields` in `tests/engine/test_entity.py`,
      per `quickstart.md`'s User Story 2 example and SC-002.
- [x] T007 [P] [US2] Write `test_resolve_entity_excludes_overlay_bookkeeping_fields` in
      `tests/engine/test_entity.py` (the effective entity's `id` is the setting id, never the
      overlay file's own `id`; `overlay_of` never leaks into the effective entity).
- [x] T008 [P] [US2] Write `test_resolve_entity_overlay_empty_value_still_overrides` in
      `tests/engine/test_entity.py` (an overlay field explicitly set to `[]`/`None` overrides —
      edge case from spec.md).
- [x] T009 [US2] Extend `resolve_entity` (T005) to merge overlay frontmatter over the setting
      frontmatter (`{**setting, **overlay_fields}` excluding T002's bookkeeping fields, per
      `research.md`'s shallow-merge decision), and validate the merged result with
      `entity.validate`, raising `state.StateError` naming the entity id on a validation failure
      (FR-009).
- [x] T010 [P] [US2] Write `test_resolve_entity_body_overlay_replaces_setting_body` and
      `test_resolve_entity_body_falls_through_when_overlay_body_empty` in
      `tests/engine/test_entity.py` (FR-007).
- [x] T011 [US2] Extend `resolve_entity` (T005/T009) to resolve the body: overlay body if
      non-empty, else the setting body, using the `setting_bodies`/`overlay_bodies` parameters.

**Checkpoint**: A single-layer overlay correctly overrides named fields and falls through on the
rest, and a merge producing invalid frontmatter is rejected.

## Phase 5: User Story 3 - Overlay promotes a bystander to a nemesis (P2)

**Goal**: `resolve_entity` supports an overlay introducing fields entirely absent from the setting
entity, and the effective entity validates against its new shape, per FR-005.

**Independent Test**: Resolve a `role: bystander` entity against an overlay adding `role: nemesis`
plus a `threat` block; confirm the effective entity carries both and the setting entity dict
passed in is unmodified.

- [x] T012 [P] [US3] Write `test_resolve_entity_promotion_adds_new_fields_and_validates` in
      `tests/engine/test_entity.py`, per `quickstart.md`'s User Story 3 example and SC-003.
- [x] T013 [P] [US3] Write `test_resolve_entity_promotion_does_not_mutate_setting_dict` in
      `tests/engine/test_entity.py` (SC-004's spirit at the in-memory level — the setting
      entity's dict object passed to `resolve_entity` is unchanged after the call).
- [x] T014 [US3] Confirm (no production code change expected beyond T009's generic merge) that
      promotion works by construction — a field-introduction overlay is not a distinct code path
      from a field-override overlay in the shallow-merge model; if T012 fails, adjust T009's
      implementation rather than adding type-specific promotion logic.

**Checkpoint**: Promotion produces a schema-valid effective entity without touching the setting
entity, satisfying design/25's stated payoff for the overlay split.

## Phase 6: Dangling overlay reference (FR-008, edge case)

**Goal**: An overlay naming a setting entity id that does not exist is reported, not silently
dropped or fabricated.

- [x] T015 [P] Write `test_resolve_entity_dangling_overlay_of_raises` in
      `tests/engine/test_entity.py`: an overlay whose `overlay_of` is absent from
      `setting_entities` raises `state.StateError` naming the overlay and the missing target,
      when resolution is attempted for that id.
- [x] T016 Ensure `resolve_entity` (T005/T009) raises the FR-008 error when `entity_id` is not in
      `setting_entities` at all but *is* named by some overlay's `overlay_of` — distinguishing
      this from T004's "no such entity anywhere" case by whether an overlay claims that id.

## Phase 7: Polish

- [x] T017 [P] Run `python3 -m ruff check .` and `python3 -m ruff format --check .`; fix any
      finding in `engine/wyrd/entity.py` or `tests/engine/test_entity.py`.
- [x] T018 [P] Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_entity.py -q` and
      confirm all tests (existing #305 tests plus this feature's) pass.
- [x] T019 Update `docs/design/25-entities.md`'s "chronicle overlay" section if implementation
      surfaced any gap between the written design and what `resolve_entity` actually does
      (`CLAUDE.md`: design documents describe the present) — otherwise leave it unchanged.

## Dependencies

- Phase 1 (T001) has no dependencies.
- Phase 2 (T002) depends on Phase 1.
- Phase 3 (US1, T003-T005) depends on Phase 2.
- Phase 4 (US2, T006-T011) depends on Phase 3 (extends the same `resolve_entity` function).
- Phase 5 (US3, T012-T014) depends on Phase 4 (promotion is the generic merge exercised further).
- Phase 6 (T015-T016) depends on Phase 4 (needs the merge/validate path to raise from).
- Phase 7 (T017-T019) depends on all prior phases.

## Parallel example

Within Phase 4, T006, T007, T008, and T010 (all `[P]`, all test-writing tasks touching disjoint
test functions in the same file) can be drafted together before T009/T011 make them pass.
