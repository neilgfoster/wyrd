# Tasks: Merge Luck into Fortune

- [X] **T001** Remove the standalone Luck subsection from `docs/design/03-rules.md`, fold "dodge
      a misfortune" and "break a tie" into Fortune's spend list, fix the Fate rename table's
      collision (FR-001, FR-002, FR-003).
- [X] **T002** Remove Luck from `docs/design/10-the-character.md`, `12-the-adversary.md`,
      `13-diegesis.md`, `19-campaign.md` (FR-001).
- [X] **T003** Remove Luck's creation step and starting-value row from
      `docs/design/11-character-creation.md`; renumber every subsequent step and cross-reference
      (FR-004, SC-006).
- [X] **T004** Remove Luck's step and `luck:` field from
      `docs/design/30-playtest-transcript.md`'s worked example; renumber (SC-006).
- [X] **T005** Write ADR 0041, superseding ADR 0039 in full; move ADR 0039 to
      `docs/adr/superseded/`, edit only its `Status:` line; update both ADR indexes (FR-005,
      FR-006).
- [X] **T006** Confirm `specs/008-character-creation/check_creation.py` is left untouched (FR-007).
- [X] **T007** Run `python3 tools/check_docs.py`, `check_dangling_mechanics.py`,
      `check_probability_coverage.py`, `check_no_setting_vocabulary.py`, `pytest -q`; confirm all
      clean (SC-002 through SC-005).
- [X] **T008** `grep -rn "Luck" docs/design/` and confirm zero matches (SC-001).
