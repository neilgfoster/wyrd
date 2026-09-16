# Quickstart: Chronicle Entity Loader Layout

Validates that `_load_chronicle_entities` finds real entity files under a chronicle laid out the
way current bootstrap tooling actually produces, without crashing on incidental files.

## Prerequisites

- `PYTHONPATH=engine` set (per this repo's own test convention).
- A local checkout of `wyrd-chronicle-darkfuture-rookie-op` (or an equivalent fixture built to
  match its layout) is useful for manual spot-checking, but the automated tests below build their
  own minimal fixture — no external repo is required to run them.

## Automated validation

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m pytest tests/engine/test_resolution.py -k chronicle_entities -v
```

Expected: new tests covering (see tasks.md for the full breakdown)
- a chronicle with per-type `.yaml` subdirectories under `setting/entities/`, `overlay/`, and
  `entities/` — full effective entity set returned, non-empty
- the same chronicle with a stray `README.md` at `setting/`'s top level and a `.gitkeep` inside an
  empty `entities/<type>/` directory — load still succeeds, neither counted as an entity
- a chronicle still in the old flat `*.md` layout — loads exactly as before (no regression)

## Manual spot-check (optional)

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -c "
from pathlib import Path
from wyrd import resolution
root = Path('/root/source/neilgfoster/wyrd-chronicle-darkfuture-rookie-op')
entities = resolution._load_chronicle_entities(root / 'chronicle.yaml')
print(len(entities), 'entities loaded')
assert entities, 'expected a non-empty entity set on a real bootstrapped chronicle'
"
```

Expected: prints a non-zero entity count (before this fix: `0 entities loaded`, or a crash on
`setting/README.md` depending on exact repo state).

## Lint/format

```bash
python3 -m ruff check .
python3 -m ruff format --check .
```

Both must exit clean, including under `specs/170-chronicle-entity-loader-layout/`.

## Documentation

If `docs/design/22-state.md` is updated to name the confirmed layout (FR-006), re-run:

```bash
python3 tools/check_docs.py
```
