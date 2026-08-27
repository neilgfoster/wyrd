---
description: "Task list for the design-doc move and numbering settlement (issue #38)"
---

# Tasks: Move the design documents under doc/ and settle numbering

**Input**: Design documents from `/specs/033-doc-move-and-numbering/`

## Phase 1: Setup

- [X] T001 Write the migration script (scratch location, not committed) implementing
  data-model.md's mapping: `git mv` every design doc and ADR to its new path, then parse and
  rewrite every relative link inside the moved files against the mapping (research.md's
  token-matching approach), re-relativizing for the sibling-directory cross-references
  data-model.md's "Cross-reference direction changes" section describes
- [X] T002 [P] Snapshot current state for verification: `grep -c "design/" -r . --include="*.md"
  --include="*.py" --exclude-dir=.claude --exclude-dir=specs` before any change, to compare
  against after

## Phase 2: The move (User Story 1)

- [X] T003 [US1] Run the migration script's `git mv` step for all 30 design documents and the
  hub (`docs/README.md` → `docs/README.md`), per data-model.md
- [X] T004 [US1] Run the migration script's `git mv` step for `docs/adr/` (including
  `superseded/`) → `docs/adr/`, numbers unchanged
- [X] T005 [US1] Run the migration script's link-rewrite step over every file now under `doc/`
- [X] T006 [US1] Update `README.md`'s "Read in this order" table: all thirty documents in the
  corrected order, including the three previously missing (`docs/design/14-oracle-answers.md`,
  `13-oracle-prompts.md`, `17-out-of-character-mode.md`)

## Phase 3: External references (User Story 2)

- [X] T007 [US2] Rewrite `README.md`'s and `CLAUDE.md`'s remaining `design/...` references to
  `docs/design/...` / `docs/adr/...`
- [X] T008 [US2] Rewrite every `design/`-referencing line in `tools/*.py` (18 lines, per the
  scope confirmed during specification) to the new paths
- [X] T009 [US2] Run `python3 -m unittest discover -s tools -p 'test_*.py'` and fix any script
  whose own tests reference an old path
- [X] T010 [US2] Query currently-open issues citing a `design/` path
  (`gh issue list --repo neilgfoster/wyrd --state open --search "design/"`), rewrite each body's
  citation to the new path via `gh issue edit`, flagging any citation carrying a line number as
  "line reference may have shifted" per research.md's decision
- [X] T011 [US2] Rewrite every `design/`-path token in `specs/*/*.{md,py}` to its new location
  (same closed mapping, path tokens only — no prose/reasoning changes), excluding this feature's
  own `specs/033-doc-move-and-numbering/` directory, per FR-008 and research.md's revised
  decision

## Phase 4: The durable check (User Story 3)

- [X] T012 [US3] Retarget `tools/check_docs.py`'s `HUB` constant at `README.md` (unchanged path,
  now pointing into `doc/`) and `ADR_INDEX`/`ADR_DIR`/`ADR_ARCHIVE` constants at `docs/README.md`,
  `docs/adr`, `docs/adr/superseded`
- [X] T013 [US3] Update `tools/test_check_docs.py`'s fixtures/paths for the new root, if any
  hardcode the old `design/` path
- [X] T014 [US3] Run `python3 tools/check_docs.py` and confirm a clean pass against the moved tree

## Phase 5: The ADR-link policy (FR-012)

- [X] T015 Write `docs/adr/0038-an-adr-path-is-repaired-not-its-reasoning.md` recording the
  Clarifications' ADR-link-repair decision, in the shape of every prior accepted ADR (context,
  decision, alternatives rejected, consequences)
- [X] T016 Add the new ADR to `docs/README.md`'s index

## Phase 6: Verification

- [X] T017 [P] Run the corruption grep from quickstart.md
  (`diffisecty|secture|otherworldly power, no database`) — expect no output
- [X] T018 [P] Run `git log --oneline --follow docs/design/01-principles.md` and confirm pre-move
  history is reachable, for a small sample of moved files
- [X] T019 Run `python3 tools/check_docs.py` one final time against the fully-updated tree
- [X] T020 [P] Run `python3 -m unittest discover -s tools -p 'test_*.py'` one final time
- [X] T021 Delete the scratch migration script from T001 — it is one-off tooling, per
  research.md's decision not to commit it
