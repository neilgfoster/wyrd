# Data Model: Holdings: accumulated stakes

## Existing (unchanged by this feature)

- **`holdings`** (`character.py`, `creation.py`, `economy.py`): `list[str]` of held entity ids,
  kept distinct from `allegiances`. `economy.gain_holding`/`lose_holding` already own its
  mutation.

## New — `engine/wyrd/holding.py`

- `flag_personal_stakes(threats: list[dict], holdings: list[str]) -> list[dict]`
  Returns a new list, same length and order as `threats` (FR-002): each entity dict is returned
  with `personal: bool` set to whether its `id` appears in `holdings` (FR-001). A Threat entity
  with no `id`, or an empty `holdings` list, yields `personal: False` (FR-003) — never raises.
  Every other field of each Threat entity is passed through unchanged.

## Example

```python
threats = [
    {"id": "the-drowned-mill", "type": "place", "threat": {"imminence": 4}},
    {"id": "some-other-place", "type": "place", "threat": {"imminence": 2}},
]
holdings = ["the-drowned-mill"]

flag_personal_stakes(threats, holdings)
# -> [
#      {"id": "the-drowned-mill", "type": "place", "threat": {...}, "personal": True},
#      {"id": "some-other-place", "type": "place", "threat": {...}, "personal": False},
#    ]
```
