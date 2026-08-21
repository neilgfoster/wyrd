# Wyrd — the ruleset

the chassis system! as the chassis, with the four the source line subsystems fitted, an AGE-derived dice
read, and another source system's Hope/Shadow balance. Sources:

---

## 1. Resolution

> **Roll `d100` and succeed if the result is at or under your `skill%`.**
> - **Success Levels (SL)** — tens digit of the skill minus tens digit of the roll — give
>   magnitude.
> - **The units digit of the natural roll** is the **Wyrd die**: what else happened.

One roll, three independent axes, no extra dice. See
[ADR 0001](adr/0001-d100-resolution.md).

### Skill percentages

the chassis system's ladder converts with **no probability drift at all**: `skill% = (skill + 1) × 5`.

| the chassis system skill | Wyrd |
|---|---|
| 4 *(untrained)* | 25% |
| 6 *(starting career)* | 35% |
| 10 *(career cap)* | 55% |
| 12 *(career cap)* | 65% |

the base source system and a science-fiction source system stat blocks are read **as printed** — `WS 41` *is* 41%. See
[ADR 0002](adr/0002-source-system-compatibility.md).

### Difficulty

2e's six bands, replacing the chassis system's two:

| Band | Modifier |
|---|---|
| Easy | +20 |
| Average | +0 |
| Challenging | −10 |
| Difficult | −20 |
| Hard | −30 |
| Very Hard | −40 |

**Modifiers apply to the skill, never to the roll.** This is what keeps the Wyrd die clean.

### Opposed tests

Both roll; **higher SL wins**. Both failing means both fail. Ties go to the defender.

### The Wyrd die

Read from the **units digit of the natural roll**:

| Units | Result |
|---|---|
| 0 | **Chaos Star** — something goes wrong in a the corrupting power-flavoured way |
| 9 | **Comet** — a significant break in the player's favour |
| 1–8 | nothing |

20% frequency. Widen to `0–1` / `8–9` (adding Bane and Boon at 40%) via `houserules.yaml` if
play proves it too sparse.

The units digit is uniform within both the success and the failure set — exactly uniform at
any skill that is a multiple of 10, never more than 2 points off otherwise. That is better
independence than any scheme with separate dice achieved.

#### The natural roll rule

**The Wyrd die is read from the dice as they first fell. Never modified. Never rerolled.**

- **Fortune** buys the *result*, never the world's reaction to the first attempt. Reroll a
  failure into a success and the Chaos Star you already rolled still lands.
- **The Dark Deal** is therefore not a clean trade: pay corruption, try again, and live with
  what the first attempt set in motion.

> You can change what happened. You cannot change what it cost.

### Corruption bends the die

| Corruption | Chaos Star on units |
|---|---|
| 0–2 | 0 |
| 3–5 | 0–1 |
| 6+ | 0–2 |

The world goes wrong around you more often as you rot; your competence is untouched.

### Luck

the chassis system's Luck, unchanged in function: a percentage the player *may choose* to test to dodge
a misfortune or break a tie. **Testing Luck costs 1 Luck for the rest of the adventure, pass
or fail.** Always the player's choice.

## 2. Combat

the chassis system's model, unchanged, because it already delivers grim lethality with no map.

- Attacks are opposed rolls. The winner rolls the weapon's damage dice.
- **Stamina is not meat** — it is cuts, bruises, and losing control of the fight.
- **Armour subtracts dice:** light `1d3`, modest `1d6`, heavy `2d6`; shield raises one rank.
  Minimum 1 stamina always gets through.
- **Mighty strike:** beat the defender by more than 3× → double stamina loss.
- **Critical hit** when damage takes a combatant **below 0 stamina**. Roll
  `1d6 + total negative stamina` on the table for the damage type
  (slashing / piercing / crushing / blast). `10+` is death.
- Weapons are **casual** or **martial**; martial weapons are illegal in most civilised
  places and mark the bearer. This social constraint does real work — keep it.

### Mobs — the Fray die

One PC plus companions cannot resolve six thugs one roll at a time. Adopt a solo source system'
**Fray die**: each round, in addition to their action, a character automatically cuts down
petty enemies weaker than themselves. Companions get a smaller one. Named enemies are never
affected.

### Death is deferred

**Nothing resolves a character's fate during the fight.** When a combatant drops, they are
*out of action*. After the encounter, roll on the **Aftermath table** — a skirmish source's D66,
reskinned:

| Band | Result |
|---|---|
| ~14% | **Dead** |
| ~42% | **Full recovery** |
| remainder | A lasting mark |

The lasting marks are the point, and most generate story rather than a penalty: a permanent
wound; **Bitter Enmity** (you now hate a named individual, their leader, or their whole
faction); **Captured** (ransom, exchange, sale, sacrifice — a hook, not an ending);
**Old Battle Wound** (roll before every future fight forever; on a 1 you cannot fight);
**Horrible Scars** (you now cause Fear); **Hardened** (immune to Fear); **Robbed**.

Deferred resolution is how a single-PC chronicle survives genuinely lethal combat. It
complements Fate points rather than competing with them.

---

## 3. Fate and Fortune

the chassis system has no death valve. A multi-year chronicle cannot lose three years to one damage
roll. the base source system's two-tier design, adopted directly:

- **Fate points** — few, permanent, spent to **avoid death**. Lost forever when spent; new
  ones are rare rewards.
- **Fortune points** — renewable each day, equal to the Fate score. Spend to reroll a failed
  test, gain an extra parry or dodge, or act sooner.

**When a Fate point is spent**, Claude invents the escape — and per 2e's own guidance, the
character **survives and is not better off**. The blow was the flat of the blade; everything
goes black; you wake hours later tended by companions, or imprisoned, or stripped and left
for dead in the forest.

Claude *chooses where they wake*. That makes Fate the campaign's course-correction tool as
well as its anti-frustration valve.

---

## 4. Hope and Shadow

another source system's balance, replacing the source system's one-way corruption ratchet.

- **Hope** — spendable, renewable. Spend for a bonus after a failed roll. Recovered in
  downtime and through companions.
- **Corruption** *(called Shadow in engine terms)* — accrues and sticks.

**When Hope falls to equal Corruption, the character is Beset** (another source system's *Miserable*). At
Hope 0 they are spent — they will not press any struggle and will withdraw from danger.
A character with Corruption 0 can never be Beset however exhausted they are.

This means the same Corruption score means different things at different times, and
recovery is part of the loop rather than an afterthought.

### Gaining Corruption

Three routes, deliberately covering both directions:

1. **Dark Deal** *(4e)* — you failed a test that mattered and have no Fortune left. You may
   **choose** to take 1 Corruption to reroll it. **Always the player's choice**; Claude may
   mention the option exists, never apply it.
2. **Exposure** — resist with a test; tiers from 4e:

   | Exposure | Fail | Marginal | Success |
   |---|---|---|---|
   | Minor | 1 | — | 0 |
   | Moderate | 2 | 1 | 0 |
   | Major | 3 | 2 | 1 |

   Minor: witnessing a lesser daemon, contact with a mutant or tainted matter, **giving in to
   despair, rage or excess**. Moderate: contact with a daemon or profane artefact,
   *embracing* those impulses. Major: making a deal with a daemon, consuming tainted matter.

   Note how many are moral rather than supernatural. That is the setting's thesis.
3. **GM Invocation** *(3e)* — before a roll, Claude may **spend one of the character's
   Corruption points** to add a penalty, narrating how the taint surfaces: temptation,
   cramps, whispered voices only they hear. Max one per check. It *consumes* the point, so
   it cannot be leaned on.

Together these make corruption a live presence rather than a number that matters only at
thresholds.

### Corruption Weakness

Following another source system, corruption is **specific, not generic**. Each character has a Weakness
derived at creation from their **Passion** and **Cruel Misfortune** (both the chassis system
Compendium 2). The labourer who took the trade to feed his family falls differently from
the scholar who wanted to know what was in the book. The Weakness names the path.

### Mutation and the doom clock

Crossing the Corruption threshold forces a **mutation** (body) or a **derangement** (mind).
The result consumes Corruption equal to its severity, dropping the character back below
threshold; if still over, roll again.

On the **first** mutation, the engine **secretly rolls `1d10 + Toughness`** — the number of
mutations this character can endure before they are lost. **The player never sees it.**
Written to state once, so every later mutation is narrated against a real countdown.

When the clock runs out the character is **damned** — and becomes an NPC that Claude
controls. They do not leave the chronicle; they join the opposition.

Mutations carry **Fear points** — corruption's cost is social as well as mechanical. The
mutant's problem is being seen.

---

## 5. Insanity, Fear and Stress

Three tiers of mental harm, distinguished by how long they last.

- **Stress** *(3e)* — short-term. Gained from failed mental tests, horror, exhaustion.
  Recovered at a Rally (see [`04-session.md`](04-session.md)). The bad night that mostly
  clears by morning.
- **Insanity points** *(2e)* — long-term and sticky. **1 per critical hit taken** (the
  trigger already exists in the chassis system's combat), 1 per failed Terror test, more at Claude's
  discretion for genuinely terrible events.
- **Derangements** — permanent. At **6+ Insanity**, test Willpower on every further point
  gained; on a failure take a derangement and **lose 6 Insanity**. The track sawtooths, so a
  character can be broken many times across years.

**Fear and Terror tests** are the connective tissue the chassis system lacks entirely: Fear makes you
unable to press an attack; Terror routs you and costs an Insanity point on a failure.

In the world, insanity is believed to be the corrupting power working on the mind — "a mutation on the
inside". The mad are feared, not pitied.

---

## 6. Experience and advancement

The governing constraint is principle 6 ([`01-principles.md`](01-principles.md)):
**power stays flat; what grows is knowledge and position.** A veteran and a novice die to the
same crossbow bolt. Advancement must therefore be mostly *lateral* — and over a decade, the
things that actually accumulate are not on the character sheet at all.

### Advances are the currency

**1–3 advances per session**, awarded against **triggers**, never an XP total. Triggers are
checkable, so the engine can verify an award rather than the GM being generous by accident
([`07-tooling.md`](07-tooling.md)).

| Trigger | Awarded when |
|---|---|
| **Learned** | you discovered something true about the world you did not know |
| **Drove** | you acted on a drive or passion **even though it cost you** |
| **Practised** | you met your career's own condition (each career declares one or two) |
| **Endured** | you survived something that should have finished you |

At most one of each per session, so a session caps at four and typically pays two.

### Spending them

| Cost | Buys |
|---|---|
| 1 | **+5%** to a skill your current career grants, up to that career's cap |
| 1 | **open** a new skill your career grants, at 25% |
| 1 | **change career**, to any legal exit, given a fictional reason |

That is the entire economy. No talent trees, no feats, no purchasable abilities — those are
the drift risk identified in [ADR 0002](adr/0002-source-system-compatibility.md), and their
absence is deliberate.

### Careers, and why changing them is the real progression

Careers form a **directed graph**: each declares its `entries` and `exits`
([`14-entities.md`](14-entities.md)). You may only move to a legal exit, so your career
history is a biography rather than a shopping list — and the engine cannot hand out a career
that your actual past does not permit.

Changing career is cheap (1 advance) but requires a **fictional reason**: something must have
happened that makes it make sense. The graph constrains *what* you can become; the fiction
constrains *when*.

**Completing a career** — bringing every skill it grants to its cap — is the only thing that
makes you durably tougher:

- **+1 maximum Stamina**, permanently
- a **Mark**: one small, lasting benefit that persists across every later career

Marks are the reward for depth over breadth, and they are the only permanent mechanical
accumulation in the game. Three completed careers across ten years is +3 Stamina and three
Marks. That is the whole power curve.

### What actually grows

Over a long chronicle these dominate, and none of them improve a die roll:

| | |
|---|---|
| **Reputation** | a score with a *label* that changes with recent deeds. The engine rolls it when you meet someone; passing means **recognised**, which may or may not help. Notoriety is a threat vector, not a reward. |
| **Allegiances** | which organisations claim you, and at what depth |
| **Holdings** | what you own, and therefore what can be taken |
| **Knowledge** | threads closed, entities discovered, connections mapped |
| **Bonds** | who trusts you, and who will not be in a room with you |

This is the mechanical expression of *"what accumulates is what you know and what it cost."*
A character ten years in is not harder to kill. They are harder to *replace*.

### Companions

Companions advance rarely and simply: at a Fellowship phase, one companion may gain a single
competence or lose a limitation. They have no career graph and no Marks — consistent with
their deliberately thin mechanical layer ([`04-session.md`](04-session.md)).

### Succession

A successor inherits **none** of the competence and **all** of the position — reputation,
allegiances, holdings, open threads, and enemies ([`05-campaign.md`](05-campaign.md)).
They start with their own advances at zero. The chronicle keeps its weight; the character
does not.

---

## 7. Danger scaling

Content is written once with a **danger rating** used as a multiplier inside the
content (a solo source system): a trap written `Nd4` does `6d4` at danger 6; enemy counts and
skill values scale from it.

This is how a chronicle stays interesting for years **without escalating the fiction**. The
same village mystery runs in year one or year eight. Danger scales; scope need not. It is
the mechanical expression of constraint 6.

---

## 8. The the science-fiction line overlay

The same engine with different data, plus one rules overlay:

- Careers → the science-fiction line careers (a science-fiction source system supplies the list)
- casual/martial → civilian/military; the social constraint is *stronger* in the the science-fiction setting
- The existing **blast** critical table covers energy weapons
- Magic → psychic powers; **Wrath of the Otherworld becomes Perils of the Warp with no
  structural change** — reskin the miscast table, keep the mechanism
- Corruption stays exactly as-is; only its vocabulary changes
- the chassis system Compendium 2's firearms rules (Readiness / Misfire / Boom!) port directly

Fantasy first. The overlay is a data exercise once the engine is proven.
