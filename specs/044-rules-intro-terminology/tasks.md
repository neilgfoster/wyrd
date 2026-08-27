# Tasks: 03-rules.md introduces engine-wide values before first use

- [X] **T001** Add the Skill/Stamina intro block to `docs/design/03-rules.md`, before
      `## 1. Resolution` (FR-001, FR-003, FR-004).
- [X] **T002** Cross-check the new text against `10-the-character.md`'s "What a character
      carries" table and `11-character-creation.md`'s retune note for consistency (FR-002,
      SC-003).
- [X] **T003** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`,
      confirm clean (SC-002).
