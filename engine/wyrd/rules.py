"""Resolution primitives: pure functions, no I/O, no state.

docs/design/01-principles.md principle 1: the dice bind the GM. This is the only place a
random result comes from -- the model narrates from what this module returns and never
recomputes it (docs/design/27-tooling.md section 3).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import random


def roll_d100(sides: int = 100, seed: int | None = None) -> int:
    """Roll one die of the given number of sides (default: d100).

    A locally-seeded `random.Random` instance is used rather than the module-level
    `random` global, so one call's seed can never leak into an unrelated call in the same
    process. Given the same seed, the result is always identical; with no seed, the result
    is drawn from the platform's default randomness (not reproducible).
    """
    if not isinstance(sides, int) or sides <= 0:
        raise ValueError(f"sides must be a positive integer, got {sides!r}")
    rng = random.Random(seed)
    return rng.randint(1, sides)
