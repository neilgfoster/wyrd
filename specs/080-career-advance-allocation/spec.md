# Feature Specification: Career graph and advance allocation

**Feature Branch**: `231-career-graph-advance-allocation`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Career graph and advance allocation — implement a career/ancestry data shape and a deterministic validator for the 8-advance allocation from docs/design/11-character-creation.md section 3. Depends on #229. Part of #210/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A career declares what it grants (Priority: P1)

A career is described by the skills it grants (each with the cap it bounds that skill to) and
whether it is a legal starting point. The engine holds this shape so both creation and
advancement can read it the same way.

**Why this priority**: Everything else in this feature checks an allocation *against* a career's
declared skills and caps — without the shape, there's nothing to validate against.

**Independent Test**: Construct a career value directly and confirm its skills and caps are
readable — no allocation logic needed to verify the shape itself.

**Acceptance Scenarios**:

1. **Given** a career declaring skills `{"stealth": 55, "swordplay": 45}` (name → cap), **When**
   its skills are read, **Then** both are present with their declared caps.

---

### User Story 2 - An 8-advance allocation is validated, not generated (Priority: P1)

The GM/player chooses how to spend 8 advances inside a career (optionally widened by an
ancestry); the engine checks that choice against every documented rule and reports exactly which
rule failed if it's invalid, rather than silently accepting or correcting it.

**Why this priority**: Per ADR 0014, "a character is chosen, not generated" — this is the whole
point of the feature, and the one place a bug would let an out-of-band character (a skill above
its cap, more or less than 8 spent) into play unnoticed.

**Independent Test**: Construct an allocation and a career directly, call the validator, and
confirm it reports valid or the specific violated rule — no full creation procedure needed.

**Acceptance Scenarios**:

1. **Given** a career granting `stealth` (cap 55) and `swordplay` (cap 45), and an allocation
   that opens both then raises `stealth` four more times and `swordplay` two more times (2 opens
   + 6 raises = 8 total), **When** validated, **Then** it is accepted, with `stealth` at 45%
   (25 + 4×5) and `swordplay` at 35% (25 + 2×5).
2. **Given** the same career, **When** an allocation totals 7 or 9 actions, **Then** it is
   rejected, naming the total spent.
3. **Given** the same career, **When** an allocation opens only one skill (however many actions
   spent), **Then** it is rejected — at least two skills must be opened.
4. **Given** the same career, **When** an allocation tries to raise `swordplay` (cap 45) past
   45%, **Then** it is rejected, naming the skill and its cap.
5. **Given** the same career, **When** an allocation acts on a skill the career does not grant
   and no ancestry covers, **Then** it is rejected, naming the skill.
6. **Given** the same career plus an ancestry granting `herbalism`, **When** an allocation opens
   `herbalism` (in addition to two career skills, still totalling 8), **Then** it is accepted —
   the ancestry widens which skills are eligible, without adding to the 8-advance budget.
7. **Given** an allocation that tries to open a skill already open, **When** validated, **Then**
   it is rejected — opening is a one-time action per skill, not repeatable.
8. **Given** an allocation that tries to raise a skill not yet open, **When** validated, **Then**
   it is rejected — raising requires the skill already be open.

### Edge Cases

- What happens when the career grants zero skills? Any allocation against it is rejected —
  there is nothing to open, so the two-skills-minimum can never be met (a career this thin is a
  setting-authoring error, not something this feature works around).
- What happens when the ancestry and the career grant the same skill name, with different caps?
  Out of scope for this feature to reconcile — treated as an Assumption below (the higher cap
  applies, since the union is of *eligibility*, and a setting is expected not to declare
  conflicting caps for the same skill in practice).
- What happens with zero advances spent (an empty allocation)? Rejected — total must be exactly
  8, and 0 ≠ 8.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST represent a career as a mapping from skill name to that skill's
  cap, plus a flag for whether it is a legal entry point.
- **FR-002**: The engine MUST represent an ancestry as a mapping from skill name to that skill's
  cap (or no cap constraint of its own — see Assumptions), used only to widen eligibility.
- **FR-003**: The engine MUST validate an allocation as a sequence of actions, each either
  `open <skill>` (cost 1, sets the skill to 25%) or `raise <skill>` (cost 1, +5% to the skill's
  current value).
- **FR-004**: The engine MUST reject an allocation whose total action count is not exactly 8.
- **FR-005**: The engine MUST reject an allocation that opens fewer than 2 distinct skills.
- **FR-006**: The engine MUST reject a `raise` on a skill that would exceed that skill's cap
  (from the career, or from an ancestry entry if the skill isn't in the career).
- **FR-007**: The engine MUST reject any action on a skill outside the union of the career's and
  (if given) the ancestry's granted skills.
- **FR-008**: The engine MUST reject `open` on a skill already opened by an earlier action in the
  same allocation.
- **FR-009**: The engine MUST reject `raise` on a skill not yet opened by an earlier action in
  the same allocation.
- **FR-010**: On success, the engine MUST return the resulting skill percentages for every skill
  acted on.
- **FR-011**: Every rejection MUST name the specific rule violated and the skill/total involved,
  not a generic failure.
- **FR-012**: The CLI MUST expose allocation validation as a `describe`-discoverable,
  catalog-driven verb.
- **FR-013**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Career**: `{skills: {name: cap}, entry_point: bool}`.
- **Ancestry**: `{skills: {name: cap}}` (optional; widens eligibility only).
- **Advance action**: `{action: "open" | "raise", skill: <name>}`.
- **Allocation result**: `{valid: bool, skills: {name: pct} (on success), error: <reason> (on
  failure)}`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four worked spreads from `docs/design/11-character-creation.md` section 3
  (open 2 everything-into-one → 55%/25%; open 2 split evenly → 40%/40%; open 3 → 35%/35%/30%;
  open 4 → 30%×4) are accepted and produce exactly the documented percentages.
- **SC-002**: Each of the eight rejection scenarios in User Story 2's acceptance scenarios is
  rejected with a distinct, correctly-attributed reason — eight cases, zero false accepts.
- **SC-003**: An ancestry-widened allocation (Acceptance Scenario 6) is accepted with the
  ancestry skill's value correctly computed, confirming the union check doesn't accidentally
  also check the ancestry's own budget (there is none).

## Assumptions

- If a skill appears in both the career and an ancestry with different caps, the **higher** cap
  applies — a setting is expected not to declare genuinely conflicting caps for the same skill,
  and this feature does not attempt to detect or reject that as a setting-authoring error (no
  setting loader exists yet to validate settings against).
- Which career is chosen, and which specific allocation a player wants, are GM/player judgment
  calls this feature does not make — it validates a given allocation, per ADR 0014 ("chosen, not
  rolled"), and never proposes or completes one itself.
- Career-graph traversal (successor careers, prerequisites, completion and its +1 Stamina bonus)
  is out of scope — this feature is the data shape and the one deterministic rule (the 8-advance
  spend) that both creation (#232) and future advancement work need, not the whole graph.
- Setting-requirements validation (at least one entry career must exist, etc., per
  `docs/design/11-character-creation.md` section 4) is out of scope — no setting loader exists in
  this engine yet.
- Following #221-#229's precedent: Python 3.11+, standard library only, stdlib `unittest`, no
  pytest, catalog-driven CLI dispatch, no state I/O (this feature's functions are pure, like
  #222's `opposed_test`).
