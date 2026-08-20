# WFRP — the mechanics Wyrd needs

Notes on the four subsystems Warlock! lacks: **Fate**, **Insanity**, **Corruption**, and
**Fear/Terror**. Sourced from WFRP 2e core, WFRP 4e core, and *Tome of Corruption* (2e).
See [warlock-rules.md](warlock-rules.md) for the base system.

Mechanics summarised for implementation. Not a substitute for the books.

## 1. Fate points — the death valve (2e)

**The most important addition for Wyrd.** A single-PC chronicle cannot lose three years to
one damage roll.

Two tiers, and the split matters:

- **Fate points** — permanent, spent to **avoid certain death** (combat, traps, poison,
  disease, anything). Lost permanently when spent; new ones granted only as rewards for
  heroic action. May also be spent to avoid maiming.
- **Fortune points** — renewable. You get a number each day equal to your Fate
  characteristic. Spend for: reroll a failed test, an extra parry/dodge, +1d10 initiative,
  an extra half action.

**The GM's job when a Fate point is spent** is to invent the escape — and 2e is unusually
direct about doing it *right*:

> "You should be careful to ensure that the character is not too much better off as a
> result of expending a Fate Point. The character should survive the situation, but
> that's it."

It gives a worked example of the **wrong** way (ignore the critical, character still at 0
Wounds, burns three Fate points in three rounds and dies anyway) and the right way: the
blow was the flat of the blade, everything goes black, and you wake hours later — tended
by your comrades, or imprisoned in the mutants' lair, or stripped of everything and left
for dead in the forest.

That last point is a **narrative repair tool**, and 2e says so outright: "You, the GM,
control when and where characters wake up, and you can use this to your advantage" — if
the players missed a vital clue, they wake in a village where someone mentions the black
tower beyond the wood.

For Wyrd this is doubly valuable: it is both the anti-frustration valve *and* a legitimate
way to get a drifting solo campaign back onto a thread.

## 2. Insanity (2e)

A points track, not a state.

**Gaining Insanity Points (IP):**
- **1 IP per Critical Hit taken.** Permanent, survives the injury healing.
- **1 IP per failed Terror test.**
- GM discretion for terrible events — being tortured, trapped in the dark with rats,
  failing to save a loved one, meeting a Daemon, "stumbling across the disturbing
  iconography of Chaos."

For discretionary gains the GM sets the stake first, then the character makes a Will Power
test; pass = no points, fail = the stated number. Guidance: a set number (rarely above 6),
or 1 per degree of failure, or `1d10/2` for most situations — `1d10` only for the direst.

**The break:** at **6+ IP**, make a Will Power test immediately, and again on every further
IP gained. On a failure the character **develops a disorder and loses 6 IP**. So the track
sawtooths — you can be broken many times over a long campaign.

There are 20 named disorders (The Beast Within, Blasphemous Rage, Heart of Despair, Knives
of Memory, Terrible Thirstings, Venomous Thoughts…).

**Setting note that earns its place:** in the Old World insanity is believed to be caused
by Chaos — "just as it can mutate the body, so too can it twist the mind and spirit.
Therefore, insanity is seen by many as just a mutation on the inside." A vocal minority
say it is daemonic possession. Which is why the mad are treated with fear, not pity.

**Why this fits Warlock! exactly:** Warlock already resolves serious injury as a critical
hit. `1 Insanity per critical` bolts on with zero new bookkeeping — the trigger already
exists in the base system.

## 3. Corruption

### 4e version — cleanest, and the one to base Wyrd on

Two routes in:

**Dark Deals.** You failed an important test and have no Fortune left. You may
**purposefully choose to take a Corruption point to reroll it** — even a test already
rerolled. Explicitly "always a choice for you, not the GM," though the GM may gently
remind you the option exists.

*This is the best mechanic found in any of these books for Wyrd's purposes.* It is the
whole theme — desperation, expedience, the slow sale of the soul — as a single player-side
decision. It works solo because it needs no group to pressure you; the pressure is the
situation.

**Corrupting Influences.** Resist with a Challenging Endurance test (physical) or Cool
test (spiritual), GM's call which. Three tiers:

| Exposure | Fail | Marginal (0–1) | Success | Impressive (4+) |
|---|---|---|---|---|
| Minor | 1 CP | — | 0 | — |
| Moderate | 2 CP | 1 CP | 0 (2+) | — |
| Major | 3 CP | 2 CP | 1 CP (2–3) | 0 |

- **Minor:** witness a lesser daemon; contact with a mutant or refined warpstone; *giving
  in to despair, rage, excess, or the need to change your lot*; prolonged exposure to
  cultists, Skaven, mutant lairs.
- **Moderate:** witness multiple daemons; contact with a daemon or profane artefact;
  *embracing* despair/rage/excess; brief exposure to an environment steeped in Dhar.
- **Major:** witness a greater daemon; making a deal with a daemon; consuming refined
  warpstone; prolonged exposure to dhar.

Note how many entries are **moral, not supernatural**. Giving in to despair corrupts you.
That is the setting's actual thesis and it is doing real work mechanically.

**Mutating.** On crossing the threshold: lose Corruption equal to Willpower Bonus, roll to
see whether **body or mind** blossoms (race-weighted — Elves *always* mind, Dwarfs almost
always mind, Humans roughly even), then roll on the Physical or Mental Corruption table.

**The end:** more mutations than your Toughness Bonus, or more mental corruptions than your
Willpower Bonus, and you are **damned — the character becomes an NPC controlled by the GM**,
"meaning you may well see the wretched creature again."

That last clause is excellent for a long chronicle: your fallen character doesn't leave the
story, it joins the opposition.

### 2e / Tome of Corruption — the parts worth keeping

**Corrupted Environments** — a *location* property, which suits Wyrd's state model since
locations are tracked anyway. Each area has a Corruption Value:

| CV | Exposure frequency | Test difficulty | Effect | Magic |
|---|---|---|---|---|
| None | never | — | none | normal |
| Faint | 1/year | Routine (+10%) | disturbing sensations only | normal |
| Mild | 1/month | Average (+0%) | roll once on Mutations | normal |
| Moderate | 1/week | Challenging (−10%) | roll once | +1 die |
| Major | 1/day | Hard (−20%) | roll once | +1 die |
| Severe | 1/hour | Very Hard (−30%) | roll **twice** | +2 dice |

**The mutation ratchet.** Once you have one mutation you are at risk of more: when
Morrslieb is next full (`3d10` days), test Toughness or gain another — and keep testing
each full moon until you pass. Tie it to the calendar and it becomes a recurring dread beat
that arrives on its own schedule.

**The secret doom clock.** On gaining a first mutation the **GM secretly rolls
`1d10 + Toughness Bonus`** — the maximum mutations that character can endure before
becoming Chaos Spawn. The player never learns the number.

This is ideal for an LLM GM: it is a hidden, deterministic value written to state at the
moment of first corruption, and every subsequent mutation can be narrated against a real
countdown rather than an improvised sense of doom.

**Fear Points.** Mutations make you horrifying to others — 1 point Menacing, 2 Unsettling,
5+ Frightening, 10+ Terrifying, cumulative across mutations. Corruption therefore carries
a *social* cost, not just a mechanical one; the mutant's problem is being seen.

**Framing:** *Tome of Corruption* notes that for most campaigns "gaining mutations is
utterly unthinkable." Corruption is an opt-in dark road, not an ambient tax.

## 4. Fear and Terror

Warlock! has no fear rules at all — `Fear` exists only as a spell. WFRP's Terror test is
the natural trigger for Insanity (1 IP per failure) and the mechanism by which the undead
and daemonic feel categorically different from a man with a knife. Wyrd needs a
Fear/Terror test; it is the connective tissue between the bestiary and the Insanity track.

## Synthesis for Wyrd

The four subsystems interlock cleanly on the Warlock! chassis:

- **Critical hit** (already in Warlock) → **1 Insanity point**
- **Failed Terror test** → **1 Insanity point**
- **6+ Insanity** → Willpower test → disorder, reset by 6
- **Failed test you can't afford** → optional **Dark Deal** → 1 Corruption point, reroll
- **Exposure to taint** → resist test → 1–3 Corruption by tier
- **Corruption threshold** → mutation (body or mind) → **Fear points** → social consequence
- **First mutation** → GM secretly rolls the doom clock (`1d10 + Toughness Bonus`)
- **Death** → optionally spend a **Fate point** → survive, worse off, GM chooses where you
  wake — which is also the campaign's course-correction tool

Every trigger is an event the engine already has to notice. Nothing here requires tracking
state the GM wasn't tracking anyway.
