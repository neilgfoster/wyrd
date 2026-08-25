# Specification Quality Checklist: The adversary model

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

All items pass. Three `[NEEDS CLARIFICATION]` markers were carried out of the first draft rather
than guessed, and all three were answered in the clarification session of 2026-08-25 and folded into
the spec:

- **Q1** (unlisted-skill fallback) → a per-adversary **baseline**, now FR-006.
- **Q2** (does danger scale skill values) → **yes, both counts and skills**, `03-rules.md` §7 stands
  as published. This was answered against the drafting recommendation, and the objection that drove
  that recommendation — a percentage cannot be multiplied by a ratio, and an unbounded adjustment
  leaves the difficulty ladder — is carried forward as a requirement to satisfy rather than dropped:
  FR-013a (additive), FR-013b (identity-exact), FR-013c (bound computed before it is written down).
- **Q3** (traits) → a **closed effect vocabulary**, now FR-012.

The one thing this spec deliberately does *not* fix is the shape of the skill adjustment curve.
Choosing a round number here and computing afterwards is the fault `CLAUDE.md` records twice over;
the curve is derived in the plan from the party sizes and danger ratings a chronicle actually
produces.
