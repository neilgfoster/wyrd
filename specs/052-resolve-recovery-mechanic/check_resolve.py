#!/usr/bin/env python3
"""Confirm the Resolve recovery/cap formula actually delivers what ADR 0049 claims: a positive,
spendable value whenever Taint and/or Trauma is above 0, with Spent reachable through ordinary
play on either axis independently, and never reachable when both sit at 0.

CLAUDE.md: where a claim can be checked by a script, check it. ADR 0043's first draft (cap =
Taint exactly, no margin) was caught as broken during design -- a fully-rested character would
sit exactly at the Spent boundary. ADR 0049 widens the same formula to counter both Taint and
Trauma via max(Taint, Trauma) + 3, with the Taint-0 exemption generalised per axis. This script
proves the widened formula still has real headroom at every combination, and that each
exemption holds independently -- not just the Taint-only case ADR 0043 originally proved.

Run: python3 specs/052-resolve-recovery-mechanic/check_resolve.py
"""
from __future__ import annotations

MARGIN = 3  # one Transformation threshold-interval, per ADR 0043, carried forward by ADR 0049


def cap(taint: int, trauma: int) -> int:
    return max(taint, trauma) + MARGIN


def is_spent(resolve: int, taint: int, trauma: int) -> bool:
    """Spent = Resolve fallen to AT OR BELOW whichever of Taint/Trauma is higher, with each
    axis exempted independently at 0 (03-rules.md sec4's own carve-out, generalised per ADR
    0049 -- not derived from the cap formula, the same reasoning applied twice). At-or-below,
    not exact equality: Spent is a persisting state from the moment a threshold is reached, not
    a one-instant boundary crossing -- an exact-equality check would wrongly report "not Spent"
    once Resolve is spent past the threshold rather than landing on it exactly, caught by this
    script's own dual-axis check below (Taint 3/Trauma 12: Resolve==3 must still read Spent,
    since Trauma's threshold at 12 was already crossed on the way down)."""
    spent_via_taint = taint > 0 and resolve <= taint
    spent_via_trauma = trauma > 0 and resolve <= trauma
    return spent_via_taint or spent_via_trauma


FAILURES: list[str] = []


def check(claim: str, ok: bool, detail: str = "") -> None:
    status = "OK " if ok else "FAIL"
    print(f"[{status}] {claim}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(claim)


def main() -> int:
    print("Checking Resolve's dual-threshold cap across Taint 0-20 x Trauma 0-20 "
          "(representative combinations, not the full grid, for readable output)...\n")

    combos = []
    for t in range(0, 21, 4):
        for tr in range(0, 21, 4):
            combos.append((t, tr))
    # Explicitly include the two single-axis cases ADR 0043 already proved, plus the pure-Trauma
    # case ADR 0043 never had reason to exercise.
    combos += [(0, 0), (5, 0), (0, 5), (5, 5), (12, 3), (3, 12)]

    for taint, trauma in combos:
        rested = cap(taint, trauma)
        binding = max(taint, trauma)

        check(f"Taint {taint}, Trauma {trauma}: fully-rested Resolve ({rested}) is not itself "
              f"Spent", not is_spent(rested, taint, trauma),
              f"cap={rested}, binding={binding}")

        if binding > 0:
            check(f"Taint {taint}, Trauma {trauma}: at least one point of Resolve is spendable "
                  f"before Spent", rested - binding > 0, f"headroom={rested - binding}")

            spent_down = rested - (rested - binding)
            check(f"Taint {taint}, Trauma {trauma}: spending Resolve down to {spent_down} "
                  f"triggers Spent", is_spent(spent_down, taint, trauma))
        else:
            check(f"Taint 0, Trauma 0: spending Resolve all the way down never triggers Spent",
                  not is_spent(0, taint, trauma))

    print("\nConfirming the binding axis is genuinely whichever is HIGHER, not always Taint "
          "(the case ADR 0043's own verification never exercised):")
    check("Taint 3, Trauma 12: Spent is reached via Trauma (the higher axis) at Resolve == 12, "
          "well before Resolve would ever need to fall as low as Taint's own value (3)",
          is_spent(12, 3, 12) and not is_spent(13, 3, 12))
    check("Taint 3, Trauma 12: Spent, once reached via Trauma at 12, still reads Spent if "
          "Resolve keeps falling all the way to 3 -- a persisting state, not a one-instant "
          "boundary crossing that exact equality would have missed",
          is_spent(3, 3, 12))
    check("Taint 12, Trauma 3: Spent is reached via Taint (the higher axis) at Resolve == 12",
          is_spent(12, 12, 3) and not is_spent(13, 12, 3))

    print("\nConfirming each axis's exemption is independent:")
    check("Taint 0, Trauma 8: Spent is still reachable via Trauma alone",
          is_spent(8, 0, 8))
    check("Taint 8, Trauma 0: Spent is still reachable via Taint alone",
          is_spent(8, 8, 0))
    check("Taint 0, Trauma 0: Spent is never reachable at any Resolve value down to 0",
          not any(is_spent(r, 0, 0) for r in range(0, 4)))

    print("\nChecking the superseded (ADR 0043) Taint-only formula actually differs here, to "
          "confirm this isn't a vacuous widening:")
    old_cap = lambda t, tr: t + MARGIN  # noqa: E731 -- ADR 0043's own formula, for contrast
    differs = old_cap(3, 12) != cap(3, 12)
    check("At Taint 3, Trauma 12: the superseded formula (6) and the widened one (15) genuinely "
          "differ", differs, f"old={old_cap(3, 12)}, new={cap(3, 12)}")

    print()
    if FAILURES:
        print("FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print(f"All checks pass. Resolve's cap (max(Taint, Trauma) + {MARGIN}) leaves real, "
          "spendable headroom whenever either axis is above 0, Spent is reachable "
          "independently via either axis, and both exemptions (Taint 0, Trauma 0) hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
