# Quickstart: Engine scaffolding

Validates the two load-bearing guarantees this feature provides — deterministic dice, and
persist-before-narrate state — end to end, plus the minimal CLI entry point.

## Prerequisites

- Python 3.11+, no packages to install (stdlib only).
- Run from the repository root.

## 1. The CLI runs with no setup

```bash
python3 -m wyrd.client describe
```

Expected: the `TOOLS` catalog as JSON, containing at least the `roll` verb (SC-004).

## 2. A roll is deterministic given a seed

```bash
python3 -m wyrd.client roll --seed 1
python3 -m wyrd.client roll --seed 1
```

Expected: both calls print the identical `result` value (SC-001, FR-002).

## 3. A roll without a seed is not fixed

```bash
python3 -m wyrd.client roll
python3 -m wyrd.client roll
```

Expected: the two `result` values are not guaranteed equal (drawn from a real random source,
FR-003) — run a few times to observe variation.

## 4. An invalid roll is rejected, not silently wrong

```bash
python3 -m wyrd.client roll --sides 0
```

Expected: a structured `{"error": {...}}` result, not a numeric roll (FR-004).

## 5. State round-trips through a save/load cycle

```bash
python3 -m wyrd.client roll --seed 1
python3 -c "from wyrd.state import load; print(load()['last_roll']['result'])"
```

Expected: the printed value matches the `result` the `roll` call reported (SC-002, FR-005/006).

## 6. An interrupted write never corrupts the file

Covered by an automated test (`tests/engine/test_state.py`) that simulates a kill mid-write and
asserts the file still parses as either the prior or the new valid state (SC-003, FR-007) — not
practical to demonstrate reliably by hand at a terminal.

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```

Expected: all tests pass, covering every scenario above plus `test_client.py`'s coverage of
`describe`'s structured-error path for an unknown `--name`.
