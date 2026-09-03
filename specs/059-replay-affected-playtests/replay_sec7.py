"""Re-check sec7's combat exchange (Senna vs the bounty hunter) against ADR 0044's virtual-roll
formula, using the exact rolls already published there. No new attack/defence rolls -- the
divergence is purely in how degrees are read from an already-recorded failed defence roll."""


def degrees(skill, roll):
    return skill // 10 - roll // 10


EFF_DEF = 30  # Senna's defence effective%, fixed for the fight (sec7)
THRESHOLD = 6  # ADR 0028's telling-blow threshold

defence_rolls = [
    (1, 43),
    (2, 86),
    (3, 64),
]

print("Re-checking sec7's three failed defence rolls against ADR 0044's virtual-roll formula:")
print(f"  eff_def = {EFF_DEF}, virtual_eff = {100 - EFF_DEF}\n")
for round_no, r in defence_rolls:
    virtual_eff = 100 - EFF_DEF
    virtual_roll = 101 - r
    d = degrees(virtual_eff, virtual_roll)
    telling = d >= THRESHOLD
    print(
        f"  Round {round_no}: r={r:>3}  virtual_roll={virtual_roll:>3}  "
        f"degrees={d:>2}  {'TELLING BLOW' if telling else 'not telling'}"
    )

print("\nRound 2 becomes a telling blow: weapon roll (4) doubles to 8 before armour, armour still")
print("subtracts its already-rolled 1: 8 - 1 = 7 through, not the original 3.")
print("Senna: 4 (post-round-1) - 7 = -3 -- she drops in round 2, not round 3.")
print("Round 3 never happens under the corrected timeline (Round 2's Fair Omen, still pending")
print("from Round 2's own attack roll, lapses unused -- the fight ends before Senna's next roll).")

print("\nCritical, reusing the same 1d6 draw (die is independent of the modifier; only the")
print("points-below addend changes): original 1d6+2=5 means d6=3.")
d6 = 3
points_below = 3
total = d6 + points_below
print(f"  New: {d6} + {points_below} = {total} -> critical-slashing 6-9 band: slashing-scored")
print(
    "  (one wound record, effect dread:+1) -- not slashing-glancing (2-5) as originally recorded."
)

print("\nAftermath, reusing the same d100 draw (independent of the modifier): original 73+10=83.")
d100 = 73
new_total = d100 + 5 * points_below
print(f"  New: {d100} + 5*{points_below} = {new_total} -> still the 79-88 band: taken")
print(f"  (same outcome as originally recorded, {new_total} sits at the top edge of the band).")
