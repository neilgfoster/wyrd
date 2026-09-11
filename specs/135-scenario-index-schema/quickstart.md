# Quickstart: Scenario index schema and deterministic selection (scenarios.json)

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_scenario as cs

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

cs.validate_scenario_record(record)  # no error

scaled = cs.scale_danger(record, party=6)

requirements = cs.check_requirements(record, available_access=[], available_capability=["literacy"])
assert requirements["access"]["unmet"] == ["temple"]
assert requirements["capability"]["met"] == ["literacy"]

assert cs.is_eligible_for_setting(record, "my-setting") is True
assert cs.is_eligible_for_setting(record, "some-other-setting") is False
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_scenario -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test,
including all nine `scale` values, all four `season` values, and the "never filters" behaviour
of requirement/helped-by checks.
