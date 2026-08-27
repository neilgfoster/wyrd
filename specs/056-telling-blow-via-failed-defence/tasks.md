# Tasks: Clarify how telling blow is computed via a failed defence roll

- [X] **T001** Read `check_conversion.py`'s existing telling-blow/defence modelling to identify
      what symmetry it already assumes (FR-003).
- [X] **T002** Write `check_defence_telling.py`: an independent per-roll implementation of the
      virtual-roll procedure, iterating every natural roll, compared against
      `check_conversion.py`'s own aggregate `telling_rate` (FR-003, FR-004).
- [X] **T003** Confirm the two computations match exactly across a spread of effective% values;
      confirm ADR 0028 needs no re-derivation (FR-004).
- [X] **T004** Write ADR 0044 recording the decision, including the rejected attack-only
      alternative (FR-005).
- [X] **T005** Rewrite `03-rules.md` §2's degrees bullets to state the per-roll procedure
      explicitly (FR-001, FR-002).
- [X] **T006** Add the ADR 0044 index entry to `docs/README.md`.
- [X] **T007** Add a resolution note to §7 of `docs/design/30-playtest-transcript.md`, and update
      §13's synthesis table's #155 row and closing sentence to reflect the fix.
- [X] **T008** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
