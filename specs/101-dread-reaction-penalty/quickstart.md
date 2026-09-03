# Quickstart: Dread as a reaction/social test penalty

## Prerequisites

- `PYTHONPATH=engine` set, from the repo root.
- A target character/companion file with nonzero `dread` in its frontmatter (any existing fixture
  with an accrued Transformation qualifies, or set `dread: 3` directly for a quick check).

## Validate: Dread penalises an unfamiliar witness's reaction

```bash
PYTHONPATH=engine python3 -m wyrd.client propose \
  --actor path/to/witness.md \
  --mechanic ordinary-test \
  --skill composure \
  --target path/to/transformed-character.md \
  --difficulty average \
  --dread-witnessed \
  --seed 1
```

Expected: the returned `roll.effective_pct` is the witness's `composure` skill, plus the Average
difficulty bonus (+0), minus the target's `dread`, run through the engine's existing clamp — lower
than the same call made without `--dread-witnessed`.

## Validate: no penalty once peace is established

```bash
PYTHONPATH=engine python3 -m wyrd.client propose \
  --actor path/to/witness.md \
  --mechanic ordinary-test \
  --skill composure \
  --target path/to/transformed-character.md \
  --difficulty average \
  --seed 1
```

(Omit `--dread-witnessed`.) Expected: `roll.effective_pct` matches ordinary-test's pre-existing
behaviour exactly — identical to a call made before this feature existed.

## Validate: zero Dread is a no-op either way

Repeat the first command against a target whose `dread` is `0`. Expected: `roll.effective_pct` is
identical with or without `--dread-witnessed`.

## Automated coverage

```bash
PYTHONPATH=engine python3 -m pytest -q engine/tests -k dread
ruff check .
ruff format --check .
```
