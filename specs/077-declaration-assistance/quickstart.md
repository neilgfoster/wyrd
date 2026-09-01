# Quickstart: Declaration and assistance bonuses

## Prerequisites

- #221 and #222 already merged.
- Run from the repository root with `PYTHONPATH=engine`.

## 1. Each declaration category returns its documented value

```bash
python3 -m wyrd.client declaration-bonus --category specific
python3 -m wyrd.client declaration-bonus --category specific_leveraging
python3 -m wyrd.client declaration-bonus --category brief
python3 -m wyrd.client declaration-bonus --category against_nature
python3 -m wyrd.client declaration-bonus --category removes_risk
```

Expected bonuses: +10, +20, 0, −20, and `no_roll: true` respectively (SC-001).

## 2. An unrecognized category is a structured error

```bash
python3 -m wyrd.client declaration-bonus --category bogus
```

Expected: `{"error": {...}}`, not a crash (FR-002).

## 3. Assistance scales and caps

```bash
python3 -m wyrd.client assistance-bonus --helper-skill 30
python3 -m wyrd.client assistance-bonus --helper-skill 45
python3 -m wyrd.client assistance-bonus --helper-skill 100
```

Expected: +3, +4, +10 (SC-002).

## 4. A helper who could not attempt contributes nothing

```bash
python3 -m wyrd.client assistance-bonus --helper-skill 100 --can-attempt false
```

Expected: bonus 0.

## 5. Modifiers compose into a real opposed test

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --declaration specific --helper-skill 45 --seed 1
```

Expected: `effective_pct: 64` (50 + 10 + 4).

## 6. Removes-risk skips the roll entirely

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --declaration removes_risk
```

Expected: `no_roll: true`, `success: true`, `roll: null` (SC-004).

## 7. Neither modifier supplied is unchanged from #222

```bash
python3 -m wyrd.client opposed-test --skill 70 --opponent 30 --seed 1
```

Expected: identical output to #222's own quickstart step 2, plus `declaration: null,
helper_skill: null, no_roll: false` (SC-003).

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```
