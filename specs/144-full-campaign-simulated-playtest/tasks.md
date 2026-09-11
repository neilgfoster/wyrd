# Tasks: Full-campaign simulated playtest across every subsystem

- [X] **T001** [US1] Script character creation continuity for Senna Vask (or a fresh character,
      if not reusing the established one) as the arc's starting state (FR-002).
- [X] **T002** [US1] Generate the real seeded rolls (a single stated seed, in a fixed draw order)
      for at least three sessions, each closing at a Rally or downtime step (FR-001, FR-002).
- [X] **T003** [US1] Script a conflict that produces harm to the character, using the engine's
      actual resolution/combat mechanics (FR-002).
- [X] **T004** [US1] Script the recovery step that follows the harm (a Rally's Stamina/Strain
      recovery, or a downtime Mend), reading the engine's actual behavior (FR-002).
- [X] **T005** [US1] Script at least one economic-advancement event (career advance, Standing or
      coin change) using the engine's actual economy mechanics (FR-002).
- [X] **T006** [US1] Script at least one solo-procedure-driven scene — an oracle consultation, a
      companion beat, or a journey leg — using the engine's actual mechanics (FR-002).
- [X] **T007** [US1] Write the new section in `docs/design/30-playtest-transcript.md`, following
      the existing document's structure and tone (SC-001, SC-002).
- [X] **T008** [US1] Grade the transcript against `docs/design/`, reporting functional
      correctness (did each step produce a legal outcome) and behavioral fidelity (did
      pacing/difficulty/outcome shape match the design prose) as two distinct, separately
      verdicted subsections (FR-003, FR-004, SC-003).
- [X] **T009** [US2] If the behavioral-fidelity subsection names a real design/behavior mismatch,
      raise it as its own follow-up GitHub issue, following specs/055/059's pattern; otherwise
      state plainly that no follow-up is warranted (FR-005, SC-004).
- [X] **T010** Confirm the scripted run executes without crashing (FR-006).
- [X] **T011** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean, no new finding class (SC-005).
- [X] **T012** Run `python3 -m pytest -q`, `python3 -m ruff check .`, and
      `python3 -m ruff format --check .`; confirm no regression (SC-006).

## Dependencies

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 (each session/beat builds on the
prior state; the transcript section (T007) and its grading (T008/T009) can only be written once
the arc is fully scripted). T010-T012 run last, as verification over the finished change.

## Implementation strategy

MVP is User Story 1 (T001-T008): the scripted arc and its graded, two-verdict transcript section.
User Story 2 (T009) depends on what US1's grading actually finds — it cannot be scripted ahead of
that finding.
