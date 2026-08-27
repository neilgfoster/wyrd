# Tasks: Full design consistency check

**Input**: Design documents from `/specs/040-design-consistency-check/`
**Prerequisites**: plan.md, spec.md, research.md

## Task List

- [X] **T001** Perform the cross-reading pass over the identified document pairs, recording
      findings in `research.md` regardless of outcome (FR-001, FR-002, SC-006).
- [X] **T002** Write `tools/check_probability_coverage.py`: a closed table mapping every derived
      probability claim in `docs/design/` to its backing script, re-running each and failing on
      any regression (FR-003, SC-001).
- [X] **T003** Write `tools/check_no_setting_vocabulary.py`: derive a denylist from
      `settings.yaml`'s live catalogue and grep `docs/design/*.md` + `README.md` (FR-004, SC-002).
- [X] **T004** Run T003 against the current corpus; found and fixed one real leak
      (`docs/design/26-corpus-index.md` named the "Maelstrom" setting as a worked example) (FR-005).
- [X] **T005** Run `python3 tools/check_docs.py` and confirm a clean pass (FR-006, SC-003).
- [X] **T006** Run `python3 tools/backlog.py check` and confirm a clean pass (FR-006, SC-004).
- [X] **T007** Run `python3 -m pytest -q` and confirm no regression (SC-005).

No new mechanism, no ADR, no code beyond the two verification scripts and one prose fix — per
spec.md's Assumptions.
