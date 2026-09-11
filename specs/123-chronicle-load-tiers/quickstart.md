# Quickstart: Chronicle load-tier resolution and recap.md

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.
- A chronicle's entity files loadable via `wyrd.entity.load_set`.

## Validate the always tier

```python
from wyrd import entity, loadtier

entities = entity.load_set(paths)  # existing loader, unchanged
tier = loadtier.always_tier(entities)

tier["player_character"]   # the one role: player entity, or None
tier["companions"]         # {id: frontmatter} for role: companion, status: with-party
tier["threads"]            # {id: frontmatter} for type: thread, heat >= 3
```

Change a companion's `status` from `with-party` to `departed` (or a thread's `heat` below 3) in
the source entities and re-run `always_tier` — the changed entity drops out of the result with no
other state to update (FR-009).

## Validate on-demand fetch

```python
loadtier.lookup("some-place-id", entities)       # full frontmatter, or None
loadtier.search("burned mill", entities, bodies)  # ids whose text matches
```

## Validate recap.md regeneration

```python
from wyrd import state

text = loadtier.generate_recap(
    entities,
    chronicle,
    where="the old quarter, three days after the fire",
    changes=["the mill burned", "a companion left the party"],
    body_mind="tired but steady",
)
state.write_text_atomic(text, pathlib.Path("recap.md"))
```

Confirm the result names at most three threads (the highest-`heat` ones), mentions every
with-party companion, and lands near 200 words (`len(text.split())`).

## Run the tests

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_loadtier -v
PYTHONPATH=engine python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m ruff check .
python3 -m ruff format --check .
```
