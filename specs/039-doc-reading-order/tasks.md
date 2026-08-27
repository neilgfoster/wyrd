# Tasks: Reorder the design documents into a logical reading sequence

**Input**: Design documents from `/specs/039-doc-reading-order/`

## Phase 1: Setup

- [X] **T001** Write the migration script (scratch location, not committed) implementing the
      spec.md mapping: two-phase `git mv` (via `_tmp_`-prefixed intermediate names) for all 30
      design documents, per plan.md's Migration approach.
- [X] **T002** Snapshot current `docs/design/` reference state:
      `grep -rn "docs/design/" --include="*.md" --include="*.py" . | wc -l` before any change,
      for before/after comparison.

## Phase 2: The move (User Story 1)

- [X] **T003** [US1] Run the migration script's two-phase `git mv` for all 30 design documents.
- [X] **T004** [US1] Run the migration script's link-rewrite step over every file under `docs/`
      (design docs' cross-links, ADR→design-doc links, design-doc→ADR links).
- [X] **T005** [US1] Update `README.md`'s reading-order table to the new sequence.

## Phase 3: External references (User Story 3)

- [X] **T006** [US3] Rewrite every `docs/design/NN-...` reference in `tools/*.py`.
- [X] **T007** [US3] Run `python3 -m pytest -q` and fix any script/test whose own fixtures
      reference an old path.
- [X] **T008** [US3] Query currently-open issues citing a `docs/design/NN-...` path
      (`gh issue list --repo neilgfoster/wyrd --state open --search "docs/design/"`), rewrite each
      citation via `gh issue edit`, flagging any citation carrying a line number as "line
      reference may have shifted."
- [X] **T009** [US3] Rewrite every `docs/design/NN-...` path token in `specs/*/*.md` (excluding
      this feature's own `specs/039-doc-reading-order/`), path tokens only — no prose changes.

## Phase 4: Verification (User Story 2)

- [X] **T010** [US2] Run `python3 tools/check_docs.py` and confirm a clean pass.
- [X] **T011** [US2] `grep -rn "docs/design/[0-9]" --include="*.md" --include="*.py" .` (excluding
      `.git` and this feature's own spec directory) and confirm every match points at a number
      that exists on disk (SC-002).
- [X] **T012** [US2] `git log --follow docs/design/<any-renumbered-file>.md` to confirm continuous
      history through both migration phases (SC-004).
