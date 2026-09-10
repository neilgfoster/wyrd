# Quickstart: The Rally: recovery, advance award and commit

## Prerequisites

```bash
export PYTHONPATH=engine
```

## Fixed recovery clamps at 0 and at maximum

```python
from wyrd import advancement, rally

recovered = rally.apply_recovery(strain=3, stamina=4, stamina_max=6)
assert recovered == {"strain": 2, "stamina": 5}

floored = rally.apply_recovery(strain=0, stamina=4, stamina_max=6)
assert floored["strain"] == 0  # never goes negative

capped = rally.apply_recovery(strain=1, stamina=6, stamina_max=6)
assert capped["stamina"] == 6  # never exceeds the maximum
```

## A Rally with no award is a valid outcome

```python
record = advancement.new_record()
result = rally.apply_rally(strain=3, stamina=4, stamina_max=6, advancement_record=record)
assert result["strain"] == 2
assert result["stamina"] == 5
assert result["award"] is None  # recovery applies identically whether or not an award is claimed
```

## Claiming a valid trigger reuses `advancement.award_advance`, unchanged

```python
record = advancement.new_record()
result = rally.apply_rally(
    strain=3, stamina=4, stamina_max=6, advancement_record=record, trigger="endured",
)
assert result["award"]["awarded"] is True
assert result["award"]["trigger"] == "endured"
assert result["award"]["record"]["advances_unspent"] == 1

# a refused claim (e.g. already awarded this session) surfaces the same refusal award_advance
# would give directly -- the Rally still applies its fixed recovery regardless
already = advancement.award_advance("endured", record)["record"]
refused = rally.apply_rally(
    strain=3, stamina=4, stamina_max=6, advancement_record=already, trigger="endured",
)
assert refused["award"]["awarded"] is False
assert refused["award"]["refusal"] == "already_awarded"
assert refused["strain"] == 2 and refused["stamina"] == 5  # recovery still applied
```

## The persist/commit step runs exactly once, after recovery and any award

```python
calls = []
rally.apply_rally(
    strain=3, stamina=4, stamina_max=6, advancement_record=advancement.new_record(),
    trigger="learned", commit=lambda: calls.append("committed"),
)
assert calls == ["committed"]  # exactly once

# omitting commit is a valid Rally with nothing persisted yet (#300 not wired in)
rally.apply_rally(strain=3, stamina=4, stamina_max=6, advancement_record=advancement.new_record())
```

## Verification

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_rally -v
python3 -m ruff check .
python3 -m ruff format --check .
```

All checks must be clean before this feature is considered done, per spec.md's Success Criteria.
