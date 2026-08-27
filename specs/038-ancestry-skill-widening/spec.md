# Feature Specification: Ancestry widens creation's skill pool, never its budget

**Feature Branch**: `038-ancestry-skill-widening`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "State the engine's position on mechanical species/ancestry differentiation (closes #121). Decision: an optional, setting-declared ancestry may widen the skill pool creation's 8 advances can be spent against, alongside the starting career's own list. Same 8 advances — no separate ancestry budget, no stat modifier."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author gives ancestries mechanical texture (Priority: P1)

A setting author whose world distinguishes dwarves from elves (or any other ancestry-shaped
grouping) wants two characters who chose the same starting career to still come out different,
without inventing a stat-bonus mechanic the engine doesn't support.

**Why this priority**: This is the exact case #121 raised — the engine currently has no answer,
and silence reads as an oversight rather than "career and fiction are the only axes, on purpose."

**Independent Test**: A setting declares an ancestry with its own skill list; a player creating a
dwarf and a player creating an elf, both taking the same entry career, can legally spend their 8
advances on different skills because each ancestry's list differs.

**Acceptance Scenarios**:

1. **Given** a setting that declares an ancestry granting skills `Endure` and `Appraise`, and a
   starting career granting `Melee` and `Haggle`, **When** a player spends their 8 creation
   advances, **Then** they may open any of `Endure`, `Appraise`, `Melee`, or `Haggle` — the union
   of both lists — under the same cost table creation already uses (§3 of
   `05-character-creation.md`).
2. **Given** a setting with no ancestry concept at all, **When** a character is created, **Then**
   creation behaves exactly as it does today — the eligible pool is the starting career's list
   alone, unchanged.
3. **Given** an ancestry is declared, **When** a player counts their creation budget, **Then** it
   is still exactly 8 advances — ancestry adds no additional advances and no stat, Stamina, or
   Luck modifier.

### User Story 2 - A GM reads the design and confirms there is no hidden mechanic (Priority: P2)

A GM running a setting with no ancestry concept wants confidence that nothing else in the engine
secretly differentiates species/ancestry (e.g. no buried stat table), so they can answer a
player's "does my character's ancestry do anything mechanically?" question correctly.

**Why this priority**: The issue's core complaint is that the current silence is indistinguishable
from an oversight. This closes that gap for the "no ancestry" case too, not only the "yes" case.

**Independent Test**: Read `docs/design/05-character-creation.md` and confirm it states plainly
that ancestry, where a setting has one, only ever widens the eligible skill pool — never a stat,
never an extra advance, never a separate roll.

**Acceptance Scenarios**:

1. **Given** the updated design document, **When** a GM reads the creation section, **Then** they
   find an explicit statement of what ancestry can and cannot do mechanically, with no need to
   infer it from absence.

### Edge Cases

- What if an ancestry and the starting career grant the same skill? The union simply has one
  entry for it — no double-counting, no stacking of the open cost.
- What if a setting wants an ancestry to grant more than a skill list (e.g. a permanent Stamina
  bonus)? Out of scope and against the position taken here — ADR 0040 records why (no new
  mechanism, no stat modifier).
- Can an ancestry's list exceed the career's cap for a given skill? No — the existing "nothing may
  exceed the career's cap" rule (`03-rules.md` §6) is untouched; ancestry only changes which
  skills are eligible to open, not the cap once opened.
- Is ancestry required for every character? No — a setting with no ancestry concept simply never
  populates the field, and creation is identical to today (User Story 1, Scenario 2).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST state explicitly whether the engine provides mechanical
  species/ancestry differentiation, closing the silence #121 identified.
- **FR-002**: Where a setting declares an optional ancestry for a character, its skill list MUST
  be eligible for creation's advances alongside the starting career's own list — the pool widens
  to the union of both.
- **FR-003**: Ancestry MUST NOT grant additional advances beyond creation's existing 8, and MUST
  NOT modify Stamina, Luck, or any other flat value.
- **FR-004**: Ancestry MUST be optional, setting-declared data — a setting with no ancestry
  concept requires no change to its careers or creation flow.
- **FR-005**: The design MUST record the decision as an ADR, since a real, workable alternative
  (a separate ancestry advance budget; no mechanical differentiation at all) is being rejected in
  favour of this one, and someone could plausibly propose either alternative again.
- **FR-006**: The document changes MUST NOT introduce any new engine mechanism beyond "a second
  source of eligible skills feeding the same doors" — no new roll, clock, or resource.

### Key Entities

- **Ancestry**: an optional, setting-declared grouping (e.g. a species, lineage, or culture) that
  declares a list of skills, exactly as a career does. Carries no stat, Stamina, or Luck modifier
  of its own — its only effect is widening the pool of skills creation's advances may open.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `docs/design/05-character-creation.md` can state, without consulting any
  other document, whether ancestry has a mechanical effect and exactly what it is.
- **SC-002**: `python3 tools/check_docs.py` passes with the new text and new ADR in place.
- **SC-003**: `python3 tools/check_dangling_mechanics.py` introduces no new dangling reference from
  this change.
- **SC-004**: The creation advance count stays exactly 8 in every worked example the document
  gives — no example implies a larger or ancestry-dependent budget.

## Assumptions

- The position taken: ancestry is optional, setting-declared, and mechanically limited to widening
  the eligible skill pool for creation's existing 8 advances — never a separate budget, never a
  stat/Stamina/Luck modifier. This is what the operator confirmed after reviewing the two live
  alternatives (no mechanical differentiation at all; a separate ancestry-only advance budget).
- This closes #121 by giving a positive answer (ancestry does have a defined, narrow mechanical
  effect) rather than the "no mechanical differentiation" alternative also considered.
- No code, schema, or validator changes are needed in this repository: career and skill data is
  setting-declared and lives in `wyrd-setting-*` repositories, not here (confirmed — this repo
  holds no career/skill schema file). The change is entirely to `docs/design/05-character-creation.md`
  and a new ADR.
- `docs/design/27-entities.md`'s character schema is the NPC/nemesis entity shape and does not
  model the player character's creation mechanics (those live in `05-character-creation.md`), so
  no entity schema change is needed there either.
