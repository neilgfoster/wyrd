# Quickstart: Companion and party simulation engine support

## Prerequisites

```bash
export PYTHONPATH=engine
```

## Validate a companion record

```python
from wyrd import party

companion = {
    "role": "companion",
    "status": "with-party",
    "objective": {"wants": "clear her brother's name", "next_step": "find the ledger"},
    "flaw": "will not abandon a debt",
    "secret": "the ledger implicates her too",
    "arc": "confess or burn the ledger",
    "career": "hedge-lawyer",
    "bond": 1,
    "taint": 0,
    "strain": 0,
    "wounds": [],
}
assert party.validate_companion(companion) == {"valid": True}
```

## Compute a Tension event against Bond

```python
assert party.tension_delta(1, bond=3, strained_pairing=False) == 0
assert party.tension_delta(1, bond=-2, strained_pairing=False) == 3
assert party.tension_delta(1, bond=None, strained_pairing=False) == 1  # no companion named
```

## Apply Tension and see a break

```python
result = party.apply_tension(current=5, delta=2)
assert result == {"tension": 0, "broke": True}
```

## Gate a join on Loyalty

```python
relations = {("crown", "free-companies"): "irreconcilable"}
result = party.can_join("free-companies", ["crown"], relations, party_size=2)
assert result["allowed"] is False
assert "irreconcilable" in result["reason"]
```

## Verification

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_party.py -q
python3 -m ruff check .
python3 -m ruff format --check .
python3 tools/check_companion_layers.py
```

All four checks must be clean before this feature is considered done, per spec.md's Success
Criteria.
