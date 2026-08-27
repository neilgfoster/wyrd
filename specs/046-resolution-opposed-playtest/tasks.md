# Tasks: Resolution and opposed-tests playtest

- [X] **T001** Generate the real seeded roll sequence (seed `20260827`) for every scenario in
      scope, checking `eff <= 0` before drawing to satisfy FR-003 (no die drawn for an
      already-impossible attempt).
- [X] **T002** Write the new "Resolution and opposed tests: a deeper pass" section in
      `docs/design/30-playtest-transcript.md`, following the existing document's tone and
      structure, reporting degrees only on success (FR-004).
- [X] **T003** Confirm the two edge cases found during play (a natural 100, degrees-on-failure)
      against `03-rules.md` §1's actual wording, and record the two-player-controlled-entities
      edge case's resolution.
- [X] **T004** Write the Findings subsection stating plainly that no fault was found (FR-005).
- [X] **T005** Fix the stale "creation steps 1–9" cross-reference (now 1–8, since the Luck merge)
      found while editing the same document.
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm no new finding class (SC-003).
- [X] **T007** Run `python3 -m pytest -q`; confirm no regression (SC-004).
