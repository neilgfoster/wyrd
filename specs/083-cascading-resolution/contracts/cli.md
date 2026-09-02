# Contract: extended `propose` response shape

`propose`'s existing CLI/library contract (specs/082-propose-commit-core/contracts/cli.md) is
unchanged in signature. Its response gains a `steps` field:

```python
def propose(
    actor: str | pathlib.Path,
    mechanic: str,
    skill: str | None = None,
    target: str | pathlib.Path | None = None,
    difficulty: str = "average",
    declaration_bonus: int = 0,
    *,
    tier: str | None = None,
    weapon_dice: str | None = None,
    armour_dice: str | None = None,
    stamina_field: str = "stamina",  # actor's stamina sub-dict key, e.g. {"current": .., "max": ..}
    seed: int | None = None,
) -> dict:
    """Returns {"proposal_id": str, "roll": dict, "mutations": list[dict], "steps": list[dict]}.
    "roll" and "mutations" keep #235's exact shape (roll == steps[0]["roll"], mutations ==
    concatenation of every step's own mutations) -- an existing caller reading only those two
    keys sees no change. "steps" is new: the full cascade, each with step_id/mechanic/roll/
    mutations/depends_on."""

def commit(proposal_id: str) -> dict:
    """Unchanged signature. Applies every mutation across every staged step atomically."""

def discard(proposal_id: str) -> dict:
    """Unchanged signature."""
```

New mechanics accepted by `propose`'s `mechanic` argument: `combat-attack` (requires `target`,
`weapon_dice`, `armour_dice`), `transformation` (not called directly by a caller — only staged by
`exposure`'s own cascade, per FR-002/FR-007; naming it directly is out of scope). `weapon-damage`/
`armour`/`critical` are step-internal mechanic names, never passed by a caller to `propose`
directly.
