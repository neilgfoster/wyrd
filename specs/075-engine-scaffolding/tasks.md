# Tasks: Engine scaffolding

**Input**: Design documents from `/specs/075-engine-scaffolding/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included — the spec's acceptance scenarios and success criteria (SC-001..SC-004) are
only meaningfully verified by automated tests (determinism across repeated calls, atomicity under
a simulated kill), not by manual inspection.

**Organization**: Tasks are grouped by user story per spec.md's priorities (P1 dice, P2 state,
P3 CLI). US3 (the CLI) is the wiring layer that exposes US1's and US2's work through the `roll`
verb per contracts/cli.md, so it depends on both — noted explicitly below since this differs
from the fully-independent case the template describes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project, per plan.md: `engine/wyrd/` for source, `tests/engine/` for tests.

---

## Phase 1: Setup

**Purpose**: Project initialization

- [x] T001 Create `engine/wyrd/__init__.py` (empty package marker) and `tests/engine/__init__.py`
- [x] T002 [P] Create empty `engine/wyrd/render.py` with a `to_json(obj: dict) -> str` and
      `to_text(obj: dict) -> str` stub pair (json.dumps with sorted keys; text stub raises
      NotImplementedError until US3 fills it in)

**Checkpoint**: Package importable (`python3 -c "import wyrd"` from `engine/`), nothing else yet.

---

## Phase 2: Foundational

No cross-story blocking infrastructure beyond Phase 1 — `rules.py` (US1) and `state.py` (US2)
share no code and can be built independently and in parallel. Skipping a separate Foundational
phase; Phase 1's package skeleton is the only shared prerequisite.

---

## Phase 3: User Story 1 - Deterministic dice (Priority: P1) 🎯 MVP

**Goal**: A pure, seedable d100 roll function — the code-level half of principle 1 ("the dice
bind the GM").

**Independent Test**: Import `rules.roll_d100` directly and call it with a fixed seed twice,
confirming identical results — no CLI or state layer needed (spec User Story 1's own test).

### Tests for User Story 1

- [x] T003 [P] [US1] Write `tests/engine/test_rules.py`: same seed → identical result across 100
      calls (SC-001); no seed → not all-identical across repeated calls (FR-003); `sides=0` and
      `sides=-5` each raise `ValueError` (FR-004); result always in `[1, sides]` for `sides=100`
      and `sides=6` (FR-001, data-model.md's Roll result validation)

### Implementation for User Story 1

- [x] T004 [US1] Implement `roll_d100(sides: int = 100, seed: int | None = None) -> int` in
      `engine/wyrd/rules.py`: validate `sides` is a positive int (raise `ValueError` with a clear
      message otherwise, FR-004); use a locally-seeded `random.Random(seed)` instance (never the
      module-level global, per research.md) so one call's seed cannot affect another's result;
      return an int in `[1, sides]`

**Checkpoint**: `python3 -m unittest tests.engine.test_rules` passes. User Story 1 is complete
and independently verified.

---

## Phase 4: User Story 2 - Persist-before-narrate state (Priority: P2)

**Goal**: Atomic save/load for a minimal chronicle state shape — the code-level half of
principle 2.

**Independent Test**: Call `state.save(...)` then `state.load()` and confirm a round trip,
independent of any dice/CLI code (spec User Story 2's own test).

### Tests for User Story 2

- [x] T005 [P] [US2] Write `tests/engine/test_state.py`: save-then-load round trip recovers an
      identical value for every field in data-model.md's Chronicle state shape (SC-002); loading
      before any save creates the file rather than failing (edge case in spec.md); loading a
      hand-corrupted file raises a clear, specific error rather than silently defaulting
      (FR-008); a simulated interrupted write (mock `os.replace` to raise partway, or write a
      truncated temp file directly and assert the *target* file is untouched) leaves the prior
      valid state intact, never a partial file (SC-003, FR-007)

### Implementation for User Story 2

- [x] T006 [US2] Implement `save(state: dict, path: Path) -> None` in `engine/wyrd/state.py`:
      serialize with the restricted internal reader/writer per `docs/design/02-architecture.md`
      (no third-party YAML dependency, per `docs/design/27-tooling.md` section 2 and research.md);
      write to a temp file in the same directory, then `os.replace()` onto `path` (atomic,
      FR-007)
- [x] T007 [US2] Implement `load(path: Path) -> dict` in `engine/wyrd/state.py`: return the
      minimal Chronicle state shape from data-model.md (`schema_version`, `last_roll`); if `path`
      does not exist, return the default empty shape rather than failing (edge case in spec.md);
      if the file exists but fails to parse, raise a clear, specific exception naming the file
      and the parse failure (FR-008)

**Checkpoint**: `python3 -m unittest tests.engine.test_state` passes. User Story 2 is complete
and independently verified.

---

## Phase 5: User Story 3 - CLI entry point (Priority: P3)

**Goal**: A catalog-driven `wyrd` CLI (per `docs/design/27-tooling.md` section 3 and
contracts/cli.md) exposing `describe` and `roll`, wiring US1's dice and US2's state together
through the `roll` verb.

**Depends on**: US1 (T004) and US2 (T006, T007) — the `roll` verb calls both.

**Independent Test**: Run `python3 -m wyrd.client describe` with no other setup and confirm it
exits successfully with the catalog as JSON (spec User Story 3's own test) — this part needs
neither US1 nor US2 internals, only the catalog data structure itself.

### Tests for User Story 3

- [x] T008 [P] [US3] Write `tests/engine/test_client.py`: `describe` (no args) returns the full
      `TOOLS` catalog as JSON containing a `roll` entry matching contracts/cli.md's shape;
      `describe --name roll` returns just that entry; `describe --name bogus` returns the
      structured `{"error": {...}}` shape from contracts/cli.md, not a traceback, and exits 0
      (contracts/cli.md's exit-code contract)
- [x] T009 [P] [US3] Write `tests/engine/test_verbs.py`: `verbs.roll(sides=100, seed=1)` returns
      the Roll result shape from data-model.md and writes `last_roll` to state (`state_written:
      true`, matching the same value `state.load()` then returns) — the end-to-end wiring
      contracts/cli.md's `roll` output depends on

### Implementation for User Story 3

- [x] T010 [US3] Define the `TOOLS` catalog in `engine/wyrd/catalog.py`: one entry for `roll`
      with `name`, `description`, `annotations` (`readOnlyHint: false`, `destructiveHint: false`,
      `idempotentHint: false`, `openWorldHint: false`), and a flat `inputSchema` (`sides`
      optional int ≥1 default 100, `seed` optional int) — exactly the shape in contracts/cli.md's
      `describe` example. Pure data, per `27-tooling.md` section 3.
- [x] T011 [US3] Implement `roll(sides: int = 100, seed: int | None = None) -> dict` in
      `engine/wyrd/verbs.py`: call `rules.roll_d100`, then `state.save` to persist `last_roll`
      *before* returning (principle 2 — the persist happens inside this call, not after), and
      return the Roll result shape from data-model.md with `state_written: true`
- [x] T012 [US3] Implement `engine/wyrd/client.py`: argparse dispatch built from `catalog.TOOLS`
      (iterate the catalog to build subcommands, per `27-tooling.md` section 3's "built FROM the
      catalog" requirement — no hardcoded second list of verb names); a `describe` verb (whole
      catalog, or `--name X` for one entry, or the structured error from contracts/cli.md for an
      unknown name); a `roll` verb wired to `verbs.roll`, with `--sides`/`--seed`/`--format
      json|text`; a `ValueError` from `verbs.roll` (bad `--sides`) is caught and reported as the
      structured `{"error": {...}}` shape rather than propagating as a traceback (exit code 0
      per contracts/cli.md); an unhandled/unexpected failure (e.g. `load()`'s parse error from
      T007) propagates and exits non-zero
- [x] T013 [US3] Fill in `render.to_text` in `engine/wyrd/render.py`: a short human-readable line
      per contracts/cli.md (e.g. `d100: 42` for a roll result), used when `client.py` is invoked
      with `--format text`

**Checkpoint**: `python3 -m unittest tests.engine.test_client tests.engine.test_verbs` passes.
All three user stories are independently verified and wired together.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T014 Run every step of `specs/075-engine-scaffolding/quickstart.md` by hand from the repo
      root and confirm each expected result matches
- [ ] T015 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/` if `ruff` is configured for this repo (check `pyproject.toml`/`ruff.toml`
      first); if no ruff config exists, skip this task rather than introducing new tooling as a
      side effect of this feature — **skipped**: no ruff config exists in this repo
- [x] T016 Update `docs/design/02-architecture.md`'s `engine/` tree comment
      ("fully specified, not yet built (#90)") to reflect that `engine/wyrd/{catalog,client,
      verbs,rules,state,render}.py` now exist, once this PR merges — per CLAUDE.md's rule that
      design documents describe the present

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Skipped — no shared blocking work beyond Phase 1
- **US1 (Phase 3)** and **US2 (Phase 4)**: Both depend only on Phase 1; independent of each other,
  can proceed in parallel
- **US3 (Phase 5)**: Depends on US1 (T004) and US2 (T006, T007) completing — its `roll` verb
  calls both directly. This is the one place this feature's stories are not fully independent,
  noted explicitly since the task template's default assumption is that they are.
- **Polish (Phase 6)**: Depends on all three user stories

### Parallel Opportunities

- T003 (US1 tests) and T005 (US2 tests) can be written in parallel — different files, no shared
  code
- T004 (US1 impl) and T006+T007 (US2 impl) can proceed in parallel once their own tests exist
- T008 and T009 (US3 tests) can be written in parallel
- T015 can run alongside T014/T016

---

## Parallel Example: Phase 3 + Phase 4 together

```bash
# Once Phase 1 is done, US1 and US2 can proceed at the same time:
Task: "Write tests/engine/test_rules.py per T003"
Task: "Write tests/engine/test_state.py per T005"
# ...then, in parallel again:
Task: "Implement engine/wyrd/rules.py per T004"
Task: "Implement engine/wyrd/state.py per T006+T007"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 (Setup)
2. Phase 3 (US1 — dice)
3. **STOP and VALIDATE**: `python3 -m unittest tests.engine.test_rules`

This alone delivers principle 1's code-level guarantee and is independently demonstrable, even
before state or the CLI exist.

### Incremental delivery

1. Setup → US1 (dice) → validate → US2 (state) → validate → US3 (CLI, wires both) → validate →
   Polish
2. Each checkpoint above is a complete, independently-testable increment per spec.md's own
   per-story Independent Test criteria

---

## Notes

- [P] tasks touch different files with no completed-task dependency between them
- Every implementation task's file path is exact, per plan.md's Project Structure
- Write each story's tests before its implementation and confirm they fail first
- Commit after each checkpoint
