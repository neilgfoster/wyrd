#!/usr/bin/env python3
"""Compute what a party counts for, and what content actually runs at.

CLAUDE.md: where a claim can be checked by a script, check it. Two scaling claims in this repo
were wrong, and both were caught only by computing them -- one of them the figure this feature
replaces, "roughly danger 2", which docs/design/26-corpus-index.md has quoted since it was
written and which was never computed from anything, because until now there was nothing to
compute it from.

Every figure docs/design/03-rules.md section 7 and docs/design/26-corpus-index.md publish is
asserted here, so an edit to either that drifts from the rule fails loudly rather than reading
as authoritative.

From merged design documents:

1. The scaling equation is danger_effective = danger x (party_effective / written_for)
   (docs/design/03-rules.md section 7). Its shape is not changed by this feature.
2. written_for is the head count the content was written for, a scaling input and never a gate
   (docs/design/26-corpus-index.md). Its meaning is not changed by this feature.
3. The party is a query, not a roster: characters with role companion and status with-party,
   plus the player character (docs/design/22-state.md). status has exactly five values.
4. danger is a multiplier inside content -- a trap written Nd4 does 6d4 at danger 6, and enemy
   counts and skill values scale from the same number (docs/design/03-rules.md section 7).

Decided by this feature (specs/016-party-effective/spec.md, and the ADR):

5. A head count of p bodies has an effective size of 1 + 1/2 + 1/3 + ... + 1/p. The k-th
   companion is worth 1/(k+1).
6. Both sides of the ratio are converted by that same function, so like is compared with like.
7. danger_effective is never rounded. Every quantity built from it rounds half up at its own
   point of use, and never below 1 where the written quantity was at least 1.

Run: python3 specs/016-party-effective/check_party.py
"""

import math
from fractions import Fraction

# ---------------------------------------------------------------------------
# The five status values a companion can hold (docs/design/22-state.md). Only one
# of them puts a body in the party.
# ---------------------------------------------------------------------------

COMPANION_STATUSES = ("with-party", "away", "dead", "lost", "departed")
COUNTS_TOWARD_PARTY = "with-party"

# The party sizes a real chronicle has: one player character, plus companions.
# Not a midpoint -- CLAUDE.md, "run the numbers at the values a real character
# actually has".
REAL_COMPANION_COUNTS = (0, 1, 2, 3, 4)

# The party sizes published content is written for.
REAL_WRITTEN_FOR = (4, 6)

# The band of written danger ratings the corpus carries.
REAL_DANGER = (1, 2, 3, 4, 5, 6)

FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


# ---------------------------------------------------------------------------
# The curve
# ---------------------------------------------------------------------------


def effective_size(bodies: int) -> Fraction:
    """The effective size of a party of `bodies` heads.

    The first body is worth 1, the second 1/2, the third 1/3, and so on: the
    p-th harmonic number. Order-independent by construction, so no roster
    ordering has to be invented and two readers counting the same party in
    different orders get the same number.
    """
    if bodies < 0:
        raise ValueError("a party cannot have a negative number of bodies")
    return sum((Fraction(1, k) for k in range(1, bodies + 1)), Fraction(0))


def party_effective(companions: list[dict]) -> Fraction:
    """The effective size of the party actually present.

    A pure function of party composition: the player character, plus every
    companion whose status is with-party. Nothing else is consulted, and no
    judgement call is left inside it.
    """
    bodies = 1 + sum(1 for c in companions if c.get("status") == COUNTS_TOWARD_PARTY)
    return effective_size(bodies)


def danger_effective(danger: int, bodies: int, written_for: int | None) -> Fraction:
    """The exact effective danger. Never rounded here -- see `at_use` below."""
    if not written_for:  # absent, None, or 0: the content runs as written.
        return Fraction(danger)
    return danger * effective_size(bodies) / effective_size(written_for)


def at_use(written_quantity: int, scaled_danger: Fraction, written_danger: int) -> int:
    """Round one quantity built from danger_effective, at its own point of use.

    Round half up, and never below 1 where the written quantity was at least 1.
    """
    scaled = Fraction(written_quantity) * scaled_danger / written_danger
    rounded = math.floor(scaled + Fraction(1, 2))
    if written_quantity >= 1:
        return max(1, rounded)
    return rounded


def ratio(bodies: int, written_for: int) -> Fraction:
    return effective_size(bodies) / effective_size(written_for)


# ---------------------------------------------------------------------------
# 1. The curve is a curve
# ---------------------------------------------------------------------------


def check_the_curve() -> None:
    print("The effective size of a party, by head count")
    print("  bodies  effective size   this body added")
    previous = Fraction(0)
    added = []
    for p in range(1, 21):
        size = effective_size(p)
        gain = size - previous
        added.append(gain)
        if p <= 8 or p in (10, 15, 20):
            print(f"    {p:>2}       {float(size):>6.3f}          {float(gain):>6.3f}")
        previous = size

    for k in range(1, len(added)):
        check(
            added[k] < added[k - 1],
            f"body {k + 1} added {added[k]}, not less than the {added[k - 1]} body {k} added -- "
            "the curve is meant to diminish at every step.",
        )

    check(
        effective_size(1) == 1,
        "A party of the player character alone must have an effective size of exactly 1.",
    )
    check(
        effective_size(2) == Fraction(3, 2),
        "The first companion is worth exactly a half.",
    )
    check(
        effective_size(3) == Fraction(11, 6),
        "The second companion is worth exactly a third.",
    )

    # Bounded well below the head count: this is what stops a retinue being an
    # exploit, and it is a computed property rather than a hope.
    for p in range(2, 21):
        check(
            effective_size(p) < p,
            f"a party of {p} has effective size {effective_size(p)}, not below its head count.",
        )
    check(
        effective_size(20) < 4,
        f"twenty bodies reach effective size {float(effective_size(20)):.3f}; the retinue bound "
        "is meant to keep twenty below the effective size of four written-for parties.",
    )
    print(f"\n  Twenty bodies reach effective size {float(effective_size(20)):.3f}.")
    print(f"  Doubling four bodies to eight buys a factor of {float(ratio(8, 4)):.3f}.")
    check(
        ratio(8, 4) < Fraction(7, 5),
        f"doubling the party from four bodies to eight buys {float(ratio(8, 4)):.3f}; the curve "
        "is meant to make a second party-worth of bodies buy markedly less than double.",
    )


# ---------------------------------------------------------------------------
# 2. The identity case is exact
# ---------------------------------------------------------------------------


def check_identity() -> None:
    print("\nThe identity case: p bodies against content written for p")
    for p in range(1, 21):
        for d in REAL_DANGER:
            got = danger_effective(d, p, p)
            check(
                got == Fraction(d),
                f"{p} bodies against written_for {p} at danger {d} gives {got}, not {d}. The "
                "identity case is meant to be exact, not approximately exact.",
            )
    print("  Exact for every party size 1-20 at every written danger 1-6.")


# ---------------------------------------------------------------------------
# 3. Scaled danger at the parties a real chronicle has
# ---------------------------------------------------------------------------


def check_real_parties() -> dict:
    published = {}
    for wf in REAL_WRITTEN_FOR:
        print(f"\nScaled danger, content written for {wf}")
        header = "  companions  bodies  ratio  " + "  ".join(f"d{d}" for d in REAL_DANGER)
        print(header)
        for n in REAL_COMPANION_COUNTS:
            bodies = 1 + n
            r = ratio(bodies, wf)
            cells = []
            for d in REAL_DANGER:
                de = danger_effective(d, bodies, wf)
                published[(n, wf, d)] = de
                cells.append(f"{float(de):>4.2f}")
            print(f"      {n}         {bodies}    {float(r):>5.3f}  " + "  ".join(cells))

    # Every scaled danger falls, or holds, as written_for rises.
    for n in REAL_COMPANION_COUNTS:
        for d in REAL_DANGER:
            check(
                published[(n, 6, d)] < published[(n, 4, d)],
                f"with {n} companions at danger {d}, content written for 6 does not scale below "
                "content written for 4.",
            )
    return published


# ---------------------------------------------------------------------------
# 4. The retinue bound
# ---------------------------------------------------------------------------


def check_retinue() -> None:
    print("\nWhat a retinue buys, against content written for 4")
    for bodies in (1, 3, 5, 10, 20):
        r = ratio(bodies, 4)
        print(
            f"  {bodies:>2} bodies  ratio {float(r):>5.3f}  danger 3 runs at {float(3 * r):>5.3f}"
        )
    check(
        ratio(10, 4) < Fraction(3, 2),
        f"ten bodies buy {float(ratio(10, 4)):.3f} against content written for four, more than "
        "the half again the curve is meant to hold them under.",
    )
    check(
        ratio(20, 4) < 2,
        f"twenty bodies buy {float(ratio(20, 4)):.3f} against content written for four. Five "
        "times the head count is meant never to buy double the danger; a retinue is not a way "
        "to flatten every arc.",
    )


# ---------------------------------------------------------------------------
# 5. The rounding rule at its awkward points
# ---------------------------------------------------------------------------


def check_rounding() -> None:
    print("\nRounding at the point of use")

    # An exact half rounds up.
    half = Fraction(1, 2)
    check(
        at_use(1, half, 1) == 1,
        "a written quantity of 1 at a scaled danger of one half must round up to 1, not down.",
    )
    check(
        at_use(3, half, 1) == 2,
        f"3 at a scaled danger of one half gives {at_use(3, half, 1)}, not the 2 that rounding "
        "half up requires.",
    )
    check(
        at_use(5, half, 1) == 3,
        "5 at a scaled danger of one half must round to 3.",
    )

    # Nothing written as at least 1 ever comes out as 0, at any party size, any
    # written_for, and any written danger.
    zeroed = []
    for bodies in range(1, 21):
        for wf in (1, 2, 3, 4, 5, 6, 8):
            for d in REAL_DANGER:
                de = danger_effective(d, bodies, wf)
                for quantity in (1, 2, 3, 6, 10):
                    got = at_use(quantity, de, d)
                    if got < 1:
                        zeroed.append((bodies, wf, d, quantity, got))
    check(
        not zeroed,
        f"{len(zeroed)} written quantities of at least 1 rounded to 0 or below, the first being "
        f"{zeroed[0] if zeroed else ''}. A trap written Nd4 must always throw at least one die.",
    )
    print(
        "  No written quantity of 1 or more rounds to 0, across parties 1-20 and written_for "
        "1-8 at every written danger 1-6."
    )

    # The lone player character against content written for four, at the worst
    # case: still a playable trap.
    lone = danger_effective(1, 1, 4)
    print(
        f"  A lone character, content written for 4 at danger 1: scaled {float(lone):.3f}, "
        f"a trap written 1d4 throws {at_use(1, lone, 1)}d4."
    )
    check(at_use(1, lone, 1) == 1, "a lone character's danger-1 trap must still throw one die.")


# ---------------------------------------------------------------------------
# 6. Degenerate inputs
# ---------------------------------------------------------------------------


def check_degenerate() -> None:
    print("\nDegenerate inputs")
    for bodies in range(1, 8):
        for d in REAL_DANGER:
            for missing in (None, 0):
                got = danger_effective(d, bodies, missing)
                check(
                    got == Fraction(d),
                    f"written_for {missing!r} at danger {d} with {bodies} bodies gives {got}, "
                    f"not the {d} that running as written requires.",
                )
    print(
        "  written_for absent and written_for 0 both run content as written, at every party "
        "size 1-7 and every written danger 1-6."
    )


# ---------------------------------------------------------------------------
# 7. Which companions count
# ---------------------------------------------------------------------------


def check_who_counts() -> None:
    print("\nWhich companions count")
    for status in COMPANION_STATUSES:
        got = party_effective([{"status": status}])
        expected = effective_size(2) if status == COUNTS_TOWARD_PARTY else effective_size(1)
        print(f"  a lone companion at status {status:<12} -> party_effective {float(got):.3f}")
        check(
            got == expected,
            f"a companion at status {status} gives party_effective {got}, not {expected}.",
        )

    mixed = [
        {"status": "with-party"},
        {"status": "with-party"},
        {"status": "away"},
        {"status": "dead"},
        {"status": "lost"},
        {"status": "departed"},
    ]
    check(
        party_effective(mixed) == effective_size(3),
        "a party of the player character and six companions, two of them with-party, must count "
        "as three bodies.",
    )

    # Order-independent: the same companions counted in any order give the same
    # number. This is what lets two readers agree without a roster ordering.
    check(
        party_effective(mixed) == party_effective(list(reversed(mixed))),
        "party_effective depends on the order companions are counted in.",
    )
    print("  Order-independent, and only with-party contributes.")


# ---------------------------------------------------------------------------
# 8. Every figure the design documents publish
# ---------------------------------------------------------------------------


def check_published_figures(published: dict) -> None:
    print("\nFigures the design documents publish")

    # docs/design/03-rules.md section 7, the effective-size table.
    for bodies, expected in (
        (1, "1.000"),
        (2, "1.500"),
        (3, "1.833"),
        (4, "2.083"),
        (5, "2.283"),
        (6, "2.450"),
    ):
        got = f"{float(effective_size(bodies)):.3f}"
        print(f"  effective size of {bodies} bodies: {got}")
        check(
            got == expected,
            f"the effective size of {bodies} bodies is {got}; the design document publishes "
            f"{expected}.",
        )

    # docs/design/03-rules.md section 7 and docs/design/26-corpus-index.md, the worked
    # case that replaces "roughly danger 2".
    worked = published[(2, 4, 3)]
    print(f"  danger 3, written for 4, one character and two companions: {float(worked):.2f}")
    check(
        f"{float(worked):.2f}" == "2.64",
        f"the worked case gives {float(worked):.2f}; the design documents publish 2.64.",
    )
    # The quantities that case actually builds, each rounded at its own point of use.
    for quantity, expected, what in ((1, 1, "a trap written 1d4"), (6, 5, "six enemies")):
        got = at_use(quantity, worked, 3)
        print(f"    {what}: {got}")
        check(
            got == expected,
            f"{what} at the worked case comes out as {got}; the design documents publish "
            f"{expected}.",
        )

    # docs/design/03-rules.md section 7, the lone character's ratio against a party
    # of four.
    lone_ratio = ratio(1, 4)
    print(f"  a lone character against content written for 4: ratio {float(lone_ratio):.2f}")
    check(
        f"{float(lone_ratio):.2f}" == "0.48",
        f"the lone character's ratio is {float(lone_ratio):.2f}; the design document publishes "
        "0.48.",
    )

    # docs/design/03-rules.md section 7, the worked case's ratio.
    print(f"  three bodies against content written for 4: ratio {float(ratio(3, 4)):.2f}")
    check(
        f"{float(ratio(3, 4)):.2f}" == "0.88",
        f"the worked case's ratio is {float(ratio(3, 4)):.2f}; the design document publishes 0.88.",
    )

    # docs/design/03-rules.md section 7, the retinue table.
    for bodies, expected in ((1, "0.48"), (3, "0.88"), (5, "1.10"), (10, "1.41"), (20, "1.73")):
        got = f"{float(ratio(bodies, 4)):.2f}"
        print(f"  {bodies:>2} bodies against content written for 4: ratio {got}")
        check(
            got == expected,
            f"{bodies} bodies buy {got}; the design document's retinue table publishes {expected}.",
        )

    # docs/design/03-rules.md section 7, what a companion buys, first against fifth.
    for label, gain, expected in (
        ("first", ratio(2, 4) - ratio(1, 4), "0.24"),
        ("fifth", ratio(6, 4) - ratio(5, 4), "0.08"),
    ):
        check(
            f"{float(gain):.2f}" == expected,
            f"the {label} companion buys {float(gain):.2f}; the design document publishes "
            f"{expected}.",
        )


# ---------------------------------------------------------------------------
# 9. Every figure the worked example publishes
# ---------------------------------------------------------------------------

# specs/016-party-effective/worked-scaling.md: one arc record, danger 3,
# written_for 4, taken through three parties. The quantities its text builds
# from danger, as written for a party of four.
WORKED_QUANTITIES = (
    ("flooded stair", 1),
    ("the cult", 6),
    ("the watch", 3),
    ("the prior", 15),
)

# What worked-scaling.md publishes: bodies -> (ratio, danger_effective, rounded
# quantities in the order above).
WORKED_EXAMPLE = {
    1: ("0.480", "1.440", (1, 3, 1, 7)),
    3: ("0.880", "2.640", (1, 5, 3, 13)),
    6: ("1.176", "3.528", (1, 7, 4, 18)),
}


def check_worked_example() -> None:
    print("\nThe worked example, one arc at three parties")
    for bodies, (r_pub, de_pub, rounded_pub) in WORKED_EXAMPLE.items():
        r = ratio(bodies, 4)
        de = danger_effective(3, bodies, 4)
        check(
            f"{float(r):.3f}" == r_pub,
            f"{bodies} bodies give ratio {float(r):.3f}; worked-scaling.md publishes {r_pub}.",
        )
        check(
            f"{float(de):.3f}" == de_pub,
            f"{bodies} bodies give danger_effective {float(de):.3f}; worked-scaling.md "
            f"publishes {de_pub}.",
        )
        got = tuple(at_use(q, de, 3) for _, q in WORKED_QUANTITIES)
        print(
            f"  {bodies} bodies: ratio {float(r):.3f}, danger_effective {float(de):.3f}, "
            f"quantities {got}"
        )
        check(
            got == rounded_pub,
            f"{bodies} bodies round to {got}; worked-scaling.md publishes {rounded_pub}.",
        )

    # The claim that rounding danger_effective up front is wrong at the arc's
    # heaviest count: at three bodies, a pre-rounded 3 gives six cultists where
    # the exact 2.640 gives five.
    pre_rounded = at_use(6, Fraction(3), 3)
    exact = at_use(6, danger_effective(3, 3, 4), 3)
    print(f"  the cult, pre-rounded danger_effective: {pre_rounded}; exact: {exact}")
    check(
        (pre_rounded, exact) == (6, 5),
        f"the pre-rounded/exact comparison gives {(pre_rounded, exact)}; worked-scaling.md "
        "publishes six bodies against five.",
    )
    # And that the watch is unmoved by the same pre-rounding, so the cult is the
    # only quantity that disagrees.
    check(
        at_use(3, Fraction(3), 3) == at_use(3, danger_effective(3, 3, 4), 3) == 3,
        "the watch is meant to be 3 both pre-rounded and exact; worked-scaling.md says the cult "
        "is the one quantity where the two disagree.",
    )
    # The floor erases nothing but the stair, and only for the lone character.
    lone = danger_effective(3, 1, 4)
    unfloored = math.floor(Fraction(1) * lone / 3 + Fraction(1, 2))
    check(
        unfloored == 0,
        f"without the floor the lone character's stair throws {unfloored} dice; "
        "worked-scaling.md says it throws none.",
    )
    check(
        math.floor(Fraction(3) * lone / 3 + Fraction(1, 2)) == 1,
        "without the floor the lone character's watch is meant to survive at 1; the worked "
        "example says the stair is the only quantity the ratio can erase.",
    )
    # A quantity written as one die stays one die until thirteen bodies.
    for bodies in range(1, 13):
        check(
            at_use(1, danger_effective(3, bodies, 4), 3) == 1,
            f"one written die becomes {at_use(1, danger_effective(3, bodies, 4), 3)} at {bodies} "
            "bodies; the worked example says it stays one die to twelve.",
        )
    check(
        at_use(1, danger_effective(3, 13, 4), 3) == 2,
        "one written die is meant to become two at thirteen bodies.",
    )
    # The ratio a companion buys, first against fifth.
    first = ratio(2, 4) - ratio(1, 4)
    fifth = ratio(6, 4) - ratio(5, 4)
    print(f"  the first companion buys {float(first):.3f}, the fifth {float(fifth):.3f}")
    check(
        (f"{float(first):.3f}", f"{float(fifth):.3f}") == ("0.240", "0.080"),
        f"the first companion buys {float(first):.3f} and the fifth {float(fifth):.3f}; "
        "worked-scaling.md publishes 0.240 and 0.080.",
    )


def main() -> int:
    check_the_curve()
    check_identity()
    published = check_real_parties()
    check_retinue()
    check_rounding()
    check_degenerate()
    check_who_counts()
    check_published_figures(published)
    check_worked_example()

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
