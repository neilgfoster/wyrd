# Research: Holdings: accumulated stakes

No `[NEEDS CLARIFICATION]` markers remain in spec.md. The one substantive question — how much of
this issue's scope is already implemented — was resolved by reading the existing codebase rather
than guessing:

- **Finding**: `economy.gain_holding`/`lose_holding` (#276-280, epic #216) already implement
  holding recording, and `character.py`/`creation.py` already keep `holdings` and `allegiances`
  as two entirely separate list fields, with existing passing test coverage
  (`tests/engine/test_economy.py`'s `test_gaining_a_holding_*`/`test_losing_a_holding_*`). This
  issue's first acceptance criterion ("Holdings are recorded and distinguishable from
  allegiances") is therefore already met, not new work.
  **Implication**: this feature's actual scope narrows to the issue's second acceptance
  criterion — the personal-stakes flag — which has no existing implementation anywhere in
  `engine/wyrd/`.

- **Decision**: `flag_personal_stakes` takes a plain `holdings: list[str]` and a list of Threat
  entity dicts, with no import of `threat.py` itself.
  **Rationale**: matches `journey.py`'s existing convention (`resolve_leg` takes a `threats: dict`
  argument rather than importing `threat.py`) of keeping sibling runtime modules decoupled —
  each one operates on the shape another produces, without a hard dependency between them.
  **Alternatives considered**: importing `threat.active_threats`' return type directly and adding
  a `holdings` parameter to `threat.py` itself — rejected, since `threat.py`'s own scope
  (docs/design/19-campaign.md's "Threats" section) is deliberately silent on holdings; keeping
  the connection in a separate module matches the issue's own framing ("Threats feature reads
  holdings to raise stakes" — a reader, not a modification of the Threat module itself).
