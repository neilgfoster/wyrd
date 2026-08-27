# Feature Specification: 03-rules.md introduces engine-wide values before first use

**Feature Branch**: `044-rules-intro-terminology`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "03-rules.md: introduce engine-wide values before first use (closes #138). docs/design/03-rules.md uses skill% at section 1 without Skill ever being defined in this document or anything read before it -- Skill's actual definition lives in docs/design/10-the-character.md, eleven documents later in the current reading order. Surfaced by #122's reorder."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A first-time reader meets Skill and Stamina before the ruleset uses them (Priority: P1)

Someone reading `docs/design/` in order (per #122's reading order: principles, architecture,
rules, ...) reaches `03-rules.md` third and immediately meets `skill%` in the resolution formula.
They want to know what a Skill *is* before the document assumes they already do.

**Why this priority**: This is the exact gap #138 raised — a genuine forward reference introduced
as a side effect of #122's reorder, not present in the previous write-order sequence.

**Independent Test**: Read `03-rules.md` from the top; confirm Skill and Stamina are named and
briefly defined before `## 1. Resolution` first uses `skill%`.

**Acceptance Scenarios**:

1. **Given** `03-rules.md` read from the top, **When** the reader reaches `## 1. Resolution`,
   **Then** they have already met a brief definition of both Skill and Stamina, with a pointer to
   `10-the-character.md` for full detail.
2. **Given** the new intro text and `10-the-character.md`'s own "What a character carries" table,
   **When** read against each other, **Then** both describe Skill and Stamina consistently — no
   two-coherent-descriptions divergence (the fault #92's cross-reading pass exists to catch).

### User Story 2 - A reader can tell engine-fixed from setting-overridable at a glance (Priority: P1)

The operator specifically asked that engine-fixed values and setting-overridable ones be visibly
distinguished up front, not discovered piecemeal across several documents.

**Why this priority**: Stated explicitly in the originating feedback, not inferred.

**Independent Test**: Read the new intro text and confirm it states which part of Skill/Stamina is
engine-fixed (the mechanism) versus setting data (the list, the names, the starting figure).

**Acceptance Scenarios**:

1. **Given** the new intro text, **When** read, **Then** it states Skill's percentage-tested
   mechanism is engine-fixed while the skill list and names are setting data, and Stamina's
   recovery rule is engine-fixed while its starting figure may be retuned.

### Edge Cases

- Does this duplicate `10-the-character.md`'s own definitions, risking the two-coherent-descriptions
  fault? No — the new text is a one-line pointer plus the minimum needed to make `skill%`
  comprehensible on first read, explicitly deferring full detail to `10-the-character.md` rather
  than restating it.
- Does the existing engine-labels rename table (Taint, Trauma, Strain, ...) already partly do this
  job? Yes, for the tracks it lists — but it never included Skill or Stamina, which is exactly
  the gap. The new text notes the same engine-fixed/setting-data split applies to everything in
  that table too, rather than leaving the reader to infer it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` MUST define Skill and Stamina, at least briefly, before its first use
  of either (currently `## 1. Resolution`'s `skill%`).
- **FR-002**: The new definitions MUST be consistent with `10-the-character.md`'s existing
  descriptions of the same terms — no divergent restatement.
- **FR-003**: The new text MUST distinguish, for both Skill and Stamina, what is engine-fixed
  (the mechanism) from what a setting may supply or retune (the list, names, starting figures).
- **FR-004**: This feature MUST NOT introduce a new mechanism or duplicate `10-the-character.md`'s
  full definitions — a pointer plus minimal orientation, not a restatement.

### Key Entities

*(none — this feature adds introductory prose, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `03-rules.md` alone, read top to bottom, meets Skill and Stamina before
  `skill%`'s first use.
- **SC-002**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.
- **SC-003**: No claim in the new text is contradicted by `10-the-character.md` or
  `11-character-creation.md` (verified by direct comparison, not assumed).

## Assumptions

- Documentation-only: no ADR needed (no alternative rejected, purely a documentation-ordering fix
  surfaced by #122), no code changes.
- The fix lives in `03-rules.md` itself (a short intro paragraph) rather than moving
  `10-the-character.md` earlier in the reading order — #122's order was already
  operator-approved, and reordering again to avoid one forward reference would be a much larger
  change for a problem a short pointer solves cleanly.
