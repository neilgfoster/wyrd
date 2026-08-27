# Specification Quality Checklist: Systems-of-power costs paid only on a failed invocation

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

- The operator's own request fully scoped this feature (Resolve follows Strain; reflect through
  design; new playtest); no [NEEDS CLARIFICATION] markers were needed.
- A pre-existing, unrelated wording inconsistency was found and fixed while editing the worked
  example this feature touches directly: "the character's Strain drops by 2" should have read
  "rises by 2" (Strain is a harm track that grows from cost and only drops at a Rally; Resolve is
  a spendable pool that correctly drops when spent). Fixed alongside, not raised as a separate
  issue, since the edit was already touching that exact sentence.
