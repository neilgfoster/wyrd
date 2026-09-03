# Implementation Plan: Adversary turn parity and the Aftermath exemption

**Spec**: [spec.md](spec.md) | **Issue**: #262 | **Created**: 2026-09-03

## Approach

One decision point, enforced at the staging site.

`resolution._stage_aftermath` is currently wired to no caller (specs/091's own T008 says a later
feature wires it up). That makes it the right place to put the exemption *before* any caller
exists: a caller cannot bypass a rule the staging function itself enforces (SC-004). The
alternative -- a free-standing predicate callers are expected to check first -- was rejected
because the first caller that forgets it produces exactly the bug this feature exists to
prevent, silently.

So:

1. `rolls_aftermath(entity_state)` -- a public predicate in `resolution.py`, true only when
   `entity_state.get("type") == "character"`. Absent `type`, any other `type`, or `None` is
   false (FR-001, FR-003, FR-005). This is the one place the rule lives.
2. `_stage_aftermath` gains a **required keyword-only `entity_state`** and raises `ValueError`
   naming the entity when `rolls_aftermath` is false (FR-002). Required, not optional-with-a-
   default: a default would be a bypass, and every existing call site is a test we own.
3. `role` is deliberately not consulted -- player, companion and antagonist are all `character`
   entities and all roll (FR-004). The design's own wording is that the test is entity type,
   not importance.

Nothing in `combat.py` changes: FR-006/007 are confirmations, discharged by tests that would
fail if an adversary-specific branch were ever introduced.

## Files

| File | Change |
|---|---|
| `engine/wyrd/resolution.py` | add `rolls_aftermath`; `_stage_aftermath` gains required `entity_state` and the refusal |
| `tests/engine/test_resolution.py` | update 4 existing `_stage_aftermath` call sites; new exemption/parity tests |
| `docs/design/12-the-adversary.md` | no change -- it already states the rule; this implements it |

## Constraints

stdlib only, Python 3.11+. `ruff check . && ruff format --check . && python3 -m pytest -q` green
(tests need `PYTHONPATH=engine`).
