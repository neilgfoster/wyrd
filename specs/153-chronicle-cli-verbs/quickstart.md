# Quickstart: Chronicle CLI Verbs

## Prerequisites

- Python 3.11+, standard library only.
- A chronicle fixture directory with `chronicle.yaml`, `setting/`, `overlay/`, `entities/`,
  `log/`, and `recap.md` (the fixtures under `tests/engine/fixtures/` already provide this
  shape; reuse or extend one rather than inventing a new layout).

## Run the test suite for this feature

```bash
cd /path/to/wyrd
PYTHONPATH=engine python3 -m unittest discover -s tests/engine -p "test_*.py"
```

## Exercise each verb by hand

```bash
export PYTHONPATH=engine

python3 -m wyrd.client session-context --chronicle-dir <fixture>
python3 -m wyrd.client get <entity-id> --chronicle-dir <fixture>
python3 -m wyrd.client find --type character --status with-party --chronicle-dir <fixture>
python3 -m wyrd.client party --chronicle-dir <fixture>
python3 -m wyrd.client threads --chronicle-dir <fixture>
python3 -m wyrd.client threats --chronicle-dir <fixture>
python3 -m wyrd.client log --last 5 --chronicle-dir <fixture>
python3 -m wyrd.client validate --chronicle-dir <fixture>
python3 -m wyrd.client save --chronicle-dir <fixture>
python3 -m wyrd.client load --chronicle-dir <fixture>
python3 -m wyrd.client recap --chronicle-dir <fixture>
python3 -m wyrd.client advance-time 14 --seed 1 --chronicle-dir <fixture>
python3 -m wyrd.client threat-check <threat-id> --seed 1 --chronicle-dir <fixture>
```

Every command above should exit 0 and print one JSON object matching the shape in
`data-model.md`. `get` on a deliberately nonexistent id, and `log` with both or neither of
`--last`/`--since`, should exit non-zero with a message naming the specific problem.

## Expected outcome

- Every verb named in docs/design/02-architecture.md's list, except `doctor`/`optimise`, is
  callable and returns the structured shape `data-model.md` documents.
- `ruff check .` and `ruff format --check .` report no findings.
