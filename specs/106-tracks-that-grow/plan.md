# Implementation Plan: The tracks that actually grow

**Branch**: `280-tracks-that-grow` | **Spec**: [spec.md](spec.md) | **Issue**: #280

## Summary

Add two idempotent set-membership verbs — `gain_allegiance`/`lose_allegiance` and
`gain_holding`/`lose_holding` — operating on the existing `allegiances`/`holdings` list fields
(docs/design/22-state.md), plus one d100 verb, `roll_standing`, that bands `reputation.score`
into one of three outcomes (recognised favourably / not recognised / recognised unfavourably).
No new persistent state beyond what `22-state.md` already declares. Knowledge and Bonds are
explicitly out of scope (spec.md Edge Cases).

## Technical Context

- **Language**: Python 3.11+, standard library only (docs/design/27-tooling.md §2).
- **Existing modules**: `engine/wyrd/economy.py` (#279's Standing/coin verbs — this feature is
  the same domain, same file), `engine/wyrd/character.py` (field list), `engine/wyrd/verbs.py`
  (thin dispatch layer), `tools/check_oracle_answers.py` (the precedent for asserting a d100
  band's row-width maths by computation rather than eyeballing).
- **Testing**: `tests/` mirrors `tests/test_economy.py`'s existing conventions (added under
  #279).

## Design decisions

- **All four new verbs land in `engine/wyrd/economy.py`**, not a new module — they are the same
  "what a character's position owes them" domain #279 already opened that file for, and the
  file's own docstring already anticipates more than Standing/coin arriving there.
- **`gain_allegiance`/`gain_holding` take the current list and the id to add**, returning a new
  list with the id present exactly once — a set-membership add, not a list append, so the
  idempotency FR (FR-001/FR-003) is enforced by construction rather than by a separate dedup
  step.
- **`lose_allegiance`/`lose_holding` refuse (`success: False`, list unchanged) when the id is not
  present** — same refusal shape `spend_coin` already established for "can't afford it": a
  `{"success": False, "reason": ..., ...}` dict, never an exception, matching every other verb in
  this module.
- **`roll_standing` takes an already-rolled d100 value plus the Standing score**, not a random
  source — matching how `roll()` in `verbs.py`/`resolution.py` keeps randomness at the CLI/session
  boundary and pure banding logic in the engine layer. It returns which of the three bands the
  roll landed in; it never reads or writes a skill or difficulty value (FR-006), and nothing it
  returns is consumed by `resolution.py`'s opposed-test path.
- **Band widths are computed, not asserted by inspection** — `tools/check_reputation_roll.py`
  follows `check_oracle_answers.py`'s exact shape: compute the three row-range widths for a swept
  range of Standing scores, assert they sum to exactly 100 and cover 1-100 with no gaps or
  overlaps, for every score tried (CLAUDE.md "check the maths").
- **No richer allegiance/holding object** — plain ids on the existing string lists (spec.md
  Assumptions); nothing beyond identity is validated, matching how `career` and `loyalty` ids are
  held without cross-checking a setting's vault.

## Project Structure

```
engine/wyrd/economy.py           # gain/lose_allegiance, gain/lose_holding, roll_standing
engine/wyrd/verbs.py             # thin wrappers for the five new verbs
tools/check_reputation_roll.py   # new: asserts roll_standing's band-width maths
tests/test_economy.py            # extended with the five new verbs' cases
```

## Constitution Check

- Setting-agnostic: "allegiance", "holding", "Standing" are already the engine's own descriptive
  labels (docs/design/03-rules.md, docs/design/19-campaign.md); no setting vocabulary introduced.
- Deterministic over inference: `roll_standing`'s banding is computed and asserted by
  `check_reputation_roll.py`, not eyeballed (docs/design/27-tooling.md §2, CLAUDE.md).
- Docs stay the present-tense description: no `22-state.md` schema change needed — `allegiances`,
  `holdings` and `reputation` are already documented there; this feature adds verbs, not fields.
- Capability change: `specs/106-tracks-that-grow/` is committed alongside the code, per the Spec
  Kit gate.

No violations to track.
