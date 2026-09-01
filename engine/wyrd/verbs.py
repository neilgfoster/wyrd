"""The operations behind each catalog entry.

Each function here wires `rules.py`'s pure logic to `state.py`'s persistence, so the state
write happens as part of resolving the verb -- before the result is returned for narration
(docs/design/01-principles.md principle 2). Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import rules, state


def roll(
    sides: int = 100,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Resolve the `roll` verb: roll, persist, then return the structured result.

    Raises `ValueError` for an invalid `sides` (propagated from `rules.roll_d100`,
    unchanged) -- `client.py` is responsible for turning that into the structured
    `{"error": ...}` shape at the CLI boundary; this function stays a plain Python API.
    """
    result = rules.roll_d100(sides=sides, seed=seed)
    current = state.load(state_path)
    current["last_roll"] = {"verb": "roll", "sides": sides, "result": result, "seed": seed}
    state.save(current, state_path)
    return {
        "verb": "roll",
        "sides": sides,
        "result": result,
        "seed": seed,
        "state_written": True,
    }


def opposed_test(skill: int, opponent: int, seed: int | None = None) -> dict:
    """Resolve the `opposed-test` verb.

    A thin wrapper over `rules.opposed_test` -- no state read or write, unlike `roll`.
    Nothing yet depends on a stored opposed-test result, so none is persisted
    (specs/076-opposed-test-resolution/research.md's "No state I/O" decision).
    """
    return rules.opposed_test(skill=skill, opponent=opponent, seed=seed)
