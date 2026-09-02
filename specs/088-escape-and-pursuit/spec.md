# Feature Specification: Escape and pursuit

**Feature Branch**: `088-escape-and-pursuit`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Escape and pursuit — implement the group-test resolution for getting away from a scene entirely, per docs/design/03-rules.md §2, building on #244's single-opponent breaking-off."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Escaping a pursued scene (Priority: P1)

The party wants to leave a fight entirely rather than breaking off one opponent at a time. Whether
they get away depends on how many opponents are able and willing to give chase, and on the whole
party's slowest member — one bad roll at the back can bring the whole group back into the fight.

**Why this priority**: This is the entire feature. Without it, the only way to leave a scene is
one parting blow at a time (#244), with no way to escape as a group.

**Independent Test**: Resolve an escape attempt against one pursuer, with a seed that produces a
success, and confirm the party leaves the scene with no further consequence.

**Acceptance Scenarios**:

1. **Given** a party attempting to leave a scene with exactly one pursuer able and willing to
   follow, **When** the escape is resolved, **Then** it is tested as a group test at Challenging
   difficulty.
2. **Given** a party attempting to leave a scene with multiple pursuers able and willing to
   follow, **When** the escape is resolved, **Then** the difficulty is one rung harder than
   Challenging for each pursuer beyond the first.
3. **Given** a successful escape, **When** the result is applied, **Then** the party has left the
   scene and no fight state remains to resume.
4. **Given** a failed escape, **When** the result is applied, **Then** the fight resumes exactly
   where the slowest member of the party was, with no other change to who was engaged with whom.

### User Story 2 - No one able or willing to follow (Priority: P2)

Sometimes nothing is left in a state to chase, or nothing that remains wants to. The party should
simply be able to leave, without a roll standing between them and safety they have already
earned.

**Why this priority**: Named explicitly in the ladder ("no one able or willing to follow: no
test"). Skipping this case would force a roll the fiction has already resolved.

**Independent Test**: Resolve an escape attempt with an empty pursuer list and confirm no test is
rolled and the party simply leaves.

**Acceptance Scenarios**:

1. **Given** no pursuer is able or willing to follow, **When** the escape is resolved, **Then** no
   test is rolled and the party leaves the scene unconditionally.

### Edge Cases

- What happens with a very large pursuer count (more than the ladder has named rungs below Very
  Hard)? The ladder bottoms out at Very Hard; a sixth-or-later pursuer does not push difficulty
  past it (there is no rung below Very Hard to move to).
- What happens when the party has only one member? The "everyone must get through" shape still
  applies — the group test's selected skill degenerates to that one member's own skill, which is
  exactly how `group_test`'s existing selection already behaves for a single-member list.
- What happens when a member of the party has no relevant skill at all for the test being rolled?
  Handled already by the existing `select_group_skill`/`group_test` machinery (untrained rate
  substituted, never excluded) — this feature does not change that behaviour.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST resolve an escape-the-scene attempt as a group test in the
  "everyone must get through" shape (the party's slowest member sets the pace), reusing the
  existing `group_test`/`select_group_skill` mechanism rather than a new resolution mechanic.
- **FR-002**: The system MUST set escape difficulty from the count of pursuers able and willing to
  follow: one pursuer is Challenging; each additional pursuer is one rung harder on the existing
  difficulty ladder (Challenging → Difficult → Hard → Very Hard), with Very Hard as the floor for
  four or more pursuers.
- **FR-003**: The system MUST skip the test entirely when no pursuer is able and willing to
  follow — the party leaves the scene with no roll.
- **FR-004**: On a successful escape, the system MUST report that the party has left the scene.
- **FR-005**: On a failed escape, the system MUST report that the fight resumes, with the
  resuming position being wherever the slowest party member (the member whose skill was selected
  for the group test) already was, and with no other change to engagement or position state.
- **FR-006**: The system MUST NOT alter or reimplement `group_test`'s or `select_group_skill`'s
  own selection or roll behaviour; this feature only supplies the difficulty input and interprets
  the result.

### Key Entities

- **Escape attempt**: the act of a party trying to leave a scene entirely, characterized by the
  party's member skills for the relevant escape/evasion capability, and the number of pursuers
  able and willing to follow.
- **Pursuer**: an opponent capable of, and choosing to, continue the chase if the party attempts
  to leave. Only pursuers meeting both conditions count toward the difficulty ladder.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An escape attempt against any pursuer count from zero through five-or-more resolves
  to exactly the difficulty (or no-test) the ladder specifies, verified by a scripted check
  against every count in that range.
- **SC-002**: A failed escape leaves engagement and position state unchanged except for resuming
  at the slowest member's position, verified by a seeded scenario asserting state before and
  after are identical apart from that.
- **SC-003**: A successful escape and the no-pursuer case both leave no residual fight state to
  resume, verified by a seeded scenario for each.

## Assumptions

- "Able and willing to follow" is supplied by the caller as a pursuer count (or equivalent), not
  computed by this feature — deciding which specific opponents are able/willing is a fiction-level
  GM judgement call outside this feature's scope, consistent with how `select_group_skill`
  already leaves "who is left behind" to the caller.
- The skill tested for the group test is the party's existing escape/evasion-relevant skill per
  member, supplied by the caller the same way `group_test` already expects `member_skills` —
  this feature does not introduce a new skill name or select which skill is relevant.
- The crowd rule (#4) is explicitly out of scope, per the driving issue.
- "The slowest member" is the party member whose skill `select_group_skill` selected for the
  test (the `"least_capable"` mode, matching "everyone must get through" — the party is only as
  fast as its slowest member).
