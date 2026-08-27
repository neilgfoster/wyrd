# Feature Specification: Reconcile 02-architecture.md against the engine-design decisions

**Feature Branch**: `190-reconcile-architecture`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Reconcile 02-architecture.md against the engine-design decisions (closes #190, depends on #187, #188, #189, part of #133). Bring 02-architecture.md fully current: apply #187/#188/#189's decisions, and fix the repo-table/tree drift, so the document describes the engine's actual current shape rather than a stale sketch."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The repo tree names the same directory consistently across documents (Priority: P1)

`02-architecture.md`'s own `wyrd-chronicle-<name>/` tree named the directory holding a
chronicle's own created entities `codex/`, while `22-state.md` and `23-chronicle-bootstrap.md`
both consistently name the same directory/concept `entities/`.

**Why this priority**: This is exactly the "two documents describing one thing differently"
fault class this repo's own review discipline names as hard to see — each document reads as
internally coherent on its own, and it is only caught by reading them against each other.

**Independent Test**: `grep -rn "codex/" docs/design/*.md` returns no hits; the
`wyrd-chronicle-<name>/` tree's entity-storage line reads `entities/`, matching
`22-state.md`/`23-chronicle-bootstrap.md`.

**Acceptance Scenarios**:

1. **Given** `02-architecture.md`'s ASCII tree, **When** compared against
   `22-state.md`/`23-chronicle-bootstrap.md`'s own naming for the same concept, **Then** all
   three agree on `entities/`.

### User Story 2 - The document reflects #187/#188/#189's already-landed decisions (Priority: P1)

`02-architecture.md` is the hub document these three prior features extended (Memory tiers,
the Code-versus-prose boundary and CLI sketch, and the pointer to `27-tooling.md`'s model-tiering
target) — a reader should not find any part of it describing a shape those decisions have since
superseded.

**Why this priority**: The document exists specifically to describe the engine's actual current
shape; content that no longer matches that shape is worse than no content, since it reads as
authoritative.

**Independent Test**: Read the "Inside each repository" tree's `engine/` line; confirm it no
longer describes the engine CLI as unspecified, since #187/#188/#189 have since specified it in
full.

**Acceptance Scenarios**:

1. **Given** the `engine/` tree line previously read "not yet built (#133, #90)", **When**
   checked against #133's now-fully-specified children, **Then** the line distinguishes "fully
   specified" from "not yet built (#90)" rather than implying neither has happened.

### Edge Cases

- Does this earn an ADR? No — this reconciles a document against decisions already recorded
  elsewhere (#187/#188/#189's own specs and any ADRs they introduced); it makes no new decision
  of its own.
- Could the `codex/`→`entities/` fix be read as a rename decision rather than a correction? No —
  `entities/` was already the majority, consistent naming across two other design documents;
  `02-architecture.md` was the outlier being corrected to match, not the other way round.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `02-architecture.md`'s `wyrd-chronicle-<name>/` tree MUST name the
  chronicle-created-entities directory `entities/`, matching `22-state.md` and
  `23-chronicle-bootstrap.md`.
- **FR-002**: The `engine/` tree line MUST NOT describe the engine as unspecified, since
  #187/#188/#189 have specified its CLI, memory tiers, and code/prose boundary.
- **FR-003**: The document MUST NOT contain content #187/#188/#189 have since superseded.
- **FR-004**: `tools/check_docs.py` and `tools/check_dangling_mechanics.py` MUST pass with no
  new finding class relative to `main`.

### Key Entities

*(none — this feature is a design-document reconciliation, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `grep -rn "codex/" docs/design/*.md` returns zero hits.
- **SC-002**: The `engine/` tree line no longer implies the CLI is unspecified.
- **SC-003**: `python3 tools/check_docs.py` passes.
- **SC-004**: `python3 tools/check_dangling_mechanics.py`'s output, delta-compared against
  `main`, introduces no new finding class.

## Assumptions

- No ADR: this reconciles `02-architecture.md` against decisions #187/#188/#189 already made and
  recorded; it decides nothing new of its own.
- This is a design specification, not an implementation.
