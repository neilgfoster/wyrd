# Tasks: Decide whether reroll resources may stack unbounded on one roll

- [X] **T001** Ask the operator whether to cap reroll-resource stacking or state it as
      deliberately unbounded; operator chose deliberately unbounded (FR-002).
- [X] **T002** Write ADR 0046 recording the decision, including the rejected per-test-cap
      alternative and citing #153's own seven-trial evidence (FR-002, FR-003).
- [X] **T003** Add the stacking statement to `03-rules.md` §3 (Fortune) and §4 (the Bargain),
      cross-referencing each other and ADR 0046 (FR-001).
- [X] **T004** Add a resolution note to §12 of `docs/design/30-playtest-transcript.md`, and
      update §13's synthesis table's #167 row and closing sentence.
- [X] **T005** Add the ADR 0046 index entry to `docs/README.md`.
- [X] **T006** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
