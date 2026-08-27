# Tasks: Review all playtest findings and resolve outstanding gaps

- [X] **T001** Read §6-§12's Findings subsections together and list every distinct finding
      (FR-001).
- [X] **T002** Verify each finding's tracked-issue status against live GitHub state (`gh issue
      view`), not the playtest prose alone (FR-002).
- [X] **T003** Identify the identical recurrence (Resolve gap, §8/§10) and the thematic
      recurrence (#163/#167, repeated-spend pacing) (FR-003).
- [X] **T004** Cross-reference the thematic recurrence on both #163 and #167 as GitHub comments
      (FR-003).
- [X] **T005** Write the synthesis section in `docs/design/30-playtest-transcript.md`, making no
      design decision for any open follow-up (FR-004, FR-005).
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`;
      confirm clean.
- [X] **T007** Run `python3 -m pytest -q`; confirm no regression.
