# Tasks: The dangling-mechanic check

**Input**: Design documents from `/specs/028-dangling-mechanic-check/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included — the spec's own acceptance criteria (issue #59) require the check's test
suite to prove detection against fixtures, so tests are integral to Definition of Done, not
optional polish.

**Organization**: Tasks are grouped by user story from `spec.md` for independent
implementation and testing. All three stories converge on one script pair
(`tools/check_dangling_mechanics.py` + `tools/test_check_dangling_mechanics.py`), so "phase"
here means an incremental capability slice of that one pair, matching the priorities in
`spec.md`.

## Phase 1: Setup

- [ ] T001 Create `tools/check_dangling_mechanics.py` with the module docstring, `Problem(str)`
      class, and `REPO` path constant, mirroring `tools/check_docs.py`'s header shape exactly
      (per research.md's "reuse check_docs.py's script shape" decision).
- [ ] T002 Create `tools/test_check_dangling_mechanics.py` with the `TreeCase` unittest base
      class (temp dir + `write(rel, text)` helper + `problems()` accessor), copied from
      `tools/test_check_docs.py`'s pattern, importing the new module via
      `sys.path.insert(0, str(pathlib.Path(__file__).parent))`.

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: The scan/match core every user story's tests exercise. No user story can be
implemented or tested until this exists.

- [ ] T003 Implement `find_definitions(root: Path) -> list[MechanicDefinition]` in
      `tools/check_dangling_mechanics.py`: scans `design/**.md` for ATX headings, table rows
      (leading cell), and glossary-style bolded-term-plus-explanation paragraphs, per
      data-model.md's `MechanicDefinition` shape. Must skip fenced code blocks (reuse
      `check_docs.py`'s `FENCE` regex pattern) so a heading-like line inside a code sample is
      not treated as a definition.
- [ ] T004 Implement `find_references(root: Path, vocabulary: set[str]) ->
      list[MechanicReference]` in `tools/check_dangling_mechanics.py`: scans `design/**.md`
      prose/table cells (excluding fenced code blocks and inline code spans — reuse
      `check_docs.py`'s `FENCE`/`INLINE_CODE` regexes) for occurrences of any name in
      `vocabulary`, excluding the line/section that is itself that name's own definition (per
      data-model.md's validation rule).
- [ ] T005 Implement `find_problems(root: Path) -> list[Problem]` in
      `tools/check_dangling_mechanics.py`: calls `find_definitions`, builds the vocabulary set,
      calls `find_references`, and yields one `Problem` per reference whose name is not in the
      vocabulary, formatted per contracts/cli.md ("`<file>:<line>: '<name>' is referenced but
      not defined anywhere in design/`").

**Checkpoint**: `find_problems()` is callable and returns an (empty) list against an empty
temp tree — foundation ready for user story work.

## Phase 3: User Story 1 - A script catches a mechanic named before it is defined (Priority: P1)

**Goal**: Running the check against a design tree with a planted dangling reference fails and
names it; running it against a clean tree passes.

**Independent Test**: Plant one dangling reference in a two-document temp tree, call
`find_problems()`, and confirm it reports exactly that reference.

- [ ] T006 [P] [US1] In `tools/test_check_dangling_mechanics.py`, add
      `TestDanglingReference.test_reference_with_no_definition_is_caught`: a temp tree with one
      document referencing a mechanic name that no document defines; asserts `problems()`
      contains one entry naming that mechanic and file.
- [ ] T007 [P] [US1] In `tools/test_check_dangling_mechanics.py`, add
      `TestDanglingReference.test_defined_and_referenced_mechanic_is_clean`: a temp tree with
      one document defining a mechanic (heading) and a second document referencing it by name;
      asserts `problems()` is empty.
- [ ] T008 [US1] Run `python3 -m unittest tools.test_check_dangling_mechanics -v` and confirm
      T006 fails (proves the fixture actually exercises detection) before any fix, then confirm
      T003–T005's implementation makes both T006 and T007 pass.

**Checkpoint**: User Story 1 fully independently functional — the core promise of the feature
is proven end to end.

## Phase 4: User Story 2 - The check is proven against the six known historical faults (Priority: P1)

**Goal**: Each of the six historical dangling-mechanic instances, reconstructed as a minimal
fixture, fails independently when checked.

**Independent Test**: For each of the six instances, build its fixture and confirm
`find_problems()` reports it, run in isolation from the other five.

- [ ] T009 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_engine_characteristics_referenced_before_defined`: a temp
      tree reproducing the conversion-contract reference to engine characteristics with no
      definition present; asserts it fails.
- [ ] T010 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_standing_referenced_in_upkeep_before_defined`: reproduces
      the Standing-in-Upkeep instance; asserts it fails.
- [ ] T011 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_party_effective_referenced_in_danger_formula_before_defined`:
      reproduces the `party_effective`-in-danger-formula instance; asserts it fails.
- [ ] T012 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_damage_type_critical_tables_referenced_before_defined`:
      reproduces the damage-type critical tables instance; asserts it fails.
- [ ] T013 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_skill_list_referenced_before_defined`: reproduces the skill
      list instance; asserts it fails.
- [ ] T014 [P] [US2] In `tools/test_check_dangling_mechanics.py`, add
      `TestHistoricalInstances.test_wound_schema_referenced_before_defined`: reproduces the
      wound schema instance; asserts it fails.
- [ ] T015 [US2] Run the full `TestHistoricalInstances` class and confirm all six pass
      independently against T003–T005's implementation (no cross-test coupling — each builds
      its own temp tree, per T002's `TreeCase` pattern).

**Checkpoint**: Both P1 stories complete — the check both works and is proven against the
fault history that motivated it (spec SC-001).

## Phase 5: User Story 3 - A contributor runs the check on demand and understands the result (Priority: P2)

**Goal**: The check is runnable as a CLI with a clear pass/fail summary and machine-readable
mode, per contracts/cli.md.

**Independent Test**: Run the script directly against a clean tree and a tree with one planted
failure; confirm human-readable and JSON output both match contracts/cli.md's documented
shapes, and exit codes are 0/1 respectively.

- [ ] T016 [US3] Implement the `argparse` CLI (`--format {text,json}`) and `main()` in
      `tools/check_dangling_mechanics.py`, producing the text/JSON output shapes documented in
      `contracts/cli.md`, and exiting `0` on no problems / `1` otherwise — matching
      `check_docs.py`'s CLI wiring pattern.
- [ ] T017 [P] [US3] In `tools/test_check_dangling_mechanics.py`, add
      `TestCLI.test_exit_code_zero_on_clean_tree` and `TestCLI.test_exit_code_one_on_dangling_reference`
      (invoke `main()` or the module's CLI function directly against a temp tree, matching
      `check_docs.py`'s own CLI test pattern if one exists, otherwise calling `find_problems`
      and asserting the documented exit-code mapping).
- [ ] T018 [P] [US3] In `tools/test_check_dangling_mechanics.py`, add
      `TestCLI.test_code_span_reference_is_not_flagged` and
      `TestCLI.test_fenced_code_block_reference_is_not_flagged` (FR-010): a temp tree where the
      only occurrence of an undefined-elsewhere name is inside `` `inline code` `` or a fenced
      block; asserts `problems()` is empty.
- [ ] T019 [P] [US3] In `tools/test_check_dangling_mechanics.py`, add
      `TestDefinitionForms.test_table_row_definition_is_recognized` and
      `TestDefinitionForms.test_glossary_entry_definition_is_recognized` (spec edge case:
      definitions are not headings-only) — confirms T003 covers all three definition shapes.
- [ ] T020 [US3] Manually run `python3 tools/check_dangling_mechanics.py` and
      `python3 tools/check_dangling_mechanics.py --format json | python3 -m json.tool` against
      the repo's actual `design/` tree per `quickstart.md`, and record the result (pass/fail
      count) — this is the check's first real run against the live design tree, separate from
      its own unit tests.

**Checkpoint**: All three user stories complete and independently verified.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T021 [P] Add a short section to `docs/design/20-tooling.md` section 1 (or wherever the
      existing `tools/backlog.py check` / `tools/check_docs.py` guidance lives) documenting
      `tools/check_dangling_mechanics.py` as the third checked-claim script, per issue #59's
      "decide whether it runs in CI or on demand, and record why" scope item — decide on-demand
      vs. CI here and record the reasoning (research.md leaves this open per spec Assumptions).
- [ ] T022 Run `ruff check tools/check_dangling_mechanics.py tools/test_check_dangling_mechanics.py`
      and `ruff format --check` on both, and fix any findings.
- [ ] T023 Run `python3 -m unittest discover -s tools -p 'test_*.py'` (the full suite, not just
      the new module) to confirm no regression in `check_docs.py`, `backlog.py`, or any other
      existing check.
- [ ] T024 Run `python3 tools/check_docs.py` to confirm the new spec/plan/research/data-model
      files this feature added are all properly reachable/linked per this repo's own documents
      check.

## Dependencies & Execution Order

- **Setup (Phase 1)**: T001–T002, no dependencies, can run in parallel with each other.
- **Foundational (Phase 2)**: T003 → T004 → T005 (each builds on the previous function);
      blocks every user story.
- **User Story 1 (Phase 3)**: depends on Phase 2. T006/T007 parallel with each other, both
      before T008.
- **User Story 2 (Phase 4)**: depends on Phase 2 (independent of Phase 3, but Phase 3's
      passing state is what makes Phase 4's fixtures meaningful evidence — sequence after
      Phase 3 in practice, run in parallel with it only if desired). T009–T014 fully parallel
      with each other, all before T015.
- **User Story 3 (Phase 5)**: depends on Phase 2 (CLI wraps `find_problems`); T017/T018/T019
      parallel with each other after T016; T020 last (manual, needs everything).
- **Polish (Phase 6)**: depends on all user stories complete.

## Implementation Strategy

**MVP = User Story 1 + User Story 2** (both P1): the check must both work and be proven
against the six historical faults before it delivers what issue #59 actually asked for.
User Story 3 (CLI ergonomics/JSON mode) is valuable but the check is already usable via direct
Python import without it — ship P1 first if time-boxing is needed, but this feature is small
enough that all three stories are expected to land in one pass.

**Parallel opportunities**: T006/T007; all of T009–T014 (six independent fixtures, the biggest
parallel block); T017/T018/T019.
