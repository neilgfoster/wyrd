# Feature Specification: Combination and minmaxing playtest pass

**Feature Branch**: `054-combination-minmaxing-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Combination and minmaxing playtest pass (closes #153, part of the playtest epic #134, depends on #147-#151). Hunts for edge cases and minmaxing exploits at the seams between mechanics, not re-proving any one in isolation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A deliberate minmax attempt at the seam between three reroll mechanics is played with real dice (Priority: P1)

Someone worried a player could stack every reroll-granting resource (the Bargain, Resolve,
Fortune) on one failed roll wants that tested directly across multiple real trials, not argued
from the rules text alone.

**Why this priority**: This is the epic's own distinguishing purpose — CLAUDE.md records the one
existing playtest correcting the resolution mechanic three times inside two rolls, "none of it
visible on paper," exactly the class of fault only combination play surfaces.

**Independent Test**: Read the new section's stacking-trials table; confirm every independent
trial is reported (not a curated single result), including at least one trial that exhausts the
full stack and still fails.

**Acceptance Scenarios**:

1. **Given** a fixed test setup (skill, difficulty, starting Taint/Resolve/Fortune), **When**
   several independent trials are run with real dice, **Then** every trial's full sequence and
   outcome is reported, whether or not it makes the intended point.
2. **Given** the trials show a material shift in success rate from stacking, **When** the
   finding is genuine (not a contrived worst case), **Then** it is raised as its own follow-up
   issue rather than resolved inline.

### User Story 2 - A scope boundary between two Omen-bearing mechanisms is confirmed, not assumed (Priority: P2)

Systems of power (an ordinary test) and the combat/opposed-test Omen modifier (ADR 0042) both
attach a consequence to an Ill Omen. Someone wants confirmation the two don't collide outside
their stated scopes.

**Why this priority**: A genuine place two independently-landed features could interact
unexpectedly — exactly the seam this pass exists to check.

**Independent Test**: Read the new section's confirming-check subsection; confirm a system of
power invoked outside combat/an opposed test is checked against ADR 0042's stated scope.

**Acceptance Scenarios**:

1. **Given** a system-of-power invocation outside combat and outside an opposed-test shape,
   **When** an Ill Omen occurs, **Then** only the Taint consequence applies — no combat/opposed-test
   roll modifier, confirming the scope boundary holds.

### Edge Cases

- Is every possible pairwise mechanic interaction tested? No — this pass hunts the interaction
  judged most likely to hide an exploit (reroll-resource stacking), not an exhaustive
  cross-product of #147-#152's mechanics against each other. Stated explicitly in "what this pass
  does not prove," not implied as exhaustive.
- Does this pass re-prove what #147-#151 already proved individually? No — it builds on Senna
  Vask's arc as already documented in §6-§11, without re-deriving any of those sections' own
  findings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching the established
  discipline.
- **FR-002**: The playtest MUST run multiple independent trials of a deliberately-stacked
  minmax attempt, reporting every trial (not a curated single result), including any trial that
  exhausts the full resource stack.
- **FR-003**: Any genuine combination-level gap found (a stacking behaviour with no stated
  pacing limit) MUST be reported as a finding and raised as its own follow-up issue, not fixed
  inline.
- **FR-004**: The playtest MUST confirm at least one scope boundary between two independently-landed
  mechanisms (systems of power's Ill-Omen-Taint vs. the combat/opposed-test Omen modifier) holds
  as stated, rather than assuming it from the two features' separate specs.
- **FR-005**: The playtest MUST NOT claim to be an exhaustive combination test — its actual
  coverage (one deliberately-chosen interaction, one scope-boundary confirmation) is stated
  plainly, not oversold.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering the
  reroll-stacking trials and the Omen-scope confirmation, following the existing document's
  established structure and tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, with all
  seven stacking trials reported in full.
- **SC-003**: The stacking finding is reported with a follow-up issue raised (#167).
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR of its own — the stacking gap's eventual resolution belongs to
  #167's own follow-up, not this playtest record.
- Documentation-only: no code changes; the roll-generation script is scratch tooling, not
  committed, matching the established precedent.
