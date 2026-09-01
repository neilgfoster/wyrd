# Quickstart: Character entity schema and validator

## Prerequisites

- #221-#224 already merged.
- Run from a scratch directory with `PYTHONPATH=<repo>/engine`.

## 1. A full character round-trips

```bash
python3 -m wyrd.client character-save --path pc.md --frontmatter-json '{"id":"aria","type":"character","role":"player","skills":{"stealth":45},"stamina":{"current":10,"max":10},"wounds":[]}'
python3 -m wyrd.client character-load --path pc.md
```

Expected: the loaded `frontmatter` matches what was saved exactly (SC-001).

## 2. An invalid wound effect is rejected

```bash
python3 -m wyrd.client character-save --path bad.md --frontmatter-json '{"id":"x","wounds":[{"id":"w1","effect":{"damage":5}}]}'
```

Expected: `{"error": {...}}` naming the wound and the invalid effect key.

## 3. A skill effect without bears_on is rejected

```bash
python3 -m wyrd.client character-save --path bad2.md --frontmatter-json '{"id":"x","wounds":[{"id":"w1","effect":{"skill":-10}}]}'
```

Expected: a structured error.

## 4. A recurring wound with `closed` set is rejected

```bash
python3 -m wyrd.client character-save --path bad3.md --frontmatter-json '{"id":"x","wounds":[{"id":"w1","effect":{"dread":1},"recurring":true,"closed":10}]}'
```

Expected: a structured error.

## 5. A closed wound is retained but excluded from active effects

Save a character with one open and one closed wound, load it, and confirm `wounds` still lists
both while the active-effects computation reports only the open one.

## 6. Skill-scale constants

```bash
python3 -m wyrd.client skill-scale
```

Expected: `{"open_value": 25, "advance_step": 5, "untrained": 10}` (SC-004).

## Running the automated suite

```bash
python3 -m unittest discover -s tests/engine
```
