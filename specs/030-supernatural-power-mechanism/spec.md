# Feature Specification: Systems of power

**Feature Branch**: `030-supernatural-power-mechanism`

**Created**: 2026-08-26

**Status**: Draft

**Input**: Issue [#96](https://github.com/neilgfoster/wyrd/issues/96) — an engine-level mechanism
for supernatural power, general enough that a setting declares one or more systems of power as
data, specific enough that casting has real mechanical weight.

## Why this exists

The engine has no concept of magic or the supernatural at all — grepping `design/` and
`README.md` finds nothing. Every catalogued setting has practitioners of some kind, and
`doc/design/26-authoring-a-setting.md`'s hard rule forbids a setting adding its own mechanism: *"A
setting may extend, retune or disable what the engine provides. It may never add a mechanism the
engine does not have."* Magic cannot be left for a setting to invent without that rule being
broken by every setting that has tried.

## Clarifications

None raised back to the operator. The issue's own scope list is a complete decision checklist, and
every open question in it has a reasonable default resolvable from the engine's own established
conventions:

- **The load-bearing fork** (one configurable mechanism vs. a closed set of mechanism shapes) is
  resolved as *one mechanism* — see [ADR 0036](../../doc/adr/0036-one-configurable-power-mechanism.md).
  The engine's whole pattern for setting texture (`bestiary.yaml`, `gear.yaml`, the career graph)
  is one schema instantiated with data, never a menu of engine-side shapes to pick between; a
  closed set of shapes would itself be several mechanisms wearing one name, and
  `13-authoring-a-setting.md`'s hard rule exists precisely to keep the engine from accumulating
  those.
- **What casting costs**: Strain, mandatory on every invocation, exactly as the engine already
  spends Strain for short-term pressure; Resolve, optional, for a system whose exceptional
  workings warrant the spendable counterweight to Taint. No new track — `06-state.md`'s reuse
  guidance and the issue's own "prefer reuse over a new track" are both explicit.
- **The failure mode**: the existing Ill Omen, not a new table family. `03-rules.md` §1 already
  gives every roll a "something also goes wrong" signal on the Wyrd die's units digit; a power
  test reads it exactly as any other test does, and the consequence — a point of Taint for the
  caster — reuses the transformation-threshold machinery `03a-3-transformations.md` already
  defines rather than inventing a second consequence ladder next to it.
- **Who may use a system, and how it is learned**: reuses the existing trained/untrained boundary
  and the career graph exactly as any other skill (`03-rules.md` §1, `03b-the-character.md`) — a
  system of power may mark itself as requiring training, in which case there is no untrained
  attempt, the same rule a setting already applies to a language it does not speak.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting declares a system of power (Priority: P1)

A setting author writes a system-of-power declaration — the skill it tests, its Strain cost, an
optional Resolve cost, and whether it requires training — and validates it against the engine's
schema before using it in play.

**Why this priority**: nothing else in scope is testable until a system of power can be declared
at all; this is the schema the rest of the feature hangs off.

**Independent Test**: run the new validator against a worked-example declaration and confirm it
accepts a well-formed one and rejects a declaration missing a required field or carrying a field
the schema does not define.

**Acceptance Scenarios**:

1. **Given** a setting's `power.yaml` declaring one system of power with `id`, `name`, `skill`,
   `strain_cost` and `requires_training`, **When** the validator runs, **Then** it passes with no
   errors.
2. **Given** the same declaration missing `strain_cost`, **When** the validator runs, **Then** it
   is rejected with an error naming the missing field.
3. **Given** the same declaration carrying an unrecognised field (e.g. `mana_pool: 20`), **When**
   the validator runs, **Then** it is rejected — the unrecognised-field rejection that
   `13-authoring-a-setting.md` already relies on for `bestiary.yaml` and `gear.yaml` to keep a
   setting from smuggling in a new mechanism.

---

### User Story 2 - A character invokes a system of power (Priority: P1)

A character with the declared skill attempts to invoke it. The GM resolves it as an ordinary
d100 test against that skill, at whatever difficulty the fiction sets, and the player pays the
system's declared Strain (and Resolve, if the system calls for it) once the roll is made.

**Why this priority**: this is the mechanism the issue exists to define — casting with real
mechanical weight, using nothing the engine does not already have.

**Independent Test**: run `tools/check_power_systems.py` against a worked example and confirm the
resolution steps it asserts (skill test, cost applied, no new dice) match `03-rules.md` §1
exactly, with no branch specific to power tests.

**Acceptance Scenarios**:

1. **Given** a character trained in a system of power's skill, **When** they attempt to invoke it,
   **Then** the GM resolves a standard d100 test against that skill (difficulty, declaration and
   assistance apply exactly as any other test) and the player's Strain drops by the system's
   declared cost once the roll resolves, regardless of success or failure.
2. **Given** a system of power that also declares a Resolve cost, **When** a character invokes it,
   **Then** Resolve drops by that amount in addition to Strain.
3. **Given** a system of power marked `requires_training: true`, **When** an untrained character
   attempts to invoke it, **Then** there is no attempt — the same rule already applied to an
   unlearned language.

---

### User Story 3 - An Ill Omen turns the working against the caster (Priority: P2)

A power test rolls an Ill Omen. The caster takes a point of Taint (or the system's declared
variant of it) in addition to any other consequence of failure, using the engine's existing Taint
accrual and transformation-threshold machinery — no separate roll, no separate table.

**Why this priority**: this is what gives casting weight beyond an ordinary skill check, and it
must reuse the existing consequence chain rather than open a second one next to it.

**Independent Test**: inspect a resolved power test carrying an Ill Omen and confirm the Taint
gain is applied through the same accrual path Exposure and the Bargain already use, with no
system-of-power-specific table consulted.

**Acceptance Scenarios**:

1. **Given** a power test whose natural roll's units digit is 0, **When** the roll resolves,
   **Then** the caster gains the system's declared `ill_omen_taint` (default 1) via the existing
   Taint-accrual path, and a transformation-table roll follows immediately if that crosses a
   threshold, exactly as any other Taint gain does.
2. **Given** a setting that has disabled Taint entirely (`overrides.disable: [taint]`), **When** a
   power test rolls an Ill Omen, **Then** no Taint is gained — a disabled track disables every
   mechanic that feeds it, including this one; the system's declared Strain/Resolve costs and the
   base d100 resolution are unaffected.

### Edge Cases

- A setting declares a system of power whose skill does not exist in that setting's skill list —
  rejected by the validator; a system of power cannot reference a skill the setting never
  declared.
- A setting declares two systems of power that test the same skill (e.g. one martial, one
  supernatural use of the same trained ability) — permitted; the schema does not require skill
  uniqueness across systems.
- A far-future or non-mythic setting (psionics, applied technology treated as the setting's
  "supernatural") declares a system of power using the identical schema, with `voice.md` and
  `rename:` carrying every register difference — this is the general-enough test the issue's
  scope calls for directly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a single configurable system-of-power declaration schema —
  not a closed set of engine-defined mechanism shapes a setting picks between.
- **FR-002**: A system-of-power declaration MUST require `id`, `name`, `skill`, `strain_cost`, and
  `requires_training`.
- **FR-003**: A system-of-power declaration MAY declare an optional `resolve_cost` and an optional
  `ill_omen_taint` (defaulting to 1 if omitted).
- **FR-004**: Invoking a system of power MUST resolve as the engine's standard d100 test (§1 of
  `03-rules.md`) against the declared skill — the same difficulty bands, declaration bonuses,
  assistance and Wyrd-die reading as any other test, with no additional dice mechanism.
- **FR-005**: The declared `strain_cost` MUST be paid once the roll resolves, regardless of
  success or failure; the declared `resolve_cost`, if present, MUST be paid identically.
- **FR-006**: A system of power marked `requires_training: true` MUST NOT permit an untrained
  attempt — mirroring the existing rule for a skill requiring training.
- **FR-007**: An Ill Omen on a power test MUST apply the declared `ill_omen_taint` through the
  engine's existing Taint-accrual and transformation-threshold path; the engine MUST NOT introduce
  a second, power-specific consequence table.
- **FR-008**: When a setting has disabled Taint (`overrides.disable: [taint]`), an Ill Omen on a
  power test MUST NOT apply any Taint-track consequence, consistent with Taint's existing
  disable behaviour.
- **FR-009**: A setting MAY declare more than one system of power; each is independent data with
  no cross-system constraint the engine enforces.
- **FR-010**: Every engine-level label introduced by this feature (e.g. "system of power",
  "invocation") MUST be descriptive English, never a term borrowed from a source system; a setting
  renames what it likes via its `rename:` block.
- **FR-011**: A validator MUST reject a system-of-power declaration with a missing required field,
  a field the schema does not define, or a `skill` value absent from the setting's own skill list
  — the same unrecognised-field rejection `check_bestiary.py` and `check_gear.py` already enforce.

### Key Entities

- **System of power**: a setting-declared mechanism for supernatural or extraordinary effort.
  Attributes: `id` (stable, kebab-case, unique), `name`, `skill` (the setting's own skill it
  tests), `strain_cost`, `resolve_cost` (optional), `requires_training` (bool), `ill_omen_taint`
  (optional, default 1), `description` (flavour, no mechanical effect).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM resolves a power test using only the steps already used for any other d100
  test, plus applying the system's own declared cost — no new procedure to learn at the table.
- **SC-002**: A setting author can declare a working system of power in a schema no larger than
  `bestiary.yaml`'s per-creature block, validated by the new checker before it is ever used in
  play.
- **SC-003**: The identical schema accommodates at least two structurally different worked
  examples (a mythic-fantasy system and a far-future/psionic one) without either needing a field
  the other does not use.

## Assumptions

- Casting cost reuses Strain (mandatory) and Resolve (optional) rather than introducing a new
  track, per the issue's own "prefer reuse" instruction and `06-state.md`'s existing track set.
- The failure/backlash signal is the existing Ill Omen and existing Taint-accrual path, not a new
  table family — the issue explicitly allows either choice, and reuse is preferred absent a reason
  a new table would do something the existing consequence chain cannot.
- Learning a system of power reuses the existing skill-acquisition and career-graph path; this
  feature does not add a "schools of magic" progression mechanism, since the issue's scope never
  asks for one and the engine already has a mechanism for how skills are learned.
- Casting content itself (specific spells, powers, their names and flavour) is out of scope, as
  the issue states — it is setting data in a `wyrd-setting-*` repository, not an engine schema.
