# Quickstart: Chronicle state invariants

Validates that `commit()` now enforces `docs/design/22-state.md` § Invariants' passive rules, and
that the three existing active cascades still land correctly once those checks sit in front of it.

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine` set (or run via `python3 -m pytest` from
  the repo root, which the existing test suite already assumes).
- No external services; everything below runs against a temporary chronicle directory a test
  fixture creates.

## Run the new tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m pytest tests/engine/test_resolution.py -q
```

Expected: all tests pass, including the new ones this feature adds (passive-check rejections,
cascade-still-lands regressions, `is_spent()` boundary cases).

## Manual validation scenario — a rejected commit writes nothing

1. Build a temporary chronicle directory with one character entity whose `fortune.current` is at
   `fate.max` already.
2. `propose()` a mutation that would raise `fortune.current` by 1.
3. `commit()` the returned proposal id.
4. **Expected**: `commit` raises `ProposalError`; re-reading the character entity file from disk
   shows `fortune.current` unchanged from step 1 — nothing was written.

## Manual validation scenario — a cascade still stages inside one proposal

1. Build a temporary chronicle directory with a character entity at `taint: 2`.
2. `propose()` a mutation that raises `taint` by 1 (crossing to `3`, a multiple of 3).
3. **Expected**: the returned proposal already contains a Transformation roll's steps — before
   `commit` is called at all.
4. `commit()` the proposal.
5. **Expected**: the character entity file on disk reflects both the taint change and the
   transformation's own mutations, applied together.

## Manual validation scenario — Spent is never written

1. Build a temporary chronicle directory with a character entity at
   `resolve.current: 2, taint: 5, trauma: 0`.
2. Call the new `is_spent()` accessor against the loaded frontmatter.
3. **Expected**: returns `True` (`2 <= max(5, 0)` with trauma exempted at 0 collapses to
   `2 <= 5`).
4. Re-read the character entity file from disk (no commit was involved).
5. **Expected**: no `spent` field is present, before or after the call.

Full acceptance criteria and edge cases are in [spec.md](spec.md); the rule-by-rule mechanism is
in [data-model.md](data-model.md).
