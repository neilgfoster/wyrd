"""Kester spams minor-tier ember-craft across an encounter -- the typical caster-in-a-fight
case, contrasted with #151/#174's major-tier minmax spam. Same character, same max Stamina (6),
same ADR 0045 threshold rule; only the declared tier differs (minor: eff. 50, strain_cost 2, no
Ill Omen Taint bonus, vs major: eff. 10, strain_cost 8, +3 Ill Omen Taint bonus). Real d100
draws, seeded 20260850, 26 attempts -- the same count as the major-tier sequence already on
record, for a direct rate comparison, even though a real encounter more plausibly runs 8-12
rounds (the first dozen are called out separately below)."""

import random

MAX_STAMINA = 6
STRAIN_COST = 2  # minor tier, no multiplier
EFF = 50  # minor tier, no difficulty shift
ILL_OMEN_TAINT = 1  # minor tier, no Ill Omen Taint bonus
TEST_SKILL = 50  # same GM-chosen Affliction-test assumption as the major-tier replay


def crossings(before, after, modulus):
    return max(0, (after - 1) // modulus - max(before - 1, 0) // modulus)


rng = random.Random(20260850)
strain = 0
taint = 0
trauma = 0
log = []

for i in range(1, 27):
    roll = rng.randint(1, 100)
    success = roll <= EFF
    before = strain
    strain += STRAIN_COST
    units = roll % 10
    band = 2 if taint >= 3 else 1
    ill_omen = units < band
    if ill_omen:
        taint += ILL_OMEN_TAINT
    gained = 0
    afflictions_this = 0
    if not success:
        gained = crossings(before, strain, MAX_STAMINA)
        if gained:
            strain %= MAX_STAMINA
            for _ in range(gained):
                trauma += 1
                if trauma > 6:
                    t = rng.randint(1, 100)
                    if t > TEST_SKILL:
                        trauma -= 6
                        afflictions_this += 1
    log.append((i, roll, success, strain, ill_omen, taint, trauma, gained, afflictions_this))

fails = 0
for i, roll, success, strain_v, ill_omen, taint_v, trauma_v, gained, aff in log:
    if not success:
        fails += 1
    flag = f"  <<< +{gained} Trauma" + (f", {aff} Affliction(s)" if aff else "") if gained else ""
    print(
        f"  #{i:>2} roll {roll:>3} {'PASS' if success else 'fail':<4} Strain {strain_v:>2} "
        f"IllOmen {'Y' if ill_omen else 'n'} Taint {taint_v:>2} Trauma {trauma_v:>2}{flag}"
    )

final = log[-1]
trauma_events = sum(1 for r in log if r[7])
print(
    f"\nFinal (26 attempts): {fails}/26 fail, Strain {final[3]}, Taint {final[5]}, "
    f"Trauma {final[6]}. Trauma gained on {trauma_events} of {fails} failures "
    f"({trauma_events}/{fails} = {trauma_events / fails * 100:.0f}% of fails cost Trauma)."
)

first12 = log[:12]
fails12 = sum(1 for r in first12 if not r[2])
trauma12 = first12[-1][6]
print(
    f"\nFirst 12 attempts (a more realistic single-encounter length): "
    f"{fails12}/12 fail, Trauma after 12: {trauma12}."
)
