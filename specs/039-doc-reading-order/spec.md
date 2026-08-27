# Feature Specification: Reorder the design documents into a logical reading sequence

**Feature Branch**: `039-doc-reading-order`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Reorder the design documents into a logical reading sequence (closes #122). #38 flattened numbering but preserved the existing (write-order) sequence; this reorders the content itself: principles -> architecture -> resolution/rules -> character -> oracle -> session/campaign -> world-building/authoring -> maintenance/evolution/tooling, with the playtest transcript moved to the end as a worked example. Operator-approved grouping (see below)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A new reader follows the numbered sequence and builds understanding in order (Priority: P1)

Someone opening `docs/design/` for the first time reads `01-principles.md` through
`30-journeys.md` in order and finds each document builds on what came before: principles, then
how the engine is put together, then the rules that resolve action, then the character who acts,
then the oracle tools a GM reaches for, then session/campaign structure, then how a setting is
authored and its entities modeled, then maintenance/evolution/tooling — with the worked playtest
example at the end, after every mechanic it demonstrates has been introduced.

**Why this priority**: This is the entire point of #122 — the current order (preserved verbatim
by #38) reads as write-order, not read-order, and #122 exists specifically to fix that.

**Independent Test**: Read `README.md`'s reading-order table top to bottom; confirm no document
references a concept it hasn't yet introduced from an earlier-numbered document, other than
forward pointers the prose already flags as such.

**Acceptance Scenarios**:

1. **Given** the renumbered `docs/design/` tree, **When** a reader opens files in numeric order,
   **Then** the sequence is principles (01) → architecture (02) → resolution/rules (03-09) →
   character (10-13) → oracle (14-15) → session/campaign (16-23) → world-building/authoring
   (24-26) → maintenance/evolution/tooling (27-29) → worked playtest example (30).
2. **Given** any cross-reference between two design documents, **When** the link is followed,
   **Then** it resolves to the correct renumbered file — no link points at a stale number.
3. **Given** any cross-reference from an ADR to a design document, or from a design document to
   an ADR, **When** the link is followed, **Then** it resolves correctly under the new numbering.

### User Story 2 - The checked-graph invariant survives the renumbering (Priority: P1)

The repo's own tooling (`tools/check_docs.py`) continues to pass after the move — every document
stays reachable from the hub, every link resolves, the ADR index stays accurate.

**Why this priority**: `check_docs.py` is the mechanism that has caught prior link drift
(including #38's own motivating incident); a renumbering that breaks it would be the same fault
class recurring immediately after the confirmed order.

**Independent Test**: `python3 tools/check_docs.py` exits 0 after the move.

**Acceptance Scenarios**:

1. **Given** the renumbered tree, **When** `python3 tools/check_docs.py` runs, **Then** it
   reports all documents reachable and all links resolved, with no manual patching afterward.

### User Story 3 - Every other reference to a design-doc path stays correct (Priority: P2)

`README.md`'s reading-order table, `tools/*.py` path references, `specs/*/*.md` path tokens, and
any currently-open GitHub issue citing a `docs/design/NN-...` path all point at the renumbered
file, not the old number.

**Why this priority**: #38 already established that a path reference left behind is a live fault
(the same class this migration must not reintroduce), and #122 explicitly asks for the same
migration discipline.

**Independent Test**: `grep -r "docs/design/" --include="*.md" --include="*.py"` across the repo
(excluding this feature's own `specs/039-doc-reading-order/`, which documents the migration
itself and legitimately mentions old numbers) shows no reference to a number that no longer
exists on disk.

**Acceptance Scenarios**:

1. **Given** the renumbered tree, **When** `tools/*.py` is grepped for `docs/design/` references,
   **Then** every one points at the current filename.
2. **Given** the renumbered tree, **When** open GitHub issues are queried for `docs/design/`
   citations, **Then** each is updated to the new path (a line-number citation is flagged as
   possibly shifted, per the same policy #38 used).

### Edge Cases

- What about `specs/*/*.md` prose that quotes an old path as historical record (e.g. describing
  what #38 itself did)? Per #38's own established policy (data-model.md, "What is explicitly NOT
  remapped"), only literal path *tokens* are repaired in other features' spec files — prose
  reasoning is left untouched, and this feature's own `specs/039-doc-reading-order/` is excluded
  entirely since it documents the old numbers as history.
- What about closed GitHub issues citing an old path? Left as historical record, same as #38.
- What if a design document's own prose names its neighbor by number (e.g. "see document 12")?
  Checked and repaired the same as any other link — `check_docs.py`'s link-resolution check would
  catch a broken one regardless of whether it's markdown-link or prose-referenced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every file in `docs/design/` MUST be renumbered per the operator-confirmed mapping
  (see Assumptions) via `git mv`, preserving history.
- **FR-002**: Every relative link between design documents, and between a design document and an
  ADR (in either direction), MUST be rewritten to the new numbering — no unverified bulk
  find-and-replace (CLAUDE.md's own recorded fault class).
- **FR-003**: `README.md`'s reading-order table MUST reflect the new sequence.
- **FR-004**: Every `docs/design/NN-...` reference in `tools/*.py` MUST be updated to the new
  number.
- **FR-005**: Every `docs/design/NN-...` path *token* in `specs/*/*.md` (excluding this feature's
  own spec directory) MUST be updated to the new number, without altering surrounding prose.
- **FR-006**: Every currently-open GitHub issue citing a `docs/design/NN-...` path MUST have its
  citation updated to the new number; a citation carrying a line number is flagged as possibly
  shifted rather than silently corrected.
- **FR-007**: `python3 tools/check_docs.py` MUST pass cleanly after the move, with no manual
  reachability or link-resolution failure remaining.
- **FR-008**: The migration MUST use `git mv` for every renumbered file, never a delete-and-recreate,
  so file history is preserved.

### Key Entities

*(none — this feature renames files, it does not add data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `python3 tools/check_docs.py` exits 0 after the move.
- **SC-002**: `grep -rn "docs/design/[0-9]" --include="*.md" --include="*.py" .` (excluding this
  feature's own spec directory and `.git`) shows zero references to a number that does not exist
  on disk after the move.
- **SC-003**: `README.md`'s reading-order table lists all 30 documents in the new numeric order,
  matching the files on disk exactly (same check #38's own T006 verified).
- **SC-004**: `git log --follow` on any renumbered file shows continuous history through the
  rename (confirms `git mv`, not delete-and-recreate, per FR-008).

## Assumptions

- **The operator-confirmed mapping** (old number/name → new number, filename unchanged except the
  leading digits):

  | New | Old | File |
  |---|---|---|
  | 01 | 01 | principles.md |
  | 02 | 02 | architecture.md |
  | 03 | 03 | rules.md |
  | 04 | 07 | tables.md |
  | 05 | 08 | criticals.md |
  | 06 | 09 | aftermath.md |
  | 07 | 10 | transformations.md |
  | 08 | 11 | afflictions.md |
  | 09 | 14 | systems-of-power.md |
  | 10 | 04 | the-character.md |
  | 11 | 05 | character-creation.md |
  | 12 | 06 | the-adversary.md |
  | 13 | 23 | diegesis.md |
  | 14 | 12 | oracle-answers.md |
  | 15 | 13 | oracle-prompts.md |
  | 16 | 16 | session.md |
  | 17 | 17 | out-of-character-mode.md |
  | 18 | 28 | arcs-and-beats.md |
  | 19 | 18 | campaign.md |
  | 20 | 30 | journeys.md |
  | 21 | 25 | parallel-chronicles.md |
  | 22 | 19 | state.md |
  | 23 | 29 | chronicle-bootstrap.md |
  | 24 | 26 | authoring-a-setting.md |
  | 25 | 27 | entities.md |
  | 26 | 24 | corpus-index.md |
  | 27 | 20 | tooling.md |
  | 28 | 21 | maintenance.md |
  | 29 | 22 | evolution.md |
  | 30 | 15 | playtest-transcript.md |

- ADR numbers are **not** renumbered — same policy #38 established (they are historical
  identifiers). Only design-document numbers move.
- This is documentation-only: no code behavior changes, only file paths and the links that name
  them. `tools/check_docs.py` itself needs no retargeting (its `HUB`/`ADR_INDEX` constants already
  point at `README.md`/`docs/README.md`, which do not move).
