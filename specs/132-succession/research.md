# Research: Succession: successor selection and inheritance

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Two decisions worth recording:

- **Decision**: the entanglement vocabulary is exactly `wronged`, `investigating`, `bystander`,
  `rival`, `found_evidence`, `companion`, in that fixed priority order, closed (rejects anything
  else).
  **Rationale**: this is a direct, engine-neutral slugging of docs/design/19-campaign.md's own
  ordered list ("Someone the predecessor wronged... Someone who was investigating them... A
  bystander whose life the predecessor's actions changed... A rival... Whoever found what you
  left behind... A companion"), matching this codebase's established closed-vocabulary
  convention (ADR 0026, adversary traits) rather than leaving it open to arbitrary strings a
  caller might supply.
  **Alternatives considered**: an open string field with no validation — rejected; ranking
  against an undefined vocabulary would silently misorder (or crash on) any typo, and this
  codebase already has a working precedent (ADR 0026) for a closed vocabulary exactly this
  shape.

- **Decision**: `inherit` takes the predecessor's full state dict and an explicit
  `inherited_holding: dict | None` parameter — never reads a `holdings` list off the predecessor
  and decides for itself which (if any) to carry.
  **Rationale**: docs/design/19-campaign.md is explicit that "Holdings are not automatically
  passed on... Losing the holding is often the better story" — the decision of *whether* one
  reaches the successor is a GM call this feature must not make on its own; taking it as an
  explicit argument keeps that call visibly outside this function rather than buried in a
  default.
  **Alternatives considered**: a `holdings: list` parameter defaulting to `[]`/passed through
  unfiltered — rejected, since that would either always drop holdings (making the "arrives
  encumbered" acceptance criterion untestable) or risk a future caller passing the full list
  and getting automatic inheritance by accident.
