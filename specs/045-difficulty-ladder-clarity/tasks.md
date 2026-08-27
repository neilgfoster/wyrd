# Tasks: Clarify the difficulty ladder's asymmetry and the untrained-attempt table's stacked bonuses

- [X] **T001** Add the asymmetry-rationale paragraph after the difficulty ladder in
      `docs/design/03-rules.md` (FR-001).
- [X] **T002** Rework the untrained-attempt table into Base/Difficulty/Declaration/At columns
      (FR-002).
- [X] **T003** Check every row's arithmetic by hand (Base + Difficulty + Declaration = At)
      (SC-002).
- [X] **T004** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      found and fixed one false-positive Title Case trigger ("Below Average") from the new prose
      (SC-003).
- [X] **T005** Run `python3 -m pytest -q`; confirm no regression.
