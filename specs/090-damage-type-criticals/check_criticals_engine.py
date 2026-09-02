#!/usr/bin/env python3
"""Cross-check the engine's own critical-table constants against the already-validated model.

specs/015-damage-type-criticals/check_criticals.py already computes and asserts every
probability figure docs/design/05-criticals.md publishes, from a standalone `TABLES` dict -- not
from the engine module itself. This script's job is narrower and different: confirm that
`engine/wyrd/resolution.py`'s `CRITICAL_*_TABLE` constants -- the data the engine actually rolls
against -- agree with that already-validated dict, row for row. CLAUDE.md's "check the maths" is
satisfied by specs/015's script; this one guards against the engine's own copy drifting from it
(exact factual claim, findable only by comparing two tables against each other -- CLAUDE.md
"Recurring faults worth checking for" #3).

Run: python3 specs/090-damage-type-criticals/check_criticals_engine.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "015-damage-type-criticals"))

from wyrd import resolution  # noqa: E402

from check_criticals import TABLES as VALIDATED_TABLES  # noqa: E402

# engine/wyrd/resolution.py's own constants, keyed the same way as VALIDATED_TABLES.
ENGINE_TABLES = {
    "critical-slashing": resolution.CRITICAL_SLASHING_TABLE,
    "critical-piercing": resolution.CRITICAL_PIERCING_TABLE,
    "critical-blunt": resolution.CRITICAL_BLUNT_TABLE,
    "critical-searing": resolution.CRITICAL_SEARING_TABLE,
}

#: The validated model's effect shape uses {"none": True} for "nothing lasting" and
#: {"mortal": True} for the open top row; the engine's shape uses `None` for both (the open top
#: row is a separate, implicit row in the engine -- CRITICAL_TABLES's own mortal_key). Translate
#: the validated model's rows into the engine's own shape before comparing.


def _validated_as_engine_rows(rows):
    out = []
    for (lo, hi), key, effect in rows:
        if effect.get("mortal"):
            continue  # the engine's open top row is implicit, not a data row
        engine_effect = None if effect.get("none") else effect
        out.append((lo, hi, key, engine_effect))
    return out


FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def main() -> int:
    print("=" * 78)
    print("Engine critical tables vs. the already-validated model")
    print("=" * 78)
    for table_name, validated_rows in VALIDATED_TABLES.items():
        expected = _validated_as_engine_rows(validated_rows)
        actual = ENGINE_TABLES[table_name]
        check(
            actual == expected,
            f"{table_name}: engine rows {actual} do not match the validated model's rows "
            f"{expected}.",
        )
        print(
            f"  {table_name:<20} {len(actual)} rows, matches validated model: {actual == expected}"
        )

    # Every damage type in the closed set has a table and a mortal key that matches the
    # validated model's own open-top-row key.
    for table_name, validated_rows in VALIDATED_TABLES.items():
        damage_type = table_name.removeprefix("critical-")
        mortal_key = [key for (_, key, effect) in validated_rows if effect.get("mortal")]
        check(len(mortal_key) == 1, f"{table_name} has {len(mortal_key)} mortal rows, not 1.")
        engine_table, engine_mortal_key = resolution.CRITICAL_TABLES[damage_type]
        check(
            engine_table is ENGINE_TABLES[table_name],
            f"CRITICAL_TABLES[{damage_type!r}] does not point at {table_name}'s own constant.",
        )
        check(
            engine_mortal_key == mortal_key[0],
            f"CRITICAL_TABLES[{damage_type!r}]'s mortal key is {engine_mortal_key!r}, not "
            f"{mortal_key[0]!r}.",
        )

    print()
    if FAILURES:
        print("FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("All checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
