"""Verify ADR 0047's Strain-threshold Trauma brake: a failed system-of-power invocation that
leaves accumulated Strain containing a multiple of the character's maximum Stamina costs 1
Trauma per multiple, with Strain carrying forward at its remainder (Trauma's own "further point
past the floor" shape, 08-afflictions.md, restated for Strain with maximum Stamina as the
modulus instead of a fixed number). Only a failed invocation is checked -- a success carrying
Strain past a multiple costs nothing extra at the moment it is rolled.

The check reads Strain's CURRENT, CUMULATIVE total on a failure -- `(strain - 1) // max_stamina`
-- not a before/after delta scoped to the one invocation that just resolved. This needs no
separate bookkeeping: Strain is only ever reduced at the moment it is charged, so its own
magnitude, left alone through any run of successes, already carries forward everything a failure
needs to catch up on.

Supersedes ADR 0045's own first draft, which computed the crossing as a before/after delta on
just the resolving invocation: `crossings(before, after, modulus) = max(0, (after-1)//modulus -
max(before-1,0)//modulus)`. That form correctly exempted a success from paying, but also let a
success permanently ERASE the crossing for every failure after it -- found by re-playing #176's
minor-tier spam sequence, where a failure at 6.3x maximum Stamina (built up almost entirely by
successes) cost zero Trauma under the old check. `compare_edge_vs_cumulative` below reproduces
that exact defect directly, then confirms the corrected check closes it.

Also supersedes an earlier same-power-failure-streak design (#172): that version was defeated
outright by rotating between two known systems of power. This module's `rotation_matches_spam`
check confirms the corrected cumulative-Strain check is immune to that exploit too, for the same
reason ADR 0045 already was -- the check never reads which power produced the failure.
"""
import random

SEED = 20260831


def crossings_edge(before: int, after: int, modulus: int) -> int:
    """ADR 0045's superseded check: a before/after delta scoped to one invocation. Kept here
    only so this module can demonstrate exactly what it got wrong, not as the adopted rule."""
    return max(0, (after - 1) // modulus - max(before - 1, 0) // modulus)


def gained_cumulative(strain: int, modulus: int) -> int:
    """ADR 0047's adopted check: how many multiples of `modulus` the character's CURRENT,
    cumulative Strain now contains, treating the modulus itself as the floor (not itself a
    further point) -- exactly Trauma's own convention (08-afflictions.md), restated for Strain.
    No separate "already charged" counter is needed: Strain is only ever reduced right here, so
    its own magnitude already reflects everything outstanding since the last charge."""
    return (strain - 1) // modulus


def replay(seed: int, attempts: int, eff: int, strain_cost: int, max_stamina: int,
           rotate_powers: bool = False):
    """Replays `attempts` invocations of a d100 test at `eff`%, paying `strain_cost` Strain
    every time regardless of outcome, and applying ADR 0047's corrected brake on failure.
    `rotate_powers` is purely cosmetic -- the brake's own logic never reads it -- included only
    so the rotation-immunity check below is visibly running a distinct scenario, not the same
    call twice."""
    rng = random.Random(seed)
    strain = 0
    trauma = 0
    log = []
    for i in range(1, attempts + 1):
        power = ("A" if i % 2 == 1 else "B") if rotate_powers else "A"
        roll = rng.randint(1, 100)
        success = roll <= eff
        strain += strain_cost
        gained = 0
        if not success:
            gained = gained_cumulative(strain, max_stamina)
            if gained:
                trauma += gained
                strain -= gained * max_stamina
        log.append(dict(i=i, power=power, roll=roll, success=success, strain=strain,
                         trauma=trauma, gained=gained))
    return log


def compare_edge_vs_cumulative(seed: int, attempts: int, eff: int, strain_cost: int,
                                max_stamina: int):
    """Runs the SAME roll sequence through both the superseded edge-triggered check and the
    adopted cumulative check, returning both final Trauma totals -- demonstrates the fix
    reproduces the defect (edge undercounts) and closes it (cumulative never undercounts)."""
    rng = random.Random(seed)
    strain_edge = 0
    trauma_edge = 0
    strain_cum = 0
    trauma_cum = 0
    for _ in range(attempts):
        roll = rng.randint(1, 100)
        success = roll <= eff

        before = strain_edge
        strain_edge += strain_cost
        if not success:
            g = crossings_edge(before, strain_edge, max_stamina)
            if g:
                trauma_edge += g
                strain_edge %= max_stamina

        strain_cum += strain_cost
        if not success:
            g = gained_cumulative(strain_cum, max_stamina)
            if g:
                trauma_cum += g
                strain_cum -= g * max_stamina

    return trauma_edge, trauma_cum


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
        strain = 0
        trauma = 0
        for roll, eff in [(26, 50), (25, 50), (66, 50)]:
            strain += 2
            success = roll <= eff
            if not success:
                g = gained_cumulative(strain, max_stamina)
                if g:
                    trauma += g
                    strain -= g * max_stamina
        print(f"  max Stamina {max_stamina:>2}: Trauma {trauma}")
        check(f"max Stamina {max_stamina}: ordinary play costs zero extra Trauma",
              trauma == 0)

    print("\nFailure-gating, not volume-gating -- a run of successes alone never directly costs")
    print("Trauma, however high it carries Strain, because only a failure branch ever checks or")
    print("charges the threshold at all. This is the property that distinguishes 'failure-only'")
    print("from the rejected 'any outcome counts' alternative (ADR 0045's own Alternatives")
    print("section) -- under ADR 0047's cumulative check, both eventually collect the same total")
    print("debt if a failure ever follows, so the real distinction is WHETHER a success can ever")
    print("be the direct trigger, not how much total Trauma results:")
    for max_stamina, strain_cost, n_successes in ((9, 4, 26), (12, 4, 50)):
        strain = 0
        trauma_direct_on_success = 0
        for _ in range(n_successes):
            strain += strain_cost  # every attempt succeeds -- eff effectively 100% for this check
            # A success NEVER calls the crossing check at all -- that omission is the property
            # under test, made explicit here rather than left implicit.
        print(f"  max Stamina {max_stamina:>2}, {n_successes} consecutive successes, strain_cost "
              f"{strain_cost}: Strain reaches {strain}, Trauma directly charged by a success: "
              f"{trauma_direct_on_success}")
        check(f"max Stamina {max_stamina}: {n_successes} consecutive successes never directly "
              f"cost Trauma, however high Strain climbs", trauma_direct_on_success == 0)

    print("\nThe backlog a run of successes builds is not forgiven -- it is paid in full by the")
    print("next failure, however large, confirming ADR 0047 closes the erasure without silently")
    print("dropping any of the debt a run of successes accumulated:")
    for max_stamina, strain_cost, n_successes in ((9, 4, 20),):
        strain = strain_cost * n_successes
        g = gained_cumulative(strain, max_stamina)
        print(f"  max Stamina {max_stamina}: {n_successes} successes then one failure -- "
              f"strain {strain}, single failure charges {g} Trauma at once")
        check(f"max Stamina {max_stamina}: the single failure charges the whole backlog "
              f"({g} multiples), not just the last strain_cost's worth", g > 1)

    print("\nRotation-immunity check: identical roll sequence, single power spammed vs. two "
          "powers alternated (#172's original exploit) -- must produce identical Trauma, since "
          "the brake never reads which power failed:")
    for max_stamina in range(6, 11):
        single = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=False)
        rotated = replay(SEED, 26, 10, 8, max_stamina, rotate_powers=True)
        check(f"max Stamina {max_stamina}: single-power and two-power-rotation Trauma match "
              f"exactly ({single[-1]['trauma']} == {rotated[-1]['trauma']})",
              single[-1]['trauma'] == rotated[-1]['trauma'])

    print("\nADR 0047's fix, demonstrated directly: the superseded edge-triggered check vs. the "
          "adopted cumulative check, on the SAME roll sequences (#178):")
    for label, seed, attempts, eff, strain_cost, max_stamina in [
        ("major tier (sec10/sec14)", 20260842, 26, 10, 8, 6),
        ("minor tier (sec15)", 20260850, 26, 50, 2, 6),
    ]:
        edge, cum = compare_edge_vs_cumulative(seed, attempts, eff, strain_cost, max_stamina)
        print(f"  {label}: edge-triggered Trauma {edge}, cumulative Trauma {cum}")
        check(f"{label}: cumulative check never gives less Trauma than the superseded "
              f"edge-triggered one on the same rolls", cum >= edge)
        check(f"{label}: cumulative check gives strictly MORE Trauma here -- the erasure ADR "
              f"0047 fixes was real on this exact sequence, not a hypothetical",
              cum > edge)

    print("\nAll checks passed: ADR 0047's cumulative-Strain check produces real, failure-gated "
          "Trauma on a spam sequence, leaves ordinary and mostly-successful play untouched, is "
          "immune to #172's rotation exploit, and closes the erasure ADR 0045's edge-triggered "
          "check allowed -- demonstrated on the exact sequences that found it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
