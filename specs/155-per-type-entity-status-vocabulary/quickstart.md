# Quickstart: Per-type entity status vocabulary

## Prerequisites

- Python 3.11+, standard library only (no install step).
- Run from the repo root with `PYTHONPATH=engine`, matching `tests/engine/`'s own convention.

## Reproduce the bug (before the fix)

```bash
cd engine
PYTHONPATH=. python3 - <<'PY'
from wyrd import entity

companion = {
    "id": "hallam", "type": "character", "name": "Hallam",
    "setting": "example-setting", "role": "companion", "status": "with-party",
}
print(entity.validate(companion))
PY
```

Before this fix: `{'valid': False, 'error': "invalid status 'with-party'"}` — a real, documented
companion status is rejected outright.

## Validate the fix

Same script, run again after the fix lands — expected output: `{'valid': True}`.

The same check for a thread:

```bash
cd engine
PYTHONPATH=. python3 - <<'PY'
from wyrd import entity

thread = {
    "id": "the-missing-envoy", "type": "thread", "name": "The Missing Envoy",
    "setting": "example-setting", "status": "open",
}
print(entity.validate(thread))
PY
```

Expected: `{'valid': True}`.

## Run the full test suite for this module

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_entity -v
```

The new end-to-end tests (`FR-005`) load an actual companion entity file and an actual thread
entity file from a temporary directory via `wyrd.state.load_entity`, not an in-memory dict, and
assert `entity.validate()` accepts both — this is the exact gap `#408` reports (no prior test
loaded such a file from disk).

## Regression check

```bash
python3 -m ruff check .
python3 -m ruff format --check .
PYTHONPATH=engine python3 -m unittest discover -s tests/engine -v
```

All must pass — no existing entity type's validation behaviour should change (`SC-003`).
