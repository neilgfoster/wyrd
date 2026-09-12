# Tasks: Setting-Level Character Creation Data

**Input**: Design documents from `specs/146-setting-character-creation-data/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included — `spec.md`'s User Story 1 explicitly requires the validator to be tested
against both correct and deliberately-broken fixtures.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Documentation (User Story 2, P2 — but done first since US1's validator documents
what it checks against)

- [X] T001 [US2] Add `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml`, and
  `ancestries.yaml` schema sections to `docs/design/24-authoring-a-setting.md`, in the existing
  table/example style, using `data-model.md`'s Rules as source.
- [X] T002 [US2] Update `docs/design/11-character-creation.md` §4's table to link each
  requirement (Entry careers, Names, Drives, Misfortunes, Loyalties) to the schema section T001
  added, rather than restating the shape in prose.
- [X] T003 [US2] Run `python3 tools/check_docs.py` to confirm the new links resolve and no
  document went unreachable.

## Phase 2: Validator (User Story 1, P1)

- [X] T004 [US1] Write `tools/check_character_creation_data.py`: entry point taking a setting
  directory, importing `read_yaml`/`YamlError` from `check_bestiary.py` (matches `check_gear.py`'s
  existing import pattern).
- [X] T005 [US1] Implement `careers.yaml` validation inside T004: required fields, entry/
  prerequisites exclusivity, at least one entry career, dangling-prerequisite check, acyclic-graph
  check, duplicate-id check (FR-003).
- [X] T006 [US1] Implement `loyalties.yaml` validation inside T004: non-empty loyalties, unique
  ids, relation pairs reference declared loyalties, `a != b`, closed `kind` vocabulary, no
  duplicate unordered pair (FR-004).
- [X] T007 [US1] Implement `drives.yaml`/`misfortunes.yaml` validation inside T004: shared helper,
  non-empty list, unique id, non-empty text (FR-005).
- [X] T008 [US1] Implement `names.yaml` validation inside T004: non-empty cultures, unique id,
  at least one non-empty name-pool list per culture (FR-006).
- [X] T009 [US1] Implement optional `ancestries.yaml` validation inside T004: absence is not an
  error; when present, non-empty, unique id, non-empty skills (FR-007).
- [X] T010 [US1] Wire a CLI (`argparse`, `--format json` flag mirroring `check_setting.py`) and a
  summary report that lists every failure found across all files, plus a per-file OK/absent
  summary line (matches `check_bestiary.py`'s all-failures-reported behaviour).

## Phase 3: Tests (User Story 1, P1)

- [X] T011 [P] [US1] `tools/test_check_character_creation_data.py`: fixture with all six files
  correct → validator reports success, exit 0.
- [X] T012 [P] [US1] Fixture tests, one per rejected-shape class in `data-model.md`'s Rules
  sections (missing required field, unrecognised field, entry/prerequisites conflict, no entry
  career, dangling prerequisite, prerequisite cycle, duplicate career id, undeclared Loyalty in a
  relation, self-referential relation, bad relation `kind`, duplicate relation pair, empty
  drives/misfortunes/names list, duplicate id within a list, name-culture with no pools, malformed
  ancestries entry) → each reported, non-zero exit.
- [X] T013 [US1] Fixture test: `ancestries.yaml` absent entirely → accepted, not an error (FR-007,
  edge case).
- [X] T014 [US1] Fixture test: `loyalties.yaml` with one Loyalty and no `relations` key at all →
  accepted (edge case, §4).

## Phase 4: Repo-wide verification

- [X] T015 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` — both clean.
- [X] T016 Run `python3 -m pytest -q` — full suite green, including the new test file.
- [X] T017 Run `python3 tools/check_docs.py` and `python3 tools/backlog.py check` — both clean.

## Dependencies

- T001 → T002 (the table needs somewhere to link to) → T003.
- T004 is the shared scaffold T005–T010 all extend; T005–T010 can be written in any order but are
  not independently parallelizable since they share one file.
- T011–T014 depend on T004–T010 being complete.
- T015–T017 run last, after everything else.
