# Tasks: Luck restoration rule

**Input**: Design documents from `/specs/034-luck-restoration-rule/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Not requested — this is a documentation-only decision (no code exists for this
mechanic per spec.md's Constraints). Validation is the quickstart.md read-through and
`tools/check_docs.py`, listed under Polish below.

**Organization**: One user story (spec.md has a single P1 story; the feature is small enough that
splitting it further would only fragment one paragraph edit and one ADR across phases).

## Phase 1: Setup

- [X] T001 Confirm the next ADR number by listing `docs/adr/` (already established in
      research.md/plan.md as 0039) and confirm no other in-flight branch has claimed it

## Phase 2: Foundational

*No foundational/blocking work — there is no shared infrastructure this feature depends on.*

## Phase 3: User Story 1 - Reading the rule settles what Luck spent this arc means (Priority: P1)

**Goal**: `docs/design/03-rules.md` §1 states explicitly that Luck resets to maximum at the start
of each top-level arc, and the decision is recorded as an ADR.

**Independent Test**: Read `03-rules.md` §1 top to bottom (quickstart.md Step 1); confirm the
restoration rule is stated with no follow-on question, and that it names the same "arc" boundary
`18-campaign.md` defines (quickstart.md Step 2).

- [X] T002 [US1] Write ADR 0039 at `docs/adr/0039-luck-resets-at-the-top-level-arc-boundary.md`,
      recording the decision (Luck resets to maximum at the start of each top-level arc), the
      rejected alternative (Luck never restores) and why, per research.md's Decision/Rationale/
      Alternatives — following the format of existing ADRs under `docs/adr/`
- [X] T003 [US1] Update `docs/design/03-rules.md` §1 (Luck) to state the restoration rule
      explicitly, referencing ADR 0039, immediately after the existing "costs 1 Luck for the rest
      of the arc, pass or fail" sentence
- [X] T004 [US1] Cross-check the new `03-rules.md` text against `docs/design/19-campaign.md`'s
      arc/era structure (spec.md Acceptance Scenario 2) and adjust wording only if needed so both
      documents describe the same top-level-arc boundary — do not alter `18-campaign.md` itself

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T005 Run `python3 tools/check_docs.py` and confirm a clean pass (spec.md SC-002) — no broken
      links, no orphaned document, ADR index picks up 0039
- [X] T006 Walk through `quickstart.md` end to end and confirm every expected outcome holds

## Dependencies & Execution Order

- T001 → T002 → T003 → T004 → T005 → T006 (strictly sequential: the ADR informs the design-doc
  wording, and both must exist before the document check can validate them)
- No tasks are parallelizable — this feature touches two files serially, one referencing the
  other's exact wording

## Implementation Strategy

**MVP = the whole feature.** There is only one user story, sized at roughly two files (one ADR,
one section edit) and one existing check script. Deliver it in one pass; there is no incremental
slice smaller than "the rule is stated" that has independent value.
