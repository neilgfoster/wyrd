"""Re-play sec10's two findings against Kester's own actual character, now that ADR 0043 and
ADR 0045 are both settled. Kester: ember-craft 50, strain_cost 2, ill_omen_taint 1,
intensity_tiers as published, starting Strain 0, Taint 0, Stamina 6/6 (creation default --
sec10 never stated one explicitly, so this uses the same default sec8/sec9's Senna started
from). Fresh seeded rolls, seeded 20260841 for the Resolve recurrence and 20260842 for the
spam re-run (distinct seeds so this pass's own draws are separable from sec10's original
20260831 sequence, which this does not reuse -- the scenario itself has changed, not just the
reading of an already-drawn roll, unlike sec7)."""
import random

MAX_STAMINA = 6


def crossings(before, after, modulus):
    return max(0, (after - 1) // modulus - max(before - 1, 0) // modulus)


print("=== The Resolve gap recurrence, replayed under ADR 0043 ===\n")
rng = random.Random(20260841)
taint = 0
resolve = 0
print(f"Kester, resolve_cost: 1 added to ember-craft. Starting Taint {taint}, Resolve {resolve}.")
print("At Taint 0, cap = Taint + 3 = 3 -- but Resolve is still 0 until a Rally, exactly as any")
print("other fresh character (11-character-creation.md: everything starts at 0).")
print("The very first invocation still cannot pay resolve_cost: 1 -- not a gap anymore, though:")
print("it is the same 'nothing has happened yet' state Stamina/Strain/Taint all start from, and")
print("the fix is simply the same one every other track already uses: a Rally first.\n")
resolve += 1
print(f"After a Rally: Resolve {resolve - 1} -> {resolve}. Now he can invoke.")
roll = rng.randint(1, 100)
eff = 50
print(f"Invocation, eff. {eff}: roll {roll} -- ", end="")
success = roll <= eff
print("success." if success else "fails.")
resolve -= 1
print(f"resolve_cost: 1 paid regardless of outcome: {resolve + 1} -> {resolve}. Pays cleanly --")
print("the gap sec10 found (cannot pay it as written, ever) is closed.\n")

print("=== The spam sequence, replayed against Kester's own character under ADR 0045 ===\n")
rng2 = random.Random(20260842)
strain = 0
taint2 = 0
trauma = 0
strain_cost = 8  # 2 base x4 major-tier multiplier, as sec10's own worked numbers use
eff2 = 10  # major tier, Very Hard
test_skill = 50  # GM-chosen skill for the Affliction test, disclosed as an assumption

log = []
for i in range(1, 27):
    roll = rng2.randint(1, 100)
    success = roll <= eff2
    strain += strain_cost
    units = roll % 10
    band = 2 if taint2 >= 3 else 1
    ill_omen = units < band
    if ill_omen:
        taint2 += 1 + 3  # ill_omen_taint 1 + major-tier bonus +3
    gained = 0
    afflictions_this = 0
    if not success:
        gained = crossings(strain - strain_cost, strain, MAX_STAMINA)
        if gained:
            strain %= MAX_STAMINA
            for _ in range(gained):
                trauma += 1
                if trauma > 6:
                    t = rng2.randint(1, 100)
                    if t > test_skill:
                        trauma -= 6
                        afflictions_this += 1
    log.append((i, roll, success, strain, ill_omen, taint2, trauma, gained, afflictions_this))

for i, roll, success, strain_v, ill_omen, taint_v, trauma_v, gained, aff in log:
    flag = f"  <<< +{gained} Trauma" + (f", {aff} Affliction(s)" if aff else "") if gained else ""
    print(f"  #{i:>2} roll {roll:>3} {'PASS' if success else 'fail':<4} Strain {strain_v:>2} "
          f"IllOmen {'Y' if ill_omen else 'n'} Taint {taint_v:>2} Trauma {trauma_v:>2}{flag}")

final = log[-1]
print(f"\nFinal: Strain {final[3]}, Taint {final[5]}, Trauma {final[6]} "
      f"({26 - sum(1 for r in log if r[2])}/26 fail).")
