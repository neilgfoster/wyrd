# Tasks: Fix 02-architecture.md's repo table, naming and stale layout trees

- [X] **T001** Clone `wyrd-setting-template` and `wyrd-chronicle-template` fresh and diff their
      real layouts against 02-architecture.md's trees (FR-002 through FR-006 evidence).
- [X] **T002** Fix the repo table: add `wyrd-setting-template` and `wyrd-research`; rename
      `wyrd-<setting>` to `wyrd-setting-<name>` (FR-001, FR-002).
- [X] **T003** Fix the `wyrd/` tree: `doc/` -> `docs/`; note `engine/` doesn't exist yet (FR-003,
      FR-004).
- [X] **T004** Fix the `wyrd-setting-<name>/` tree: rename, add `corpus/` and `library/` (FR-002,
      FR-005).
- [X] **T005** Fix the `wyrd-chronicle-<name>/` tree: rename, `entities/` -> `codex/` (FR-002,
      FR-006).
- [X] **T006** Run `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`,
      confirm clean (SC-004).
