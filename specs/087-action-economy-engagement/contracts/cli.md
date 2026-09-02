# Contract: library API (no CLI subcommand — same rationale as #243's plan.md)

```python
def has_acted(actor, *, state_path=...) -> bool: ...
def engaged_with(actor, *, state_path=...) -> list[str]: ...
def is_engaged(actor, *, state_path=...) -> bool: ...

def close(actor, opponent, *, state_path=...) -> dict:
    """Raises ValueError if actor has already acted this round."""

def break_off(actor, opponent_attacks: dict[str, dict], *, seed=None, state_path=...) -> dict:
    """opponent_attacks: {"<opponent path>": {"skill", "weapon_dice", "armour_dice"}} -- must
    name exactly engaged_with(actor). Returns resolution.propose_batch's own shape, or a no-op
    result ({"proposal_id": None, "roll": None, "mutations": [], "steps": []}) if actor had no
    engagements."""

def ranged_attack_difficulty(shooter, target, *, state_path=...) -> str:
    """"difficult" | "challenging" | "average"."""

def resolve_ranged_attack(
    shooter, target, skill, weapon_dice, armour_dice, *, seed=None, state_path=...,
) -> dict:
    """Same return shape as resolution.propose. Redirects to the target's own engaged ally
    (not the shooter) on an Ill Omen when the Challenging row applies."""
```

## `resolution.py` fix (no signature change)

`combat-attack`'s own `declaration_bonus` (a request's stated value, not only a reroll-resource/
Omen delta) now actually reaches the attacker's boosted skill — previously silently dropped.
