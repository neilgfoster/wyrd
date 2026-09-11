# Data Model: Succession: successor selection and inheritance

## Entanglement vocabulary (closed, six members, fixed priority order)

`wronged` > `investigating` > `bystander` > `rival` > `found_evidence` > `companion`

## Function signatures (pure, no I/O) — `engine/wyrd/succession.py`

- `rank_candidates(candidates: list[dict]) -> list[dict]`
  Returns `candidates` sorted by their `entanglement` field's priority index, stable on ties
  (FR-001, FR-002). Raises `ValueError` naming the offending candidate if any `entanglement`
  value is outside the six-member vocabulary.

- `propose_successors(ranked: list[dict], limit: int = 3) -> list[dict]`
  Returns the first `limit` entries of `ranked` (FR-003) — fewer if `ranked` has fewer.

- `inherit(predecessor: dict, inherited_holding: dict | None = None) -> dict`
  Returns `{"threads": ..., "enemies": ..., "active_threats": ..., "world_belief": ...,
  "predecessor_reputation": ...}`, copying each field from `predecessor` when present (absent
  when the predecessor didn't have it) (FR-004, FR-005). Never includes `skills`, `careers`,
  `advances`, `stamina`, `fate`, `taint`, `transformations`, `afflictions`, or `holdings` keys,
  regardless of whether `predecessor` carried them. When `inherited_holding` is given, it is
  added under `holding`, with `encumbered: True` set on it (FR-006) — absent otherwise.

- `record_predecessor(outcome: str, *, fact: str | None = None, rumour: str | None = None) -> dict`
  `outcome` is one of `"lost" | "died" | "retired"` (FR-007). Returns `{"status":
  "gm-controlled"}` for `lost`, `{"status": "findable"}` for `retired`, and `{"status": "died",
  "fact": fact, "rumour": rumour}` for `died` — `fact`/`rumour` present (possibly differing)
  only for that outcome. Raises `ValueError` for any other `outcome` string.

## Example

```python
candidates = [
    {"id": "a-rival-merchant", "entanglement": "rival"},
    {"id": "the-inquisitor", "entanglement": "investigating"},
    {"id": "an-old-companion", "entanglement": "companion"},
]
ranked = rank_candidates(candidates)
# [inquisitor, rival, companion] -- investigating outranks rival outranks companion

proposal = propose_successors(ranked)  # all 3, since limit defaults to 3 and only 3 exist

inherited = inherit(
    {"threads": [...], "enemies": [...], "skills": [...], "reputation": "a notorious killing"},
    inherited_holding={"id": "the-mill"},
)
# inherited == {
#     "threads": [...], "enemies": [...],
#     "predecessor_reputation": "a notorious killing",
#     "holding": {"id": "the-mill", "encumbered": True},
# }
# -- no "skills" key at all

recorded = record_predecessor("died", fact="killed in the flood", rumour="vanished, some say taken")
```
