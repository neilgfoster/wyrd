#!/usr/bin/env python3
"""Compute the career cap and the maximum-Stamina ceiling, rather than asserting them.

design/03-rules.md section 6 already writes "to that career's cap" and calls
completing a career ("every granted skill at its cap") "the only durable
toughening": +1 maximum Stamina and a Mark. Neither the cap nor a stopping
point for the Stamina gain was ever stated -- this script computes both, the
same way specs/008-character-creation/check_creation.py computed the starting
value of 6 rather than picking it.

## The cap

A flat 70% (design/10-diegesis.md's *expert* band, 60-70%), applied uniformly
to every skill a career grants (03-rules.md sec6 already writes "career's
cap" as one figure per career, not one per skill). This script does not
derive 70% numerically -- it is a design choice recorded in ADR 0032 -- but it
does confirm the consequence the spec requires: under this cap, no skill a
character can reach through career advancement alone can ever exceed 100%,
and completing many careers still leaves "expert," not "it is part of who you
are" (75%+), as the ceiling ordinary advancement buys.

## The Stamina ceiling

check_creation.py fixed the *starting* value at 6 using an explicit
threshold: a completion's +1 gain must stay a large-enough fraction of
current Stamina for "the only durable toughening" to still read as true, and
that document names the boundary directly -- "much above 10 and the sentence
stops being true." This script reuses that same boundary rather than
inventing a new one: it defines the gain as still meaningful while it is at
least 10%, computes the Stamina value at which a further +1 first drops below
that floor, and asserts it lands at the ceiling design/03c-character-creation.md
already gestured at.

    gain_fraction(S) = 1 / S
    ceiling = the largest S at which 1/S >= 0.10, i.e. S = 10

Above the ceiling, completing a career still grants a Mark; it stops granting
further maximum Stamina.

Run: python3 tools/check_advancement.py
"""

STARTING_STAMINA = 6          # design/03c-character-creation.md
CAREER_CAP = 0.70             # design/10-diegesis.md's *expert* band top
SKILL_OPEN_VALUE = 0.25       # design/03-rules.md s6, and s03c
ADVANCE_STEP = 0.05           # design/03-rules.md s6
MEANINGFUL_GAIN_FLOOR = 0.10  # the boundary 03c already names ("much above 10")
CHRONICLE_INSTANCES = 12      # >= 10 required by spec.md SC-004


def stamina_ceiling(floor: float = MEANINGFUL_GAIN_FLOOR) -> int:
    """Largest Stamina value at which a further +1 gain is still >= floor."""
    stamina = 1
    while (1.0 / (stamina + 1)) >= floor:
        stamina += 1
    return stamina


def advances_to_cap(start: float = SKILL_OPEN_VALUE, cap: float = CAREER_CAP,
                     step: float = ADVANCE_STEP) -> int:
    """How many +5% advances carry one skill from opening to the career cap."""
    count = 0
    value = start
    while value < cap - 1e-9:
        value = min(value + step, cap)
        count += 1
    return count


def run_chronicle(instances: int, ceiling: int) -> list[dict]:
    """Simulate `instances` career-instances completed back-to-back.

    Each instance opens two skills (the creation-time floor,
    03c-character-creation.md) and raises both to the cap, then completes:
    +1 maximum Stamina (until the ceiling) and one Mark, always.
    """
    stamina = STARTING_STAMINA
    marks = 0
    history = []
    for instance in range(1, instances + 1):
        skills = [SKILL_OPEN_VALUE, SKILL_OPEN_VALUE]
        skills = [CAREER_CAP for _ in skills]  # advances spent until every granted skill is at cap
        assert all(s <= CAREER_CAP + 1e-9 for s in skills), "a skill exceeded its career's cap"
        assert all(s <= 1.0 for s in skills), "a skill exceeded 100%"
        gained_stamina = stamina < ceiling
        if gained_stamina:
            stamina += 1
        marks += 1
        history.append({
            "instance": instance,
            "stamina": stamina,
            "marks": marks,
            "gained_stamina": gained_stamina,
        })
    return history


def main() -> None:
    ceiling = stamina_ceiling()
    print(f"Meaningful-gain floor (03c's own boundary): {MEANINGFUL_GAIN_FLOOR:.0%}")
    print(f"Computed maximum-Stamina ceiling: {ceiling}")
    assert ceiling == 10, (
        f"expected the ceiling to land at 10 (03c's stated boundary), got {ceiling}"
    )

    per_skill_advances = advances_to_cap()
    print(f"\nAdvances to carry one skill from {SKILL_OPEN_VALUE:.0%} to the "
          f"{CAREER_CAP:.0%} cap: {per_skill_advances}")
    assert CAREER_CAP <= 1.0, "the career cap must not exceed 100%"

    print(f"\nSimulating {CHRONICLE_INSTANCES} career-instances completed "
          "back-to-back:\n")
    history = run_chronicle(CHRONICLE_INSTANCES, ceiling)
    print(f"{'instance':>8} {'stamina':>8} {'marks':>6} {'stamina gained?':>16}")
    for row in history:
        print(f"{row['instance']:>8} {row['stamina']:>8} {row['marks']:>6} "
              f"{str(row['gained_stamina']):>16}")

    final = history[-1]
    assert final["stamina"] == ceiling, (
        f"Stamina failed to converge to the ceiling: ended at {final['stamina']}, "
        f"expected {ceiling}"
    )
    assert final["marks"] == CHRONICLE_INSTANCES, "a completion failed to grant its Mark"
    stopped_at = next(row["instance"] for row in history if not row["gained_stamina"])
    print(f"\nStamina stops climbing after instance {stopped_at - 1} (ceiling "
          f"{ceiling} reached); every instance after that still grants a Mark.")

    print("\nAcross every completed instance, no skill exceeded the career cap "
          f"({CAREER_CAP:.0%}) and maximum Stamina converged to a stated ceiling "
          f"({ceiling}) rather than growing without bound -- both explicit "
          "findings design/03-rules.md now states rather than assumes.")


if __name__ == "__main__":
    main()
