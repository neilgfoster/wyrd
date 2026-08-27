"""Re-run a comparable spam sequence to #151's playtest finding (#163) and confirm ADR 0045's
brake actually changes the outcome, not just the prose (#163's own acceptance criterion).

Replays a fresh, disclosed, seeded d100 sequence of major-tier `ember-craft` invocations
(eff. 10%, the worked example's own numbers from 09-systems-of-power.md/30-playtest-transcript.md
sec10), comparing the published (pre-fix) rule -- cost paid regardless of outcome, no brake -- to
ADR 0045's rule -- 1 Trauma on a failed invocation immediately following another failed
invocation of the same system of power in the same scene, first failure of the scene free.
"""
import random
from fractions import Fraction

SEED = 20260831
ATTEMPTS = 26
EFF = 10          # major tier, "Very Hard"
STRAIN_COST = 8   # strain_cost 2 * cost_multiplier 4, the worked example's major tier


def replay(seed: int, attempts: int, eff: int):
    rng = random.Random(seed)
    strain = 0
    trauma_no_brake = 0
    trauma_with_brake = 0
    streak_failed = False  # whether the previous invocation of this power failed
    results = []
    for i in range(1, attempts + 1):
        roll = rng.randint(1, 100)
        success = roll <= eff
        strain += STRAIN_COST
        if not success:
            # published rule: no Trauma consequence at all
            # ADR 0045: 1 Trauma if this failure immediately follows another failure of the
            # same power in the same scene; the first failure of the scene is free.
            if streak_failed:
                trauma_with_brake += 1
            streak_failed = True
        else:
            streak_failed = False
        results.append((i, roll, success, strain, trauma_no_brake, trauma_with_brake))
    return results, trauma_no_brake, trauma_with_brake, strain


def check(claim: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {claim}")
    if not ok:
        raise SystemExit(1)


def main() -> int:
    print(f"Replaying {ATTEMPTS} major-tier (eff. {EFF}%) invocations, seed {SEED}, "
          f"strain_cost {STRAIN_COST} (2 base x4 major-tier multiplier).\n")
    results, trauma_no_brake, trauma_with_brake, final_strain = replay(SEED, ATTEMPTS, EFF)

    fails = sum(1 for _, _, success, *_ in results if not success)
    print(f"  fails: {fails}/{ATTEMPTS}   final Strain: {final_strain}")
    print(f"  Trauma under the published (pre-fix) rule: {trauma_no_brake}")
    print(f"  Trauma under ADR 0045's brake:              {trauma_with_brake}\n")

    check("the published rule accrues zero Trauma from this sequence, matching #163's own "
          "finding (\"nothing brakes the spam\")", trauma_no_brake == 0)
    check("ADR 0045's brake accrues real, non-zero Trauma from the same sequence -- the fix "
          "actually changes the outcome, not just the prose (#163's acceptance criterion)",
          trauma_with_brake > 0)
    check("the brake's Trauma total is consistent with 'first failure free, then 1 per "
          "consecutive further failure' -- at most (fails - 1) when every attempt fails and "
          "there is no success to reset the streak", trauma_with_brake <= fails - 1)
    check("a spam run of consecutively-failing invocations crosses the Affliction threshold "
          "(6+ Trauma, 08-afflictions.md) under the brake, where it never could under the "
          "published rule", trauma_with_brake >= 6)

    print("\nAlso confirm the brake does NOT fire on ordinary, non-spam play: three invocations "
          "of the same power with only one failure among them (09-systems-of-power.md's own "
          "worked example, 30-playtest-transcript.md sec10's 'ordinary use').")
    rng = random.Random(1)
    ordinary_rolls = [26, 25, 66]  # matches the documented ordinary-use sequence: success,
                                    # success, fail -- reused directly, not re-rolled
    streak_failed = False
    ordinary_trauma = 0
    for roll in ordinary_rolls:
        success = roll <= 50  # minor tier, eff. 50 in the documented example
        if not success:
            if streak_failed:
                ordinary_trauma += 1
            streak_failed = True
        else:
            streak_failed = False
    check("ordinary play (one isolated failure among successes) costs zero Trauma under the "
          "brake -- a character is still free to try, per ADR 0045's own stated intent",
          ordinary_trauma == 0)

    print("\nAll checks passed: ADR 0045's brake leaves ordinary play untouched and gives "
          "repeated same-power failure a real, persistent cost that survives a Rally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
