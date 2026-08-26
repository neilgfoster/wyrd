#!/usr/bin/env python3
"""Compute the affliction sawtooth's cadence, rather than asserting it.

doc/design/03-rules.md section 5: at 6+ Trauma, test on every further point; on a
failure take an Affliction (doc/design/11-afflictions.md) and lose 6 Trauma. Trauma
itself accrues 1 per critical taken and 1 per failed Terror test (both ordinary,
frequent events), plus occasional GM-discretion additions this script does not
model (rare, and undefined in size).

Below 6 Trauma nothing tests. At 6 Trauma and above, every further Trauma-adding
event is itself a test: pass and Trauma keeps climbing; fail and an Affliction
fires, dropping Trauma by 6. That is an exact, finite-state Markov chain over
integer Trauma values once a character first reaches 6.

## The closed form

Let `skill` be the test's pass chance and `p` the long-run fraction of
Trauma-adding events spent at 6+ Trauma (mid-test). Each event changes Trauma by
+1 on a pass and by `1 - 6 = -5` on a fail (climb by 1, then drop 6). A character
who has been playing long enough for the process to settle has zero net drift in
Trauma (otherwise it would run away to infinity), so:

    (1 - p) * 1 + p * (skill - 5 * (1 - skill)) = 0
    =>  p = 1 / (6 * (1 - skill))                    ... provided skill < 5/6

The long-run Affliction rate per Trauma-adding event is `p * (1 - skill)`, and the
`(1 - skill)` cancels exactly:

    rate = p * (1 - skill) = 1 / 6

**The skill dependence cancels.** The sawtooth's cadence, once a character first
reaches 6 Trauma, is exactly one Affliction per six Trauma-adding events --
independent of what the test is rolled against -- because the floor (6) and the
drop (6) are the same number. That is a property of the two sixes agreeing, not a
coincidence of any particular skill value, and it is why this document does not
need to fix which skill the test uses (03a-4-afflictions.md leaves that to the
fiction, matching Exposure).

**It only holds below `skill = 5/6` (~83%).** Above that, `p > 1` is impossible --
there is no stationary distribution, and Trauma drifts upward without bound
instead of sawtoothing, because the character passes reliably enough that a
single failure's -6 drop no longer offsets the accumulated climb on average. This
script verifies the closed form numerically below the threshold and confirms the
runaway above it, rather than asserting the boundary is exactly 5/6.

Run: python3 tools/check_affliction.py
"""

FLOOR = 6   # first Trauma value at which a further point is tested (03-rules.md s5)
DROP = 6    # Trauma lost on a failed test (03-rules.md s5)
CAP = 400   # truncation for the numeric check; large enough that clipping is negligible below 5/6
ITERATIONS = 20000  # lazy power iteration steps -- see stationary_affliction_rate

CLOSED_FORM_RATE = 1.0 / DROP
DIVERGENCE_SKILL = 1.0 - 1.0 / DROP  # 5/6 for DROP=6

# Representative test skills (03-rules.md s1). The test is fiction-chosen (matching
# Exposure), so the GM picks a skill the character actually has, not the flat 10%
# untrained rate. "Trained, average difficulty" starts at 25%; a "competent"
# character is used at 45% elsewhere in the ruleset (s1's extended-task example);
# 65% represents a specialist -- all three sit below the 5/6 divergence point.
SKILLS_BELOW_THRESHOLD = [0.25, 0.45, 0.65]
SKILL_ABOVE_THRESHOLD = 0.90  # to confirm the runaway, not to model real play

EVENTS_PER_SESSION = [0.25, 0.5, 1.0, 2.0]  # criticals taken + failed Terror tests
SESSIONS_PER_YEAR = 45  # roughly weekly play allowing for breaks; stated, not derived


def stationary_affliction_rate(skill: float, cap: int = CAP) -> float:
    """Numeric cross-check of the closed form via the lazy chain's stationary mass.

    The raw chain is periodic during the deterministic climb below FLOOR, so plain
    power iteration settles into a limit cycle rather than the stationary
    distribution. Iterating the lazy chain instead (half the time nothing happens)
    has the same stationary distribution and does converge.
    """
    fail = 1.0 - skill
    pi = [0.0] * (cap + 1)
    pi[0] = 1.0
    for _ in range(ITERATIONS):
        nxt = [0.5 * mass for mass in pi]
        for t, mass in enumerate(pi):
            if mass == 0.0:
                continue
            if t < FLOOR:
                nxt[min(t + 1, cap)] += 0.5 * mass
            else:
                nxt[min(t + 1, cap)] += 0.5 * mass * skill
                nxt[max(t + 1 - DROP, 0)] += 0.5 * mass * fail
        total = sum(nxt)
        pi = [x / total for x in nxt]
    return sum(mass * (1.0 - skill) for t, mass in enumerate(pi) if t >= FLOOR)


def main() -> None:
    print("Below the 5/6 divergence point, the numeric chain must match the "
          f"closed form (1/{DROP} = {CLOSED_FORM_RATE:.4f}):\n")
    for skill in SKILLS_BELOW_THRESHOLD:
        numeric = stationary_affliction_rate(skill)
        print(f"  skill {skill:>4.0%}: numeric rate {numeric:.4f}")
        assert abs(numeric - CLOSED_FORM_RATE) < 0.01, (
            f"closed form mismatch at skill={skill}: numeric={numeric}, "
            f"closed_form={CLOSED_FORM_RATE}"
        )

    print(f"\nAbove {DIVERGENCE_SKILL:.0%} the process has no stationary "
          "distribution -- Trauma drifts upward instead of sawtoothing. A capped "
          "simulation should show mass still piling up at the cap rather than "
          "settling:")
    small_cap = 120
    tail_mass = stationary_pi_tail_mass(SKILL_ABOVE_THRESHOLD, small_cap)
    print(f"  skill {SKILL_ABOVE_THRESHOLD:.0%}, cap {small_cap}: "
          f"{tail_mass:.1%} of probability mass sits in the top 10% of the cap")
    assert tail_mass > 0.2, (
        "expected substantial mass piled at the truncation cap above the "
        "divergence point, found none -- the runaway is not showing up"
    )

    print(f"\nCadence at the closed-form rate (1/{DROP} per Trauma-adding event, "
          "valid for skill < 83%), across a spread of event rates:\n")
    print(f"{'events/session':>15} {'sessions/affliction':>20} "
          f"{'per chronicle-year':>19}")
    cadences = []
    for events in EVENTS_PER_SESSION:
        afflictions_per_session = CLOSED_FORM_RATE * events
        sessions_per_affliction = 1.0 / afflictions_per_session
        per_year = SESSIONS_PER_YEAR / sessions_per_affliction
        cadences.append(sessions_per_affliction)
        print(f"{events:>15.2f} {sessions_per_affliction:>20.1f} "
              f"{per_year:>19.2f}")

    assert min(cadences) > 1.0, "some event rate breaks an Affliction more than once a session"
    assert max(cadences) < SESSIONS_PER_YEAR * 10, "some event rate goes a decade+ between Afflictions"
    print("\nAcross every scanned event rate, the cadence stays between "
          "'more than once a session' and 'once a decade' -- both explicit "
          "findings the design document states rather than assumes.")


def stationary_pi_tail_mass(skill: float, cap: int) -> float:
    fail = 1.0 - skill
    pi = [0.0] * (cap + 1)
    pi[0] = 1.0
    for _ in range(ITERATIONS):
        nxt = [0.5 * mass for mass in pi]
        for t, mass in enumerate(pi):
            if mass == 0.0:
                continue
            if t < FLOOR:
                nxt[min(t + 1, cap)] += 0.5 * mass
            else:
                nxt[min(t + 1, cap)] += 0.5 * mass * skill
                nxt[max(t + 1 - DROP, 0)] += 0.5 * mass * fail
        total = sum(nxt)
        pi = [x / total for x in nxt]
    threshold = int(cap * 0.9)
    return sum(pi[threshold:])


if __name__ == "__main__":
    main()
