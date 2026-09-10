# Quickstart: Chronicle.yaml schema, load/save and versioning

Validates the feature end-to-end from a Python shell (or a pytest scratch test). No external
services or setup — standard library only.

## Prerequisites

```bash
cd /root/source/neilgfoster/wyrd
export PYTHONPATH=engine
```

## Create a fresh chronicle and round-trip it

```python
import pathlib
from wyrd import state

path = pathlib.Path("/tmp/chronicle.yaml")
fresh = state.default_chronicle_state(
    name="test-chronicle",
    engine_repo="wyrd", engine_version="0.4.0",
    setting_repo="some-setting", setting_version="0.3.1",
)
state.save_chronicle(fresh, path)
loaded = state.load_chronicle(path)
assert loaded == fresh
```

Expected: no exception; `loaded` equals `fresh` field-for-field (spec User Story 1).

## Version bump preserves `created_under`, migrations stay append-only

```python
loaded["engine"]["version"] = "0.5.0"
loaded = state.append_migration(loaded, {
    "from": {"engine": "0.4.0"}, "to": {"engine": "0.5.0"},
    "class": "tuning", "applied": "2026-09-10", "note": "tuning pass",
})
state.save_chronicle(loaded, path)
reloaded = state.load_chronicle(path)
assert reloaded["engine"]["created_under"] == "0.4.0"   # unchanged
assert reloaded["engine"]["version"] == "0.5.0"
assert len(reloaded["migrations"]) == 1
```

Expected: `created_under` untouched by the bump (spec User Story 2); migrations log carries the
new entry (spec User Story 3).

## An illegal edit to an already-appended migration is rejected

```python
tampered = dict(reloaded)
tampered["migrations"] = [dict(reloaded["migrations"][0], note="rewritten")]
try:
    state.save_chronicle(tampered, path)
    raise AssertionError("expected StateError")
except state.StateError:
    pass
```

Expected: `StateError` raised, file on disk unchanged (spec User Story 3, scenario 2).

## `pending` round-trips opaquely

```python
loaded["pending"] = {"beat": "beat-42", "awaiting": "a decision", "rolled": None}
state.save_chronicle(loaded, path)
reloaded = state.load_chronicle(path)
assert reloaded["pending"] == {"beat": "beat-42", "awaiting": "a decision", "rolled": None}
```

Expected: exact round-trip with no interpretation of `pending`'s contents (spec User Story 4).

## Run the automated test suite

```bash
python3 -m unittest tests.engine.test_state -v
```

Expected: all tests pass, including the round-trip, versioning, migration-immutability, and
missing-required-field cases from spec.md's acceptance scenarios.
