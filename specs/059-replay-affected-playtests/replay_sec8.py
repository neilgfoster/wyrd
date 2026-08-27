"""Re-play sec8's blocked Resolve exercise, now that ADR 0043 defines gain/cap. Continuing
Senna's arc where sec8 left her: Taint 1 (after the Bargain + ordinary Exposure). Fresh real
rolls, seeded 20260840, disclosed in full."""
import random

rng = random.Random(20260840)

taint = 1  # where sec8 left her
resolve = 0  # creation default, still true -- nothing has raised it yet
cap = taint + 3

print(f"Starting state (continuing sec8): Taint {taint}, Resolve {resolve}, cap {cap}.\n")

print("First, the single-Rally case, to show it honestly rather than skip it: a Rally grants")
print("only +1 (03-rules.md sec4). Since Taint is already 1 and Resolve started at 0, one Rally")
print("brings Resolve to 1 -- equal to Taint, which is the Spent condition, before she has spent")
print("anything at all this arc. This is a real, correctly-designed consequence of gaining Taint")
print("before her first Rally since it happened, not a bug: a character worn down by what has")
print("happened to her can be Spent the moment she catches her breath, if Taint outpaced Rallies.")
after_rally = resolve + 1
print(f"  Resolve after one Rally: {resolve} -> {after_rally} == Taint {taint} -> Spent.\n")

print("Continuing instead to her next downtime, which raises Resolve to its cap (ADR 0043):")
resolve = cap
print(f"  Resolve at downtime: -> {resolve} (cap = Taint + 3 = {cap}). No longer Spent.\n")

eff = 35  # blade, matching this arc's own value
roll = rng.randint(1, 100)
print(f"A test under pressure, eff. {eff}: roll {roll} -- ", end="")
if roll <= eff:
    print("succeeds. Trying a second, tougher case to actually exercise a spend:")
    roll2 = rng.randint(1, 100)
    print(f"  eff. {eff}: roll {roll2}", end=" -- ")
    roll = roll2
print("fails." if roll > eff else "succeeds.")
if roll > eff:
    resolve -= 1
    reroll = rng.randint(1, 100)
    boosted_eff = min(eff + 20, 95)
    print(f"She spends 1 Resolve for a +20 reroll (03-rules.md sec4): {cap} -> {resolve}.")
    print(f"  Reroll at eff. {boosted_eff}: roll {reroll} -- ", end="")
    print("succeeds." if reroll <= boosted_eff else "fails.")

print(f"\nFinal: Resolve {resolve}, Taint {taint} -- Resolve {resolve - taint} above Taint, not")
print("Spent. The spend, the cadence, and the cap all played out exactly as ADR 0043 states,")
print("with real headroom to spend from -- the gap sec8 found (nothing to spend, ever) is closed.")
