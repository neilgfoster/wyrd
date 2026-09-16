# Tasks: Proposals survive across separate CLI invocations

**Input**: Design documents from `/specs/159-persist-open-proposals/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Persistence primitives

- [X] T001 Add `DEFAULT_PROPOSALS_DIR`, `_proposal_path`, `_new_proposal_id`,
      `_read_open_proposal`, `_write_open_proposal` to `engine/wyrd/resolution.py`, reusing
      `state.write_text_atomic` for the write (research.md Decision 1/2).
- [X] T002 Remove `_proposal_ids`/`_open_proposals` (the in-process store) entirely
      (research.md Decision 3).

## Phase 2: Wire propose/propose_batch/reroll/commit/discard onto the file store

- [X] T003 `propose_batch`: accept `proposals_dir` keyword (default
      `DEFAULT_PROPOSALS_DIR`), mint via `_new_proposal_id`, persist via `_write_open_proposal`.
- [X] T004 `propose`: thread `proposals_dir` through to its `propose_batch` call.
- [X] T005 `reroll`: accept `proposals_dir`, read via `_read_open_proposal`, persist the revised
      proposal via `_write_open_proposal` after merging.
- [X] T006 `_pop_open_proposal`: accept `proposals_dir`, read then `unlink()` the file --
      deleting it *is* invalidating the id (research.md Decision 1).
- [X] T007 `commit`/`discard`: accept `proposals_dir`, thread through to `_pop_open_proposal`.
- [X] T008 Update every touched function's docstring to describe the new persistence and drop
      now-false "writes nothing"/"in-memory" claims.

## Phase 3: Tests

- [X] T009 [P] `tests/engine/test_resolution.py`: add `CrossProcessProposalPersistenceTest`,
      spawning `python3 -m wyrd.client propose`/`commit`/`discard` as genuinely separate
      `subprocess.run` invocations -- the exact class of bug this feature fixes (FR-001/FR-002).
- [X] T010 Fix `PassiveValidationCommitTest._stage`, the one test helper that poked
      `_open_proposals`/`_proposal_ids` directly, to use `_new_proposal_id`/
      `_write_open_proposal` instead.
- [X] T011 [P] Add `setUpModule`/`tearDownModule` cwd isolation to `test_resolution.py` and
      `test_combat.py` (module-scoped tmpdir), and per-class `chdir` to the specific test
      classes in `test_client.py`, `test_chronicle.py` and `test_integration.py` that call
      `propose`/`commit`/`discard`/`reroll` directly -- without this, every such test would
      stage a real (if orphaned) proposal file under this repo's own working directory when the
      suite runs, rather than under Wyrd tests where it was invisible.

## Phase 4: Validation

- [X] T012 Full suite green (`PYTHONPATH=engine python3 -m pytest -q`), `ruff check`/`ruff
      format --check` clean repo-wide.
