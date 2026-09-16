# Quickstart: validating the anti-inflation checks

## Prerequisites

- Python 3.11+, standard library only (no install step).
- `engine/wyrd/generation.py` (#420) already present — this feature's candidate/request shapes
  extend its `GenerationRequest`/`GenerationResult`.

## Run the tests

```bash
cd /path/to/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_generation_checks -v
```

Expected: every test passes — one passing case and one rejecting/narrowing case per check
(spec.md's own acceptance criteria), plus `run_checks`'s aggregation order.

## Manually exercise a rejection

```bash
PYTHONPATH=engine python3 - <<'PY'
from wyrd import generation, generation_checks

request = generation.new_request(
    scale="beat",
    mode="live-play",
    setting_ref="some-setting",
    tone_contract={"prophecy": "forbidden", "scale_drift": "suppressed"},
    written_for=4,
    threads=[{"id": "the-ledger", "heat": 2}],
    danger_rating=3,
    era="present",
)
candidate = {
    "danger": 3,
    "named_entities": ["the-ledger-keeper"],
    "prophecy_claim": "destiny",
    "threat_updates": [],
    "coincidences": [],
}

checks = generation_checks.run_checks(request, candidate, known_entities=["the-ledger-keeper"])
for entry in checks:
    print(entry)
PY
```

Expected: the `FR-008` entry reports `outcome: reject` (a `destiny` claim under
`prophecy: forbidden`); every other entry reports `pass` for this otherwise-clean candidate.

## Confirm ruff cleanliness

```bash
python3 -m ruff check engine/wyrd/generation_checks.py tests/engine/test_generation_checks.py
python3 -m ruff format --check engine/wyrd/generation_checks.py tests/engine/test_generation_checks.py
```

Both must exit clean, per CLAUDE.md's repo-wide lint gate.
