# Tasks: Condition-tracks playtest

- [X] **T001** Generate the real seeded sequence (seed `20260830`) for the Bargain (repeated
      until a real failure), a Fault-Line-biased Exposure crossing a Taint threshold, and an
      ordinary Exposure — reporting every attempt (FR-001, FR-002).
- [X] **T002** Resolve the Transformation roll and, since it was the character's first, the
      hidden-threshold roll, against `07-transformations.md`'s actual tables.
- [X] **T003** Generate the Trauma sawtooth (repeated Terror tests until 6+) and the Affliction
      test/roll, against `08-afflictions.md`'s tables.
- [X] **T004** Generate Strain accrual and a Rally recovery.
- [X] **T005** Attempt to demonstrate Resolve/Spent; find and confirm the gap (no stated gain
      trigger anywhere in `docs/design/` or `docs/adr/`, grep-verified) rather than inventing a
      mechanic (FR-004).
- [X] **T006** Raise a follow-up issue (#157) for the Resolve gap (FR-005).
- [X] **T007** Write the Findings subsection reporting both the clean results and the Resolve
      gap plainly.
- [X] **T008** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
- [X] **T009** Run `python3 -m pytest -q`; confirm no regression.
