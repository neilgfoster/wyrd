# Quickstart: Career graph and advance allocation

## Prerequisites

- #221-#229 already merged.
- Run from the repository root with `PYTHONPATH=engine`.

## 1. A valid spread is accepted

```bash
python3 -m wyrd.client validate-allocation \
  --career-json '{"skills": {"stealth": 55, "swordplay": 45}, "entry_point": true}' \
  --actions-json '[{"action":"open","skill":"stealth"},{"action":"open","skill":"swordplay"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"swordplay"},{"action":"raise","skill":"swordplay"}]'
```

Expected: `valid: true`, `stealth: 45`, `swordplay: 35` (SC-001).

## 2. Wrong total is rejected

Drop the last action from the list above (7 total) and re-run.

Expected: `valid: false`, naming the total.

## 3. Fewer than two skills opened is rejected

Spend all 8 on a single skill's open+7 raises.

Expected: `valid: false`.

## 4. Exceeding a cap is rejected

Raise `swordplay` (cap 45) past its cap.

Expected: `valid: false`, naming the skill and its cap.

## 5. An ancestry widens eligibility without adding budget

```bash
python3 -m wyrd.client validate-allocation \
  --career-json '{"skills": {"stealth": 55, "swordplay": 45}, "entry_point": true}' \
  --ancestry-json '{"skills": {"herbalism": 40}}' \
  --actions-json '[{"action":"open","skill":"stealth"},{"action":"open","skill":"herbalism"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"herbalism"},{"action":"raise","skill":"herbalism"}]'
```

Expected: `valid: true`, `herbalism: 35`.

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```
