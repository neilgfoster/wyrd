#!/usr/bin/env python3
"""specs/092-mortal-blows-fate-death, SC-002: both re-read directions -- a mortal critical
forcing an Aftermath result onto `death`, and a spent Fate point re-reading `death` onto the
worst non-death row -- must be fully deterministic (no second roll, no judgement call) and
idempotent. This script re-resolves the same scenarios many times over and asserts the outcome
is byte-identical every time, rather than eyeballing a handful of manual runs
(CLAUDE.md "Deterministic over inference").

Run: python3 tools/check_death_row_determinism.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

from wyrd import resolution  # noqa: E402

REPEATS = 200


def _stage(*, points_below_zero, mortal=False, mortality="standard", seed=1):
    steps: list[dict] = []
    resolution._stage_aftermath(
        steps,
        entity="pc",
        points_below_zero=points_below_zero,
        depends_on_step=0,
        seed_cursor=resolution._SeedCursor(seed=seed),
        bears_on_skill="swordplay",
        mortal=mortal,
        mortality=mortality,
    )
    return steps[0]["roll"]


def check_mortal_forcing_is_deterministic():
    print("Mortal-critical forcing, repeated across a spread of seeds and drops:")
    for seed in range(1, 21):
        for points_below_zero in (1, 3, 6, 9, 12):
            results = {
                (
                    resolution._stage_aftermath.__name__,
                    r["key"],
                    r["forced_mortal"],
                    r["closed_by"],
                )
                for _ in range(REPEATS)
                for r in [_stage(points_below_zero=points_below_zero, mortal=True, seed=seed)]
            }
            assert len(results) == 1, (
                f"mortal forcing is not deterministic at seed={seed}, "
                f"points_below_zero={points_below_zero}: {results}"
            )
            (_, key, forced, closed_by) = next(iter(results))
            assert key == "death", f"a mortal critical must force death, got {key!r}"
            assert forced is True
            assert closed_by is None
    print(f"  {REPEATS} repeats x 20 seeds x 5 drop values: always forces death, no variance.")


def check_mortality_low_closure_is_deterministic():
    print()
    print("mortality: low closure, repeated across rolled and mortal-forced death:")
    worst_key, worst_effect = resolution._worst_non_death_row()
    for mortal in (False, True):
        pbz = 25 if not mortal else 1  # rolled-death needs a large drop; forced needs any drop
        results = {
            (r["key"], r["closed_by"], r["fate_spent"])
            for _ in range(REPEATS)
            for r in [_stage(points_below_zero=pbz, mortal=mortal, mortality="low")]
        }
        assert len(results) == 1, f"mortality:low closure is not deterministic: {results}"
        key, closed_by, fate_spent = next(iter(results))
        assert key == worst_key, f"expected the worst non-death row {worst_key!r}, got {key!r}"
        assert closed_by == "mortality"
        assert fate_spent is False
    print(f"  always closes onto {worst_key!r} (effect {worst_effect}), never spends Fate.")


def check_fate_spend_is_deterministic_and_idempotent():
    print()
    print("Fate-spend re-read, repeated against fresh death results:")
    worst_key, _ = resolution._worst_non_death_row()
    outcomes = set()
    for _ in range(REPEATS):
        steps = [
            {
                "step_id": 0,
                "mechanic": "aftermath",
                "roll": {
                    "key": "death",
                    "closed_by": None,
                    "fate_spent": False,
                    "bears_on_skill": "swordplay",
                },
                "mutations": [],
            }
        ]
        pc_state = {"fate": {"current": 2}}
        resolution.close_death_row(
            steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
        )
        outcomes.add(
            (steps[0]["roll"]["key"], steps[0]["roll"]["closed_by"], pc_state["fate"]["current"])
        )
        # Idempotence: a second attempt against the now-closed step must be rejected outright,
        # never silently re-close or spend a second Fate point.
        try:
            resolution.close_death_row(
                steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "a second Fate spend against an already-closed row must be rejected"
            )
        assert pc_state["fate"]["current"] == 1, "a rejected second spend must not deduct Fate"
    assert len(outcomes) == 1, f"Fate-spend re-read is not deterministic: {outcomes}"
    key, closed_by, fate_after = next(iter(outcomes))
    assert key == worst_key
    assert closed_by == "fate"
    assert fate_after == 1
    print(
        f"  {REPEATS} repeats: always re-reads onto {worst_key!r}, spends exactly 1 Fate, "
        "rejects a second spend."
    )


def main():
    check_mortal_forcing_is_deterministic()
    check_mortality_low_closure_is_deterministic()
    check_fate_spend_is_deterministic_and_idempotent()
    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
