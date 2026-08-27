# Feature Specification: Review all playtest findings and resolve outstanding gaps

**Feature Branch**: `055-playtest-findings-synthesis`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Review all playtest findings and resolve outstanding gaps (closes #162, part of the playtest epic #134, depends on #147-#153 all closed). Read every playtest's Findings section together, confirm every real gap has either been fixed or has its own tracked follow-up issue, flag any finding that recurred across more than one playtest."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every finding from every playtest is accounted for, in one place (Priority: P1)

Someone who has followed the playtest epic across seven separate PRs wants a single place that
confirms nothing fell through: every real gap either landed a fix or has its own tracked,
board-ranked follow-up issue.

**Why this priority**: This is #162's own stated purpose — a synthesis pass across all seven
playtests' output, not a repeat of any one of them.

**Independent Test**: Read the new synthesis section; confirm it lists every distinct finding
from §6–§12's Findings subsections, with its tracked-issue status.

**Acceptance Scenarios**:

1. **Given** every playtest's Findings subsection, **When** read together, **Then** each
   distinct finding is listed with its current tracking status (fixed, open and tracked, or
   resolved by the playtest's own stated reasoning).
2. **Given** the complete list, **When** cross-checked against the actual open GitHub issues
   (not just what's named in the playtest prose), **Then** no finding is left untracked.

### User Story 2 - A finding that recurred across more than one playtest is called out explicitly (Priority: P1)

Someone wants to know whether any gap surfaced independently more than once — a stronger signal
than a single mention, and exactly what #162 was raised to check for.

**Why this priority**: #162's own acceptance criteria explicitly require this check, not just an
inventory.

**Independent Test**: Read the new section's recurrence subsection; confirm at least the known
recurrence (the Resolve gap, found independently in §8 and §10) is named, and any other genuine
recurrence found during the review is named alongside it.

**Acceptance Scenarios**:

1. **Given** the Resolve gap (found in §8, recurring in §10), **When** the synthesis runs,
   **Then** it is named as a recurrence, not just listed twice as two separate findings.
2. **Given** a thematic (not identical) recurrence — #163 and #167 both being instances of "no
   pacing limit on repeated spend" — **When** found during the review, **Then** it is named and
   cross-referenced on both issues, even though the two findings are not the same bug.

### Edge Cases

- Does this feature fix #155, #163, or #167 itself? No — each names a real, workable rejected
  alternative and a genuine design consequence, exactly what CLAUDE.md's own test says an ADR is
  for. Per #162's own Definition of Done, resolving any of them belongs to that issue's own
  feature, not to this synthesis pass.
- Does this feature re-run any playtest? No — #162 explicitly forbids it; this reviews what
  already happened.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every distinct finding across `docs/design/30-playtest-transcript.md` §6–§12's
  Findings subsections MUST be listed, with its current tracking status.
- **FR-002**: Each finding's tracked-issue status MUST be confirmed against the actual GitHub
  issue state (open/closed), not assumed from the playtest prose alone.
- **FR-003**: Any finding that recurred across more than one playtest — identical or thematic —
  MUST be named explicitly, with cross-references added to the affected issues.
- **FR-004**: This feature MUST NOT resolve #155, #163, or #167 — each requires its own design
  decision and belongs to its own tracked issue.
- **FR-005**: This feature MUST NOT re-run or re-derive any of §6–§12's own playtest content.

### Key Entities

*(none — this feature is a synthesis document, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section listing every finding
  from §6–§12 with its tracked-issue status, verified against live GitHub issue state.
- **SC-002**: At least two recurrences are named explicitly: the Resolve gap (§8/§10, identical)
  and the repeated-spend pacing theme (#163/#167, thematic) — cross-referenced on both affected
  issues.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.
- **SC-004**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR — it makes no design decision, only a synthesis and cross-reference
  pass, per #162's own Definition of Done.
- Documentation-only: no code changes.
