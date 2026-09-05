# Feature Specification: Spend advances — raise, open, change career

**Feature Branch**: `103-spend-advances`

**Created**: 2026-09-05

**Status**: Draft

**Input**: Issue #277 — "Implements docs/design/03-rules.md section 6, Spending: 1 advance raises
a granted skill by +5% to its career cap, opens a new granted skill at 25%, or changes career —
freely to any entry career, or to a non-entry career whose prerequisites the character satisfies."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One advance raises a granted skill by +5% (Priority: P1)

A character with an unspent advance and Blade already open spends it to raise Blade by 5%. The
engine takes the advance, moves the skill, and refuses the spend outright if the skill is not one
this career grants or if the raise would carry it past that career's cap.

**Why this priority**: Raising is the commonest spend in play, and it is the one that has a
boundary — the career cap — that a character actually reaches.

**Independent Test**: Raise an open skill repeatedly from a fresh balance and confirm each spend
costs exactly one advance, moves the skill by exactly 5%, and is refused at the cap.

**Acceptance Scenarios**:

1. **Given** a character with 1 unspent advance and Blade at 30% under a career granting Blade at
   a 70% cap, **When** they spend on raising Blade, **Then** Blade is 35% and unspent advances
   are 0.
2. **Given** a character with Blade at that career's cap, **When** they spend on raising Blade,
   **Then** the spend is refused, the advance is not taken, and the refusal names the cap.
3. **Given** a skill the character's career does not grant, **When** they spend on raising it,
   **Then** the spend is refused naming that the career does not grant it — including when the
   character already holds that skill from an earlier career.
4. **Given** a character with 0 unspent advances, **When** any spend is attempted, **Then** it is
   refused for want of an advance and nothing changes.

---

### User Story 2 - One advance opens a new granted skill at 25% (Priority: P1)

A character spends an advance to open a skill their career grants but which they have never
trained, and it begins at 25%.

**Why this priority**: Opening and raising are the two halves of the same currency; a career
cannot be completed without opening every skill it grants.

**Independent Test**: Open an unheld granted skill from a fresh balance and confirm it lands at
25%; attempt to open one already held and confirm refusal.

**Acceptance Scenarios**:

1. **Given** a career granting Watch and a character who does not hold Watch, **When** they spend
   on opening Watch, **Then** Watch is 25% and unspent advances fall by 1.
2. **Given** a character who already holds Watch at any percentage, **When** they spend on opening
   Watch, **Then** the spend is refused as already open — the raise action is the one that moves
   an open skill.
3. **Given** a skill the career does not grant, **When** they spend on opening it, **Then** the
   spend is refused; a career never opens a skill outside its own grant list.

---

### User Story 3 - One advance changes career (Priority: P1)

A character spends an advance to leave their career for another. Any entry career is always
available. A non-entry career is available only when the character has completed at least one of
the careers it names as prerequisites.

**Why this priority**: This is the rule that makes the career graph a graph rather than a list,
and it is the only spend whose legality depends on the character's history rather than their
current sheet.

**Independent Test**: From a character with a known completed-career history, attempt a change to
an entry career, to a reachable non-entry career, and to an unreachable non-entry career, and
confirm the three outcomes.

**Acceptance Scenarios**:

1. **Given** any character with an advance to spend, **When** they change to a career declared as
   an entry career, **Then** the change is accepted whatever their history — starting over from a
   fresh entry point is always legal.
2. **Given** a character who has completed Guard, and a career Guard-Captain whose prerequisites
   are Guard or Soldier, **When** they change to Guard-Captain, **Then** the change is accepted —
   completing any one listed prerequisite qualifies.
3. **Given** a character who has completed neither Guard nor Soldier, **When** they change to
   Guard-Captain, **Then** the change is refused naming the prerequisites they do not satisfy.
4. **Given** a character who *entered* Guard but left it unfinished, **When** they change to
   Guard-Captain, **Then** the change is refused — eligibility keys off a career completed, never
   a career merely held.
5. **Given** an accepted career change, **When** it is applied, **Then** the career left is
   recorded in the character's career history with whether it was completed, the new career
   becomes the current one, and no skill percentage is altered by the change itself.
6. **Given** a change naming a career absent from the setting's career table, **When** it is
   spent, **Then** it is refused naming the unknown career.

---

### Edge Cases

- **A skill held from an earlier career that the current career does not grant** — it stays on the
  sheet at its earned percentage and is simply unspendable-on until a career granting it is held
  again. Skills are never lost by changing career, and never raised by an advance the current
  career does not authorise.
- **A skill held above the new career's cap** — legal and untouched. A cap bounds what an advance
  may *raise* a skill to; it never claws back a percentage already earned under a more generous
  grant.
- **Re-entering a career already completed once** — legal. Eligibility once earned never expires,
  and the fresh instance is a fresh instance; what it grants on a second completion belongs to
  #278.
- **Changing career with the current career complete** — the completion is recorded in history as
  the character leaves, which is what a later prerequisite check reads.
- **A spend of an action the engine does not know** — refused naming the three spends there are.
  There is no fourth thing an advance buys.
- **The fictional reason for a career change** — required by the rules, judged by the GM. The
  engine verifies legality only, exactly as the award side never judges whether a trigger fired.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST recognise exactly three spends — raise a skill, open a skill, change
  career — each costing exactly 1 advance, and refuse any other named spend.
- **FR-002**: Every spend MUST be refused, with nothing changed, when the character has no unspent
  advance.
- **FR-003**: A raise MUST move the named skill by exactly +5%, MUST require the skill already
  open, MUST require the current career (optionally widened by ancestry) to grant it, and MUST be
  refused when the result would exceed that grant's cap.
- **FR-004**: An open MUST set the named skill to 25%, MUST require the current career (optionally
  widened by ancestry) to grant it, and MUST be refused when the character already holds it.
- **FR-005**: A change of career to a career declared `entry: true` MUST always be accepted.
- **FR-006**: A change to a non-entry career MUST be accepted exactly when at least one career
  named in its `prerequisites` is recorded complete in the character's career history, and refused
  otherwise.
- **FR-007**: A change to a career not present in the setting's career table MUST be refused.
- **FR-008**: An accepted change MUST append the departed career to the career history, recording
  whether it was complete at departure, and MUST leave every skill percentage untouched.
- **FR-009**: A career MUST be judged complete for a character exactly when every skill it grants
  is held at that career's cap.
- **FR-010**: Every refusal MUST name which rule refused it, distinctly enough that a caller can
  tell an unaffordable spend from an illegal one.
- **FR-011**: The engine MUST NOT judge the fictional reason offered for a career change.
- **FR-012**: No spend MUST mutate the caller's inputs; a refusal leaves the character exactly as
  it found it.

### Key Entities

- **Spend**: one of the three purchases an advance buys, each priced at 1.
- **Career**: an id, an `entry` flag, a skills grant with a cap, and — for a non-entry career —
  the prerequisite careers completing any one of which grants eligibility
  (docs/design/24-authoring-a-setting.md).
- **Career history entry**: a career the character has left, and whether it was complete when they
  left it — the record eligibility is computed from.
- **Unspent advances**: the balance #276 mints and this feature is the only consumer of.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A skill opened at 25% reaches a 70% cap in exactly 9 further advances, and the
  tenth is refused — the same figure `tools/check_advancement.py` already publishes.
- **SC-002**: Every one of the three spends costs exactly 1 advance, and no accepted spend leaves
  the balance unchanged.
- **SC-003**: For any career table, a change to an entry career succeeds from every history, and a
  change to a non-entry career succeeds exactly on the histories containing one of its declared
  prerequisites as complete.
- **SC-004**: Every refusal path leaves the character's skills, career, career history and balance
  byte-identical to the inputs.

## Assumptions

- **Ancestry widening applies to a spend as it does at creation.** `career.effective_cap` already
  takes an optional ancestry that widens which skills are grantable and never narrows a cap; a
  spend reuses that function rather than a second eligibility rule.
- **Career completion's rewards are #278's.** This feature supplies the predicate for "complete"
  because eligibility cannot be computed without it, and grants nothing for it — no Stamina, no
  Mark, no per-instance ledger beyond the completed flag a history entry carries.
- **The career table is supplied by the caller**, the way a career dict already is at creation.
  Loading `careers.yaml` and validating the graph's acyclicity belongs to the setting-loading
  work, not here.
- **Spends are one at a time.** There is no batch allocation after creation; creation's 8-advance
  allocation validator stays the only bulk path.
- **Where a spend is offered in the session loop** — at a Rally, at downtime — belongs to #219.
