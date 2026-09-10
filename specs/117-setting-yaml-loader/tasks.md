# Tasks: setting.yaml loader and validator

**Input**: Design documents from `/specs/117-setting-yaml-loader/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested in the spec; `check_bestiary.py`/`check_gear.py` (this
feature's own precedent) have no dedicated pytest suite either — verified instead via the fixture
runs in `quickstart.md`. Following that precedent, no separate test-task phase is generated;
quickstart fixture verification is folded into Polish.

**Organization**: Tasks are grouped by user story from spec.md to enable independent
implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Give the engine a version to check `requires_engine` against (Research Unknown 1) —
blocking for every user story since even loading a valid `setting.yaml` (US1) needs this.

- [x] T001 Add `__version__ = "0.1.0"` to `engine/wyrd/__init__.py`

**Checkpoint**: Engine has a version constant importable as `from wyrd import __version__`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema constants and the comparator/version-compare helper every user story's
validation logic depends on.

- [x] T002 In `tools/check_setting.py`, import `read_yaml`/`YamlError` from `check_bestiary`
      (`from check_bestiary import YamlError, read_yaml`), matching `check_gear.py`'s existing
      import (Research Unknown 4)
- [x] T003 In `tools/check_setting.py`, define `REQUIRED_FIELDS`, `OPTIONAL_FIELDS` (including
      `overrides` as recognised-but-unvalidated per data-model.md's Edge case note), and
      `TONE_REQUIRED_FIELDS`/`TONE_VOCAB` closed-vocabulary constants per data-model.md
- [x] T004 In `tools/check_setting.py`, implement `_parse_requires_engine(spec: str) ->
      list[tuple[str, tuple[int,int,int]]]` parsing the closed comparator syntax from Research
      Unknown 2 (`>=`, `<`, `==`, `>`, `<=`, comma-joined AND clauses), raising a `ValueError` with
      a clear message on anything outside that syntax
- [x] T005 In `tools/check_setting.py`, implement `_engine_satisfies(requires_engine: str,
      engine_version: str) -> bool` using `_parse_requires_engine` and simple tuple comparison of
      `MAJOR.MINOR.PATCH`

**Checkpoint**: Foundational parsing/comparison helpers exist and are independently callable —
nothing yet reads a full `setting.yaml`.

## Phase 3: User Story 1 - Loading a well-formed setting.yaml (Priority: P1) 🎯 MVP

**Goal**: A setting author or engine caller can load a valid `setting.yaml` and get back its
parsed identity/version/tone data.

**Independent Test**: Load the `quickstart.md` "good setting.yaml" fixture and confirm the
returned structure matches its fields.

- [x] T006 [US1] In `tools/check_setting.py`, implement `validate(data: dict, path: str,
      engine_version: str = __import__("wyrd").__version__) -> list[str]` returning an empty
      problems list for a well-formed input, per data-model.md's Setting identity and Tone
      contract tables (T001's engine version is the default `engine_version`)
- [x] T007 [US1] In `tools/check_setting.py`'s `validate()`, add the `requires_engine`
      compatibility check using T005's `_engine_satisfies`, producing a problem string naming both
      the declared range and the running engine's `__version__` on failure (FR-004)
- [x] T008 [US1] In `tools/check_setting.py`, implement `load_setting(path: pathlib.Path) -> dict`
      that runs `read_yaml`, then `validate()`, and returns the parsed dict on success or raises
      `YamlError`-style exception carrying every problem string on failure (FR-001, FR-005 —
      YAML-parse failures from `read_yaml` propagate as-is, matching `check_bestiary.py`'s
      pattern)

**Checkpoint**: A valid `setting.yaml` loads and returns structured identity/version/tone data;
an engine-incompatible one is rejected.

## Phase 4: User Story 2 - Rejecting a malformed setting.yaml (Priority: P1)

**Goal**: Every required-field, tone-vocabulary, or unrecognised-field problem is reported by
name, and every problem is reported at once (not just the first).

**Independent Test**: Run `validate()` against each of `quickstart.md`'s bad fixtures (missing
field, bad tone value, unrecognised field) and confirm each specific problem is named; run it
against a fixture combining two problems and confirm both appear.

- [x] T009 [US2] In `tools/check_setting.py`'s `validate()`, add missing-required-top-level-field
      checks (`name`, `title`, `line`, `requires_engine`, `version`, `description`, `tone`), each
      producing a problem string naming the specific field (FR-002)
- [x] T010 [US2] In `tools/check_setting.py`'s `validate()`, add the unrecognised-top-level-field
      check against `REQUIRED_FIELDS | OPTIONAL_FIELDS` from T003, producing a problem string
      naming the field — mirroring `check_bestiary.py`'s unrecognised-field rejection, but with
      `overrides` excluded per data-model.md's Edge case note
- [x] T011 [US2] In `tools/check_setting.py`'s `validate()`, add tone-block validation: missing
      required tone key, and a tone value outside its closed vocabulary, each producing a problem
      string naming the key and its allowed values (FR-003)
- [x] T012 [US2] Confirm (by inspection/manual run, not a new function) that `validate()` collects
      every problem into one list rather than returning after the first — `check_bestiary.py`'s
      stated design already requires this pattern; this task is verifying `validate()`'s control
      flow does not short-circuit

**Checkpoint**: Every documented failure mode (missing field, bad tone value, unrecognised field,
incompatible engine version, malformed YAML) is caught and named; multiple simultaneous problems
are all reported.

## Phase 5: User Story 3 - Running the validator as a standalone check (Priority: P2)

**Goal**: A setting author can validate a `setting.yaml` from the command line.

**Independent Test**: Run `python3 tools/check_setting.py <path>` against a known-good and a
known-bad file and check exit code + printed message.

- [x] T013 [US3] In `tools/check_setting.py`, add the `argparse`-based CLI entry point (mirroring
      `check_bestiary.py`'s `Usage:` docstring shape: `python3 tools/check_setting.py <path> [...]`
      and `--format json`), calling `load_setting`/`validate` per path, printing each problem, and
      exiting non-zero if any file had problems (FR-007)
- [x] T014 [US3] Add a module docstring to `tools/check_setting.py` (matching
      `check_bestiary.py`'s style: what it validates, the failure classes, `Usage:`) documenting
      it the same way `check_bestiary.py` is documented, per FR-007's "documented the same way"
      requirement

**Checkpoint**: `tools/check_setting.py` is runnable standalone exactly like
`check_bestiary.py`/`check_gear.py`.

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T015 [P] Run every scenario in `specs/117-setting-yaml-loader/quickstart.md` by hand against
      the finished script and confirm each expected outcome
- [x] T016 [P] `python3 -m ruff check tools/check_setting.py engine/wyrd/__init__.py && python3 -m
      ruff format --check tools/check_setting.py engine/wyrd/__init__.py`
- [x] T017 Add a one-line cross-reference to `tools/check_setting.py` in
      `docs/design/24-authoring-a-setting.md`'s `setting.yaml` section, matching how
      `check_bestiary.py`/`check_gear.py` are already referenced there
- [x] T018 Run `python3 tools/check_docs.py` to confirm the doc edit in T017 didn't break
      reachability/link checks

## Dependencies & Execution Order

- **Setup (Phase 1)**: T001, no dependencies — blocks everything.
- **Foundational (Phase 2)**: T002-T005 depend on T001 (T005 needs `__version__` to exist) —
  blocks all user stories.
- **User Story 1 (Phase 3)**: T006-T008, depend on Phase 2. T006 blocks T007, T007 blocks T008
  (each builds directly on the last).
- **User Story 2 (Phase 4)**: T009-T012, depend on T006 (all extend the same `validate()`
  function) — independently testable once T006-T008 exist, but implemented after US1 since it
  adds to the same function rather than a separate one.
- **User Story 3 (Phase 5)**: T013-T014, depend on T008 (needs `load_setting`) — independent of
  Phase 4's specific problem-string wording, so could run in parallel with Phase 4 if desired, but
  ordered after both here since the CLI's `--format json` output should reflect Phase 4's finished
  problem set.
- **Polish (Phase 6)**: T015-T016 depend on all of Phase 3-5; T017 depends on nothing but is
  ordered last for narrative flow; T018 depends on T017.

## Parallel Execution Examples

- T004 and T003 touch the same file (`tools/check_setting.py`) sequentially — not parallel despite
  being in the same phase, since both write to one new file under active construction.
- T015 and T016 are `[P]` — independent verification passes (manual fixture run vs. ruff) that
  read the finished file without modifying it.

## Implementation Strategy

**MVP = User Story 1 (Phase 3)**: a valid `setting.yaml` loads and its `requires_engine` is
checked. This alone is independently testable and delivers the core loader FR-001/FR-004 promise.

**Incremental delivery**: Phase 3 (MVP) → Phase 4 (rejection quality, both P1, deliver together
since #316 and any chronicle-bootstrap caller need both to trust the loader) → Phase 5 (CLI
convenience, P2) → Phase 6 (polish).
