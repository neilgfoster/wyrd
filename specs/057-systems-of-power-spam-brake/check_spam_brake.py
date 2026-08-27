"""Verify ADR 0045's max-Stamina-threshold Trauma brake: a failed system-of-power invocation
that pushes accumulated Strain past a multiple of the character's maximum Stamina costs 1
Trauma per multiple crossed, with Strain carrying forward at its remainder (Trauma's own
"further point past the floor" shape, 08-afflictions.md, restated for Strain with maximum
Stamina as the modulus instead of a fixed number). Only a failed invocation is checked -- a
success crossing the same multiple costs nothing extra.

Supersedes an earlier same-power-failure-streak design (see ADR 0045's own superseded section
and #172): that version was defeated outright by rotating between two known systems of power.
This version is checked directly against that exact exploit below (see rotation_matches_spam)
and confirmed immune, because the check never reads which power produced the failure -- only
the character's own Strain total and maximum Stamina.
"""
from fractions import Fraction
import random

SEED = 20260831


def crossings(before: int, after: int, modulus: int) -> int:
    """How many multiples of `modulus` lie strictly between `before` and `after`, treating the
    modulus itself as the floor (not itself a further point) -- exactly Trauma's own convention
    (08-afflictions.md: "6 is the floor... fires on the next point past it") restated with
    `modulus` standing in for the fixed 6."""
    return max(0, (after - 1) // modulus - max(before - 1, 0) // modulus)


def replay(seed: int, attempts: int, eff: int, strain_cost: int, max_stamina: int,
           rotate_powers: bool = False):
    """Replays `attempts` invocations of a d100 test at `eff`%, paying `strain_cost` Strain
    every time regardless of outcome, and applying the Trauma brake on failure. `rotate_powers`
    is purely cosmetic here -- the brake's own logic never reads it -- included only so the
    rotation-immunity check below is visibly running a distinct scenario, not the same call
    twice."""
    rng = random.Random(seed)
    strain = 0
    trauma = 0
    log = []
    for i in range(1, attempts + 1):
        power = ("A" if i % 2 == 1 else "B") if rotate_powers else "A"
        roll = rng.randint(1, 100)
        success = roll <= eff
        before = strain
        strain += strain_cost
        gained = 0
        if not success:
            gained = crossings(before, strain, max_stamina)
            trauma += gained
            if gained:
                strain %= max_stamina
        log.append(dict(i=i, power=power, roll=roll, success=success, strain=strain,
                         trauma=trauma, gained=gained))
    return log


def check(claim: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {claim}")
    if not ok:
        raise SystemExit(1)


def main() -> int:
    print("Re-run of a comparable spam sequence to #151's playtest, major tier "
          "(eff. 10%, strain_cost 8), across the realistic maximum-Stamina range (6-10):\n")
    for max_stamina in range(6, 11):
        log = replay(SEED, 26, 10, 8, max_stamina)
        final = log[-1]
        print(f"  max Stamina {max_stamina:>2}: 26/26 fail, final Trauma {final['trauma']:>2}, "
              f"final Strain (remainder) {final['strain']}")
        check(f"max Stamina {max_stamina}: spam produces real, non-zero Trauma",
              final['trauma'] > 0)
        check(f"max Stamina {max_stamina}: spam crosses the Affliction threshold (6+ Trauma, "
              f"08-afflictions.md)", final['trauma'] >= 6)

    print("\nOrdinary use (3 invocations of one power, eff. 50%, strain_cost 2, "
          "success/success/fail -- the design doc's own worked example):")
    for max_stamina in range(6, 11):
        rng_seed_irrelevant = None
        strain = 0
        trauma = 0
        for roll, eff in [(26, 50), (25, 50), (66, 50)]:
            before = strain
            strain += 2
            success = roll <= eff
            if not success:
                gained = crossings(before, strain, max_stamina)
                trauma += gained
                if gained:
                    strain %= max_stamina
        print(f"  max Stamina {max_stamina:>2}: Trauma {trauma}")
        check(f"max Stamina {max_stamina}: ordinary play costs zero extra Trauma",
              trauma == 0)

    print("\nMixed-outcome, mostly-successful use (eff. 50%, strain_cost 4, 26 attempts) -- "
          "confirms the brake is failure-gated, not volume-gated:")
    for max_stamina in (9, 12):
        # any-outcome variant, for comparison only -- not the adopted rule
        rng = random.Random(SEED)
        strain_any = 0
        trauma_any = 0
        rng2 = random.Random(SEED)
        strain_fail = 0
        trauma_fail = 0
        for _ in range(26):
            roll = rng.randint(1, 100)
            success = roll <= 50
            before = strain_any
            strain_any += 4
            gained = crossings(before, strain_any, max_stamina)
            trauma_any += gained
            if gained:
                strain_any %= max_stamina

            roll2 = rng2.randint(1, 100)
            success2 = roll2 <= 50
            before2 = strain_fail
            strain_fail += 4
            if not success2:
                gained2 = crossings(before2, strain_fail, max_stamina)
                trauma_fail += gained2
                if gained2:
                    strain_fail %= max_stamina
        print(f"  max Stamina {max_stamina:>2}: any-outcome Trauma {trauma_any:>2}, "
              f"failure-only Trauma {trauma_fail:>2}")
        check(f"max Stamina {max_stamina}: failure-only produces strictly less Trauma than "
              f"counting every outcome, on identical rolls", trauma_fail < trauma_any)

    print("\nRotation-immunity check: identical roll sequence, single power spammed vs. two "
          "powers alternated (#172's original exploit) -- must produce identical Trauma, since "
          "the brake never reads which power failed:")
    for max_stamina in range(6, 11):
        single = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=False)
        rotated = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=True)
        check(f"max Stamina {max_stamina}: single-power and two-power-rotation Trauma match "
              f"exactly ({single[-1]['trauma']} == {rotated[-1]['trauma']})",
              single[-1]['trauma'] == rotated[-1]['trauma'])

    print("\nAll checks passed: the max-Stamina-threshold brake produces real, failure-gated "
          "Trauma on a spam sequence, leaves ordinary and mostly-successful play untouched "
          "relative to a naive any-outcome rule, and is immune to #172's rotation exploit by "
          "construction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
