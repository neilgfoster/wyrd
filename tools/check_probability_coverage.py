#!/usr/bin/env python3
"""Confirm every derived probability/statistical claim in docs/design/ is backed by a passing
check_*.py script that computes it, rather than resting on prose alone.

CLAUDE.md: "Check the maths. Probability claims were wrong twice, and both were only caught by
computing them." Stage 13's closing requirement (#92) is to make that a checkable property of the
whole design corpus rather than a claim about individual features. This script does not recompute
every figure itself -- each backing script below already does that, at the values a real character
has, and already fails loudly if its document's figure drifts. This script's job is coverage: every
design document identified below as carrying a *derived* claim (a probability or rate computed
from the rules, not a defined input constant) has at least one script in COVERAGE that is run and
must pass.

## What counts as a "derived claim" here, and what does not

A design document is full of percentages. Most are **defined input constants** -- the untrained
10% (docs/design/03-rules.md sec1), the 25%-open/+5%-per-advance advancement economy, diegesis's
descriptive bands (docs/design/13-diegesis.md) -- stated by the ruleset, not derived from it. Those
need no script; there is nothing to compute, only to declare, and the declaration itself is the
source of truth.

A **derived claim** is a rate or probability that follows from combining rules -- attrition across
a fight, a critical table's own weighting, how often a crowd-clear qualifies. Those are exactly the
figures that have been wrong twice in this repo's history (CLAUDE.md), and every one currently
published in docs/design/ is listed in COVERAGE below, each pointing at the script that computed it.

The one design document with a percentage that reads as derived but is not --
docs/design/20-journeys.md's "hazard_rating: 4 gives a 40% chance per leg" -- is a direct
multiplication (rating x 10 on d100) the document itself states as its formula. It is exact by
construction, not by simulation, so it needs no separate script the way an attrition figure
combining several distributions does.

Run: python3 tools/check_probability_coverage.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# (docs/design file, what it publishes, the script that computes and asserts it)
COVERAGE = [
    (
        "06-aftermath.md",
        "Aftermath table ranges and death-row distribution",
        "specs/002-aftermath-table/check_aftermath.py",
    ),
    (
        "11-character-creation.md",
        "starting Stamina/Luck and the 8-advance pool",
        "specs/008-character-creation/check_creation.py",
    ),
    (
        "03-rules.md",
        "opposed-test behaviour at real skill values",
        "specs/010-opposed-tests/check_opposed.py",
    ),
    (
        "03-rules.md",
        "assistance divisor and group/extended-task shapes",
        "specs/011-assistance-and-group-tests/check_assistance.py",
    ),
    (
        "03-rules.md",
        "combat-sequencing mapping (turn order, surprise)",
        "specs/012-combat-sequencing/check_mapping.py",
    ),
    (
        "03-rules.md",
        "fight length and first-strike value in rounds",
        "specs/012-combat-sequencing/check_sequencing.py",
    ),
    (
        "03-rules.md",
        "the crowd rule's clearing threshold and one-blow attrition",
        "specs/013-the-mob-rule/check_mobs.py",
    ),
    (
        "03-rules.md",
        "Stamina recovery -- Rallies owed, and the Mend ladder",
        "specs/014-stamina-recovery/check_recovery.py",
    ),
    (
        "05-criticals.md",
        "every figure the four damage-type critical tables publish",
        "specs/015-damage-type-criticals/check_criticals.py",
    ),
    (
        "12-the-adversary.md",
        "the adversary model's baseline and crowd interaction",
        "specs/017-adversary-model/check_adversary.py",
    ),
    (
        "03-rules.md",
        "the player-facing combat conversion (telling-blow threshold)",
        "specs/018-player-facing-combat/check_conversion.py",
    ),
    ("08-afflictions.md", "the affliction sawtooth's cadence", "tools/check_affliction.py"),
    (
        "14-oracle-answers.md",
        "oracle-answer band widths and outcome probabilities",
        "tools/check_oracle_answers.py",
    ),
    (
        "11-character-creation.md",
        "the career cap and the maximum-Stamina ceiling",
        "tools/check_advancement.py",
    ),
    (
        "07-transformations.md",
        "the transformation re-roll loop terminates",
        "tools/check_transformation.py",
    ),
]


def main() -> int:
    failures = []
    print(f"Running {len(COVERAGE)} backing scripts...")
    for doc, claim, script in COVERAGE:
        script_path = ROOT / script
        if not script_path.exists():
            failures.append(f"{doc} ({claim}): backing script {script} does not exist")
            continue
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        status = "ok" if result.returncode == 0 else "FAIL"
        print(f"  {status:4}  docs/design/{doc:<28} {claim}")
        if result.returncode != 0:
            tail = "\n".join(result.stdout.strip().splitlines()[-5:])
            failures.append(f"{doc} ({claim}): {script} exited {result.returncode}\n{tail}")

    print()
    if failures:
        print("FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(
        f"All {len(COVERAGE)} derived probability claims in docs/design/ are backed by a "
        "passing computation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
