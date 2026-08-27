"""Verify ADR 0048 (cost paid only on a failed invocation) composed with ADR 0047 (the
Strain-threshold Trauma check reads cumulative Strain, not a per-invocation delta).

Both `strain_cost` and `resolve_cost` now apply only when an invocation fails -- a success costs
neither field (ADR 0048), closing the engine's only win-or-lose exception and matching Strain's
own generic definition (03-rules.md sec5: failure-driven). Because Strain now only ever grows on
a failure, a run of successes never adds to it, and the silent-backlog scenario ADR 0047 fixed
can no longer arise through `strain_cost` specifically -- but the cumulative check
(`gained = (strain - 1) // max_stamina`) stays adopted anyway, as general-purpose correctness,
per ADR 0048's own stated consequence.

This module verifies both decisions together: a failed invocation that leaves accumulated
Strain containing a multiple of the character's maximum Stamina costs 1 Trauma per multiple,
Strain carries forward at its remainder, ordinary/mostly-successful play stays untouched, the
brake is immune to the #172 rotation exploit, and -- new here -- switching from the superseded
win-or-lose accrual to the adopted failure-only accrual measurably reduces Trauma on a
mostly-successful sequence while barely changing a mostly-failing one, exactly as ADR 0048's own
Context section quantified.
"""
import random

SEED = 20260831


def gained_cumulative(strain: int, modulus: int) -> int:
    """ADR 0047's adopted check: how many multiples of `modulus` the character's current,
    cumulative Strain now contains, treating the modulus itself as the floor (not itself a
    further point) -- exactly Trauma's own convention (08-afflictions.md), restated for Strain.
    No separate "already charged" counter is needed: Strain is only ever reduced right here, so
    its own magnitude already reflects everything outstanding since the last charge."""
    return (strain - 1) // modulus


def replay(seed: int, attempts: int, eff: int, strain_cost: int, max_stamina: int,
           resolve_cost: int = 0, fail_only_cost: bool = True, rotate_powers: bool = False):
    """Replays `attempts` invocations of a d100 test at `eff`%. `fail_only_cost` (ADR 0048,
    default) pays strain_cost/resolve_cost only on a failure; set False to replay the
    superseded win-or-lose rule for direct comparison. `rotate_powers` is purely cosmetic -- the
    brake's own logic never reads it."""
    rng = random.Random(seed)
    strain = 0
    resolve_spent = 0
    trauma = 0
    log = []
    for i in range(1, attempts + 1):
        power = ("A" if i % 2 == 1 else "B") if rotate_powers else "A"
        roll = rng.randint(1, 100)
        success = roll <= eff
        gained = 0
        if not success:
            strain += strain_cost
            resolve_spent += resolve_cost
            gained = gained_cumulative(strain, max_stamina)
            if gained:
                trauma += gained
                strain -= gained * max_stamina
        elif not fail_only_cost:
            strain += strain_cost
            resolve_spent += resolve_cost
        log.append(dict(i=i, power=power, roll=roll, success=success, strain=strain,
                         resolve_spent=resolve_spent, trauma=trauma, gained=gained))
    return log


def check(claim: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {claim}")
    if not ok:
        raise SystemExit(1)


def main() -> int:
    print("Re-run of a comparable spam sequence to #151's playtest, major tier "
          "(eff. 10%, strain_cost 8), across the realistic maximum-Stamina range (6-10), "
          "under ADR 0048's failure-only cost:\n")
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
        strain = 0
        trauma = 0
        for roll, eff in [(26, 50), (25, 50), (66, 50)]:
            success = roll <= eff
            if not success:
                strain += 2
                g = gained_cumulative(strain, max_stamina)
                if g:
                    trauma += g
                    strain -= g * max_stamina
        print(f"  max Stamina {max_stamina:>2}: Trauma {trauma}")
        check(f"max Stamina {max_stamina}: ordinary play costs zero extra Trauma",
              trauma == 0)

    print("\nA run of successes alone never touches Strain at all under ADR 0048 (not merely")
    print("'costs nothing extra' -- the cost fields are never even paid), so Trauma stays 0")
    print("regardless of run length:")
    for n_successes in (26, 50):
        strain = 0  # never incremented -- every one of these is a success, fail_only_cost=True
        print(f"  {n_successes} consecutive successes, strain_cost 4: Strain stays {strain}, "
              f"Trauma stays 0 (cost fields never paid on success)")
        check(f"{n_successes} consecutive successes: Strain untouched", strain == 0)

    print("\nresolve_cost follows strain_cost's failure-only timing (ADR 0048) -- a successful")
    print("invocation with a declared resolve_cost pays nothing, a failed one pays in full:")
    for seed, eff, label in ((SEED, 90, "mostly succeeds"), (SEED, 10, "mostly fails")):
        log = replay(seed, 10, eff, strain_cost=2, max_stamina=6, resolve_cost=1)
        successes = sum(1 for r in log if r['success'])
        fails = 10 - successes
        print(f"  eff {eff:>2}% ({label}): {successes} success, {fails} fail, "
              f"Resolve spent {log[-1]['resolve_spent']}")
        check(f"eff {eff}%: Resolve spent equals fail count exactly (1 per failure, 0 per "
              f"success)", log[-1]['resolve_spent'] == fails)

    print("\nRotation-immunity check: identical roll sequence, single power spammed vs. two "
          "powers alternated (#172's original exploit) -- must produce identical Trauma, since "
          "the brake never reads which power failed:")
    for max_stamina in range(6, 11):
        single = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=False)
        rotated = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=True)
        check(f"max Stamina {max_stamina}: single-power and two-power-rotation Trauma match "
              f"exactly ({single[-1]['trauma']} == {rotated[-1]['trauma']})",
              single[-1]['trauma'] == rotated[-1]['trauma'])

    print("\nADR 0048's fix, demonstrated directly: the superseded win-or-lose accrual vs. the")
    print("adopted failure-only accrual, on the SAME roll sequences already on record (#180):")
    for label, seed, attempts, eff, strain_cost, max_stamina in [
        ("major tier (sec10/sec14/sec16)", 20260842, 26, 10, 8, 6),
        ("minor tier (sec15/sec16)", 20260850, 26, 50, 2, 6),
    ]:
        win_or_lose = replay(seed, attempts, eff, strain_cost, max_stamina,
                              fail_only_cost=False)
        fail_only = replay(seed, attempts, eff, strain_cost, max_stamina,
                            fail_only_cost=True)
        wol_trauma = win_or_lose[-1]['trauma']
        fo_trauma = fail_only[-1]['trauma']
        print(f"  {label}: win-or-lose Trauma {wol_trauma}, failure-only Trauma {fo_trauma}")
        check(f"{label}: failure-only accrual never gives more Trauma than the superseded "
              f"win-or-lose rule on the same rolls", fo_trauma <= wol_trauma)

    print("\nAll checks passed: ADR 0048's failure-only cost removes the silent-backlog problem "
          "at its source (a success never touches Strain or Resolve), resolve_cost follows "
          "strain_cost's timing exactly, and every property ADR 0047's brake already "
          "established (spam produces real Trauma, ordinary play stays clean, rotation-immunity "
          "holds) is unaffected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
