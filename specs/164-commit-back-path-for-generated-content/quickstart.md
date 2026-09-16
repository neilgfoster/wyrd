# Quickstart: validating the commit-back path

## Prerequisites

- Python 3.11+, standard library only (no install step).
- `engine/wyrd/generation.py` (#420) and `engine/wyrd/generation_checks.py` (#421) already
  present — `accept_result`/`reject_result` take a `GenerationResult` that has already been run
  through `run_checks`.
- A scratch directory to write the demonstration entity file into (never a real setting's
  `entities/` tree for this quickstart).

## Run the tests

```bash
cd /path/to/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_generation_commit -v
```

Expected: every test passes — an accepted write (User Story 1), a declined/rejected no-write case
asserted against the filesystem directly (User Story 2), and a test asserting the accept path
calls `thread.py`'s/`threat.py`'s own functions rather than equivalent inline logic (FR-003).

## Manually exercise an accepted commit

```bash
PYTHONPATH=engine python3 - <<'PY'
import pathlib
import tempfile

from wyrd import generation, generation_commit

request = generation.new_request(
    scale="beat", mode="live-play", setting_ref="some-setting",
    tone_contract={"prophecy": "forbidden", "scale_drift": "suppressed"},
    written_for=4, threads=[{"id": "the-ledger", "heat": 2}], danger_rating=3, era="present",
)
result = generation.new_result(
    candidate={"danger": 3}, checks=[{"rule": "FR-007", "outcome": "pass", "detail": ""}],
    consumed=["the-ledger"],
)

with tempfile.TemporaryDirectory() as tmp:
    path = pathlib.Path(tmp) / "a-new-beat.md"
    outcome = generation_commit.accept_result(
        result, entity_id="a-new-beat", entity_type="beat", name="A New Beat",
        setting="some-setting", mode="live-play", body="What happens in play.", path=path,
        thread_updates=[], threat_updates=[],
    )
    print(outcome["committed"], outcome["entity"]["sources"])
    print(path.read_text())
PY
```

Expected: `outcome["committed"]` is `True`, `outcome["entity"]["sources"]` carries exactly one
entry `{"generated": True, "mode": "live-play", "consumed": ["the-ledger"]}`, and the printed file
carries `status: drafted`.

## Manually exercise a rejected commit (writes nothing)

```bash
PYTHONPATH=engine python3 - <<'PY'
import pathlib
import tempfile

from wyrd import generation, generation_commit

result = generation.new_result(
    candidate={"danger": 99},
    checks=[{"rule": "FR-009", "outcome": "reject", "detail": "danger too high"}],
)

with tempfile.TemporaryDirectory() as tmp:
    path = pathlib.Path(tmp) / "should-not-exist.md"
    outcome = generation_commit.accept_result(
        result, entity_id="x", entity_type="beat", name="X", setting="s", mode="live-play",
        body="", path=path,
    )
    print(outcome)
    print(path.exists())
PY
```

Expected: `outcome["committed"]` is `False` with `reason: "checks_failed"`, and `path.exists()`
prints `False`.

## Confirm ruff cleanliness

```bash
python3 -m ruff check engine/wyrd/generation_commit.py engine/wyrd/entity.py tests/engine/test_generation_commit.py
python3 -m ruff format --check engine/wyrd/generation_commit.py engine/wyrd/entity.py tests/engine/test_generation_commit.py
```

Both must exit clean, per CLAUDE.md's repo-wide lint gate.
