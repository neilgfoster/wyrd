# Tasks: Widen Resolve to counter both Taint and Trauma

- [X] **T001** Investigate dedicated-track vs widening-Resolve; identify the resource-economy
      argument (a dedicated track doubles spendable currency) and confirm it with the operator
      (FR-004).
- [X] **T002** Supersede ADR 0043: `git mv` to `docs/adr/superseded/`, edit only its `Status:`
      line, add to `docs/adr/superseded/README.md`'s index (FR-004).
- [X] **T003** Write ADR 0049, recording the decision and the rejected dedicated-track
      alternative (FR-004).
- [X] **T004** Update `docs/README.md`'s live ADR index (remove 0043, add 0049).
- [X] **T005** Rewrite `03-rules.md` §4's cap/Spent paragraph for the dual-threshold formula and
      per-axis exemption (FR-001, FR-002, FR-003).
- [X] **T006** Extend `check_resolve.py` for the dual-threshold formula, both exemptions, and the
      Trauma-higher case (FR-005) — caught and fixed a real bug in the process (exact-equality
      `is_spent` instead of "at or below").
- [X] **T007** Write §18 in `docs/design/30-playtest-transcript.md`, a worked character with
      Trauma as the binding threshold, real rolls where a roll is involved (FR-006).
- [X] **T008** Run `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
      `python3 -m pytest -q`; confirm clean.
