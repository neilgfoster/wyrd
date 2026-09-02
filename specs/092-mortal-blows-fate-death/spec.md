# Feature Specification: Mortal blows, Fate, and death

**Feature Branch**: `092-mortal-blows-fate-death`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Mortal blows, Fate, and death — implement the mortal-critical-forces-death, Fate-point re-read, mortality:low death-row closure, and companion status-transition mechanisms of docs/design/05-criticals.md and docs/design/06-aftermath.md (issue #253)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A mortal critical forces the Aftermath result onto death (Priority: P1)

A combatant takes a critical whose result falls on the top, open-ended row of its damage-type
table (already flagged `mortal` by resolution — see `docs/design/05-criticals.md` "The mortal
blow"). When that combatant's Aftermath roll is resolved after the fight, whatever total is
rolled is discarded in favour of the `death` row, and `death`'s effect is what gets applied and
recorded.

**Why this priority**: Without this, a mortal critical is cosmetic — the worst wound in the game
would carry no more weight than an ordinary one at Aftermath, breaking the read of "a critical
never kills during the fight, but forces its bill" (ADR 0023).

**Independent Test**: Resolve an Aftermath step for a combatant flagged mortal, with the
underlying `d100` roll seeded to land on a low, survivable row. Confirm the outcome recorded is
`death` and its effect, not the row the raw roll would have hit.

**Acceptance Scenarios**:

1. **Given** a combatant carries a mortal critical from this fight, **When** their Aftermath step
   is resolved, **Then** the recorded row is `death` regardless of the `d100` total rolled.
2. **Given** a combatant carries a mortal critical, **When** the Aftermath step's history is
   inspected, **Then** the roll and total are recorded as actually rolled, alongside the forced
   `death` row and the fact that it was forced by a mortal critical (distinct from a `death` result
   reached by an unmodified high roll).

---

### User Story 2 - A spent Fate point re-reads death onto the worst non-death row (Priority: P1)

A player whose character (or, on a companion's behalf, under the conditions in Story 3) has
landed on `death` chooses to spend one Fate point. The `death` result is replaced, deterministically
and without a second roll, by the worst non-death row on the Aftermath table, and that row's
effect is what applies. Fate is decremented by one. A player who has no Fate, or who declines to
spend it, takes `death` as read.

**Why this priority**: This is Fate's entire mechanical promise (docs/design/06-aftermath.md,
"Closing the death rows") — without it, Fate is flavour text with no numeric effect at the one
place the ruleset says it matters.

**Independent Test**: Resolve an Aftermath step that lands on `death` for a character carrying
Fate. Spend the Fate point. Confirm the recorded outcome becomes the table's worst non-death row
(`new-enemy`, per the current table — re-derive from the live table rather than hardcoding, since
row order/keys are the table's to define) with that row's effect applied, and that the
character's Fate total dropped by exactly one.

**Acceptance Scenarios**:

1. **Given** a character's Aftermath result is `death` and they hold at least 1 Fate, **When** the
   player spends a Fate point against that result, **Then** the recorded row becomes the worst
   non-death row on the Aftermath table, that row's effect is applied, and the character's Fate
   total decreases by exactly 1.
2. **Given** a character's Aftermath result is `death` and they hold 0 Fate, **When** no Fate is
   spent, **Then** the `death` result stands and no Fate is deducted.
3. **Given** a character's Aftermath result is anything other than `death`, **When** a Fate spend
   against that result is attempted, **Then** the attempt is rejected and no row is changed and no
   Fate is deducted — Fate never improves a non-death row.
4. **Given** an Aftermath result of `death` was already re-read once by a spent Fate point,
   **When** a second Fate spend against the same result is attempted, **Then** it is rejected —
   the row is already resolved and there is nothing left to buy.

---

### User Story 3 - Fate spent on a companion's behalf requires the player present and able to act (Priority: P2)

A companion has no Fate of its own. When a companion's Aftermath result is `death`, that result
stands unless the player's own character is present in the same scene, able to act, and the
player chooses to spend one of their own Fate points on the companion's behalf.

**Why this priority**: This is the asymmetry the design deliberately wants — companions are the
chronicle's reliable source of loss precisely because they lack the valve, not because the dice
are weighted against them (docs/design/06-aftermath.md, "Companions"). Getting the gating wrong
either removes that asymmetry or makes companions completely unprotectable, both of which
contradict the design document.

**Independent Test**: Attempt a Fate spend on a companion's `death` result under three scene
conditions — player character present and able to act; player character present but unable to
act (e.g. incapacitated); player character absent — and confirm the spend succeeds only in the
first case, deducting the player's own Fate.

**Acceptance Scenarios**:

1. **Given** a companion's Aftermath result is `death`, and the player's character is present in
   the scene and able to act, **When** the player spends a Fate point on the companion's behalf,
   **Then** the companion's result is re-read onto the worst non-death row exactly as in Story 2,
   and the Fate deducted is the player character's own.
2. **Given** a companion's Aftermath result is `death`, and the player's character is absent from
   the scene, **When** a Fate spend on the companion's behalf is attempted, **Then** it is
   rejected and the companion's result stands as `death`.
3. **Given** a companion's Aftermath result is `death`, and the player's character is present but
   not able to act (e.g. downed or incapacitated), **When** a Fate spend on the companion's behalf
   is attempted, **Then** it is rejected and the companion's result stands as `death`.

---

### User Story 4 - `mortality: low` closes the death rows for everyone, unconditionally (Priority: P2)

In a setting whose tone contract sets `mortality: low`, any Aftermath result that would otherwise
land on `death` — whether rolled directly or forced there by a mortal critical — is instead
re-read onto the worst non-death row automatically, for every combatant, with no Fate spent and no
choice involved.

**Why this priority**: This is the tone contract's own mechanism for a setting that wants no
character deaths at all (docs/design/01-principles.md, docs/design/06-aftermath.md). It must
apply uniformly and must not be confused with, or double up with, a Fate spend.

**Independent Test**: Resolve an Aftermath step landing on `death` (both by direct roll and by a
mortal-critical force) inside a setting configured `mortality: low`, with the combatant holding 0
Fate. Confirm the result is still re-read onto the worst non-death row, with no Fate deducted (there
is none to deduct) and the outcome recorded as closed by the tone contract rather than by a spend.

**Acceptance Scenarios**:

1. **Given** the setting's `mortality` is `low`, **When** any combatant's Aftermath result would be
   `death`, **Then** the recorded row is instead the worst non-death row and that row's effect
   applies, with no Fate deducted.
2. **Given** the setting's `mortality` is `standard` or `high`, **When** a combatant's Aftermath
   result is `death` and no Fate is spent, **Then** the result stands as `death`.
3. **Given** the setting's `mortality` is `low`, **When** the Aftermath step's history is
   inspected, **Then** the record distinguishes this closure as the tone contract's doing, not a
   Fate spend (`fate_spent` stays `false`).

---

### User Story 5 - A companion's outcome updates their status, not a new field (Priority: P3)

When a companion's Aftermath result stands as `death` (Fate not spent, or not available under
Story 3's gate), their existing `status` field is set to `dead`. When their result is
`left-for-dead` or `taken` under a reading that the design treats as the companion being removed
from the party rather than killed, their `status` is set to `away` (per
docs/design/06-aftermath.md "Companions": "`dead` where a death result stands, `away` while they
are held"). No new status value or parallel field is introduced.

**Why this priority**: This is what makes the mechanism visible in state rather than only in a
resolution log — lower priority than the resolution logic itself (Stories 1-4), but a stated
acceptance criterion and needed for the party-membership query
(`status: with-party`, docs/design/22-state.md) to reflect losses correctly.

**Independent Test**: Resolve a companion's Aftermath result to `death` (Fate not spent) and
confirm their entity's `status` field becomes `dead`. Separately, resolve a `taken` result and
confirm `status` becomes `away`.

**Acceptance Scenarios**:

1. **Given** a companion's Aftermath result stands as `death`, **When** the outcome is applied,
   **Then** the companion's `status` field is set to `dead`.
2. **Given** a companion's Aftermath result is `taken`, **When** the outcome is applied, **Then**
   the companion's `status` field is set to `away`.
3. **Given** the player character's own Aftermath result stands as `death`, **When** the outcome
   is applied, **Then** no `status` field mutation is attempted for the player character — this
   mechanism is companion-specific (the player character's death is the chronicle-ending case and
   is out of this feature's scope; see Assumptions).

### Edge Cases

- A combatant carries a mortal critical from more than one instance in the same fight (multiple
  criticals, more than one landing on the mortal row): the forced `death` read is idempotent —
  carrying one or several mortal criticals has the same effect on the Aftermath read.
- `mortality: low` and a Fate spend are never both applied to the same result: the tone-contract
  closure is checked first, and if it already closed the row there is nothing left for a spend to
  buy (consistent with Story 2's "already resolved" rejection).
- The Aftermath table's worst non-death row is derived from the table's own row order at the time
  of the read, not hardcoded, so a future edit to the table's rows does not silently desynchronize
  this feature from `docs/design/06-aftermath.md`.
- A companion's `status` is only ever set to `dead` or `away` by this mechanism; a companion whose
  Aftermath result lands on any other row keeps whatever `status` it already had.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST, when resolving an Aftermath step for a combatant who carries one or
  more mortal criticals from the fight being resolved, force the recorded Aftermath row to `death`
  regardless of the `d100` total rolled, while still recording the roll and total as actually
  rolled.
- **FR-002**: The system MUST allow a Fate spend to be proposed against an Aftermath result that
  currently reads `death`, and MUST reject a Fate spend proposed against any other row.
- **FR-003**: The system MUST, on an accepted Fate spend against a `death` result, deterministically
  re-read that result onto the worst non-death row of the live Aftermath table (no second roll,
  no judgement call), apply that row's effect, and decrement the spending character's Fate by
  exactly 1.
- **FR-004**: The system MUST reject a Fate spend against an Aftermath result that has already been
  closed (by a prior Fate spend or by `mortality: low`), reporting that there is nothing left to
  buy.
- **FR-005**: The system MUST, for a Fate spend proposed on a companion's behalf, require that the
  player's character is present in the same scene and able to act, and MUST reject the spend
  otherwise; an accepted spend deducts Fate from the player's own character, never from the
  companion.
- **FR-006**: The system MUST, when the active setting's `mortality` is `low`, automatically
  re-read every Aftermath result that would otherwise be `death` — however reached — onto the
  worst non-death row and apply that row's effect, without requiring or accepting a Fate spend for
  that closure, and MUST record that this closure was not a Fate spend (`fate_spent: false`).
- **FR-007**: The system MUST NOT modify Aftermath results in any way when `mortality` is
  `standard` or `high` and no Fate is spent — `death` stands as read.
- **FR-008**: The system MUST, when a companion's Aftermath result stands as `death` (not closed
  by Fate spend or `mortality: low`), set that companion's `status` field to `dead`.
- **FR-009**: The system MUST, when a companion's Aftermath result is `taken` (or another row the
  design treats as the companion being held away from the party), set that companion's `status`
  field to `away`.
- **FR-010**: The system MUST NOT introduce any new status value, nor a parallel field, to record a
  companion's death or removal — only the existing `status` field's existing vocabulary is used.
- **FR-011**: The system MUST NOT apply the companion status-transition mechanism (FR-008/FR-009)
  to the player's own character.

### Key Entities

- **Aftermath result**: the outcome of resolving the Aftermath table for one combatant who dropped
  in a fight — carries the roll, the modifier, the total, the row/key, whether it was forced by a
  mortal critical, whether it was closed by a Fate spend, and whether it was closed by
  `mortality: low`.
- **Fate**: a player-character resource (`fate.current`/`fate.max`, already tracked on the
  character) spent, one point at a time, only against a `death` Aftermath result — for the
  player's own character directly, or for a companion when the player's character is present and
  able to act.
- **Companion**: a `character` entity with `role: companion` and a `status` field
  (`docs/design/22-state.md`); this feature transitions that field to `dead` or `away` depending
  on how its Aftermath result resolves.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every mortal critical taken in a fight results in that combatant's Aftermath read
  landing on `death`, in 100% of resolutions, independent of the underlying `d100` roll.
- **SC-002**: A spent Fate point changes a `death` result to the same worst non-death row every
  time it is exercised against equivalent state — the re-read is fully deterministic, with zero
  variance across repeated resolutions of the same inputs.
- **SC-003**: A Fate spend attempted against a non-`death` row, an already-closed `death` row, or a
  companion whose player character is not present-and-able is rejected 100% of the time, with no
  state mutation performed.
- **SC-004**: In a `mortality: low` setting, 0% of Aftermath resolutions across a fight leave a
  `death` row recorded as the final outcome.
- **SC-005**: A companion's `status` field reflects `dead` or `away` correctly for 100% of
  Aftermath resolutions that land (after any closure) on `death` or `taken` respectively, with no
  other row causing a `status` change.

## Assumptions

- The player character's own permanent death (what happens to the chronicle when `death` stands
  for the player's own character, with no Fate to spend and no `mortality: low`) is a
  chronicle/session-level consequence outside this feature's scope — this feature is responsible
  only for the row being correctly forced, re-read, or left standing, and for Fate accounting; the
  narrative/session handling of a standing player-character death is not defined here.
- "Present in the same scene and able to act," used to gate a Fate spend on a companion's behalf,
  is read from whatever the engine already uses to determine scene presence and incapacitation
  (e.g. the companion/character's own status and any downed/incapacitated state) — this feature
  does not introduce a new presence-tracking mechanism, only consumes the existing one.
- The recurring-wound's combat-start firing effect and the Mend undertaking are explicitly out of
  scope, per the issue's own scope note, and are not touched by this feature.
- "The worst non-death row" is read as the highest-ranged row on the Aftermath table below
  `death` — currently `new-enemy` — but this feature must derive it from the table's own
  structure rather than hardcode that key, so a future table edit stays correctly reflected.
