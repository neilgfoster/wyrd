# Tasks: Systems-of-power balance playtest

- [X] **T001** Generate the real seeded ordinary-use sequence (3 `minor`-tier invocations) and
      the minmax `major`-tier spam sequence (seed `20260831`), continuing until both the
      un-widened and Taint-widened Ill Omen bands are observed, disclosing every roll (FR-001,
      FR-002, SC-002).
- [X] **T002** Identify the cost-structure gap (nothing discourages spamming failed high-tier
      invocations); raise follow-up issue #163 rather than fixing inline (FR-003).
- [X] **T003** Exercise `resolve_cost` (the schema's own worked example) and confirm the #157
      Resolve gap recurs, cross-referencing rather than re-deriving (FR-004).
- [X] **T004** Write the non-user comparison.
- [X] **T005** Write the Findings subsection reporting both results plainly.
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
- [X] **T007** Run `python3 -m pytest -q`; confirm no regression.
