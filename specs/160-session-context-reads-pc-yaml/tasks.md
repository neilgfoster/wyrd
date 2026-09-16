# Tasks: Session-context resolves the player character from pc.yaml

**Input**: Design documents from `specs/160-session-context-reads-pc-yaml/`

**Tests**: Included — the issue's own Definition of Done requires an automated regression test.

**Organization**: This feature is small enough (one function change) that both user stories
land together rather than as separately-shippable increments; the phase split below still keeps
the read-path change and its two call-site consequences (session-context vs. get/find/party)
traceable to the user story each verifies.

## Phase 1: Setup

No setup needed — this feature adds no new dependency, module, or infrastructure. Skipped.

## Phase 2: Foundational

- [ ] T001 In `engine/wyrd/verbs.py`, change `load_effective_entities` to also load
  `<chronicle_dir>/pc.yaml` via `entity.load` when that file exists, merging its frontmatter into
  the returned dict keyed by its own `id` (after the existing `resolution._load_chronicle_entities`
  call). No change to the function's signature or return type.

**Checkpoint**: the shared entity set both user stories depend on now includes `pc.yaml`.

## Phase 3: User Story 1 — session-context returns the real player character (P1) 🎯 MVP

**Goal**: `session-context`'s `player_character` field is populated from `pc.yaml` against a real
chronicle layout.

- [ ] T002 [US1] In `tests/engine/test_verbs.py`, add a regression test that builds a real
  chronicle layout on disk (`chronicle.yaml` plus empty `setting/`, `overlay/`, `entities/`, `log/`
  directories, and a `pc.yaml` at the chronicle root only — nothing under `entities/`) and asserts
  `verbs.session_context(chronicle_dir)["player_character"]` is non-null and matches `pc.yaml`'s
  written frontmatter.
- [ ] T003 [US1] In the same test module, add a test that a chronicle with no `pc.yaml` at all
  still returns `player_character: null` from `session_context` (SC-003 / Edge Case 1 — must not
  regress).

**Checkpoint**: User Story 1 is independently verifiable — `pytest tests/engine/test_verbs.py -k
pc_yaml` passes with only T001 done.

## Phase 4: User Story 2 — get/find/party stay consistent with session-context (P2)

**Goal**: The same `pc.yaml`-derived entity is visible to `get`/`find`/`party`, not only through
`session-context`'s own field.

- [ ] T004 [US2] In `tests/engine/test_verbs.py`, add a test that, against the same real chronicle
  layout as T002, `verbs.get(pc_id, chronicle_dir)` resolves to that same frontmatter.
- [ ] T005 [US2] In the same test module, add a test that `verbs.find(chronicle_dir,
  type="character")["results"]` includes the `pc.yaml` entity's id.

**Checkpoint**: Both user stories pass independently and together.

## Phase 5: Polish

- [ ] T006 Add a regression test for the duplicate-`role: player` edge case: a chronicle with both
  `pc.yaml` and an `entities/*.md` file that also declares `role: player` — assert
  `session_context` raises (`ValueError`, per `loadtier.always_tier`'s existing contract), not a
  silent pick of one.
- [ ] T007 Add a regression test that an invalid `pc.yaml` (fails schema validation — e.g. missing
  `id`) raises `state.StateError`, matching an invalid `entities/*.md` file's existing failure
  shape.
- [ ] T008 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide; fix any
  finding the diff introduced (CLAUDE.md: both must stay green repo-wide).
- [ ] T009 Run `PYTHONPATH=engine python3 -m pytest tests/ -q` in full (not just the new tests) to
  confirm no existing test regressed.
- [ ] T010 Update `docs/design/22-state.md`'s "Where things live" tree and
  `docs/design/02-architecture.md`'s chronicle layout to note `pc.yaml` as the player character's
  actual location, so this design-doc/implementation mismatch (flagged in spec.md's Assumptions)
  does not keep misleading the next reader — a documentation-only correction, not a capability
  change, so it does not itself need its own Spec Kit cycle (CLAUDE.md: "the gate is on capability,
  not on every commit").

## Dependencies

- T001 blocks every other task (it is the actual fix).
- T002/T003 (US1) and T004/T005 (US2) are independent of each other once T001 lands — can be
  written in either order or in parallel.
- T006/T007/T008/T009/T010 (Polish) come after both user stories' tests exist and pass.

## Parallel example

```
# After T001:
Task T002 [US1] and Task T004 [US2] touch the same test file but different test functions —
sequential in one PR is simplest here (single small file), parallelism is not worth the
coordination overhead for a change this size.
```
