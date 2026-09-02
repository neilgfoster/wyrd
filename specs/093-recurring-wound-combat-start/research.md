# Research: The recurring wound's combat-start effect

No `NEEDS CLARIFICATION` markers remained in the Technical Context, so this phase confirms the
existing code this feature builds on rather than resolving open unknowns.

## Decision: read wound data via `character.active_wound_effects`

**Rationale**: `engine/wyrd/character.py`'s `active_wound_effects(wounds)` already surfaces every
wound whose `closed` is `None` as `{"wound_id", "effect", "bears_on"}`. A recurring wound is
`{"recurring": true, "effect": {"skill": -10}, "bears_on": "<skill>", "closed": None}` (never
closed, per `validate_wound`'s own rule that a recurring wound must never carry `closed`). Filter
this list for `wound.get("recurring")` (the raw wound record, not the trimmed effect dict) to
isolate recurring wounds specifically, keeping `bears_on` and using the constant penalty rather
than the wound's own stored `-10` literal.

**Alternatives considered**: reading `wounds` directly and re-deriving "active" (i.e. `closed is
None`) inline. Rejected -- issue #254's own "Current state" note says to reuse the existing
generic surface rather than a parallel path, and duplicating the closed-filter here would be a
second place that rule lives.

## Decision: reuse `combat.CHALLENGING_MODIFIER`

**Rationale**: `combat.py` already defines `CHALLENGING_MODIFIER = resolution.
DIFFICULTY_BONUSES["challenging"]` (value `-10`) for the ranged-attack difficulty feature
(specs/087). This is the exact "existing Challenging difficulty step" issue #254 requires reusing
-- importing it (or referencing `resolution.DIFFICULTY_BONUSES["challenging"]` directly) avoids a
second `-10` literal anywhere in this feature's code.

**Alternatives considered**: defining a new `RECURRING_WOUND_PENALTY = -10` constant. Rejected --
this is precisely the "no new literal" case CLAUDE.md and the issue call out; a second constant
holding the same value is exactly the kind of duplicate-source-of-truth this repo's design
process has been corrected for before (docs/design/06-aftermath.md's own text: "`-10` is not a
new number").

## Decision: compute and store the penalty once, in `start_combat`

**Rationale**: FR-005/FR-006/FR-007 require the penalty to apply unconditionally at combat start,
never recompute mid-fight, and have no effect outside the scene it was applied in. `start_combat`
already accepts each side's per-combatant flags and persists a `scene` dict to chronicle state
once, atomically, via `state.save`. Computing the stacked per-skill penalty for each combatant at
that same moment and storing it on the scene (rather than recomputing it lazily from live wound
data on every read) satisfies "fixed once, at the fight's start" directly: nothing later in the
combat's lifecycle (e.g. `advance_round`) touches it, and nothing outside `combat` state exposes
it.

**Alternatives considered**: computing the penalty lazily, on demand, whenever a skill test is
run during combat by re-reading the combatant's current wounds each time. Rejected -- this would
technically satisfy "applies for the fight" but risks silently changing mid-fight if a wound's
`closed` state changed between rounds (which the Mend design explicitly says cannot happen to a
recurring wound, but the ADR reasoning for other wound types is the general one: closing happens
between fights only). Storing the computed value once at combat start is the more literal reading
of "fires when a fight begins" and is exactly what the design phrase describes -- fixed at the
door, not re-evaluated every time it's asked.

## Decision: character data is supplied by the caller, not loaded from disk by `combat.py`

**Rationale**: `start_combat`'s `sides` parameter already takes per-combatant flags
(`armed`/`surprised`/`ambush`) as plain dicts passed in by the caller, rather than `combat.py`
loading character entities itself -- `combat.py` has no character-loading import today. This
feature follows the same shape: the caller supplies each combatant's active recurring-wound
records (or, more precisely, is expected to pass the already-computed `active_wound_effects`
output, or equivalent) alongside the existing flags, and `combat.py` does the penalty arithmetic
and storage. This keeps `combat.py`'s only new dependency `resolution` (already imported) rather
than adding a `character` import and a disk-loading responsibility this module has never had.

**Alternatives considered**: having `start_combat` accept a character file path per side and load
+ validate the character itself. Rejected -- scope creep beyond this issue (loading/resolving
character entities from paths is a caller concern elsewhere in the engine, e.g. `character.load`),
and it would make `combat.py` responsible for character-entity validation it doesn't otherwise
own.
