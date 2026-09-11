# Research: Threats aspect & activation

No `[NEEDS CLARIFICATION]` markers remain in spec.md, and the Technical Context above has no
open unknowns — this feature reuses an existing, already-documented pattern rather than
introducing a new one, so there is no research question to resolve. Recorded here for the record:

- **Decision**: model the Threat activation roll and effects-table lookup exactly on
  `journey.roll_hazard`'s existing shape (caller supplies both the activation roll and the
  sub-table roll; the function bands them, never calls `random` itself).
  **Rationale**: `journey.py`'s own module docstring already states it reuses "the Threat
  activation-roll shape (`d100 <= imminence * 10`, docs/design/19-campaign.md)" and that "No...
  Threat concept has any runtime implementation elsewhere in `engine/wyrd/` yet" — this feature is
  exactly that missing implementation, and matching the shape `journey.py` already assumed keeps
  the two modules consistent rather than introducing a second convention for the same mechanic.
  **Alternatives considered**: rolling internally via `rules.roll_d100` — rejected, because every
  other resolution-adjacent module in this engine (`resolution.py`, `journey.py`, `economy.py`)
  keeps randomness at the call site and does banding/lookup as a pure function; a seed-based
  internal roll would also complicate the exact-boundary tests SC-002 requires.

- **Decision**: represent a Threat as a plain `dict` (the `threat` block), not a dataclass or a
  ninth/tenth `entity.ENTITY_TYPES` member.
  **Rationale**: docs/design/19-campaign.md is explicit that "It is not an entity type. It is an
  *aspect*" — and `entity.py`'s existing `_TYPE_ENUM_FIELDS`/`ENTITY_TYPES` machinery is scoped to
  the ten real entity types; adding Threat there would misrepresent it as an eleventh. Plain dicts
  also match `journey.py`/`economy.py`'s existing convention for aspects/records below the entity
  layer.
  **Alternatives considered**: a `Threat` dataclass — rejected as unnecessary ceremony for a
  four-function pure-logic module with no other consumer yet requiring type-checked construction.
