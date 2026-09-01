# Tasks: Character entity schema and validator

**Input**: Design documents from `/specs/079-character-entity-schema/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, same rationale as #221-#224.

**Organization**: US1 (entity round-trip) is foundational — US2 (wound validation) is built on
top of it, since validation runs during load.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Extends `engine/wyrd/state.py`/`rules.py`; adds `engine/wyrd/character.py` (new file).

---

## Phase 1: Setup

None needed beyond what #221-#224 already provide.

---

## Phase 2: Tests (write first, confirm they fail)

- [x] T001 [P] [US1] Add to `tests/engine/test_state.py`: `parse_entity(text)` splits frontmatter
      and body correctly for a file with `---\n<yaml>\n---\n<body>`; a body containing further
      `---` lines is preserved as part of the body, not re-split; `dump_entity(frontmatter,
      body)` round-trips through `parse_entity` exactly
- [x] T002 [P] [US1] Add to `tests/engine/test_state.py`: `dump_yaml`/`parse_yaml` round-trip a
      value containing a list of mappings (e.g. `wounds`-shaped data with nested `effect` dicts)
      exactly, and a list of plain scalars still round-trips as before (no regression)
- [x] T003 [US1] Create `tests/engine/test_character.py`: a full player-character frontmatter
      populated with every field named in data-model.md round-trips through
      `character.save`/`character.load` with zero field discrepancies (SC-001); the loaded
      entity's body text is preserved unchanged
- [x] T004 [US2] Add to `tests/engine/test_character.py`: a wound with `effect: {damage: 5}` is
      rejected on load with an error naming the wound and the invalid key (FR-003); a wound with
      `effect: {skill: -10}` and no `bears_on` is rejected (FR-004); the same effect with
      `bears_on` set loads successfully; a `stamina_max`/`dread` effect with no `bears_on` loads
      successfully (FR-004's "not required" case); a `recurring: true` wound with a non-null
      `closed` is rejected (FR-005) — six cases total (SC-002)
- [x] T005 [US2] Add to `tests/engine/test_character.py`: `active_wound_effects` on a mixed list
      of one open, one closed (non-recurring), and one recurring wound returns exactly the open
      and recurring wounds' effects, excluding the closed one (SC-003); the closed wound is still
      present in the original `wounds` list passed in (FR-007, checked on the input, not
      mutated)
- [x] T006 [P] Add to `tests/engine/test_rules.py`: `rules.SKILL_OPEN_VALUE == 25`,
      `rules.SKILL_ADVANCE_STEP == 5` (SC-004)
- [x] T007 [P] Add to `tests/engine/test_verbs.py`: `verbs.character_save`/`character_load`
      round-trip via a temp path; `verbs.skill_scale()` returns the documented shape
- [x] T008 [P] Add to `tests/engine/test_client.py`: `describe --name character-save`/
      `character-load`/`skill-scale` match contracts/cli.md; `character-save`/`character-load`
      round-trip via the CLI; an invalid wound is a structured error via the CLI; `skill-scale`
      returns the documented values

---

## Phase 3: Implementation

- [x] T009 [US1] Implement `parse_entity(text: str) -> tuple[dict, str]` and
      `dump_entity(frontmatter: dict, body: str) -> str` in `engine/wyrd/state.py`: split on the
      first two `---`-only lines; parse the frontmatter block with the existing `parse_yaml`;
      return the remaining text as `body`, unchanged
- [x] T010 [US1] Extend `_dump_block`/`_parse_block` in `state.py` to support a list item that is
      a non-empty mapping (first key inline after `- `, remaining keys indented two further),
      per research.md's ported pattern; verify no regression on the existing scalar-list and
      nested-dict-value cases already covered by #221-#224's tests
- [x] T011 [US1] Create `engine/wyrd/character.py`: `PLAYER_CHARACTER_FIELDS` (the field list
      from data-model.md, for documentation/reference — not itself an enforced allow-list in
      this feature, per spec.md's scope), `load(path) -> tuple[dict, str]` (frontmatter, body) —
      calls `state`'s file read + `parse_entity`, then `validate_character`, `save(frontmatter,
      body, path)` — validates, then writes via `state`'s atomic write + `dump_entity`
- [x] T012 [US2] Implement `validate_wound(wound: dict) -> None` in `character.py`: raise
      `state.StateError` naming the wound's `id` for each violated rule (FR-003, FR-004, FR-005),
      checked in that order
- [x] T013 [US2] Implement `validate_character(frontmatter: dict) -> None` in `character.py`:
      call `validate_wound` for every entry in `frontmatter.get("wounds", [])` — depends on T012
- [x] T014 [US2] Implement `active_wound_effects(wounds: list[dict]) -> list[dict]` in
      `character.py`: filter to `closed is None`, return `{"wound_id", "effect", "bears_on"}` per
      data-model.md (omit `bears_on` key entirely when absent, rather than `null`, to match
      contracts/cli.md's shape)
- [x] T015 [P] Add `SKILL_OPEN_VALUE = 25`, `SKILL_ADVANCE_STEP = 5` to `engine/wyrd/rules.py`,
      next to the existing `UNTRAINED_SKILL`
- [x] T016 [P] Add `character-save`, `character-load`, `skill-scale` entries to `TOOLS` in
      `engine/wyrd/catalog.py`, matching contracts/cli.md
- [x] T017 [P] Implement `character_save`, `character_load`, `skill_scale` verb wrappers in
      `engine/wyrd/verbs.py` — `skill_scale` returns `rules.SKILL_OPEN_VALUE`,
      `rules.SKILL_ADVANCE_STEP`, `rules.UNTRAINED_SKILL` in one structured result
- [x] T018 [P] Add `character-save --path --frontmatter-json --body`, `character-load --path`,
      and `skill-scale` subcommands to `engine/wyrd/client.py`; wrap `state.StateError` from an
      invalid wound into the structured `{"error": ...}` shape, per contracts/cli.md
- [x] T019 Add `to_text` cases for the three new verbs in `engine/wyrd/render.py`

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes.

---

## Phase 4: Polish

- [x] T020 Run every step of `specs/079-character-entity-schema/quickstart.md` by hand and
      confirm
- [x] T021 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/`, fix anything flagged

---

## Dependencies & Execution Order

- Phase 2: T001, T002 (state.py extensions' tests) are independent of each other. T003 needs
  T001/T002's target functions to exist conceptually to call meaningfully, same as any
  pre-implementation test. T004/T005 depend on T003's character round-trip existing to build on.
  T006-T008 are independent of the character-specific chain.
- Phase 3: T009 and T010 are independent extensions to `state.py`. T011 depends on both (uses
  `parse_entity`/`dump_entity` and the extended reader/writer). T012 before T013 (T013 calls
  T012). T014 is independent of T012/T013. T015-T019 can proceed in parallel once T011-T014
  exist.
- Phase 4 depends on Phase 3.

## Implementation Strategy

Single increment. US1 (the entity format and round-trip, including the list-of-mapping fix) is
the genuine prerequisite everything else sits on; US2 (wound validation) is the feature's
distinguishing logic. Not split into separate PRs since US2 cannot be demonstrated without US1's
round-trip already working.
