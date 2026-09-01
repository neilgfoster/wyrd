# Quickstart: Core opposed-test resolution

Validates the opposed-test formula and the Wyrd die's independence, end to end.

## Prerequisites

- #221 (engine scaffolding) already merged.
- Run from the repository root with `PYTHONPATH=engine`.

## 1. An even match is a coin flip

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --seed 1
```

Expected: `effective_pct` is 50 (SC-001, US1 scenario 1).

## 2. A skill gap shifts effective%, clipped to [5, 95]

```bash
python3 -m wyrd.client opposed-test --skill 70 --opponent 30 --seed 1
python3 -m wyrd.client opposed-test --skill 95 --opponent 5 --seed 1
```

Expected: the first shows `effective_pct: 90`; the second is clipped to `effective_pct: 95`
(SC-001, US1 scenarios 2-3).

## 3. Degrees appear only on success

```bash
python3 -m wyrd.client opposed-test --skill 70 --opponent 30 --seed 1
python3 -m wyrd.client opposed-test --skill 30 --opponent 70 --seed 1
```

Expected: the first (likely success at `effective_pct: 90`) reports a `degrees` integer; the
second (likely failure at `effective_pct: 10`) reports `degrees: null` (SC-002, US2).

## 4. The Wyrd die is read independently of success

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --seed 9
python3 -m wyrd.client opposed-test --skill 5 --opponent 95 --seed 9
```

Expected: both report the same `wyrd` value for the same seed's units digit, regardless of
whether `success` differs between the two calls (SC-003, US3).

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```

Expected: all tests pass, including the new opposed-test cases in `test_rules.py`,
`test_verbs.py`, and `test_client.py`.
