# Tasks: The tracks that actually grow

**Input**: plan.md, data-model.md, spec.md in this directory.

- [X] T001 [P] Add `gain_allegiance`, `lose_allegiance`, `gain_holding`, `lose_holding`,
      `roll_standing` to `engine/wyrd/economy.py`, per data-model.md's exact input/output shapes.
- [X] T002 Wire `gain-allegiance`, `lose-allegiance`, `gain-holding`, `lose-holding`,
      `roll-standing` verb wrappers into `engine/wyrd/verbs.py`.
- [X] T003 [P] Create `tools/check_reputation_roll.py`, mirroring `tools/check_oracle_answers.py`:
      assert the three band widths sum to 100 and cover 1-100 with no gaps or overlaps, swept
      across a representative range of Standing scores (negative, zero, positive, and beyond the
      ±8 point where the favourable/unfavourable band caps at 45).
- [X] T004 [P] `tests/test_economy.py`: cover spec.md's acceptance scenarios for all three user
      stories — idempotent gain, refused loss, and the three-band Standing roll never touching a
      skill or difficulty value.
- [X] T005 Run `tools/check_reputation_roll.py` directly; must exit 0.
- [X] T006 `ruff check . && ruff format --check .` clean; `pytest -q` green.
