# Quickstart: Adversary block loading and validation

Validates that `engine/wyrd/adversary.py` loads a valid bestiary entry, rejects each malformed
class the way `tools/check_bestiary.py` already does, and defaults `ranged` sensibly.

## Prerequisites

- Python 3.11+, stdlib only. Run from the repo root, `/root/source/neilgfoster/wyrd`.

## Scenario 1: load a valid entry by id

```python
import tempfile, pathlib
from wyrd import adversary

bestiary_yaml = """
creatures:
  - id: the-hunter
    name: A named antagonist
    baseline: 35
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
      tracking: 60
    damage: 1d6
    damage_type: slashing
"""

with tempfile.TemporaryDirectory() as d:
    path = pathlib.Path(d) / "bestiary.yaml"
    path.write_text(bestiary_yaml)
    block = adversary.load("the-hunter", path)
    assert block["baseline"] == 35
    assert block["ranged"] is False  # defaulted, not omitted
```

**Expected outcome**: `block` carries every declared field, plus `ranged` defaulted to `false`.

## Scenario 2: a missing required field is rejected

```python
bestiary_yaml = """
creatures:
  - id: no-baseline
    name: Missing its baseline
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
"""
path.write_text(bestiary_yaml)
try:
    adversary.load("no-baseline", path)
    assert False, "should have raised"
except adversary.StateError as exc:
    assert "baseline" in str(exc)
```

**Expected outcome**: loading raises, naming `baseline` as the missing field.

## Scenario 3: `damage` without `damage_type` is rejected; neither is legal

```python
# damage without damage_type -> rejected
bestiary_yaml_bad = """
creatures:
  - id: half-armed
    name: Declares damage but not its type
    baseline: 20
    stamina_max: 5
    armour: none
    skills:
      blade: 40
    damage: 1d6
"""
# neither -> legal (an obstacle, not an attacker)
bestiary_yaml_ok = """
creatures:
  - id: obstacle
    name: Dangerous by being present
    baseline: 10
    stamina_max: 3
    armour: none
    skills:
      presence: 30
"""
```

**Expected outcome**: the first entry fails to load (missing `damage_type`); the second loads
successfully with neither `damage` nor `damage_type` present.

## Running the real tests

```bash
python3 -m pytest tests/engine/test_adversary.py -q
```
