# Tasks: Decide the engine-code vs. GM-contract-prose boundary

- [X] **T001** State the checkable test: deterministic-and-mechanically-checkable → code;
      requires-creative-judgment → prose (FR-001).
- [X] **T002** Check the test against `01-principles.md`'s seven principles, verifying each
      classification against that principle's own text (FR-002).
- [X] **T003** Catch and correct an unverified claim (`wyrd doctor` auditing cross-chronicle
      bleed) by checking `21-parallel-chronicles.md` directly, finding the real mechanism instead.
- [X] **T004** Apply the test to `16-session.md`'s concrete session-structure elements in a table
      (FR-003).
- [X] **T005** State the parameter-vs-decision distinction explicitly (FR-004).
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
