# Specification Quality Checklist: The Aftermath table

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-22
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Items marked incomplete require spec updates before `/kord-feature-clarify` or
  `/kord-feature-plan`.
- **All four open decisions were resolved by the operator** in the 2026-08-22 clarification session
  and are recorded under `## Clarifications` in the spec:
  1. File path — `docs/design/09-aftermath.md`, per #15's index (FR-001).
  2. The roll — `d100 + (5 × points below zero)`, lowest possible total 6 (FR-002, FR-003, FR-004).
  3. Fate — closes the death rows, does not suppress the roll (FR-016).
  4. Companions — same table, same rows, no Fate of their own (FR-017).
- **Follow-up for the operator**: issue #16's acceptance criteria still names
  `design/03a-1-aftermath.md`. That line is stale and should be corrected on the issue so the board
  does not disagree with the merged index.
- **Carried into planning**: the row ranges themselves and the outcome distribution are not fixed by
  the spec. FR-026 and SC-004 require both to be computed by a script against the rows as written,
  across the realistic range of modifiers, before the document is considered done.
