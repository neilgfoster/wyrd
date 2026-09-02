# Contract: `propose_batch` and `reroll`

```python
def propose_batch(requests: list[dict], *, seed: int | None = None) -> dict:
    """Each request: {"actor", "mechanic", "skill"?, "target"?, "difficulty"?,
    "declaration_bonus"?, "tier"?, "weapon_dice"?, "armour_dice"?} -- same keys as `propose`'s
    own kwargs. Returns {"proposal_id", "roll", "mutations", "steps"} -- "roll"/"mutations" cover
    the first request's own first step, for single-request callers; "steps" is the full,
    possibly multi-request, cascade."""

def propose(actor, mechanic, skill=None, target=None, difficulty="average",
            declaration_bonus=0, *, tier=None, weapon_dice=None, armour_dice=None,
            seed=None) -> dict:
    """Unchanged signature (#235/#236) -- now a single-request call to propose_batch."""

def reroll(proposal_id: str, step: int, resource: str, *, seed: int | None = None) -> dict:
    """resource: "resolve" | "fortune" | "bargain". Returns the same shape as propose_batch's
    response, reflecting the revised proposal. Does not invalidate proposal_id. Raises
    ProposalError if the proposal isn't open; ValueError for an unknown resource, an unknown
    step, or a step with no recorded inputs (not a top-level request)."""

def commit(proposal_id: str) -> dict:
    """Unchanged signature -- applies the proposal's current (possibly rerolled) mutations."""

def discard(proposal_id: str) -> dict:
    """Unchanged signature."""
```
