# Tasks: Combat and harm playtest

- [X] **T001** Generate the real seeded combat exchange (seed `20260828`) against a deliberately
      tougher single opponent, drawing dice only in the order the fight actually needs them.
- [X] **T002** Resolve the resulting critical and Aftermath rolls against `05-criticals.md` and
      `06-aftermath.md`'s actual tables.
- [X] **T003** Generate a separately-seeded (`20260829`) six-roll sample at the 35%-death
      Aftermath row and play the Fate spend through on a real death result (FR-003).
- [X] **T004** Play the crowd-clearing encounter, confirming the qualification test and that no
      roll is drawn for the clear itself.
- [X] **T005** Play Stamina recovery across a Rally and a downtime, checked against
      `specs/014-stamina-recovery/check_recovery.py`'s own figures.
- [X] **T006** Identify and report the telling-blow-on-defence-failure ambiguity found during
      play; use the conservative reading for this playtest without deciding the question (FR-004).
- [X] **T007** Raise a follow-up issue (#155) for the ambiguity, rather than resolving it inline.
- [X] **T008** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      found and fixed one self-introduced false positive ("Against Senna").
- [X] **T009** Run `python3 -m pytest -q`; confirm no regression.
