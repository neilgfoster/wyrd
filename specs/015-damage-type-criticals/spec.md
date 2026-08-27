# Feature Specification: The damage-type critical tables

**Feature Branch**: `015-damage-type-criticals`

**Created**: 2026-08-25

**Status**: Draft

**Input**: Issue [#17](https://github.com/neilgfoster/wyrd/issues/17) — enumerate the engine's damage
types and define one critical table per type in `docs/design/05-criticals.md`, on the shared
`1d6 + points below zero` ladder.

## Why this exists

[`docs/design/03-rules.md`](../../docs/design/03-rules.md) has told the GM to roll `1d6 + points below zero`
"on the table for the damage type" since the ruleset was written. There are no such tables, and the
engine has never enumerated its damage types at all. Two fragments are the entire evidence:
`critical-slashing` as an override example in
[`docs/design/24-authoring-a-setting.md`](../../docs/design/24-authoring-a-setting.md), and "he is Blunt 5" in
[`docs/design/13-diegesis.md`](../../docs/design/13-diegesis.md).

So this feature carries a decision, not a transcription: **which damage types the engine ships**, and
what each of their tables says.

## Clarifications

### Session 2026-08-25

- **Q: Which set of damage types does the engine ship?** → **Four: `slashing`, `piercing`,
  `blunt`, `searing`**, named for the shape of the wound rather than for a weapon or an element.
  The first three keep both surviving pieces of evidence in the repo true (`critical-slashing` in
  `13-authoring-a-setting.md`, "Blunt 5" in `10-diegesis.md`), so nothing goes stale. `searing` is
  the flexible fourth — fire in one setting, a beam weapon in another, renamed where neither fits.
  Rejected: three physical types only, which pushes a common case onto every setting; and the same
  four under plainer labels, which buys nothing and makes two documents stale.
- **Q: A critical's worst row and Aftermath both claim the killing blow — how do they compose?**
  → **A mortal critical does not kill during the fight.** It marks the blow mortal, and the
  combatant's Aftermath result is read on the `death` row. This is the exact mirror of the re-read
  `03a-2-aftermath.md` already publishes for Fate, so Fate and `mortality: low` still answer it,
  deferred death stays intact, and no new modifier touches the Aftermath roll. Rejected: criticals
  that never kill, which contradicts *high results are lethal*; and a bonus to the Aftermath total,
  which gives a one-modifier family a second modifier.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A blow takes a combatant below zero (Priority: P1)

The GM is running a fight. Damage takes a combatant below 0 Stamina, and the ruleset says to roll a
critical. The GM needs to know which table to roll on, what the total means, and what reaches state.

**Why this priority**: It is the rule the ruleset already publishes and cannot currently execute.
Nothing else in this feature matters if this does not resolve.

**Independent Test**: Given a damage type, a Stamina total and a damage roll, the modifier, the row
and the effect are all determinable from `docs/design/05-criticals.md` alone, with no judgement call.

**Acceptance Scenarios**:

1. **Given** a combatant at 2 Stamina struck for 5 of a named damage type, **When** the GM rolls the
   critical, **Then** the modifier is 3, the total is `1d6 + 3`, and exactly one row of exactly one
   table answers it.
2. **Given** any total the roll can produce, however large, **When** the GM reads the table,
   **Then** a row contains it — the ranges are contiguous from the family's lowest possible total
   and the last row is open at the top.
3. **Given** a critical is taken, **When** its effect is applied, **Then** 1 Trauma is charged once,
   by the rule in `docs/design/03-rules.md` §5, and no row charges it again.

---

### User Story 2 - A setting has no fiction for a damage type (Priority: P2)

A setting is being authored whose fiction has no place for one of the shipped types, or which calls
it something else entirely — fire in one setting, a beam weapon in another.

**Why this priority**: The engine is setting-agnostic by constraint. A type that only works for one
genre would be a setting term smuggled into the engine.

**Independent Test**: The rename and override path is stated in the document and needs no engine
change to exercise.

**Acceptance Scenarios**:

1. **Given** a setting that renames a damage type, **When** a critical is rolled, **Then** the key
   and the effect that reach state are unchanged and only what is *said* differs.
2. **Given** a setting that replaces a critical table's rows, **When** the setting loads, **Then**
   the replacement is checked against the rules in `docs/design/04-tables.md` and an unknown key is a
   load error.

---

### User Story 3 - A fight ends and both tables claim the killing blow (Priority: P2)

A combatant took a severe critical during the fight and now rolls Aftermath. Both tables can be
lethal, and the ruleset must say how they compose rather than leaving the GM to choose.

**Why this priority**: Deferred death is what lets a single-character chronicle survive lethal
combat. An unstated interaction would let a critical kill during the fight and quietly undo it.

**Independent Test**: The composition rule is stated in both documents and produces one outcome for
any pair of results, with no ordering ambiguity.

**Acceptance Scenarios**:

1. **Given** a critical whose result is the worst the table has, **When** the fight ends, **Then**
   the combatant still rolls Aftermath, and the composition rule determines a single outcome.
2. **Given** a spent Fate point, **When** the composition rule would end in death, **Then** Fate
   answers it by the mechanism `docs/design/06-aftermath.md` already publishes, unchanged.

### Edge Cases

- **The smallest possible critical.** One point below zero on a roll of 1 — the lowest total the
  family can produce. It must be the first row's lower bound, per `docs/design/04-tables.md`.
- **The largest plausible critical.** A doubled telling blow from the heaviest weapon in the band
  against a low-Stamina combatant. The rows must still be saying something at that modifier rather
  than having trailed off well below it.
- **A critical taken more than once** across a chronicle. The family is repeatable, so the same row
  may land twice.
- **A companion takes the critical.** Companions have no Fate of their own.
- **A damage type with no table**, because a setting's weapon declares one the engine does not
  publish. This is a load error, not a silent fallback.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST ship exactly four damage types — `slashing`, `piercing`, `blunt`,
  `searing` — each keyed `critical-<type>`, and MUST state the rationale for that set and the
  alternative sets rejected.
- **FR-002**: Every damage type MUST have exactly one critical table, defined in
  `docs/design/05-criticals.md`, one table per key.
- **FR-003**: Every table MUST roll `1d6` and add the points below zero, MUST begin at the family's
  lowest possible total, MUST have contiguous non-overlapping ranges, and MUST have a last row open
  at the top.
- **FR-004**: Every row MUST carry range, key, effect and description, per the row schema in
  `docs/design/04-tables.md`. The family MUST declare whether it carries any extra field, and MUST NOT
  declare one no rule reads.
- **FR-005**: Every effect MUST name a mechanic the engine already knows. The set of effects a
  critical row may produce MUST be stated and closed.
- **FR-006**: The family MUST declare itself repeatable or unique per character, and MUST answer
  the consequent obligations `docs/design/04-tables.md` places on that declaration.
- **FR-007**: The document MUST state the range of modifiers that actually occur at the Stamina,
  armour and weapon-damage values a real character has — **computed, not asserted** — and the rows
  MUST cover that range rather than trailing off below it.
- **FR-008**: A critical MUST NOT kill during the fight. The worst row of each table MUST instead
  mark the blow **mortal**, and a combatant carrying a mortal blow MUST have their Aftermath result
  read on the `death` row — the mirror of the re-read Fate already performs. Fate and
  `mortality: low` MUST still close that death by the mechanism `03a-2-aftermath.md` publishes,
  unchanged, and no modifier may be added to the Aftermath roll.
- **FR-009**: The tables MUST NOT charge Trauma. `docs/design/03-rules.md` §5 already charges 1 per
  critical taken, and a row that charged it again would double-charge the same blow.
- **FR-010**: The document MUST state what a setting may replace (rows) and may not (the die, the
  modifier, the uniqueness, the row schema, the composition with Aftermath), and MUST state how a
  setting renames a type whose fiction it lacks.
- **FR-011**: `docs/design/04-tables.md`'s index row for Criticals MUST be updated to link the file, and
  `docs/design/03-rules.md` and `docs/design/24-authoring-a-setting.md` MUST be updated wherever the
  enumeration makes them stale.
- **FR-012**: The damage-type enumeration MUST be recorded as an ADR — a real alternative is being
  rejected and someone will plausibly propose a different set in a year.
- **FR-013**: A check script committed under `specs/015-damage-type-criticals/` MUST compute the
  modifier distribution and every probability claim the document makes, and MUST exit non-zero on
  disagreement — including disagreement with figures earlier issues already computed.
- **FR-014**: No setting name, system name, or borrowed term may appear, and no row may bake in a
  tonal register. Verified by grep and by review, not asserted.

### Key Entities

- **Damage type**: a named, keyed category of harm the engine ships. Presentation may be renamed by
  a setting; the key never is.
- **Critical table**: one per damage type. Rows of range / key / effect / description.
- **Points below zero**: the count by which damage exceeded the combatant's remaining Stamina. It is
  the modifier for this family, and — multiplied by five — for Aftermath.
- **Wound record**: the state entry a lasting effect writes, already defined in
  `docs/design/06-aftermath.md` and `docs/design/22-state.md`.

## Success Criteria *(mandatory)*

- **SC-001**: A GM given a damage type, a Stamina value and a damage roll can resolve a critical
  from `docs/design/05-criticals.md` alone, with no judgement call and no second document.
- **SC-002**: Every total the family can produce, from its lowest to arbitrarily large, lands on
  exactly one row of every table — verified by script, for every table.
- **SC-003**: Every probability or range claim in the document is reproduced by the committed check
  script, which exits non-zero if the document and the maths disagree.
- **SC-004**: `python3 tools/check_docs.py` passes: the new document is reachable from `README.md`
  and the ADR index is whole.
- **SC-005**: A grep for setting and system vocabulary over `design/` returns nothing.
- **SC-006**: `docs/design/03-rules.md`, `docs/design/04-tables.md`, `docs/design/06-aftermath.md` and
  `docs/design/24-authoring-a-setting.md` agree with the new document on the damage types, the roll, and
  the composition with Aftermath — checked by reading them against each other, which is how fault
  class 3 in `CLAUDE.md` is found.

## Assumptions

- **#15 has landed**, so `docs/design/04-tables.md` is the authority on conventions and this feature
  conforms to it rather than restating it.
- **#16 has landed**, so `docs/design/06-aftermath.md` exists and the composition rule is written
  against what it actually says, not against a plan for it.
- **The weapon and armour band is the one earlier issues used** — weapons `1d3`/`1d6`/`1d8`/`2d6`,
  armour light `1d3`, modest `1d6`, heavy `2d6` with a minimum of 1 through — so the computed
  modifier range is comparable with the figures `specs/013` and `specs/014` already published.
- **Aftermath itself is out of scope.** So are armour and the telling blow, which are specified.
