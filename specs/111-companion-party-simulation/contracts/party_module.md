# Contract: `wyrd.party`

This is a library, not a network service — its "contract" is the public function surface
`engine/wyrd/party.py` exposes, matching the shape `career.py`/`character.py` already use (plain
functions over plain dicts, no classes, standard library only).

```python
def validate_companion(companion: dict) -> dict:
    """Check a companion record's mechanical layer against the closed five-field set.

    Returns {"valid": True} or {"valid": False, "error": "<which field, missing or unexpected>"}.
    Never raises for a malformed but well-typed record; raises only on structurally invalid input
    (e.g. companion is not a dict).
    """

def tension_delta(base_delta: int, *, bond: int | None, strained_pairing: bool) -> int:
    """The actual Tension change for an event, per docs/design/16-session.md and ADR 0034.

    `bond` is the named companion's Bond (-3..+3), or None if the event names no companion.
    `strained_pairing` is whether the party currently holds a strained Loyalty pairing (doubles
    the rate before any Bond offset). Result is never negative.
    """

def apply_tension(current: int, delta: int) -> dict:
    """Apply a computed delta to the current Tension (0-6).

    Returns {"tension": <new value>, "broke": <bool>}. If the result would reach or exceed 6,
    the break resolves once and the returned tension is 0.
    """

def loyalty_relation(a: str, b: str, relations: dict[tuple[str, str], str]) -> str:
    """"strained", "irreconcilable", or "undeclared" for the pair (a, b), symmetric in a/b."""

def can_join(candidate_loyalty: str, party_loyalties: list[str],
             relations: dict[tuple[str, str], str], party_size: int) -> dict:
    """Whether a candidate with this Loyalty may join.

    Returns {"allowed": True} or {"allowed": False, "reason": "<irreconcilable pair | party full>"}.
    """

def roster(companions: list[dict]) -> list[dict]:
    """The full party roster: each companion's narrative and mechanical layers together,
    unchanged from what was stored -- no narrative content is generated or altered (FR-013).
    """
```

No HTTP/CLI surface is added by this feature; `engine/wyrd/client.py`'s verb catalog is untouched
unless a future feature exposes party operations as an MCP tool.
