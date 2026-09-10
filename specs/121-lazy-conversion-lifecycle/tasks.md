# Tasks: Lazy Conversion Lifecycle

**Input**: plan.md, spec.md from `specs/121-lazy-conversion-lifecycle/`

## Phase 1: Setup

- [X] T001 Confirm `engine/wyrd/entity.py` and `tests/engine/test_entity.py` are the correct
      landing spots (per plan.md's Project Structure) — no new files needed.

## Phase 2: Foundational (schema constant)

- [X] T002 In `engine/wyrd/entity.py`, add `_SOURCE_REQUIRED_FIELDS = ("work", "licence", "path")`
      and `_SOURCE_OPTIONAL_FIELDS = ("pages",)` near the existing `_CONNECTION_*` constants.

## Phase 3: User Story 2 — source record validation (P1, but built first: US1 depends on it)

- [X] T003 [US2] In `engine/wyrd/entity.py`, add `validate_source(source: dict, *, status: str) ->
      dict`: checks `source` is a mapping; every field in `_SOURCE_REQUIRED_FIELDS` is present and
      truthy; `pages` is present and truthy when `status` is `"drafted"` or `"complete"`; no field
      outside `_SOURCE_REQUIRED_FIELDS + _SOURCE_OPTIONAL_FIELDS` is present. Returns
      `{"valid": True}` or `{"valid": False, "error": "..."}` naming the specific field.
- [X] T004 [US2] In `tests/engine/test_entity.py`, add test cases for `validate_source`: missing
      `work`/`licence`/`path`; missing `pages` at `status="drafted"` and `status="complete"`;
      `pages` not required at `status="stub"`; an unexpected extra field; a fully valid entry at
      each status.

## Phase 4: User Story 1 — stub sufficiency (P1)

- [X] T005 [US1] In `engine/wyrd/entity.py`, add `check_stub_sufficiency(frontmatter: dict, body:
      str = "") -> dict`: no-ops (`{"valid": True}`) when `frontmatter.get("status") != "stub"`;
      otherwise requires a non-empty (non-whitespace) `body` as the summary — 18-arcs-and-beats.md's
      stub example carries its summary as body text below the frontmatter, not a frontmatter
      field — non-empty `tags`, and at least one `sources` entry whose `path` is non-empty (reusing
      `validate_source`'s field name, not re-deriving the check). Returns `{"valid": True}` or
      `{"valid": False, "error": "..."}` naming the first unmet requirement, checked in the order
      summary → tags → sources[].path.
- [X] T006 [US1] In `tests/engine/test_entity.py`, add test cases for `check_stub_sufficiency`:
      empty and whitespace-only body, missing tags, missing/empty `sources`, a `sources` entry
      with an empty `path`, a fully sufficient stub, and a non-stub entity that is exempt
      regardless of the same fields being absent.

## Phase 5: User Story 3 — legal status transitions (P1)

- [X] T007 [US3] In `engine/wyrd/entity.py`, add `_LEGAL_TRANSITIONS = {("stub", "drafted"),
      ("drafted", "complete")}` and `legal_transition(from_status: str, to_status: str) -> dict`:
      returns `{"valid": True}` for the two legal pairs; otherwise `{"valid": False, "error":
      "..."}` distinguishing "skips a state" (e.g. `stub` → `complete`) from "moves backward"
      (`to_status` earlier than `from_status` in `STATUSES` order) from "not a transition" (equal
      statuses or an unrecognised status value).
- [X] T008 [US3] In `tests/engine/test_entity.py`, add test cases for `legal_transition` covering
      all nine `(from, to)` pairs over the three statuses, asserting the two legal pairs pass and
      the other seven fail with the expected reason category.

## Phase 6: User Story 4 — stub ratio report (P2)

- [X] T009 [US4] In `engine/wyrd/entity.py`, add `status_counts(entities: dict[str, dict]) ->
      dict`: returns `{status: {"count": int, "proportion": float}}` for each of `STATUSES`, over
      `entities`' `status` fields; proportion is `0.0` for every status (not a `ZeroDivisionError`)
      when `entities` is empty.
- [X] T010 [US4] In `tests/engine/test_entity.py`, add test cases for `status_counts`: a known
      mixed-status set (assert exact counts and proportions), and an empty set (assert zero counts,
      zero proportions, no exception).

## Phase 7: Polish

- [X] T011 Run `python3 -m ruff check . && python3 -m ruff format --check .` and fix any findings
      in the touched files.
- [X] T012 Run `PYTHONPATH=engine python3 -m pytest -q` and confirm the full suite (not just the
      new tests) is green.
- [X] T013 Update `docs/design/18-arcs-and-beats.md` in place only if implementation revealed a
      gap between the design doc's "Conversion is lazy" section/status table and what was actually
      built (per CLAUDE.md and the issue's Definition of Done) — otherwise skip, this task is
      conditional.

## Dependencies

- T002 blocks T003 and T005 (both use the schema constants / field names it introduces).
- T003 blocks T005 (stub sufficiency's source-path check reuses `validate_source`'s field name
  convention, and conceptually depends on the source schema being defined first).
- T005, T007, T009 are otherwise independent of each other and may be done in any order once T002
  (and T003 for T005) land.
- T011-T013 run only after every function/test task above is complete.
