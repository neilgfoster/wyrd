# Quickstart: Chronicle intent's lethality is validated against the mortality vocabulary

## Try it

```python
from wyrd import state

fresh = state.default_chronicle_state(
    name="test", engine_repo="wyrd", engine_version="0.4.0",
    setting_repo="my-setting", setting_version="0.1.0",
)
fresh["intent"]["lethality"] = "deadly"  # not in low/standard/high
try:
    state.validate_chronicle(fresh)
except state.StateError as e:
    print(e)  # names the field and the rejected value
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_state -v
```
