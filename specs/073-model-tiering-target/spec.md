# Feature Specification: Define the model-tiering target and its verification

**Feature Branch**: `189-model-tiering-target`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Define the model-tiering target and its verification (closes #189, depends on #187, #188, #192, part of #133). State the model-tiering goal concretely and checkably: what a lightweight model needs from the engine, and how 'this works on a lightweight model' is verified, even if full achievement is deferred."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The stated target matches what the engine actually decided, not a looser earlier framing (Priority: P1)

`27-tooling.md`'s own §5 already decided the GM session stays on the capable model — a
narrower, more considered position than #133's own looser "Haiku-sufficient" epic wording. A
reader needs the correct target stated, not two documents implying different things.

**Why this priority**: This is a real inconsistency between an epic's informal framing and an
already-decided design document, found while working this feature, not assumed resolved.

**Independent Test**: Read `27-tooling.md`'s new "The actual target, stated precisely"
subsection; confirm it explicitly corrects the "session runs on Haiku" framing rather than
restating it.

**Acceptance Scenarios**:

1. **Given** the epic's own "Haiku-sufficient, even if not fully achievable" wording, **When**
   checked against §5's existing decision, **Then** the correction states plainly that running
   narration on Haiku is rejected, not deferred.

### User Story 2 - The real target is checkable by inspection, not by running a model (Priority: P1)

The actual target — the capable model's job shrinks to exactly what needs narrative judgement —
needs a stated, concrete verification method.

**Why this priority**: Without one, "the target is met" would be an unfalsifiable claim.

**Independent Test**: Read the verification method; confirm it points at an actual existing
audit (#188's code/prose classification) rather than inventing a new one.

**Acceptance Scenarios**:

1. **Given** the CLI surface #187/#188/#192 already specify, **When** checked against §5's
   tiering table, **Then** everything with a computable answer is already off the capable
   model's plate — confirmed by inspection of the existing classification, not a live run.

### Edge Cases

- Does this earn an ADR? No — §5's decision (GM session stays capable-model) already exists;
  this corrects a looser restatement of it, it does not decide anything new.
- Is "the capable model's narration running on a cheaper model" a deferred goal? No — explicitly
  stated as rejected, not merely unachieved, since restating it as deferred would misrepresent an
  already-settled decision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The model-tiering target MUST be stated as "the capable model's job shrinks to
  exactly what needs narrative judgement," not "the session runs on a lightweight model."
- **FR-002**: The epic's own looser "Haiku-sufficient" framing MUST be explicitly corrected, not
  silently left to imply something §5 already rejected.
- **FR-003**: Verification MUST be stated as an audit of the CLI surface against §5's own
  tiering table (reusing #188's existing code/prose classification), not a new mechanism.
- **FR-004**: What is NOT a goal (narration itself running on a smaller model) MUST be stated
  plainly as rejected, not implied as merely deferred.

### Key Entities

*(none — this feature is a design-document reconciliation, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `27-tooling.md` §5 gains a subsection stating the corrected target precisely.
- **SC-002**: The verification method is stated as an audit, reusing #188's existing
  classification.
- **SC-003**: What is rejected (not deferred) is stated explicitly.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: §5's decision (GM session stays on the capable model) already exists and is not being
  changed — this corrects a looser restatement of it against the same, already-stated reasoning.
- This is a design specification, not an implementation.
