# Phase 1 Data Model: Action economy and engagement

## Combat scene (extends #243's `combat` key)

| Field | Type | Notes |
|---|---|---|
| `engaged` | `list[dict]` | Each entry `{"a": entity_path, "b": entity_path}` — an unordered close-engagement pair. |
| `acted` | `list[str]` | Entity paths that have spent their action this round; cleared by `advance_round`. |

## Functions

| Function | Signature | Notes |
|---|---|---|
| `has_acted` | `(actor, *, state_path) -> bool` | |
| `engaged_with` | `(actor, *, state_path) -> list[str]` | Every combatant currently paired with `actor`. |
| `is_engaged` | `(actor, *, state_path) -> bool` | `bool(engaged_with(actor))`. |
| `close` | `(actor, opponent, *, state_path) -> dict` | Raises if `actor` has already acted this round. |
| `break_off` | `(actor, opponent_attacks: dict[str, dict], *, seed=None, state_path) -> dict` | `opponent_attacks` must name exactly `engaged_with(actor)`; returns `resolution.propose_batch`'s own result (or a no-op shape if there were no engagements). |
| `ranged_attack_difficulty` | `(shooter, target, *, state_path) -> str` | `"difficult"` \| `"challenging"` \| `"average"`. |
| `resolve_ranged_attack` | `(shooter, target, skill, weapon_dice, armour_dice, *, seed=None, state_path) -> dict` | Applies the difficulty modifier via `declaration_bonus`; redirects to the target's own engaged ally on an Ill Omen. |

## Relationships

```text
close(actor, opponent)
  -> raise if has_acted(actor)
  -> engaged.append({"a": actor, "b": opponent})
  -> acted.append(actor)

break_off(actor, opponent_attacks)
  -> partners = engaged_with(actor)
  -> raise if set(opponent_attacks) != set(partners)
  -> engaged = [pair not involving actor]
  -> acted.append(actor)  # break off also spends the turn
  -> resolution.propose_batch([{"actor": opp, "mechanic": "combat-attack", "target": actor, ...}
                                for opp, gear in opponent_attacks])

ranged_attack_difficulty(shooter, target)
  -> "difficult" if is_engaged(shooter)
  -> "challenging" if engaged_with(target) minus {shooter} is non-empty
  -> "average" otherwise

resolve_ranged_attack(shooter, target, ...)
  -> modifier = DIFFICULTY_BONUSES[ranged_attack_difficulty(shooter, target)]
  -> allies = engaged_with(target) minus {shooter}
  -> propose(combat-attack, target=target, declaration_bonus=modifier)
  -> if allies and result.roll.wyrd_die == "ill_omen":
       discard(result.proposal_id)
       propose(combat-attack, target=allies[0], declaration_bonus=modifier, seed=seed+1)
```
