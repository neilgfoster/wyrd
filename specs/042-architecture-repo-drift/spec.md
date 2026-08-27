# Feature Specification: Fix 02-architecture.md's repo table, naming and stale layout trees

**Feature Branch**: `042-architecture-repo-drift`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Fix 02-architecture.md's repo table, naming and stale doc/ path (closes #136). Repos still missing reference to settings template repo, and setting repo names do not match reality. Verify that repo layouts match reality under the 'Inside each repo' section."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader learns the real repo fleet from 02-architecture.md alone (Priority: P1)

Someone reading `02-architecture.md`'s "Four repositories" table wants an accurate list of every
repo kind in the fleet, with names that match what they'd actually find on GitHub.

**Why this priority**: This is the exact gap #136 raised — the table currently omits two repo
kinds and uses a naming convention (`wyrd-<setting>`) that doesn't match the real one
(`wyrd-setting-<name>`), stated in CLAUDE.md and visible in `settings.yaml`'s own `repo:` values.

**Independent Test**: Compare the table's repo kinds and naming against CLAUDE.md's canonical
table and a real cloned setting repo's `repo:` field in `settings.yaml`.

**Acceptance Scenarios**:

1. **Given** `02-architecture.md`'s repo table, **When** compared against CLAUDE.md's canonical
   six-repo table, **Then** all six repo kinds appear (adding `wyrd-setting-template` and
   `wyrd-research`, currently missing).
2. **Given** the table's setting/chronicle repo naming, **When** compared against
   `settings.yaml`'s real `repo:` values, **Then** the convention reads `wyrd-setting-<name>`, not
   `wyrd-<setting>`.

### User Story 2 - The "Inside each repository" trees match real repo layouts (Priority: P1)

Someone reading the file trees under "Inside each repository" wants them to match what a cloned
`wyrd-setting-template` or `wyrd-chronicle-template` repo actually contains.

**Why this priority**: #136 explicitly asked this be verified against reality, not just trusted.

**Independent Test**: Diff each documented tree against the real, canonical template repo it
describes (`wyrd-setting-template`, `wyrd-chronicle-template`), cloned fresh for the comparison.

**Acceptance Scenarios**:

1. **Given** the `wyrd/` tree, **When** compared against this repo's own root, **Then** `doc/` is
   corrected to `docs/` (stale since #38's migration), and the tree honestly notes that `engine/`
   does not exist yet (the CLI implementation this tree describes is aspirational, tracked by
   epic #133/#90, not yet built).
2. **Given** the `wyrd-setting-<name>/` tree, **When** compared against a fresh clone of
   `wyrd-setting-template`, **Then** the missing `corpus/` and `library/` top-level directories
   are added.
3. **Given** the `wyrd-chronicle-<name>/` tree, **When** compared against a fresh clone of
   `wyrd-chronicle-template`, **Then** `entities/` is corrected to `codex/` — the real template
   ships `codex/README.md` ("written during play"), the same description the doc gives
   `entities/`, and no `entities/` directory exists in the template at all.

### Edge Cases

- The `wyrd-setting-template` clone's `entities/` subdirectory names (`adventure`, `campaign`,
  `faction`, `location`, `scenario`, `threat`, ...) do not match `docs/design/25-entities.md`'s
  current ten-type model (`place`, `organisation`, `arc`, `thread`, ...). This is real,
  significant drift, but it is drift **in `wyrd-setting-template`**, a different repository this
  engine repo doesn't own or write to — `25-entities.md` is this repo's own current, authoritative
  design, and rewriting it to match a stale template would codify the wrong side of the
  disagreement. Out of scope here; raised as a separate finding for a template-repo fix, not
  corrected in this feature.
- `wyrd-chronicle-hemmelfurt` (the one existing live chronicle, referenced in CLAUDE.md as "the
  session that corrected the resolution mechanic three times") has a flat, much older structure
  (`party.yaml`, `pc.yaml`, `threads.yaml`, no `engine/`/`setting/`/`overlay/`/`codex/`) --
  clearly pre-dating the current architecture entirely. Not used as a reality check for this
  feature; `wyrd-chronicle-template`, the actively-maintained canonical template, is.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo table MUST list all six repo kinds CLAUDE.md's canonical table lists.
- **FR-002**: The repo table and both "Inside each repository" trees MUST use `wyrd-setting-<name>`,
  not `wyrd-<setting>`.
- **FR-003**: The `wyrd/` tree MUST read `docs/`, not `doc/`.
- **FR-004**: The `wyrd/` tree MUST note that `engine/` does not exist yet, rather than presenting
  it as already-built.
- **FR-005**: The `wyrd-setting-<name>/` tree MUST include `corpus/` and `library/`, confirmed
  present in the real template.
- **FR-006**: The `wyrd-chronicle-<name>/` tree MUST read `codex/`, not `entities/`, confirmed
  against the real template.
- **FR-007**: This feature MUST NOT alter `docs/design/25-entities.md`'s ten-type entity model to
  match `wyrd-setting-template`'s stale vocabulary — that drift is out of scope, in a different
  repository.

### Key Entities

*(none — this feature corrects prose/table content, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `02-architecture.md`'s repo table lists 6 repo kinds, matching CLAUDE.md.
- **SC-002**: No `wyrd-<setting>` or `doc/` token remains in `02-architecture.md`.
- **SC-003**: Both "Inside each repository" trees match a fresh clone of their respective template
  repo, confirmed by direct comparison (not assumed).
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- `wyrd-setting-template` and `wyrd-chronicle-template` are the correct reality-check targets
  (canonical, actively maintained skeletons), not `wyrd-setting-wfrp-1e` (a real but
  possibly-WIP setting) or `wyrd-chronicle-hemmelfurt` (a legacy pre-architecture chronicle).
- Documentation-only: no ADR needed (no alternative rejected, only factual correction against
  observed reality); no code changes.
