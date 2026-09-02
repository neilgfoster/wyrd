#!/usr/bin/env python3
"""Cross-check the engine's own aftermath-table constant against the already-validated model.

specs/002-aftermath-table/check_aftermath.py already computes and asserts docs/design/06-
aftermath.md's own published figures (71% lasting mark / 23% death, unweighted across drops of
1-12 points below zero) from a standalone `ROWS` list -- not from the engine module itself. This
script's job is narrower and different, following specs/090-damage-type-criticals/
check_criticals_engine.py's own precedent: confirm that `engine/wyrd/resolution.py`'s
`AFTERMATH_TABLE` -- the data the engine actually rolls against -- agrees with that
already-validated model, row for row (CLAUDE.md "Recurring faults worth checking for" #3: two
documents describing one thing differently, found only by reading them against each other).

Run: python3 specs/091-aftermath-wound-records/check_aftermath_engine.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "002-aftermath-table"))

from check_aftermath import ROWS as VALIDATED_ROWS  # noqa: E402
from wyrd import resolution  # noqa: E402


def _validated_ranges():
    """VALIDATED_ROWS is (low, high-or-None, key, is_death, is_lasting_mark). `is_lasting_mark`
    answers a different question than this feature's "does this row produce a wound record" --
    it buckets rows for check_aftermath.py's own 71%/23% probability claim (e.g. `taken` counts
    as a lasting consequence there even though docs/design/06-aftermath.md gives it no wound
    record). What must agree between the two models is only the ranges and keys -- the row
    structure itself -- since that is what both scripts roll against. The open death row is
    implicit in the engine (via `_aftermath_band`'s fallthrough), so it is excluded here."""
    return [(low, high, key) for low, high, key, is_death, _ in VALIDATED_ROWS if not is_death]


def main() -> int:
    failures = []

    validated = _validated_ranges()
    engine = [(low, high, key) for low, high, key, _ in resolution.AFTERMATH_TABLE]

    if validated != engine:
        failures.append(
            f"engine AFTERMATH_TABLE ranges/keys disagree with the validated model:\n"
            f"  validated: {validated}\n"
            f"  engine:    {engine}"
        )

    if resolution._aftermath_band(111) != ("death", None):
        failures.append("engine _aftermath_band(111) does not resolve to the open death row")

    # The engine's own disfigured/recurring-wound rows must carry the exact mechanical effects
    # docs/design/06-aftermath.md publishes -- not just "some effect".
    effects_by_key = {key: effect for _, _, key, effect in resolution.AFTERMATH_TABLE}
    expected_effects = {
        "out-of-action": None,
        "lasting-wound": {},
        "left-for-dead": {},
        "new-enemy": {},
        "taken": None,
        "disfigured": {"dread": 1},
        "recurring-wound": {"skill": -10},
    }
    if effects_by_key != expected_effects:
        failures.append(
            f"engine row effects disagree with docs/design/06-aftermath.md:\n"
            f"  expected: {expected_effects}\n"
            f"  engine:   {effects_by_key}"
        )

    if failures:
        print(f"FAILED: {len(failures)} problem(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed: engine AFTERMATH_TABLE agrees with the validated model.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
