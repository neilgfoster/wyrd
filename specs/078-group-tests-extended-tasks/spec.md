# Feature Specification: Group tests and extended tasks

**Feature Branch**: `224-group-tests-extended-tasks`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Group tests and extended tasks — implement the Group tests and Extended tasks subsections of docs/design/03-rules.md section 1 on top of the opposed-test resolution from #222/#223. Depends on #222. Part of #208/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A group acts as one, rolling once (Priority: P1)

When a whole party attempts something together, the GM tells the engine every member's skill
(or that a member has none relevant, tested at the untrained 10%) and which fictional question
applies — "the thing must get done" or "everyone must get through" — and the engine selects the
one skill the test is actually rolled against, then resolves it as a single opposed test.

**Why this priority**: This is the mechanic's entire point: "the party's composition shows in
the skill tested, never in the number of dice." A bug here (rolling more than once, or picking
the wrong member) breaks the guarantee the whole subsection exists to hold.

**Independent Test**: Call the group-skill selection directly with a list of member skills and a
mode, and confirm it returns the most- or least-capable value — no roll needed to verify the
selection itself.

**Acceptance Scenarios**:

1. **Given** members with skills [70, 45, 30] and "the thing must get done", **When** the group
   skill is selected, **Then** it is 70 (the most capable).
2. **Given** the same members and "everyone must get through", **When** the group skill is
   selected, **Then** it is 30 (the least capable).
3. **Given** a member with no relevant skill at all, **When** they are included in an "everyone
   must get through" test, **Then** they are tested at the untrained 10%, not excluded or
   treated as zero.
4. **Given** a selected group skill, **When** the group test resolves, **Then** it performs
   exactly one roll — the same single opposed test #222 already resolves, not one roll per
   member.

---

### User Story 2 - An extended task accumulates across intervals (Priority: P2)

When work does not resolve in one beat, the GM tracks a target degree count and, each interval,
resolves one test whose result adds to (or fails to add to) the running total: a success adds
its degrees, minimum 1; a failure adds nothing and spends the interval.

**Why this priority**: The doc is explicit this scales with skill in a way that must not be
hidden: "an extended task at a skill you barely have is not a long task, it is a wall." A
miscomputed minimum-1 or a failure that silently adds progress would erase that guarantee.

**Independent Test**: Call the extended-task interval resolution directly with a known progress,
target, and seed, and confirm the returned progress matches success/failure and the
minimum-1 rule, without needing a full multi-interval sequence.

**Acceptance Scenarios**:

1. **Given** progress 0, target 4, and a successful roll with degrees 2, **When** the interval
   resolves, **Then** progress becomes 2 and the task is not yet done.
2. **Given** progress 3, target 4, and a successful roll with degrees 0 (a bare success, same
   tens digit as the effective skill), **When** the interval resolves, **Then** progress becomes
   4 (the minimum-1 rule applies even though raw degrees was 0) and the task is done.
3. **Given** progress 2, target 4, and a failed roll, **When** the interval resolves, **Then**
   progress remains 2 — the interval is spent and gains nothing.
4. **Given** progress reaches or exceeds target, **When** the interval resolution reports its
   result, **Then** it reports the task as done.
5. **Given** any interval, **When** it resolves, **Then** the Wyrd die is read from that
   interval's own natural roll, exactly as any other test (no special-casing for extended
   tasks).

### Edge Cases

- What happens when a group test's declared members list is empty? A structured error — there
  is no meaningful "most capable of nobody."
- What happens when an extended-task interval is called with progress already at or past target?
  The interval still resolves normally (rolling once, per "one test per interval" — a caller is
  responsible for not calling another interval once `done` is already true, per the doc's "reach
  it and the work is done"); this feature does not itself refuse to roll an interval past target,
  since detecting "the GM kept rolling after done" is a caller discipline, not a state this
  function alone can enforce without knowing whether a new interval is a legitimate re-check.
- What happens when a declaration of `"removes_risk"` is supplied to an extended-task interval
  (via #223's existing opposed-test modifiers)? Treated as an automatic success worth the
  minimum 1 degree — `docs/design/03-rules.md` does not name this combination explicitly, so
  this feature documents it as an Assumption rather than inventing unstated behavior for a
  numeric degrees value that a no-roll result does not produce.
- What happens when every member's skill is supplied and the mode is unrecognized? A structured
  error — the mode is a closed two-value set ("most_capable" | "least_capable"), not free text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST select a group test's tested skill from a list of member skills:
  the maximum for "the thing must get done," the minimum for "everyone must get through."
- **FR-002**: A member with no relevant skill (represented as the caller passing no skill value
  for them) MUST be tested at the untrained 10%, not excluded from selection.
- **FR-003**: A group test MUST resolve as exactly one opposed test (reusing #222's
  `opposed_test`), never one roll per member.
- **FR-004**: An empty member list MUST be rejected with a structured error.
- **FR-005**: An unrecognized group-test mode MUST be rejected with a structured error.
- **FR-006**: An extended-task interval MUST resolve as exactly one opposed test per call,
  reusing #222/#223's existing resolution (so declaration and assistance already compose with
  an extended task's interval for free).
- **FR-007**: On a successful interval, the engine MUST add `max(1, degrees)` to progress — a
  bare success (degrees 0) still adds the minimum of 1.
- **FR-008**: On a failed interval, the engine MUST add 0 to progress.
- **FR-009**: The engine MUST report whether the task is done (`progress >= target`) after each
  interval, without mutating or storing progress itself — the caller owns persisting it across
  intervals.
- **FR-010**: The Wyrd die MUST be read from each interval's own natural roll, with no special
  handling distinct from any other test (i.e., no new Wyrd logic — this feature adds no new
  Wyrd-die code at all, it only calls through to #222's existing reading).
- **FR-011**: The CLI MUST expose both as `describe`-discoverable, catalog-driven verbs, per the
  established shape.
- **FR-012**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Group test result**: extends #222/#223's opposed-test result shape with `member_skills`,
  `mode`, and `selected_skill` (the value actually tested). Stateless.
- **Extended task interval result**: extends #222/#223's opposed-test result shape with
  `progress` (updated), `target`, `gained` (degrees actually added this interval), and `done`.
  Stateless — the caller (a later feature's state layer) persists `progress` across intervals;
  this feature reads no chronicle state and writes none, matching #222/#223's precedent.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 50 distinct member-skill lists, the selected skill exactly matches
  `max(skills)` or `min(skills)` per mode, with zero deviation, and a missing-skill member is
  always treated as exactly 10.
- **SC-002**: A group test performs exactly one call to the underlying dice primitive, verified
  directly (not inferred from output), regardless of how many members are listed.
- **SC-003**: Across a spread of degrees values (0 through 9) on a successful interval, progress
  gain is `max(1, degrees)` exactly, with zero deviation — specifically confirming a degrees-0
  success still gains exactly 1, not 0.
- **SC-004**: A failed interval never changes progress, across at least 20 distinct failing
  seeds.
- **SC-005**: `done` is `true` if and only if resulting progress is `>= target`, checked at the
  boundary (progress exactly equal to target) and one below it.

## Assumptions

- A `"removes_risk"` declaration on an extended-task interval is treated as an automatic success
  worth the minimum 1 degree, since the doc does not define a numeric degrees value for a
  no-roll result and "a success adds its degrees, minimum 1" is the closest existing rule.
- Which fictional question applies ("must get done" vs. "everyone must get through") is a
  GM/model judgment about the scene, supplied by the caller as an explicit mode string — this
  feature does not infer it from anything.
- The Extended tasks scope-to-target table (a night's work: 2, a season's work: 4, a great
  labour: 6) is presentational guidance for the GM choosing a target, not something this
  feature's stateless interval function needs to encode itself — the caller supplies whatever
  integer target it has already chosen (following #223's precedent of not encoding every
  documented table as a mandatory lookup when the caller can simply pass the resulting number).
- Persisting progress across real intervals (so a chronicle can resume an extended task after a
  session break) is out of scope — this feature returns updated progress for the caller to
  persist, the same state-I/O boundary #222/#223 already drew for their own results.
- Following #221/#222/#223's precedent: Python 3.11+, standard library only, stdlib `unittest`,
  no pytest, catalog-driven CLI dispatch, no state I/O.
