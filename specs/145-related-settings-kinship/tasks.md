# Tasks: Related settings — shared worlds and kindred tone

- [ ] **T001** [US1] Add the `relations:` schema to `settings.yaml` (a comment block describing
      `a`, `b`, `kind` and their closed vocabulary, matching the existing header comment style),
      retire the `group:` field, and rewrite every existing `group:`-bearing entry
      (`wh40k-*`, `maelstrom-*`) as `same-world` entries under `relations:` (FR-001, data-model.md).
- [ ] **T002** [US1] Extend `tools/check_settings_catalogue.py`'s restricted-subset parser to read
      the new `relations:` list (flat mappings, same style as `settings:`) (FR-001, FR-002).
- [ ] **T003** [US1] Add validation: every `a`/`b` names an existing setting id, reporting the
      unknown id by name on failure (FR-004, SC-003).
- [ ] **T004** [US1] Add validation: `a != b` for every relation (FR-004, Edge Cases).
- [ ] **T005** [US2] Add validation: the unordered pair `{a, b}` appears at most once across
      `relations:` regardless of field order, catching both an exact duplicate and a
      swapped-fields duplicate (FR-004, symmetry).
- [ ] **T006** [US2] Add validation: the unordered pair `{a, b}` is never declared under both
      `kind` values (FR-002, User Story 2 Scenario 2).
- [ ] **T007** [US1] Add validation: a relation naming a setting id no longer present in
      `settings:` fails (Edge Cases: deleted/renamed setting).
- [ ] **T008** [US3] Add the "Related settings" section to
      `docs/design/24-authoring-a-setting.md`: the two relation kinds, what each licenses when
      borrowing (as-is for same-world; mechanical shape only, reskinned, for kindred-tone), the
      `borrowed: {from_setting, from_entity, relation, on}` stamp alongside the existing
      `converted: {rules, on}` stamp, and the rule that an entity carries at most one of the two
      (FR-005, FR-006, FR-007, data-model.md).
- [ ] **T009** [US3] Add a line to `docs/design/24-authoring-a-setting.md` (or the relevant ADR
      cross-reference) stating explicitly why kinship is author-asserted rather than derived from
      the tone contract, so the reasoning survives next to the mechanism it justifies (FR-003).
- [ ] **T010** Run `python3 tools/check_settings_catalogue.py` against the updated
      `settings.yaml` and confirm it passes cleanly with the new validations in place, and that a
      hand-crafted bad fixture (unknown id, self-relation, duplicate pair, dual-kind pair) is
      caught with a specific, named error for each case (SC-001, SC-003).
- [ ] **T011** Run `python3 tools/check_docs.py`; confirm the new design section is reachable and
      no dead link is introduced.
- [ ] **T012** Run `python3 -m pytest -q`, `python3 -m ruff check .`, and
      `python3 -m ruff format --check .`; confirm no regression.

## Dependencies

T001 (schema in `settings.yaml`) blocks T002-T007 (the checker needs the schema to validate
against) and T008-T009 (the design doc describes the schema T001 defines). T002 blocks
T003-T007 (each validation needs the parser extension in place first). T010 depends on
T001-T007 together (validates the finished checker against the finished catalogue). T011-T012
run last, as verification over the whole change.

## Implementation strategy

MVP is User Story 1 plus its supporting validation (T001-T004, T007): the schema exists, is
parsed, and the two structural failure modes named directly in User Story 1's acceptance
scenarios (unknown id, self-relation) are caught. User Story 2's dual-kind/duplicate checks
(T005-T006) and User Story 3's borrow-semantics documentation (T008-T009) build on that same
schema and can land in either order relative to each other, but both need T001-T002 first.
