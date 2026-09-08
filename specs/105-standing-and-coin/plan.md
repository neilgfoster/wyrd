# Implementation Plan: Standing and coin as one material position

**Branch**: `105-standing-and-coin` | **Spec**: [spec.md](spec.md) | **Issue**: #279

## Summary

Add a `coin` field to character state; add three verbs — `spend-coin` (buy a gear entry against
its price), `martial-weapon-sighting` (fixed −1 Standing, once per open sighting), and
`adjust-standing` (general scene-consequence Standing delta). No new persistent state beyond
`coin` — `reputation.score` already carries Standing. No encumbrance mechanism.

## Technical Context

- **Language**: Python 3.11+, standard library only (docs/design/27-tooling.md §2).
- **Existing modules**: `engine/wyrd/character.py` (field list, validation), `engine/wyrd/verbs.py`
  (thin verb dispatch), `tools/check_gear.py` (gear catalogue reader/validator, reused rather than
  reimplemented for loading a gear list).
- **Testing**: `tests/` mirrors existing verb test conventions (see `tests/test_advancement.py`
  or equivalent for `spend-advance`).

## Design decisions

- **New logic module `engine/wyrd/economy.py`**, following the pattern of `advancement.py` /
  `career.py`: pure functions the `verbs.py` layer wraps, no I/O beyond what's passed in.
- **`spend-coin` takes the gear catalogue as data**, not a path — matches how `spend_advance`
  takes `career_data`/`careers` as already-loaded data rather than reading files itself. Loading
  `gear.yaml` is the caller's job (CLI/session layer), same division as career data today.
- **`already_applied` is caller-supplied**, not tracked by the engine — spec.md's Assumptions
  rules out the engine inventing scene detection; this keeps `martial-weapon-sighting` a pure
  function like every other verb here.
- **No encumbrance code path is added anywhere** — this is a explicit non-goal (FR-005), checked
  by grep in the PR's own verification rather than a new validator script (there's nothing to
  validate against).

## Project Structure

```
engine/wyrd/economy.py      # new: spend_coin, martial_weapon_sighting, adjust_standing
engine/wyrd/character.py    # PLAYER_CHARACTER_FIELDS gains "coin"
engine/wyrd/verbs.py        # spend_coin, martial_weapon_sighting, adjust_standing wrappers
docs/design/22-state.md     # frontmatter example gains `coin: 0`
tests/test_economy.py       # new
```

## Constitution Check

- Setting-agnostic: no setting names, no borrowed vocabulary; "coin" and "Standing" are already
  the engine's own descriptive labels (docs/design/03-rules.md's rename table, row already
  present for Standing).
- Deterministic over inference: verbs are pure functions over passed-in state, no inferred
  scene-detection (docs/design/27-tooling.md §2).
- Docs stay the present-tense description: `22-state.md`'s frontmatter block updates in place.

No violations to track.
