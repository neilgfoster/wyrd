# Implementation Plan: Session friction capture

**Branch**: `171-session-friction-capture` | **Date**: 2026-09-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/171-session-friction-capture/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Document a low-cost convention for capturing session friction during chronicle play: a durable
append-only file (`log/friction.md`, per Clarifications) in each `wyrd-chronicle-<name>` repo,
a short structured entry format, and an explicit triage line distinguishing an engine gap worth
recording from ordinary narrative color. This is a documentation-only change to
`docs/design/16-session.md` — no engine code, no new tooling. The harvest step that reads these
entries across chronicles is sibling issue #95, explicitly out of scope.

## Technical Context

**Language/Version**: N/A — documentation change only (Markdown), consistent with
`docs/design/*.md`'s existing form.

**Primary Dependencies**: N/A — no code, no libraries.

**Storage**: `log/friction.md`, a plain Markdown file per chronicle repo (per Clarifications
session 2026-09-17), append-only.

**Testing**: No automated tests apply to a documentation-only change. Validation is a
`tools/check_docs.py` run (the repo's existing reachability/dead-link/ADR-index checker) plus a
manual worked-example check (one qualifying and one non-qualifying entry, per spec User Story 2
and Success Criterion SC-004).

**Target Platform**: N/A.

**Project Type**: Documentation (design spec inside `docs/design/`), per this repo's own
convention that design documents are "rewritten in place, always describing the present"
(`CLAUDE.md`).

**Performance Goals**: N/A.

**Constraints**:
- Zero player-visible ceremony (FR-007, FR-008).
- Setting-agnostic — no setting vocabulary in the convention (FR-009, per `CLAUDE.md` "the
  engine is setting-agnostic").
- Nothing unpublishable crosses into this repo (`wyrd`) — the convention lives in `docs/design/`,
  but the friction log itself lives in each `wyrd-chronicle-<name>` repo, never in `wyrd`
  (Assumptions).

**Scale/Scope**: One design document edit (`docs/design/16-session.md`), touching the existing
"The Rally" / session-loop area where other per-beat bookkeeping (state persistence) is already
documented.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` in this repo is the unfilled Spec Kit template (no
project-specific principles have been authored into it) — this repo's actual governing document
for design work is `CLAUDE.md`. Gates checked against `CLAUDE.md` directly:

- **Setting-agnostic engine** (`CLAUDE.md` "The engine is setting-agnostic"): PASS — the
  convention, its file location, and its triage line are stated in engine-generic English, with
  no setting names or borrowed vocabulary. Verified by inspection of spec.md FR-009.
- **ADR discipline** (`CLAUDE.md` "Decisions are recorded"): No ADR is raised for this feature.
  The file-location and format choices were resolved directly from issue #94's own text and
  existing design documents (`16-session.md`, `23-chronicle-bootstrap.md`), not from a rejected
  alternative a future reader would plausibly re-propose — the bar CLAUDE.md sets for an ADR.
  PASS (no gate violated by omission).
- **Design documents describe the present, no changelog prose** (`CLAUDE.md` "Design documents
  are... rewritten in place"): The edit to `16-session.md` will state the convention as it now
  stands, with no "previously..." language. Checked at implementation time (Phase where the doc
  edit itself is written) and again before PR.
- **Documents are a checked graph** (`CLAUDE.md` "The documents are a checked graph"): No new
  document is added (this is an edit to an already-linked file), so `tools/check_docs.py`'s
  reachability requirement is unaffected. The check is still run as part of validation
  (Technical Context > Testing) to catch any accidental link breakage.
- **Deterministic over inference** (`CLAUDE.md`): N/A as a code gate (no code in this feature);
  applied instead by keeping the triage line in the spec built from explicit, checkable criteria
  (FR-004's three numbered conditions) rather than a vague instruction to "use judgment."

No violations. Complexity Tracking table below is empty accordingly.

## Project Structure

### Documentation (this feature)

```text
specs/171-session-friction-capture/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `data-model.md` and no `/contracts/` — this feature defines a convention and a document edit,
not a data model or an external interface. Both are omitted per plan.md's own instructions
("Skip if project is purely internal" / the entity here, the friction entry, is fully described
in spec.md's Key Entities and needs no separate elaboration to be actionable).

### Source Code (repository root)

```text
docs/design/16-session.md      # the design document this feature edits, in place
tools/check_docs.py            # existing checker, run unmodified to validate the edit
specs/171-session-friction-capture/   # this feature's own Spec Kit artifacts
```

**Structure Decision**: Single documentation edit inside the existing `docs/design/` tree — none
of the template's Option 1/2/3 source-code layouts apply, since this feature adds no code, no
tests directory, and no new top-level project.

## Complexity Tracking

*No entries — Constitution Check reported no violations.*
