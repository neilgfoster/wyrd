# Research: Mortal blows, Fate, and death

No `NEEDS CLARIFICATION` markers were left in the Technical Context — the codebase already
answers every open question this feature raises, once read against `#251`'s and `#252`'s landed
code and tests.

## Where the mortal flag already lives

- **Decision**: read the mortal flag off the `critical` step `_stage_critical` already stages
  (`roll.mortal: bool`, `docs/design/05-criticals.md`), not a new field on the character.
- **Rationale**: `_stage_critical` (resolution.py, landed in #251) already computes and records
  `mortal` per critical step; a combatant "carries a mortal blow" for Aftermath purposes exactly
  when any critical step staged against them in the fight being resolved has `mortal: True`. No
  new state needs to be introduced to know this — the caller staging Aftermath for a combatant
  already has that fight's own `steps` list to scan.
- **Alternatives considered**: persisting a `mortal_blow: bool` flag on the character entity
  itself was rejected — it would duplicate information the step list already carries and require
  clearing it after Aftermath resolves, an extra piece of state to keep in sync for no benefit
  over scanning the fight's own steps once.

## Where the worst non-death row is read from

- **Decision**: derive "the worst non-death row" from the live `AFTERMATH_TABLE` (or equivalent
  module-level structure `_aftermath_band` already consults) by taking the highest-ranged row
  below the open-ended `death` row, at call time — never hardcode the key `new-enemy`.
- **Rationale**: spec.md's edge cases and Assumptions both require this; the table is data the
  engine owns and a future edit to its rows must not silently desynchronize this feature (the same
  reasoning `_critical_band`'s mortal-row fallthrough already applies to the critical tables).
- **Alternatives considered**: hardcoding the key was rejected outright — spec.md explicitly
  calls this out as a risk to guard against.

## How mortality reaches the aftermath resolution

- **Decision**: `mortality` is passed as an explicit `str` parameter (`"low"`/`"standard"`/
  `"high"`) to `_stage_aftermath`, exactly mirroring `creation.py`'s `create_character(...,
  mortality: str, ...)`. No settings-file loader is introduced.
- **Rationale**: nothing in `engine/wyrd/` currently reads a persisted tone-contract file at
  resolution time — `mortality` is only ever consumed as a caller-supplied value (character
  creation). Introducing a new file-reading mechanism here would be scope well beyond this
  feature's Definition of Done, and the caller (whatever assembles a fight's requests) already
  knows the active setting's `mortality` the same way it already knows it at creation time.
- **Alternatives considered**: reading `mortality` off the chronicle state or a new
  `tone_contract.yaml` loader was considered and rejected as out of scope — no such loader exists
  anywhere in the engine yet, and building one is a different, larger feature than this one.

## Why the Fate spend is not a `propose`/`commit` mechanic

- **Decision**: the Fate spend is a new standalone function, `close_death_row`, operating
  directly on an already-staged/committed `aftermath` step and a character's in-memory
  frontmatter dict — not a `_MECHANICS` entry routed through `_stage_request`.
- **Rationale**: every entry in `_MECHANICS` resolves a fresh `d100` roll
  (`_resolve_test`/`_resolve_ordinary_test`/`_resolve_exposure`); a Fate spend rolls nothing —
  it deterministically rewrites an already-rolled result. Forcing it through the roll-staging
  pipeline would mean inventing a no-op "roll" for a mechanic that spec.md's own Definition of
  Done requires be roll-free, which is a worse fit than a plain function call.
- **Alternatives considered**: adding `"fate-spend"` to `_MECHANICS` with a `resolve_fn` that
  performs no roll was considered and rejected — `_resolve_test`'s shared roll machinery
  (`effective_pct`, Wyrd die, degrees) has no meaning for a Fate spend, and threading a
  fits-nothing case through it would make that shared function harder to read for every other
  caller.

## Companion status transition scope

- **Decision**: `close_death_row` (and the staging-time closures in `_stage_aftermath`) return a
  companion `status` mutation (`dead`/`away`) only when the resolved entity's frontmatter carries
  `role: companion` (`docs/design/22-state.md`); the player character's own entity never receives
  this mutation (spec.md FR-011).
- **Rationale**: spec.md Story 5 and FR-008/FR-009/FR-011 are explicit that this is
  companion-specific; the player character's own permanent-death handling is out of this
  feature's scope (spec.md Assumptions).
- **Alternatives considered**: none — the design docs and spec.md leave no ambiguity here.
