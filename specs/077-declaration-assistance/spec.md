# Feature Specification: Declaration and assistance bonuses

**Feature Branch**: `223-declaration-assistance`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Declaration and assistance bonuses — implement the Declaration and Assistance subsections of docs/design/03-rules.md section 1 as modifiers on the opposed-test resolution from #222. Depends on #222. Part of #208/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A well-declared action earns its bonus (Priority: P1)

The GM (having judged, from the player's actual words, which declaration category applies —
specific, specific-and-leveraging, brief, against the character's nature, or so well-judged it
removes the risk) tells the engine which category applies, and the engine applies exactly that
category's fixed point value to the test — never a value derived from how much the player wrote.

**Why this priority**: This is the mechanic's entire point, per `docs/design/03-rules.md`:
"Never reward length; never penalise brevity." The engine's job is to hold a fixed, closed table
of point values so a category can never quietly become "however much text was declared."

**Independent Test**: Call the declaration lookup directly with each of the five categories and
confirm each returns exactly its documented value — no opposed test needed to verify the table
itself.

**Acceptance Scenarios**:

1. **Given** category "specific and in character", **When** looked up, **Then** the bonus is
   +10.
2. **Given** category "specific and leveraging something established", **When** looked up,
   **Then** the bonus is +20.
3. **Given** category "brief or unelaborated", **When** looked up, **Then** the bonus is 0 (no
   bonus, no penalty).
4. **Given** category "against the character's established nature", **When** looked up, **Then**
   the bonus is −20.
5. **Given** category "so well-judged it removes the risk", **When** looked up, **Then** no roll
   is called for at all — the action simply works.

---

### User Story 2 - A companion's help adds a scaled, capped bonus (Priority: P2)

When a companion assists a test, the engine computes their contribution as a tenth of their own
skill, rounded down, capped at +10 — never a flat bonus, and never more than one helper's worth
regardless of how many companions are present.

**Why this priority**: The doc is explicit this is a load-bearing balance number, not a taste
choice ("this is the rule that keeps the ladder meaning something") — a bug here (an
uncapped bonus, or a bonus that accumulates across helpers) silently deletes a difficulty rung
the GM chose.

**Independent Test**: Call the assistance lookup directly with a range of helper skills and
confirm the tenth-rounded-down-capped-at-10 formula, without needing an opposed test.

**Acceptance Scenarios**:

1. **Given** a helper with 30% skill, **When** their assistance is computed, **Then** the bonus
   is +3.
2. **Given** a helper with 45% skill, **When** their assistance is computed, **Then** the bonus
   is +4 (rounded down from 4.5).
3. **Given** a helper with 100% skill, **When** their assistance is computed, **Then** the bonus
   is capped at +10, not +10 exactly by coincidence of the formula.
4. **Given** a helper who could not attempt the task alone, **When** their assistance is
   computed, **Then** the bonus is 0 — someone who could not attempt it alone cannot improve
   someone who is attempting it.

---

### User Story 3 - Both modifiers apply to a real opposed test (Priority: P3)

A GM resolving an opposed test can supply a declaration category and/or a helper's skill, and
the opposed test resolves using the modified effective skill — without needing to hand-compute
the combined bonus first.

**Why this priority**: Lowest priority because it's wiring, not new logic — #222's opposed test
already does the real work once given a modified skill; this user story only confirms the two
lookups from US1/US2 compose correctly into that existing call.

**Independent Test**: Call the opposed-test resolution with a declaration category and a
helper's skill supplied, and confirm the resulting `effective_pct` reflects both bonuses added to
the base skill before the existing opposed-test formula runs.

**Acceptance Scenarios**:

1. **Given** a skill of 50, a "specific and in character" declaration (+10), and a helper's
   skill of 45 (+4), **When** the opposed test resolves against an opponent of 50, **Then**
   `effective_pct` reflects an effective skill of 64 (50 + 10 + 4), clipped as #222 already
   clips.
2. **Given** a "so well-judged it removes the risk" declaration, **When** the opposed test is
   asked to resolve, **Then** no roll is made and the result reports automatic success.
3. **Given** neither a declaration nor a helper supplied, **When** the opposed test resolves,
   **Then** the result is identical to calling #222's opposed test with no modifiers at all —
   this feature must not change existing behavior for callers that don't use it.

### Edge Cases

- What happens when an unrecognized declaration category is supplied? A structured error, not a
  silent zero bonus — an unrecognized category is a caller bug, not a legitimate "no bonus"
  case (distinct from the legitimate "brief" category, which *is* zero).
- What happens when more than one helper is described? Out of scope for this feature to enforce
  in code — "one does" is a rule about play, and this feature's assistance lookup takes exactly
  one helper's skill by design (a second call with a second helper is a caller error, not
  something this feature detects or prevents, since detecting "a second helper already applied
  this beat" requires state this feature does not hold).
- What happens when a helper's skill is 0 or the helper could not attempt the task? The
  assistance bonus is 0, per Acceptance Scenario 4 above.
- What happens when both a declaration and a helper are supplied alongside an opponent
  baseline that already sits far from the acting skill? The combined bonus is added to skill
  before #222's existing `effective_pct` clip runs — the clip still bounds the final result to
  [5, 95], so stacking modifiers cannot push a test outside that range.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a lookup from a closed set of five declaration categories
  to a fixed point value: "specific" → +10, "specific_leveraging" → +20, "brief" → 0,
  "against_nature" → −20, "removes_risk" → no roll (automatic success).
- **FR-002**: The declaration lookup MUST reject a category outside that closed set with a
  structured error, not a default value.
- **FR-003**: The engine MUST provide a lookup from a helper's skill (and whether they could
  attempt the task) to an assistance bonus: `min(helper_skill // 10, 10)` if they could attempt
  it, else 0.
- **FR-004**: The assistance bonus MUST never exceed +10, regardless of helper skill.
- **FR-005**: The opposed-test resolution from #222 MUST accept an optional declaration category
  and an optional helper skill, adding both resulting bonuses to the acting skill before
  computing `effective_pct` — existing callers that supply neither MUST see identical behavior
  to before this feature (no default change to `opposed_test`'s existing three-argument form).
- **FR-006**: When the declaration category is "removes_risk", the opposed-test resolution MUST
  perform no roll at all and report automatic success.
- **FR-007**: The CLI MUST expose both lookups as `describe`-discoverable, and the opposed-test
  CLI verb MUST accept the new optional declaration/helper-skill inputs, per the catalog-driven
  shape #221/#222 already established.
- **FR-008**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Declaration bonus**: a closed-set category → fixed point value (or "no roll") mapping. Pure,
  stateless — no chronicle state read or written.
- **Assistance bonus**: a helper skill (+ can-attempt flag) → capped point value mapping. Pure,
  stateless.
- **Modified opposed test**: #222's existing result shape, extended with `declaration` and
  `helper_skill` fields recording what was supplied (or `null`/absent if neither), and a
  `no_roll` field for the automatic-success case.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each of the five declaration categories returns its documented value (or no-roll
  behavior) with zero deviation, across all five cases.
- **SC-002**: For helper skills 0, 10, ..., 100 (11 values), the assistance bonus matches
  `min(skill // 10, 10)` exactly, with zero deviation, confirming the +10 cap binds at 100% and
  nowhere below it prematurely (per `specs/011-assistance-and-group-tests/check_assistance.py`'s
  own finding that a wrongly-placed cap silently flattens the scaled bonus).
- **SC-003**: An opposed test called with no declaration and no helper produces byte-identical
  results to #222's pre-existing call shape, for 100 repeated (skill, opponent, seed) triples.
- **SC-004**: An opposed test called with "removes_risk" performs zero rolls (verified by a call
  count on the underlying dice primitive) and reports success.

## Assumptions

- Which declaration category applies to a given in-character statement is a GM/model judgment
  call this feature does not make — per `docs/design/27-tooling.md`'s deterministic-over-inference
  split, the engine's job is only the point value *given* a category, never classifying prose
  into a category. The caller (GM/model) supplies the category.
- Likewise, whether a helper "could attempt the task alone" is supplied by the caller as a
  boolean, not derived — the engine does not yet hold the character/skill data (#209, not yet
  built) needed to determine that itself.
- "One does" (only one helper's bonus ever applies) is a play-time rule for the GM to follow when
  deciding what to pass in, not a runtime constraint this feature's stateless functions can
  enforce (they see one call at a time, not a beat's full history).
- Group tests and extended tasks (`docs/design/03-rules.md`'s next two subsections) are out of
  scope — separate children of #208 (#224).
- Following #221/#222's precedent: Python 3.11+, standard library only, stdlib `unittest`, no
  pytest, catalog-driven CLI dispatch, no state I/O (this feature's functions are pure, matching
  #222's `opposed_test`).
