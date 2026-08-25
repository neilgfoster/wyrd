# One exchange, played by hand

Spec FR-13. The engine has been playtested once, and that session corrected the resolution mechanic
three times inside two rolls, none of it visible on paper. This is the drafted sequencing rules run
end to end before they were settled — a ranged opening, a closing to engagement, and an attempt to
flee.

Every roll below is a real `d100`, drawn in order from a seeded sequence and used as it fell. **No
roll was rerolled and no outcome was adjusted.** Three of the rules changed because of what
happened, and those changes are recorded at the bottom rather than quietly folded in.

## The parties

| | Skills | Stamina | Armour |
|---|---|---|---|
| **The scout** (the player's character) | bow 40%, blade 45% | 6 | modest (`1d6`) |
| **The companion** | blade 35% | 6 | light (`1d3`) |
| **First traveller** | spear 35% | 6 | light (`1d3`) |
| **Second traveller** | spear 35% | 6 | light (`1d3`) |

Weapon damage is taken as `1d6`, since the engine has no weapon damage table yet — that belongs to
Stage 6 and equipment, not here. The assumption is stated because it affects the numbers below and
nothing else.

**The situation.** The scout and the companion see two travellers crossing a ford before they are
seen themselves, and the scout has time to nock an arrow.

**Turn order.** The scout's side started the exchange, so it acts first. The travellers do not know
the exchange has started, so they are **surprised** — and the arrow was nocked deliberately, so this
is an **ambush**, easing the first round's attacks by +20.

---

## Round 1 — the surprised side does not act

**The scout shoots the first traveller.** Bow 40, ambush +20 → **60%**. She is not engaged, so no
penalty for shooting. Rolls **9** — a success, and six degrees. Units digit 9: **Fair Omen**.

The traveller defends: rolls **35** against 35 — a bare success, zero degrees. Six degrees against
zero is a margin of six, past the telling blow's three, so **damage doubles**.

Damage `1d6` → **5**, doubled to **10**. Light armour `1d3` → **1**. Nine points through, against
Stamina 6: **out of action, three below zero**. Nothing resolves now; the Aftermath roll waits for
the end of the fight.

The Fair Omen is spent on the second traveller losing his footing on the wet stones.

**The companion closes to engagement** with the second traveller. Closing is his action for the
round; he does not attack.

**The travellers do not act.** They are surprised, and a surprised side loses its whole round.

## Round 2

**The scout shoots the second traveller**, who is now engaged with the companion. Bow 40, one rung
harder for shooting into a close engagement → **30%**. Rolls **44** — a miss. Units 4: nothing.

**The companion attacks.** Blade 35, rolls **55** — a miss. Units 5: nothing.

**The second traveller attacks the companion.** Spear 35, rolls **10** — a success, two degrees. The
companion defends: rolls **1** — a success, three degrees. Three beats two: **defended**.

## Round 3

**The scout shoots.** 30%, rolls **25** — a success, two degrees. Units 5: nothing. The traveller
defends: rolls **36** against 35 — a failure, so there is nothing to compare and the shot lands.

Damage `1d6` → **2**. Light armour `1d3` → **3**. The armour beats the damage, but **a minimum of 1
always gets through**. Traveller at **5**.

**The companion attacks.** Rolls **13** — success, two degrees. The traveller defends with **7** —
success, three degrees. **Defended** again.

**The traveller attacks.** Rolls **45** — a miss.

## Round 4

**The scout shoots.** Rolls **87** — a miss.

**The companion attacks.** Rolls **29** — success, one degree. The traveller defends with **98** — a
failure. The blade lands: `1d6` → **4**, armour `1d3` → **1**, three through. Traveller at **2**.

**The traveller attacks.** Rolls **33** — success, zero degrees. The companion defends with **23** —
success, one degree. **Defended**.

## Round 5 — the traveller runs

Two Stamina left against two opponents, one of them holding a bow. He breaks off.

**Breaking engagement costs a parting blow.** The companion attacks him free as he goes: rolls
**91** — a miss. He gets clear untouched, which is luck rather than the rule being soft.

**Getting away** is a group test — a party of one, so it is his own skill. The pursuit sets the
difficulty: **Challenging (−10)** for a fresh pursuer, and there are two of them, one with a bow, so
one rung harder again → **Difficult (−20)**. Spear-and-legs 35 − 20 = **15%**. Rolls **12** — a
success. He is away into the trees.

The fight ends in **five rounds**, with one traveller out of action and one gone.

## Checked against the computation

`check_sequencing.py` puts an even fight at these skills at **6.3 rounds**, and a fight where one
side is meaningfully ahead at around **5**. Five rounds, in a fight decided by an ambush and ended
by a flight, sits where the script says it should. Nothing in the play contradicted the model.

The free round did what the numbers said it does: it was **decisive but not deciding**. It removed
one of two opponents outright — and even so, the second traveller was never in real danger of being
caught, and the remaining four rounds were mostly misses.

## What the play changed

Three things were not in the drafted rules, and all three were discovered by needing them.

**1. A surprised combatant still defends.** In round 1 the first traveller is surprised, and "does
not act" could reasonably mean he cannot defend either. That reading would roughly double what
surprise is worth and would contradict `check_sequencing.py`, which models the surprised side as
defending normally. **The rule now says it explicitly**: a surprised combatant takes no turn, and
defends as usual. Without that sentence it would have been answered differently every session.

**2. Shooting into a close engagement needed a rule.** In round 2 the scout shoots at a traveller
her own companion is fighting, and nothing said whether that was harder, forbidden, or free. **The
rule now makes it one rung harder, and an Ill Omen means the ally is hit instead.** This was the
clearest gap the play found: the situation arises immediately and constantly, and it is not the kind
of thing a GM should be inventing mid-fight.

**3. The flight difficulty needed a stated ladder.** In round 5 the escaping traveller needs a
difficulty, and picking one was a judgement call — exactly what FR-2 exists to remove. **The rule
now sets it: Challenging by default, one rung harder for each pursuer past the first.**

None of the three was visible while the rules were being written. All three were unavoidable within
five rounds of playing them.
