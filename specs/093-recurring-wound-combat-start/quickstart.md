# Quickstart: The recurring wound's combat-start effect

Validates that a combat scene applies each combatant's active recurring-wound penalties at
`start_combat`, stacks multiple wounds on the same skill, and never changes them mid-fight or
outside the scene.

## Prerequisites

- Python 3.11+, repo virtualenv/deps already set up (stdlib only -- nothing extra to install).
- Run from the repo root, `/root/source/neilgfoster/wyrd`.

## Setup

No fixture files needed -- `combat.start_combat` takes wound data as a plain dict alongside the
existing `sides` flags, the same way `armed`/`surprised`/`ambush` are already passed in tests.

## Scenario 1: one recurring wound fires at combat start

```python
import tempfile, pathlib
from wyrd import combat

with tempfile.TemporaryDirectory() as d:
    path = pathlib.Path(d) / "chronicle_state.yaml"
    scene = combat.start_combat(
        sides={
            "party": {
                "armed": True,
                "wounds": [
                    {"recurring": True, "bears_on": "close-combat", "closed": None},
                ],
            },
            "opp": {"armed": False},
        },
        started_by=None,
        player_side="party",
        state_path=path,
    )
    assert scene["wound_penalties"]["party"]["close-combat"] == combat.CHALLENGING_MODIFIER
    assert "opp" not in scene["wound_penalties"]
```

**Expected outcome**: `party`'s `close-combat` skill carries exactly one Challenging-modifier
penalty (`-10`); `opp`, with no recurring wounds, has no entry.

## Scenario 2: two recurring wounds on the same skill stack

```python
scene = combat.start_combat(
    sides={
        "party": {
            "armed": True,
            "wounds": [
                {"recurring": True, "bears_on": "close-combat", "closed": None},
                {"recurring": True, "bears_on": "close-combat", "closed": None},
            ],
        },
        "opp": {"armed": False},
    },
    started_by=None,
    player_side="party",
    state_path=path,
)
assert scene["wound_penalties"]["party"]["close-combat"] == 2 * combat.CHALLENGING_MODIFIER
```

**Expected outcome**: the stored penalty is double the single-wound value -- both wounds fired
and stacked, not the strongest alone.

## Scenario 3: the penalty does not change across rounds or persist between fights

```python
combat.advance_round(state_path=path)
scene_after = combat._load_scene(path)
assert scene_after["wound_penalties"] == scene["wound_penalties"]  # unchanged by advance_round

# A fresh combat scene for a combatant with no wounds this time has no penalty at all.
fresh = combat.start_combat(
    sides={"party": {"armed": True}, "opp": {"armed": False}},
    started_by=None,
    player_side="party",
    state_path=path,
)
assert "party" not in fresh["wound_penalties"]
```

**Expected outcome**: `advance_round` leaves `wound_penalties` untouched (fixed once, at combat
start); a new `start_combat` call recomputes it fresh from whatever wound data is passed in that
time, never carrying a stale value over.

## Running the real tests

```bash
python3 -m pytest tests/engine/test_combat.py -q
```
