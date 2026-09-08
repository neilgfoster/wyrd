# Tasks: Standing and coin as one material position

**Input**: plan.md, data-model.md, spec.md in this directory.

- [X] T001 Add `coin` to `PLAYER_CHARACTER_FIELDS` in `engine/wyrd/character.py`.
- [X] T002 Add `coin: 0` to the player-character frontmatter example in `docs/design/22-state.md`.
- [X] T003 [P] Create `engine/wyrd/economy.py` with `spend_coin`, `martial_weapon_sighting`,
      `adjust_standing`, per data-model.md's exact input/output shapes.
- [X] T004 Wire `spend-coin`, `martial-weapon-sighting`, `adjust-standing` verb wrappers into
      `engine/wyrd/verbs.py`.
- [X] T005 [P] `tests/test_economy.py`: cover spec.md's acceptance scenarios for all three user
      stories plus the edge cases (exact-price purchase, zero delta, unbounded negative Standing,
      unknown gear id).
- [X] T006 Verify no encumbrance field/weight/capacity was introduced (grep check) — FR-005.
- [X] T007 `ruff check . && ruff format --check .` clean; `pytest -q` green.
