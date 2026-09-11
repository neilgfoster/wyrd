# Quickstart: End-to-end functional test suite

## Run it

```bash
cd /root/source/neilgfoster/wyrd/.claude/worktrees/agent-ad515a06838a1b523
PYTHONPATH=engine python3 -m pytest tests/engine/test_integration.py -q
# or, matching the repo's stdlib-unittest convention directly:
PYTHONPATH=engine python3 -m unittest tests.engine.test_integration -v
```

Full-repo regression check (must still pass alongside the new suite):

```bash
PYTHONPATH=engine python3 -m pytest -q
python3 -m ruff check .
python3 -m ruff format --check .
```

## What the suite proves

One `unittest.TestCase`, one test method, one temporary chronicle directory, one player
character carried through eleven subsystem areas in sequence (creation → action resolution →
combat → harm/recovery → adversaries → condition tracks → economies → systems of power → solo
procedures → session/campaign structure → chronicle bootstrap). At each of the ten handoffs
between adjacent areas, the test asserts a concrete value produced by the earlier area (a wound
id, a mutation's field/value, a scaled skill number, a proposal id) rather than only checking that
the call didn't raise. See `data-model.md` for the entity/mutation shapes and `research.md` for
the exact function signatures and seeds each area uses.

## Expected outcome

A single pass, deterministically reproducible across repeated runs (fixed seeds throughout, no
wall-clock or filesystem-ordering dependence).
