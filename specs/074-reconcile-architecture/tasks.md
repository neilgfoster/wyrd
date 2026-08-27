# Tasks: Reconcile 02-architecture.md against the engine-design decisions

**Input**: spec.md, plan.md from `specs/074-reconcile-architecture/`

## Task list

- [X] **T001** [US1] Grep `docs/design/*.md` for `codex/`, confirm `22-state.md` and
  `23-chronicle-bootstrap.md` both already use `entities/` for the chronicle-created-entities
  directory.
- [X] **T002** [US1] Fix `02-architecture.md`'s `wyrd-chronicle-<name>/` tree line to
  `entities/`, matching the other two documents.
- [X] **T003** [US2] Fix the `engine/` tree line's stale "not yet built (#133, #90)" comment to
  distinguish "fully specified" (#133's children #187/#188/#189 landed) from "not yet built
  (#90)" (implementation is separate, still open work).
- [X] **T004** [US2] Read the remainder of the document (Memory tiers, Code versus prose, CLI
  sketch, Deployment) end to end; confirm no further drift against #187/#188/#189's landed
  content. No further edits needed — confirmed already current.
- [X] **T005** Run `python3 tools/check_docs.py`; confirm it passes.
- [X] **T006** Run `python3 tools/check_dangling_mechanics.py`, delta-compared against `main`
  via `git stash`; confirm no new finding class.
