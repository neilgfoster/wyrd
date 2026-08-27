#!/usr/bin/env python3
"""Confirm the Resolve recovery/cap formula actually delivers what ADR 0043 claims: a positive,
spendable value at every Taint above 0, with Spent reachable through ordinary play and never
reachable at Taint 0.

CLAUDE.md: where a claim can be checked by a script, check it. The first draft of this decision
(Resolve's cap = Taint exactly, no margin) was caught as broken during design -- a fully-rested
character would sit exactly at the Spent boundary, with nothing positive ever spendable. This
script proves the corrected formula (cap = Taint + 3) does not have that problem, at every Taint
value across a representative range, rather than trusting the prose reasoning alone.

Run: python3 specs/052-resolve-recovery-mechanic/check_resolve.py
"""
from __future__ import annotations

MARGIN = 3  # one Transformation threshold-interval, per ADR 0043


def cap(taint: int) -> int:
    return taint + MARGIN


def is_spent(resolve: int, taint: int) -> bool:
    """Spent = Resolve fallen to equal Taint, except Taint 0 is exempted outright (03-rules.md
    sec4's own stated carve-out, not derived from the cap formula)."""
    if taint == 0:
        return False
    return resolve == taint


FAILURES: list[str] = []


def check(claim: str, ok: bool, detail: str = "") -> None:
    status = "OK " if ok else "FAIL"
    print(f"[{status}] {claim}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(claim)


def main() -> int:
    print("Checking Resolve's cap formula across Taint 0 through 20...")
    for taint in range(0, 21):
        rested = cap(taint)

        # A fully-rested character must NOT already be Spent -- there must be real headroom.
        check(f"Taint {taint}: fully-rested Resolve ({rested}) is not itself Spent",
              not is_spent(rested, taint),
              f"cap={rested}, taint={taint}")

        # There must be at least one positive spend available before Spent triggers (i.e. the
        # margin itself must be > 0, so "spendable" and "Spent, reachable" can both be true).
        check(f"Taint {taint}: at least one point of Resolve is spendable before Spent",
              rested - taint > 0,
              f"headroom={rested - taint}")

        # Spending the full margin down from a full rest must reach exactly the Spent condition
        # (except at Taint 0, where the stated exception overrides it).
        spent_down = rested - (rested - taint)  # i.e. spending "headroom" points brings it to taint
        if taint == 0:
            check("Taint 0: spending Resolve all the way down never triggers Spent",
                  not is_spent(spent_down, taint))
        else:
            check(f"Taint {taint}: spending Resolve down to {spent_down} triggers Spent",
                  is_spent(spent_down, taint))

    print()
    print("Checking the naive (rejected) cap=Taint formula actually fails, to confirm this isn't "
          "a vacuous check:")
    naive_cap = lambda t: t  # noqa: E731 -- the rejected first draft, for contrast only
    naive_broken = any(is_spent(naive_cap(t), t) for t in range(1, 21))
    check("The rejected cap=Taint formula puts a fully-rested character at Spent immediately",
          naive_broken,
          "confirms ADR 0043's own stated reason for rejecting it")

    print()
    if FAILURES:
        print("FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print(f"All checks pass across Taint 0-20. Resolve's cap (Taint + {MARGIN}) leaves real, "
          "spendable headroom at every Taint above 0, and Taint 0's exemption holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
