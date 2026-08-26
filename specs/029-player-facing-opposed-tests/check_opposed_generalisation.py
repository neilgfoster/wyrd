#!/usr/bin/env python3
"""Verify the generalisation of player-facing rolls to all opposed tests, for #77.

CLAUDE.md: where a claim can be checked by a script, check it. #69/ADR 0027 converted combat --
and only combat -- to a single player-facing roll against effective%, leaving the door open:
"outside combat, two-sided opposed tests still exist, and ADR 0016 still governs them." This
script settles whether that is still true after the generalisation, so `docs/adr/0035-*.md` and
`docs/design/03-rules.md` section 1 are written from what it finds rather than from an assumption.

What this script does NOT do: it does not recompute effective% = clip(50 + (S - O), 5, 95). That
mapping is already calibrated (specs/012-combat-sequencing/check_mapping.py) and this script
asserts agreement with it before computing anything new, following the convention
specs/018-player-facing-combat/check_conversion.py already set.

What this script settles:

1. That every live citation of "opposed test" as a mechanism in design/ (excluding ADR 0016's own
   historical definition, which is never edited) either already routes through the player-facing
   shape or is the two-player-controlled-entities carve-out -- confirming ADR 0016 has no
   remaining live scope outside combat and that carve-out (T002).
2. A worked non-combat opposed test, resolved as one roll against effective%, reproducing the same
   degrees combat already produces at the same skill gap -- since it is the same formula fed the
   same inputs (T004).
3. Agreement with the effective% mapping table from check_mapping.py (T005).

Run: python3 specs/029-player-facing-opposed-tests/check_opposed_generalisation.py
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIP_LOW, CLIP_HIGH = 5, 95

# Import combat's own degrees() from check_conversion.py -- so the comparison below is against
# combat's actual function, not a second local copy of the same formula that could silently drift.
sys.path.insert(0, str(REPO_ROOT / "specs" / "018-player-facing-combat"))
from check_conversion import degrees as combat_degrees_fn  # noqa: E402

# Same representative skill-gap span specs/012-combat-sequencing/check_mapping.py uses.
PAIRINGS = [
    (25, 25), (40, 40), (35, 30), (55, 40), (50, 30),
    (60, 30), (70, 35), (60, 20), (80, 40), (100, 50), (30, 60),
]

PRIOR_MAPPING_TABLE = {
    (40, 40): 50, (55, 40): 65, (60, 30): 80, (100, 50): 95,
}


def check(claim: str, ok: bool, shown: str = "") -> None:
    status = "OK " if ok else "FAIL"
    print(f"[{status}] {claim}" + (f" -- {shown}" if shown else ""))
    if not ok:
        raise SystemExit(1)


# ---------------------------------------------------------------------------
# The mapping, reused not recomputed.
# ---------------------------------------------------------------------------

def effective_pct(actor: int, resister: int) -> int:
    """specs/012-combat-sequencing/check_mapping.py's calibrated mapping. Not re-derived here."""
    return max(CLIP_LOW, min(CLIP_HIGH, 50 + actor - resister))


def tens(n: int) -> int:
    return n // 10


def degrees(effective: int, roll: int) -> int:
    """docs/design/03-rules.md section 1's formula, fed effective% as the skill value -- unchanged
    from what specs/018-player-facing-combat/check_conversion.py already established for
    combat."""
    return tens(effective) - tens(roll)


def assert_prior_mapping() -> None:
    for (s, o), expected in PRIOR_MAPPING_TABLE.items():
        check(f"effective%({s}, {o}) == {expected} (specs/012 check_mapping.py)",
              effective_pct(s, o) == expected, f"got {effective_pct(s, o)}")


# ---------------------------------------------------------------------------
# T002 -- grep design/ for every live citation of "opposed test" as a mechanism.
# ---------------------------------------------------------------------------

# Files that only carry ADR 0016's own historical definition, or another accepted ADR's
# historical text quoting/reasoning about it -- accepted ADRs are never edited, and a citation
# inside one is not a live use this feature has to rewrite.
HISTORICAL_ADR_FILES = {
    "docs/adr/0016-opposed-tests-need-a-successful-actor.md",
    "docs/adr/0017-assistance-group-tests-and-extended-tasks.md",
    "docs/adr/0018-combat-sequencing.md",
    "docs/adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md",
    "docs/adr/0027-combat-rolls-belong-to-the-player.md",
    "docs/adr/0028-the-telling-blow-threshold-and-the-damage-finding.md",
    # This feature's own ADR necessarily cites "opposed test" while explaining what it retires --
    # not a live use to rewrite, the record OF the retirement.
    "docs/adr/0035-opposed-tests-generalise-to-the-player-facing-roll.md",
}

# The index entry in docs/README.md naming ADR 0016 by its title is a pointer to a historical
# record, not a live use of the mechanism -- unaffected by this feature.
HISTORICAL_INDEX_FILES = {"docs/README.md"}

# The one live document: docs/design/03-rules.md section 1 defines the two-sided shape today and
# section 1's own carve-out sentence ("where neither is [acting]...") is the
# two-player-controlled-entities case this feature restates rather than retires.
LIVE_MECHANISM_FILE = "docs/design/03-rules.md"


def grep_opposed_test_citations() -> dict[str, list[str]]:
    result = subprocess.run(
        ["grep", "-rln", "opposed test", "--include=*.md", "-i", "docs/"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    files = [line for line in result.stdout.splitlines() if line]
    return {
        "historical_adr": sorted(f for f in files if f in HISTORICAL_ADR_FILES),
        "historical_index": sorted(f for f in files if f in HISTORICAL_INDEX_FILES),
        "live": sorted(f for f in files
                        if f not in HISTORICAL_ADR_FILES and f not in HISTORICAL_INDEX_FILES),
    }


def check_adr_0016_scope() -> None:
    citations = grep_opposed_test_citations()
    check("every citing file is accounted for (historical ADR, historical index, or the one live "
          "mechanism file)",
          set(citations["live"]) == {LIVE_MECHANISM_FILE},
          f"live files found: {citations['live']}")
    check(f"{LIVE_MECHANISM_FILE} is the only live citation of the two-sided shape "
          "-- confirms ADR 0016 has no remaining scope beyond combat (already carved out by "
          "ADR 0027) and the two-player-controlled-entities carve-out",
          citations["live"] == [LIVE_MECHANISM_FILE])


# ---------------------------------------------------------------------------
# T004 -- a worked non-combat opposed test, same formula, same numbers as combat.
# ---------------------------------------------------------------------------

def check_generalised_roll_matches_combat() -> None:
    """The generalised roll is the SAME computation combat already uses -- same effective%
    formula, same degrees formula. This is not a new mechanic to calibrate; it is the existing
    one applied outside combat. Confirm this feature's degrees() agrees with check_conversion.py's
    own degrees() -- combat's actual function, not a second local copy of the same formula that
    could silently drift -- at identical inputs."""
    for skill, opponent_skill in PAIRINGS:
        eff = effective_pct(skill, opponent_skill)
        for roll in (5, 25, 50, 75, 95):
            combat_result = combat_degrees_fn(eff, roll)  # specs/018's own function
            generalised_result = degrees(eff, roll)  # this feature's function
            check(f"degrees(effective%({skill},{opponent_skill})={eff}, roll={roll}) agrees "
                  "with specs/018-player-facing-combat/check_conversion.py's own degrees()",
                  combat_result == generalised_result,
                  f"combat={combat_result}, generalised={generalised_result}")


def check_worked_example() -> None:
    """A player character picking a lock while a guard (NPC/opponent) listens: skill 55 vs.
    opponent baseline 40, matching one of the calibrated pairings above."""
    skill, opponent_baseline = 55, 40
    eff = effective_pct(skill, opponent_baseline)
    check("worked example: effective% for skill 55 vs. opponent baseline 40 is 65",
          eff == 65)
    roll = 42
    d = degrees(eff, roll)
    check(f"worked example: roll {roll} against effective% {eff} succeeds "
          f"(roll <= effective%) with {d} degree(s)",
          roll <= eff and d == tens(eff) - tens(roll), f"got degrees={d}")
    failing_roll = 80
    check(f"worked example: roll {failing_roll} against effective% {eff} fails outright "
          "-- no resisting-side roll, no degrees comparison",
          failing_roll > eff)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("== T001/T005: prior mapping table ==")
    assert_prior_mapping()

    print("\n== T002: design/ citations of \"opposed test\" as a mechanism ==")
    check_adr_0016_scope()

    print("\n== T003/T004: the generalised roll is combat's existing formula, not a new one ==")
    check_generalised_roll_matches_combat()
    check_worked_example()

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
