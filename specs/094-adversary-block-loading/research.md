# Research: Adversary block loading and validation

No `NEEDS CLARIFICATION` markers remained in the Technical Context.

## Decision: reuse `state.parse_yaml`, not a new reader

**Rationale**: `engine/wyrd/state.py`'s `parse_yaml` already covers the restricted YAML subset a
bestiary file needs -- nested mappings, lists of mappings (`traits`), scalars -- and its own
docstring already frames it as "the same restricted-subset approach as tools/check_bestiary.py's
reader," deliberately kept separate from `tools/` for the reason below. A bestiary file's
top-level shape (`{"creatures": [...]}`) is exactly what `parse_yaml` already returns for any
YAML text in this subset -- no frontmatter delimiter needed (unlike `character.py`'s entity
files), since a bestiary file is plain YAML, not an entity-with-body file.

**Alternatives considered**: a third, bestiary-specific YAML reader (mirroring
`check_bestiary.py`'s own inline reader instead of reusing `state.py`'s). Rejected -- `state.py`
already exists precisely to be the engine-side counterpart of that reader; adding a second engine
reader for the same restricted subset would be the kind of duplicate-source-of-truth this repo's
process has been corrected for before.

## Decision: validation rules are re-expressed as engine code, not imported from `tools/`

**Rationale**: `engine/wyrd/state.py`'s own docstring states the constraint directly: "engine/ is
the shipped engine and tools/ is repository-maintenance scripts -- the two must not depend on
each other." `tools/check_bestiary.py`'s `check_entry` function is exactly the validation logic
this feature needs, but it must be re-implemented in `engine/wyrd/adversary.py` against the same
constants (`REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, `ARMOUR_RANKS`, `DAMAGE_TYPES`, `TRAIT_EFFECTS`)
rather than imported.

**Alternatives considered**: importing `tools/check_bestiary.py` from `engine/wyrd/adversary.py`.
Rejected outright by the existing architectural boundary; `state.py` already made and documented
this same call for the YAML reader, and this feature follows the identical precedent for the
validation rules.

## Decision: fail on first load, not lazily

**Rationale**: `character.load` (`engine/wyrd/character.py`) validates immediately on load and
raises `state.StateError` naming the problem, rather than returning an unvalidated shape a caller
might use before checking it. `adversary.load` follows the same immediate-validation contract:
FR-002 through FR-007 all describe load-time failures, matching `character.load`'s existing
behavior for its own required-field/unrecognised-field/shape checks (`validate_wound`/
`validate_character`).

**Alternatives considered**: a two-step `read()` + `validate()` API a caller must remember to
call in order. Rejected -- `character.py`'s existing single-call `load` (which validates
internally) is the established pattern this feature's own issue explicitly asks to mirror
("the same role `character.load` plays for a player character").

## Decision: `StateError` is the raised exception type, not a new exception class

**Rationale**: `character.py`'s `validate_wound`/`validate_character` already raise
`state.StateError` for load-time schema violations, and `state.py`'s `load_entity` raises it for
file-shape problems too -- it is already the engine's one exception type for "a file exists but
does not hold valid data for what asked to load it." A new `AdversaryError` would fragment error
handling for callers that already catch `StateError` from `character.load`.

**Alternatives considered**: a dedicated `AdversaryError(StateError)` subclass. Rejected as
unnecessary -- no caller in this feature's scope needs to distinguish an adversary-load failure
from any other `StateError`, and `character.py` itself doesn't subclass per-entity-type either.
