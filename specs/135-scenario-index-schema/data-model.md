# Data Model: Scenario index schema and deterministic selection (scenarios.json)

## Scenario record (deterministic fields only, this feature's own concern)

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `settings` | `list[str]` | eligible settings; `is_eligible_for_setting` checks membership. |
| `scale` | `str` | closed: village/town/city/wilderness/underground/waterway/road/ship/fortress. |
| `region` | `str` | e.g. `"any"` or a specific region id; not validated against a closed set (no fixed region vocabulary exists engine-wide). |
| `danger` | `int` | intrinsic, as written for `written_for`. |
| `written_for` | `int` | party size the scenario was written for. |
| `length` | `int` | sessions. |
| `season` | `str` | closed: `any`, `winter`, `harvest`, `festival`. |
| `needs_access` | `list[str]` | requirements, never a gate. |
| `needs_capability` | `list[str]` | requirements, never a gate. |
| `helped_by` | `list[str]` | flags only, never a gate. |
| `adaptation` | `str` | `none`/`reskin`/`rewrite`; passed through unchanged, not validated by this feature (spec.md's Assumptions). |

## Function signatures (pure, no I/O) — `engine/wyrd/corpus_scenario.py`

- `validate_scenario_record(record: dict) -> dict`
  Returns `record` unchanged if `scale` and `season` are both in their closed vocabularies
  (FR-001, FR-002); raises `ValueError` naming the offending field otherwise (FR-003).

- `scale_danger(record: dict, party: int) -> Fraction`
  `adversary.danger_effective(record["danger"], party, record["written_for"])`, unchanged
  (FR-004, FR-005).

- `check_requirements(record: dict, available_access: list[str], available_capability: list[str]) -> dict`
  Returns `{"access": {"met": [...], "unmet": [...]}, "capability": {"met": [...], "unmet":
  [...]}}` — every entry in `needs_access`/`needs_capability` classified, never filtered
  (FR-006).

- `check_helped_by(record: dict, available: list[str]) -> dict`
  Returns `{"met": [...], "unmet": [...]}` for `helped_by` — informational only (FR-007).

- `is_eligible_for_setting(record: dict, setting: str) -> bool`
  `setting in record["settings"]` — the one genuine hard gate this feature implements (FR-008).

## Example

```python
record = {
    "id": "the-drowning-well",
    "settings": ["my-setting"],
    "scale": "village",
    "region": "any",
    "danger": 3,
    "written_for": 4,
    "length": 2,
    "season": "any",
    "needs_access": ["temple"],
    "needs_capability": ["literacy"],
    "helped_by": ["medicine"],
    "adaptation": "reskin",
}

validate_scenario_record(record)  # no error -- scale/season both valid

scaled = scale_danger(record, party=6)  # == adversary.danger_effective(3, 6, 4)

requirements = check_requirements(record, available_access=[], available_capability=["literacy"])
# {"access": {"met": [], "unmet": ["temple"]},
#  "capability": {"met": ["literacy"], "unmet": []}}
# -- record is NOT excluded; the caller decides what "unmet" means for play.

assert is_eligible_for_setting(record, "my-setting") is True
assert is_eligible_for_setting(record, "some-other-setting") is False
```
