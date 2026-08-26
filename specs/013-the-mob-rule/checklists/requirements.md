# Specification Quality Checklist: The crowd rule

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-25
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

- Follows this repository's house shape (Context / Requirements / Constraints / Assumptions /
  Success criteria / Acceptance criteria) rather than the stock Spec Kit user-story template,
  matching `specs/010-*` through `specs/012-*`. The engine's "user" is a GM reading
  `doc/design/03-rules.md`, so a requirement *is* the scenario.
- Two requirements the issue did not name were added after reading the rule against the rest of §2:
  **FR-5**, that the crowd's own attacks cost no more rolls than the player's side, and **FR-9**,
  that the script assert agreement with the damage scale #44 established. FR-9 immediately caught a
  disagreement, so it was not ceremony.
- The *petty* rename question the issue raised is answered in the affirmative — the term is dropped
  — and the reasoning is in ADR 0019 rather than here, because that is where a rejected alternative
  belongs.
