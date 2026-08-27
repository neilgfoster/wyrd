# Tasks: Combination and minmaxing playtest pass

- [X] **T001** Generate seven real seeded independent trials (seed `20260835`) of stacking the
      Bargain, Resolve (x2) and Fortune (x3) on one fixed-setup failed test, reporting every
      trial in full (FR-001, FR-002).
- [X] **T002** Identify the stacking gap (no stated pacing limit); raise follow-up issue #167
      rather than fixing inline (FR-003).
- [X] **T003** Play a system-of-power invocation outside combat/an opposed-test shape and confirm
      the Omen-modifier scope boundary (ADR 0042) holds (FR-004).
- [X] **T004** State plainly that this is not an exhaustive combination test (FR-005).
- [X] **T005** Write the Findings subsection reporting both results plainly.
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
- [X] **T007** Run `python3 -m pytest -q`; confirm no regression.
