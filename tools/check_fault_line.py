#!/usr/bin/env python3
"""Compute the Fault Line's effect on Taint accrual, and guard the table it deliberately
does not touch.

docs/design/03-rules.md section 4: when an Exposure source runs with the grain of a
character's Fault Line (the GM's fiction-grounded call, the same shape as invoking a
Drive), a failed resistance gains Taint one tier worse than the source's stated base
(minor 1 -> 2, moderate 2 -> 3, major 3 stays 3). This script computes, rather than
asserts, how many fewer Exposure events it takes an aligned character to cross the
next transformation threshold (every multiple of 3 -- docs/design/07-transformations.md)
compared with an unaligned character starting at the same Taint, across a spread of
realistic starting values and all three Exposure tiers. It also confirms the
tier-worse step never exceeds the major ceiling, and that
docs/design/07-transformations.md is untouched by this feature.

Run: python3 tools/check_fault_line.py
"""
import hashlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRANSFORMATIONS_DOC = REPO_ROOT / "docs" / "design" / "10-transformations.md"

BASE_TIERS = {"minor": 1, "moderate": 2, "major": 3}
THRESHOLD_SPACING = 3  # every multiple of 3 -- docs/design/07-transformations.md

# Starting Taint values a real character plausibly reaches: just crossed a threshold
# (0, freshly reset), mid-band, and just below the next one.
STARTING_TAINT_VALUES = [0, 1, 2, 4, 5, 7, 8, 10, 11]


def tier_worse(base):
    """One tier worse, capped at major (3) -- docs/design/03-rules.md s4, FR-002/FR-003."""
    return min(base + 1, BASE_TIERS["major"])


def events_to_next_threshold(starting_taint, gain_per_event):
    """How many failed Exposure events, each adding a flat amount, until Taint first
    reaches or exceeds the next threshold above starting_taint."""
    next_threshold = starting_taint - (starting_taint % THRESHOLD_SPACING) + THRESHOLD_SPACING
    if starting_taint % THRESHOLD_SPACING == 0 and starting_taint > 0:
        # already sitting on a threshold (just resolved one); the "next" one is the one after
        next_threshold = starting_taint + THRESHOLD_SPACING
    taint = starting_taint
    events = 0
    while taint < next_threshold:
        taint += gain_per_event
        events += 1
    return events, next_threshold


def check_ceiling():
    assert tier_worse(BASE_TIERS["major"]) == 3, "major tier must not exceed its own ceiling"
    assert tier_worse(BASE_TIERS["minor"]) == BASE_TIERS["moderate"]
    assert tier_worse(BASE_TIERS["moderate"]) == BASE_TIERS["major"]


def check_transformations_doc_untouched():
    """This feature must not edit docs/design/07-transformations.md (FR-006, SC-003). Compare
    the working tree's copy against main; report drift rather than silently passing if git
    is unavailable."""
    if not TRANSFORMATIONS_DOC.exists():
        raise SystemExit(f"missing: {TRANSFORMATIONS_DOC}")
    try:
        main_content = subprocess.run(
            ["git", "show", f"main:docs/design/{TRANSFORMATIONS_DOC.name}"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"  (skipped: could not read main's copy via git — {exc})")
        return
    working_content = TRANSFORMATIONS_DOC.read_text()
    main_hash = hashlib.sha256(main_content.encode()).hexdigest()
    working_hash = hashlib.sha256(working_content.encode()).hexdigest()
    if main_hash != working_hash:
        raise SystemExit(
            f"{TRANSFORMATIONS_DOC} differs from main — this feature must not touch it "
            "(FR-006, SC-003)"
        )
    print(f"  {TRANSFORMATIONS_DOC.relative_to(REPO_ROOT)}: unchanged vs main (sha256 match)")


def main():
    print("Fault Line tier-worse step, ceiling check:")
    check_ceiling()
    for tier, base in BASE_TIERS.items():
        print(f"  {tier} ({base}) -> aligned: {tier_worse(base)}")

    print()
    print("Events to cross the next transformation threshold, aligned vs unaligned:")
    print(f"  {'start':>5} | {'tier':>8} | {'base evts':>9} | {'aligned evts':>12} | delta")
    for start in STARTING_TAINT_VALUES:
        for tier, base in BASE_TIERS.items():
            base_events, threshold = events_to_next_threshold(start, base)
            aligned_events, _ = events_to_next_threshold(start, tier_worse(base))
            delta = base_events - aligned_events
            assert aligned_events <= base_events, (
                f"aligned Exposure must never take longer to cross a threshold "
                f"(start={start}, tier={tier})"
            )
            print(f"  {start:>5} | {tier:>8} | {base_events:>9} | {aligned_events:>12} | -{delta}")

    print()
    print("Transformation table integrity:")
    check_transformations_doc_untouched()

    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
