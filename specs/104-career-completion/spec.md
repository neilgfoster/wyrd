# Feature Specification: Career completion grants Stamina and a Mark

**Feature Branch**: `104-career-completion`

**Created**: 2026-09-08

**Status**: Draft

**Input**: Issue #278 — "Implements docs/design/03-rules.md section 6, Careers: completing a
career — every skill it grants at the 70% cap — grants +1 maximum Stamina and a permanent Mark,
tracked per career-instance, with maximum Stamina ceilinged at 10 (a completion past that still
grants its Mark)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Completing a career grants +1 maximum Stamina and a Mark (Priority: P1)

A character spends the advance that carries the last skill their career grants up to that
career's cap. The career is now complete, and the completion pays out at that moment: maximum
Stamina rises by one and a Mark is recorded against the career completed.

**Why this priority**: This is the whole power curve. Without it, #277's spends move numbers and
nothing durable is ever earned.

**Independent Test**: Drive a character from a fresh career to every granted skill at cap and
confirm exactly one Stamina gain and exactly one Mark, both landing on the spend that finished
the last skill and not before.

**Acceptance Scenarios**:

1. **Given** a career granting two skills at a 70% cap, with one already at 70% and the other at
   65%, **When** the character spends an advance raising the second to 70%, **Then** the career
   is complete, maximum Stamina is one higher, and one Mark naming that career has been recorded.
2. **Given** the same career with both skills below the cap, **When** the character spends an
   advance raising one of them, **Then** no Stamina is gained and no Mark is recorded — a career
   part-finished pays nothing.
3. **Given** a career whose granted skills the character has not all opened, **When** the last
   unopened one is opened at 25%, **Then** the career is not complete — opening is not reaching
   the cap — and nothing is granted.
4. **Given** a completion, **When** it pays out, **Then** the spend that triggered it still costs
   exactly one advance; the completion is a consequence of the spend, never a second charge.

---

### User Story 2 - A completion pays exactly once per career-instance (Priority: P1)

A character who has completed their career and stays in it earns nothing further from it. One who
leaves it unfinished and re-enters later starts a fresh instance, which grants nothing for the
abandoned one but can be completed on its own terms. One who completes a career twice across a
lifetime is paid twice.

**Why this priority**: "Tracked per career-instance" is the rule that keeps the power curve
bounded. Paying per *career* would under-reward a long chronicle; paying per *time the predicate
is true* would let a single career pay indefinitely.

**Independent Test**: Complete a career, then attempt further spends inside it, then change away
and back and complete it again; confirm exactly two payouts across the whole sequence.

**Acceptance Scenarios**:

1. **Given** a character whose current career is already complete and paid, **When** any further
   spend is made inside that career, **Then** no second Stamina gain and no second Mark occur.
2. **Given** a character who leaves a career with one skill short of the cap, **When** they later
   return to it and carry that skill to the cap, **Then** the completion pays — the fresh instance
   is judged on its own, not on how far the abandoned one got.
3. **Given** a character who completed Guard, changed away, returned to Guard and completed it
   again, **Then** they hold two Marks naming Guard and gained Stamina for each completion, up to
   the ceiling.
4. **Given** a character who leaves a career unfinished, **When** they leave, **Then** no payout
   occurs and the career history records that instance as not completed.

---

### User Story 3 - Maximum Stamina stops at ten; the Mark does not (Priority: P2)

A character deep into a long chronicle reaches maximum Stamina 10. Every career they complete
after that still grants its Mark, and grants no further Stamina.

**Why this priority**: The ceiling is what stops the only growing number in the engine from
growing without bound, and `tools/check_advancement.py` already computes where it lands.

**Independent Test**: Complete careers back to back from the starting maximum of 6 and confirm
Stamina converges to 10 while the Mark count keeps rising one per completion.

**Acceptance Scenarios**:

1. **Given** a character with maximum Stamina 9, **When** they complete a career, **Then**
   maximum Stamina is 10 and a Mark is recorded.
2. **Given** a character with maximum Stamina 10, **When** they complete a career, **Then**
   maximum Stamina is still 10 and a Mark is recorded.
3. **Given** a character starting at the creation value of 6, **When** they complete twelve
   careers, **Then** they hold twelve Marks and maximum Stamina 10 — the figures
   `tools/check_advancement.py` publishes.

---

### Edge Cases

- **A career granting no skills at all** — vacuously complete, and refused as a completion the
  engine will pay for: a career that grants nothing has nothing to finish. It is a setting-data
  fault, not a free Mark.
- **A skill carried in above the cap from an earlier career** — counts toward completion. The
  predicate is "at least the cap", not "exactly the cap"; #277 already established that a cap
  bounds raises and never claws back an earned percentage.
- **A skill dropped below the cap by a wound after completion** — the completion already paid and
  is never recomputed (docs/design/29-evolution.md). Re-raising it pays nothing further.
- **Completing a career at creation** — creation's eight advances cannot carry every granted skill
  to a 70% cap, so this cannot arise; the payout path is the spend path only.
- **The Mark's fictional content** — the GM's, exactly as a career change's fictional reason is.
  The engine records that a Mark was earned and which career earned it.
- **Current Stamina when maximum rises** — unchanged. A completion widens the vessel; recovery
  fills it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST treat a career as complete for a character exactly when the career
  grants at least one skill and the character holds every skill it grants at or above that
  career's cap.
- **FR-002**: When a spend brings the character's current career from not-complete to complete,
  the engine MUST grant, as part of that same spend, +1 maximum Stamina and one Mark.
- **FR-003**: The Mark recorded MUST name the career completed, and MUST be appended to the
  character's existing Marks rather than replacing them — Marks are permanent and accumulate.
- **FR-004**: Maximum Stamina MUST NOT be raised past 10. A completion at or above that ceiling
  MUST still grant its Mark.
- **FR-005**: A completion MUST pay at most once per career-instance. A career-instance begins
  when the character enters that career and ends when they leave it.
- **FR-006**: Changing career MUST begin a fresh, unpaid instance of the career entered, whatever
  the character's history with that career.
- **FR-007**: An accepted career change MUST record in the career history whether the departed
  instance was completed, taken from whether that instance actually paid out, never recomputed
  from the character's live skills.
- **FR-008**: A completion MUST NOT alter current Stamina, any skill percentage, or the advance
  cost of the spend that triggered it.
- **FR-009**: A spend that is refused MUST grant nothing, and MUST leave Stamina and Marks exactly
  as it found them.
- **FR-010**: The engine MUST NOT judge or supply the fictional content of a Mark.
- **FR-011**: No completion MUST mutate the caller's inputs.

### Key Entities

- **Career-instance**: one occupancy of a career by a character — entered on a change of career,
  left on the next one. Completion, and therefore payout, is a property of the instance, not of
  the career.
- **Mark**: a permanent record that a career-instance was completed, naming the career. Its
  mechanical weight is nil and its fictional weight is the GM's.
- **Maximum Stamina**: the only number in the engine that grows with advancement, bounded at 10.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Completing twelve career-instances from the creation value of 6 yields maximum
  Stamina 10 and twelve Marks — identical to the figures `tools/check_advancement.py` computes,
  asserted against that script rather than restated.
- **SC-002**: Stamina stops climbing at the fourth completion (6 → 10) and every completion after
  it still adds exactly one Mark.
- **SC-003**: Across any sequence of spends, the number of payouts equals the number of
  career-instances that reached completion — never the number of spends made while complete, and
  never the number of distinct careers completed.
- **SC-004**: Every refusal path leaves Stamina and Marks byte-identical to the inputs.

## Assumptions

- **The payout fires on the spend that completes the career**, not on leaving it. The rules call
  completion itself the reward's trigger, and a character who completes a career and stays in it
  for a further chronicle should not be waiting on a career change to be paid.
- **The instance's paid state is carried on the character view** as a single flag, and is what a
  career change writes into history — replacing #277's recompute-at-departure, which would have
  disagreed with the history record once a wound lowered a skill.
- **A Mark records the career, not a benefit.** The engine has no vocabulary for "one small
  benefit"; inventing one would be a mechanic docs/design/03-rules.md does not describe.
- **The starting maximum Stamina of 6 and the ceiling of 10 are not re-derived here** — they are
  `tools/check_advancement.py`'s figures and this feature asserts agreement with them.
- **Wound effects on `stamina_max` are computed elsewhere** (`character.active_wound_effects`) and
  are not folded into the stored maximum by this feature.
