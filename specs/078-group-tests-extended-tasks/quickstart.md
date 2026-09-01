# Quickstart: Group tests and extended tasks

## Prerequisites

- #221, #222, #223 already merged.
- Run from the repository root with `PYTHONPATH=engine`.

## 1. A group test selects the most capable member

```bash
python3 -m wyrd.client group-test --member-skills 70,45,30 --mode most_capable --opponent 50 --seed 1
```

Expected: `selected_skill: 70` (SC-001).

## 2. The same group, tested the other way

```bash
python3 -m wyrd.client group-test --member-skills 70,45,30 --mode least_capable --opponent 50 --seed 1
```

Expected: `selected_skill: 30`.

## 3. An untrained member is tested at 10%

```bash
python3 -m wyrd.client group-test --member-skills 70,,30 --mode least_capable --opponent 50 --seed 1
```

Expected: `selected_skill: 10` (the empty entry means untrained).

## 4. An empty member list is a structured error

```bash
python3 -m wyrd.client group-test --member-skills "" --mode most_capable --opponent 50
```

Expected: `{"error": {...}}`.

## 5. An extended-task interval adds degrees, minimum 1

```bash
python3 -m wyrd.client extended-task-interval --skill 45 --opponent 50 --progress 2 --target 4 --seed 1
```

Expected: `gained` matches the roll's degrees (or 1 if degrees came out 0), `progress` is
`2 + gained`, `done` is true if `progress >= 4` (SC-003, SC-005).

## 6. A failed interval gains nothing

Pick a seed producing a failing roll at the same skill/opponent, and confirm `gained: 0`,
`progress` unchanged from the input (SC-004).

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```
