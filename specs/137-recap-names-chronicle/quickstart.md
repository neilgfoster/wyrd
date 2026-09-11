# Quickstart: Recap names its chronicle and setting

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import loadtier

entities = {"the-player": {"id": "the-player", "type": "character", "role": "player"}}
chronicle = {"name": "the-drowned-chronicle", "setting": {"repo": "my-setting"}}

text = loadtier.generate_recap(entities, chronicle)
assert "the-drowned-chronicle" in text
assert "my-setting" in text
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_loadtier -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered, and every pre-existing
`GenerateRecapTest` case still passes unchanged.
