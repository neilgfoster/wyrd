# Tasks: Career skill cap is one flat value, not a per-skill dict

**Input**: plan.md, spec.md from `specs/158-career-flat-cap/`

## Tasks

- [x] T001 Add `CAREER_SKILL_CAP` constant to `engine/wyrd/rules.py`, documented against
      docs/design/03-rules.md section 6. [FR-003]
- [x] T002 Rewrite `effective_cap` in `engine/wyrd/career.py` to membership-test the `skills` list
      shape and return the flat constant; correct its docstring. [FR-001, FR-002, FR-005]
- [x] T003 Rewrite `career_complete` in `engine/wyrd/career.py` to use the flat constant against
      the `skills` list shape, preserving the empty-grant-never-complete guard. [FR-001, FR-004]
- [x] T004 Audit `engine/wyrd/advancement.py` for any other place assuming the old per-skill dict
      shape; confirm none beyond the two functions already named in the issue.
- [x] T005 Fix `tests/engine/test_career.py`'s synthetic `{skill: cap}` fixtures (`CAREER`,
      `GUARD`, `SOLDIER`, `GUARD_CAPTAIN`, ancestry fixtures, the four-skill fixture) to the real
      list-of-names shape; update assertions to the flat cap value. [FR-006]
- [x] T006 Fix any `{skill: cap}` fixtures in `tests/engine/test_advancement.py` to the real
      list-of-names shape. [FR-006]
- [x] T007 Add a regression test loading a real career entry from
      `wyrd-setting-darkfuture/setting/careers.yaml` and exercising
      `effective_cap`/`validate_allocation`/`career_complete` against it; skip gracefully if that
      sibling checkout isn't present. [FR-007, SC-001]
- [x] T008 Run `ruff check .`, `ruff format --check .`, and the full engine test suite; fix any
      fallout.

## Dependencies

T001 blocks T002/T003. T002/T003 block T005/T006/T007 (fixtures must match the new contract).
T004 is independent and can run any time before T008. T008 is last.
