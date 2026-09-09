# Quickstart: Chronicle overlay resolution

## Prerequisites

```bash
cd /root/source/neilgfoster/wyrd
export PYTHONPATH=engine
```

## Validate: setting entity with no overlay resolves unchanged (User Story 1)

```python
from wyrd import entity

setting = {"hallam": {"id": "hallam", "type": "character", "name": "Hallam",
                       "setting": "demo", "status": "drafted", "role": "bystander"}}
frontmatter, body = entity.resolve_entity("hallam", setting, overlays={})
assert frontmatter == setting["hallam"]
```

## Validate: overlay changes one field (User Story 2)

```python
setting = {"the-caretaker": {"id": "the-caretaker", "type": "character", "name": "The Caretaker",
                              "setting": "demo", "status": "drafted",
                              "disposition": "unaware", "role": "bystander"}}
overlays = {"the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker",
                               "disposition": "hunting"}}
frontmatter, body = entity.resolve_entity("the-caretaker", setting, overlays)
assert frontmatter["disposition"] == "hunting"
assert frontmatter["name"] == "The Caretaker"
```

## Validate: overlay promotes a bystander to a nemesis (User Story 3)

```python
overlays = {"the-caretaker": {"id": "ov-2", "overlay_of": "the-caretaker",
                               "role": "nemesis",
                               "threat": {"imminence": 2, "connection": "..."}}}
frontmatter, body = entity.resolve_entity("the-caretaker", setting, overlays)
assert frontmatter["role"] == "nemesis"
assert frontmatter["threat"]["imminence"] == 2
# and the setting file on disk is untouched -- resolve_entity never writes.
```

## Run the test suite

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_entity -v
python3 -m ruff check .
python3 -m ruff format --check .
```

Expected: all pass, no ruff findings.
