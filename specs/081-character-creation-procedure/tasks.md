# Tasks: Character creation procedure

**Input**: Design documents from `/specs/081-character-creation-procedure/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, same rationale as #221-#231.

**Organization**: A single orchestrating function — US1 (fixed values), US2 (allocation
composition), and US3 (fiction pass-through) are all properties of the one `create_character`
call, not separately shippable increments.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Adds `engine/wyrd/creation.py` (new file); extends `catalog.py`/`verbs.py`/`client.py`.

---

## Phase 1: Setup

None needed beyond what #221-#231 already provide.

---

## Phase 2: Tests (write first, confirm they fail)

- [x] T001 Create `tests/engine/test_creation.py`: for each of `mortality` `"low"`,
      `"standard"`, `"high"`, a created character has `fate`/`fortune` matching 2/3/4
      respectively, with `fortune.current == fate.current` always (SC-001)
- [x] T002 Add to `tests/engine/test_creation.py`: across at least 3 differently-shaped valid
      inputs, `stamina` is always `{current: 6, max: 6}` and `taint`/`trauma`/`strain`/`dread`
      are always `0`, `resolve` is `{current: 0}` (SC-002)
- [x] T003 Add to `tests/engine/test_creation.py`: a valid career + 8-advance allocation produces
      a `skills` map exactly matching what `career.validate_allocation` returns for the same
      inputs, for all four worked spreads from #231 (SC-004)
- [x] T004 Add to `tests/engine/test_creation.py`: an allocation `career.validate_allocation`
      would reject (reuse #231's 8 rejection cases, at least the "wrong total" and "cap
      exceeded" ones) causes `create_character` to report `valid: false` with the same error,
      and writes **no file** at the given path (SC-003) — assert the path does not exist
      afterward
- [x] T005 Add to `tests/engine/test_creation.py`: `name`, `loyalty`, `drives`, `misfortune`,
      `fault_line` all appear in the produced frontmatter exactly as supplied; `career_history`,
      `wounds`, `holdings`, `allegiances`, `marks`, `transformations`, `afflictions` are all `[]`;
      `advances_unspent` is `0`; `hidden_threshold`/`pending_omen` are `null`; `reputation` is
      `{score: 0, label: null}`
- [x] T006 Add to `tests/engine/test_creation.py`: a created character round-trips through
      `character.save`/`character.load` (called directly, confirming creation's own save used
      the same underlying mechanism) with zero field discrepancies (SC-005)
- [x] T007 [P] Add to `tests/engine/test_verbs.py`: `verbs.create_character(...)` returns the
      documented shape for both an accepted and a rejected allocation
- [x] T008 [P] Add to `tests/engine/test_client.py`: `describe --name create-character` matches
      contracts/cli.md; a full valid creation via the CLI produces the documented JSON and a
      real file on disk (loadable via `character-load`); a rejected allocation via the CLI
      writes no file

---

## Phase 3: Implementation

- [x] T009 Create `engine/wyrd/creation.py`: `MORTALITY_FATE = {"low": 2, "standard": 3, "high":
      4}`, `STARTING_STAMINA = 6`
- [x] T010 Implement `create_character(path, name, career, actions, loyalty, mortality,
      fault_line, ancestry=None, drives=None, misfortune=None, body="") -> dict` in
      `creation.py`: call `career.validate_allocation(actions, career, ancestry)` first; if
      invalid, return `{"valid": False, "error": ...}` without touching `path` at all; otherwise
      build the full frontmatter per data-model.md (fixed values + validated skills + supplied
      fiction fields, all other fields at their documented empty/zero state), call
      `character.save(frontmatter, body, path)`, and return `{"valid": True, "path": str(path),
      "frontmatter": frontmatter}` — depends on T009
- [x] T011 [P] Add `create-character` to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md
- [x] T012 [P] Implement the `create_character` verb wrapper in `engine/wyrd/verbs.py`
- [x] T013 [P] Add the `create-character` subcommand to `engine/wyrd/client.py`: parse
      `--career-json`/`--ancestry-json`/`--actions-json`/`--drives-json` as JSON (malformed JSON
      propagates uncaught, per #231's precedent); `--misfortune`/`--ancestry-json`/
      `--drives-json` optional
- [x] T014 Add a `to_text` case for `create-character` results in `engine/wyrd/render.py`

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes.

---

## Phase 4: Polish

- [x] T015 Run every step of `specs/081-character-creation-procedure/quickstart.md` by hand and
      confirm, including inspecting the actual on-disk file after both a valid and a rejected
      creation
- [x] T016 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/`, fix anything flagged
- [x] T017 With this PR, #210 (Character creation)'s two children (#231, #232) are both closing —
      not a code task, but worth checking after merge whether #210 itself should close

---

## Dependencies & Execution Order

- Phase 2's T001-T006 build the same file sequentially. T007/T008 are independent of that chain.
- Phase 3: T009 before T010. T011-T014 depend on T010 existing to wire up, independent of each
  other.
- Phase 4 depends on Phase 3.

## Implementation Strategy

Single increment — one orchestrating function, tested against the fixed values, the allocation
composition (both accept and reject paths), and the fiction pass-through before wiring the CLI.
