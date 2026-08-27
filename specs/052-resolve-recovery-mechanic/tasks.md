# Tasks: Resolve recovers at a Rally, capped by Taint

- [X] **T001** Draft the Resolve gain/cap/spend rule for `docs/design/03-rules.md` §4.
- [X] **T002** Work through what a naive `cap = Taint` formula actually produces at full rest;
      find and confirm it puts the character at the Spent boundary immediately, with no positive
      Resolve ever spendable — reject it before shipping (FR-002).
- [X] **T003** Correct the formula to `cap = Taint + 3` (reusing the Transformation threshold
      interval); confirm real headroom exists at every Taint above 0, and Taint 0's exemption is
      stated explicitly, not derived (FR-003).
- [X] **T004** Write `check_resolve.py`, proving both the corrected formula's headroom claim and
      the rejected naive formula's actual failure (FR-004).
- [X] **T005** Write ADR 0043 recording the decision and both rejected alternatives (FR-005).
- [X] **T006** Update `docs/README.md`'s ADR index.
- [X] **T007** Run `python3 tools/check_docs.py`, `check_dangling_mechanics.py`,
      `check_resolve.py`, and `pytest -q`; confirm all clean.
