---
description: "Task list for Commit-back path for accepted generated content (issue #422)"
---

# Tasks: Commit-back path for accepted generated content

**Input**: Design documents from `specs/164-commit-back-path-for-generated-content/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/generation-commit.md

**Tests**: included — this feature is pure logic plus one filesystem write, so its acceptance
criteria are verified entirely by unit tests (spec.md's own User Stories are written as test
scenarios).

**Organization**: tasks are grouped by user story per spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: which user story this task belongs to

## Phase 1: Setup

- [X] T001 Create `engine/wyrd/generation_commit.py` with a module docstring naming FR-012-015 of
      specs/161 as its scope, restating this feature's own out-of-scope note (FR-001-011 in
      `generation.py`/`generation_checks.py`, FR-016-020 in the sibling generation-pipeline
      feature), per contracts/generation-commit.md.
- [X] T002 Create `tests/engine/test_generation_commit.py` with the standard `PYTHONPATH=engine`
      import of `wyrd.generation_commit`, matching `tests/engine/test_generation_checks.py`'s
      import style.

**Checkpoint**: empty module + test file exist, importable.

## Phase 2: Foundational — the additive `sources.generated` schema and shared gate

**⚠️ CRITICAL**: no user story task can be implemented until this phase is complete.

- [X] T003 In `engine/wyrd/entity.py`, extend `validate_source` to accept the additive
      `{generated: true, mode, consumed}` shape (data-model.md's `sources[]` entry) alongside the
      existing `{work, pages, licence, path}` shape, gated on `source.get("generated") is True` —
      per research.md's decision. Add a small `_GENERATED_SOURCE_FIELDS` constant next to the
      existing `_SOURCE_REQUIRED_FIELDS`/`_SOURCE_OPTIONAL_FIELDS` rather than overloading those.
- [X] T004 [P] In `tests/engine/test_entity.py`, test `validate_source` accepts a well-formed
      generated entry, rejects one missing `mode` or `consumed`, rejects an invalid `mode` value,
      rejects an entry carrying a field outside `{generated, mode, consumed}`, and leaves the
      existing authored-shape tests (already in this file) passing unchanged.
- [X] T005 In `engine/wyrd/generation_commit.py`, define `can_commit(result)` per
      contracts/generation-commit.md and spec.md FR-006: `False` for an empty `checks` list or any
      `reject` entry, `True` only when every entry's `outcome` is `pass` or `narrowed`.

**Checkpoint**: the schema and gate exist and are importable; no write path yet.

## Phase 3: User Story 2 — Declining or rejecting a result writes nothing (Priority: P1) 🎯 MVP

**Goal**: FR-005/FR-015 — a caller-declined result, or one `can_commit` reports `False` for,
produces zero filesystem writes and zero thread/threat mutation, verified directly rather than by
return value alone.

**Independent Test**: per spec.md User Story 2's Acceptance Scenarios.

**Note**: this is P1 alongside User Story 1, and is sequenced first because `accept_result`
(User Story 1) depends on the same `can_commit` gate this story's tests pin down first — writing
its tests first gives the write path in Phase 4 a settled contract to build against, matching
FR-015's own emphasis that side-effect-freedom is the more safety-critical half of this feature.

### Tests for User Story 2

- [X] T006 [P] [US2] In `tests/engine/test_generation_commit.py`, test `reject_result` always
      returns `{"committed": False, "reason": "declined"}` regardless of what `result["checks"]`
      contains (including a fully-passing result), and never touches the filesystem — assert
      against a `tempfile.TemporaryDirectory` that no file exists inside it afterward.
- [X] T007 [P] [US2] In `tests/engine/test_generation_commit.py`, test `can_commit` returns
      `False` for an empty `checks` list and `True` for a list of all-`pass`/`narrowed` entries.
- [X] T008 [P] [US2] In `tests/engine/test_generation_commit.py`, test `accept_result` called on a
      `result` whose `checks` contains a `reject` entry returns `{"committed": False, "reason":
      "checks_failed", "detail": [...]}` (the rejecting entries' `detail` text), writes no file at
      the given `path` (assert `path.exists()` is `False`), and does not mutate any dict passed as
      `live_threads`/`live_entities` (assert they are unchanged by identity/equality).
- [X] T009 [P] [US2] In `tests/engine/test_generation_commit.py`, test the same for a `result`
      whose `checks` list is empty (FR-006's "not yet evaluated" case) — `detail` names it as
      `["no checks were run"]`.

### Implementation for User Story 2

- [X] T010 [US2] In `engine/wyrd/generation_commit.py`, implement `reject_result` per
      contracts/generation-commit.md (depends on T005).

**Checkpoint**: User Story 2 fully testable independently — the no-write guarantee is proven
before the write path (User Story 1) is built on top of it.

---

## Phase 4: User Story 1 — Accepting a generated result commits it as ordinary content (Priority: P1)

**Goal**: FR-001-004 (this feature's own numbering) — a passing `GenerationResult` is written as
a `status: drafted` `arc`/`beat` entity with the correct `sources.generated` provenance, and its
declared thread/threat changes are applied through `thread.py`'s/`threat.py`'s own functions.

**Independent Test**: per spec.md User Story 1's Acceptance Scenarios.

### Tests for User Story 1

- [X] T011 [P] [US1] In `tests/engine/test_generation_commit.py`, test `accept_result` on a
      passing result writes a file at the given `path` whose frontmatter has `status: drafted`,
      the given `id`/`type`/`name`/`setting`, and a `sources` entry equal to `{"generated": True,
      "mode": <the result's mode>, "consumed": <result["consumed"]>}` — read the file back with
      `state.load_entity` and assert on the parsed frontmatter, not the raw text.
- [X] T012 [P] [US1] In `tests/engine/test_generation_commit.py`, test `accept_result` rejects
      (raises `ValueError`) an `entity_type` outside `{"arc", "beat"}`, and writes no file.
- [X] T013 [P] [US1] In `tests/engine/test_generation_commit.py`, test the written frontmatter
      passes `entity.validate` unchanged (User Story 3's "indistinguishable" claim, checked here
      at the point of writing).
- [X] T014 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `thread_updates` entry
      with `action: "new"` results in `accept_result`'s returned `"threads"` mapping containing a
      thread record equal to what `thread.new_thread` itself returns for the same arguments —
      assert equality against a direct `thread.new_thread(...)` call, not a hand-built dict, so
      the test fails if the implementation ever stops calling that function (FR-003's "identical
      function" requirement).
- [X] T015 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `thread_updates` entry
      with `action: "touch"` results in the referenced `live_threads` entry being replaced with
      exactly `thread.touch`'s own return value for the pre-existing record — same
      equality-against-direct-call technique as T014.
- [X] T016 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `thread_updates` entry
      with `action: "touch"` naming an id absent from `live_threads` raises `ValueError`.
- [X] T017 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `threat_updates` entry
      with `entity_id: None` results in the named `target_entity_id` in `live_entities` being
      replaced with exactly `threat.promote`'s own return value for the same `threat`/`objective`
      arguments — same equality-against-direct-call technique as T014.
- [X] T018 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `threat_updates` entry
      with a non-`None` `entity_id` applies `imminence_delta`/`ambient_add` directly onto the
      named `live_entities` entry's `threat` block (per `threat.py`'s own documented convention —
      research.md), leaving every other field of that entity unchanged.
- [X] T019 [P] [US1] In `tests/engine/test_generation_commit.py`, test a `threat_updates` entry
      with `entity_id: None` missing `target_entity_id`/`objective`/`imminence` raises
      `ValueError`, and one naming a `target_entity_id`/existing-thread id absent from the
      supplied mapping also raises `ValueError`.
- [X] T020 [P] [US1] In `tests/engine/test_generation_commit.py`, test `accept_result` called
      with no `thread_updates`/`threat_updates` at all (or both `None`) still writes the entity
      file successfully — the mutation calls are conditional on what the candidate declares, per
      spec.md's Edge Cases.

### Implementation for User Story 1

- [X] T021 [US1] In `engine/wyrd/generation_commit.py`, implement a private
      `_apply_thread_updates(thread_updates, live_threads)` helper calling `thread.new_thread`/
      `thread.touch` per data-model.md's `thread_updates` shape (depends on T005).
- [X] T022 [US1] In `engine/wyrd/generation_commit.py`, implement a private
      `_apply_threat_updates(threat_updates, live_entities)` helper calling `threat.promote` for
      `entity_id: None` entries and mutating `imminence`/`ambient` directly for the rest, per
      data-model.md's `threat_updates` shape and research.md's decision (depends on T005).
- [X] T023 [US1] In `engine/wyrd/generation_commit.py`, implement `accept_result` per
      contracts/generation-commit.md: gate via `can_commit`, build frontmatter via `entity.py`'s
      schema plus the `sources.generated` entry (T003), validate with `entity.validate`/
      `arc_selection.validate_entry_exit`, write via `state.save_entity`, then apply
      `_apply_thread_updates`/`_apply_threat_updates` (depends on T003, T010, T021, T022).

**Checkpoint**: both P1 user stories fully testable independently — FR-012/FR-013/FR-015 covered
end to end.

---

## Phase 5: User Story 3 — A committed generated entity plays exactly like an authored one (Priority: P2)

**Goal**: FR-007 (this feature's own numbering) — no regeneration/retcon path exists, and a
committed entity's frontmatter is otherwise ordinary.

**Independent Test**: per spec.md User Story 3's Acceptance Scenarios.

### Tests for User Story 3

- [X] T024 [P] [US3] In `tests/engine/test_generation_commit.py`, test `generation_commit.py`
      exposes no function that opens, rewrites, or re-validates an existing entity file — a
      structural test asserting the module's public names are exactly `{"can_commit",
      "accept_result", "reject_result"}` (SC-003/FR-007: no retcon path added).
- [X] T025 [P] [US3] In `tests/engine/test_generation_commit.py`, test calling `accept_result`
      twice with two different `path`s for what would otherwise be equivalent candidates produces
      two independent entity files, and that the first file's content is unchanged after the
      second call (spec.md Edge Cases: two results are never merged).

### Implementation for User Story 3

- [X] T026 [US3] No new production code — this story is a property of Phase 4's design (no
      update/rewrite path exists because none was written); confirm T024/T025 pass against the
      already-implemented `accept_result`/`reject_result`.

**Checkpoint**: all three user stories independently testable; FR-012-015 of specs/161 fully
covered.

---

## Phase 6: Polish

- [X] T027 [P] Run `python3 -m ruff check engine/wyrd/generation_commit.py engine/wyrd/entity.py
      tests/engine/test_generation_commit.py tests/engine/test_entity.py` and
      `python3 -m ruff format --check` on the same files; fix any findings.
- [X] T028 [P] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_generation_commit
      tests.engine.test_entity -v` and confirm every task above's test passes.
- [X] T029 Re-read spec.md's acceptance criteria and data-model.md's validation rules once more
      against the finished `generation_commit.py`, confirming nothing was missed (no code review
      substitute — a final self-check before opening the PR).

## Dependencies & Execution Order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (Foundational) depends on Phase 1 and blocks every user-story phase.
- Phase 3 (US2) depends on Phase 2 only (`can_commit`, `reject_result`'s own contract).
- Phase 4 (US1) depends on Phase 2 and reuses Phase 3's `can_commit`/`reject_result` findings for
  its own rejection-path tests, but its write-path implementation (T021-T023) does not require
  T010 to be merged first beyond sharing T005 — sequenced after Phase 3 in this document because
  FR-015's guarantee is the safety-critical property the write path must not violate.
- Phase 5 (US3) depends on Phase 4 (`accept_result`/`reject_result` must exist to test their
  absence of a retcon path against).
- Phase 6 depends on everything above.

## Parallel Example

```text
# After T005 lands, both P1 stories' test-writing can run together:
T006-T009 (US2 tests)  ‖  T011-T020 (US1 tests)
# Implementation is sequential within each story (T010; then T021-T023) since each story's
# functions build on the shared gate (T005) and, for US1, on each other.
```
