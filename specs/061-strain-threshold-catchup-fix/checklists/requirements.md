# Specification Quality Checklist: Fix the Strain-threshold check so a success cannot erase a Trauma crossing

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-27
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

- The operator's own request fully scoped this feature (fix, ADR, playtest, one PR); no
  [NEEDS CLARIFICATION] markers were needed.
- The first implementation of the fix (a separate "already charged" counter) was found subtly
  wrong during verification — undercounting in some sequences — and replaced with a simpler form
  (comparing cumulative Strain directly, no counter needed) that gives the same, correct answer.
  Caught by re-deriving the arithmetic by hand rather than trusting the first draft, matching
  CLAUDE.md's own "check the maths" precedent.
