# Tasks: Fix the Strain-threshold check so a success cannot erase a Trauma crossing

- [X] **T001** Verify the bug computationally against §15's own attempt 26 (fails at 6.3x max
      Stamina, zero Trauma under the old check) before writing anything (FR-001).
- [X] **T002** Design and verify a fix; first draft (a separate "already charged" counter) found
      subtly wrong by hand-derivation; replaced with the simpler cumulative-comparison form
      (FR-001, FR-003).
- [X] **T003** Verify the corrected check never charges Trauma directly on a success, at every
      tested run length (FR-002).
- [X] **T004** Supersede ADR 0045: `git mv` to `docs/adr/superseded/`, edit only its `Status:`
      line, add to `docs/adr/superseded/README.md`'s index (FR-004).
- [X] **T005** Write ADR 0047, stating the corrected check and what is explicitly unchanged from
      ADR 0045 (FR-004).
- [X] **T006** Update `docs/README.md`'s live ADR index (remove 0045, add 0047).
- [X] **T007** Restate the rule in `03-rules.md` §5 and `09-systems-of-power.md`'s cost section,
      cross-referencing ADR 0047 (FR-005).
- [X] **T008** Rewrite `check_spam_brake.py`: corrected `gained_cumulative` logic, re-verified
      spam/ordinary/rotation-immunity/failure-gating properties, plus a new
      `compare_edge_vs_cumulative` demonstrating the fix directly on the two sequences that found
      the bug (FR-006).
- [X] **T009** Replay §10/§14's major-tier sequence (seed `20260842`) and §15's minor-tier
      sequence (seed `20260850`) under the corrected check, including the Affliction sawtooth;
      write the corrected figures into a new §16, without editing the originals (FR-007).
- [X] **T010** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
