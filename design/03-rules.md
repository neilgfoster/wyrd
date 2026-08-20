# Wyrd — the ruleset

Warlock! as the chassis, with the four Warhammer subsystems fitted, an AGE-derived dice
read, and TOR's Hope/Shadow balance. Sources:
[warlock-rules](../reference/warlock-rules.md) ·
[wfrp-mechanics](../reference/wfrp-mechanics.md) ·
[wfrp3-concepts](../reference/wfrp3-concepts.md) ·
[tor-concepts](../reference/tor-concepts.md) ·
[dice-design](../reference/dice-design.md) ·
[systems-mined](../reference/systems-mined.md)

---

## 1. Resolution

> **Roll 3d6 + skill vs 20.** One die is the **Wyrd die**, a different colour.
> - **The total** decides success or failure.
> - **Doubles** (any two dice matching) decide *whether something else happened*.
> - **The Wyrd die** decides *what kind*.

`3d6` has the same mean as `d20` (10.5), so **Warlock's target of 20 and every skill value
in its books carry over unchanged** — but the curve tightens, so competence tells and
extremes are rare.

**Difficulty:** a penalty of **2** (difficult) or **4** (very difficult) to skill. That is
the whole difficulty system, as in Warlock.

**Opposed:** both roll `3d6 + skill`; higher total wins. Ties go to the defender.

### The Wyrd die

Read **only when doubles are rolled** (44.4% of rolls):

| Wyrd die | Result |
|---|---|
| 1 | **Chaos Star** — something goes wrong in a Chaos-flavoured way |
| 2 | **Bane** — a complication |
| 3–4 | **Twist** — a detail, no mechanical weight |
| 5 | **Boon** — an advantage |
| 6 | **Comet** — a significant break in the player's favour |

Because doubles are orthogonal to the total, *every* combination is reachable: a success
carrying a Chaos Star, a failure carrying a Comet. Rare, but never impossible — which is
what margin-based systems get wrong.

**Magnitude**, when it matters, is the doubled value (as AGE's stunt points). Banes and
boons should draw from a costed menu per the AGE model rather than being invented freely —
see `engine/tables/`.

### Corruption bends the die

Following TOR's Eye-of-Sauron rule, the threat is **gated by state**, not by the roll:

| Corruption | Chaos Star on |
|---|---|
| 0–2 | 1 |
| 3–5 | 1–2 |
| 6+ | 1–3 |

The world goes wrong around you more often as you rot, and your competence is untouched.

### Luck

Warlock's Luck, unchanged: a score the player *may choose* to test to dodge a misfortune or
break a tie. **Testing Luck costs 1 Luck for the rest of the adventure, pass or fail.**
Always the player's choice.

---

## 2. Combat

Warlock's model, unchanged, because it already delivers grim lethality with no map.

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

One PC plus companions cannot resolve six thugs one roll at a time. Adopt Scarlet Heroes'
**Fray die**: each round, in addition to their action, a character automatically cuts down
petty enemies weaker than themselves. Companions get a smaller one. Named enemies are never
affected.

### Death is deferred

**Nothing resolves a character's fate during the fight.** When a combatant drops, they are
*out of action*. After the encounter, roll on the **Aftermath table** — Mordheim's D66,
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

Warlock has no death valve. A multi-year chronicle cannot lose three years to one damage
roll. WFRP 2e's two-tier design, adopted directly:

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

TOR's balance, replacing WFRP's one-way corruption ratchet.

- **Hope** — spendable, renewable. Spend for a bonus after a failed roll. Recovered in
  downtime and through companions.
- **Corruption** *(called Shadow in engine terms)* — accrues and sticks.

**When Hope falls to equal Corruption, the character is Beset** (TOR's *Miserable*). At
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

   Minor: witnessing a lesser daemon, contact with a mutant or warpstone, **giving in to
   despair, rage or excess**. Moderate: contact with a daemon or profane artefact,
   *embracing* those impulses. Major: making a deal with a daemon, consuming warpstone.

   Note how many are moral rather than supernatural. That is the setting's thesis.
3. **GM Invocation** *(3e)* — before a roll, Claude may **spend one of the character's
   Corruption points** to add a penalty, narrating how the taint surfaces: temptation,
   cramps, whispered voices only they hear. Max one per check. It *consumes* the point, so
   it cannot be leaned on.

Together these make corruption a live presence rather than a number that matters only at
thresholds.

### Corruption Weakness

Following TOR, corruption is **specific, not generic**. Each character has a Weakness
derived at creation from their **Passion** and **Cruel Misfortune** (both Warlock
Compendium 2). The rat-catcher who took the trade to feed his family falls differently from
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
  trigger already exists in Warlock's combat), 1 per failed Terror test, more at Claude's
  discretion for genuinely terrible events.
- **Derangements** — permanent. At **6+ Insanity**, test Willpower on every further point
  gained; on a failure take a derangement and **lose 6 Insanity**. The track sawtooths, so a
  character can be broken many times across years.

**Fear and Terror tests** are the connective tissue Warlock lacks entirely: Fear makes you
unable to press an attack; Terror routs you and costs an Insanity point on a failure.

In the Old World, insanity is believed to be Chaos working on the mind — "a mutation on the
inside". The mad are feared, not pitied.

---

## 6. Advancement

Warlock's, because it is already the flat curve the setting requires.

- 1–3 advances per session.
- An advance raises **one skill in the current career only**, to that career's cap.
- **Career skill** = the *lowest* skill in the career, so it creeps.
- **Max Stamina +1** only when the career skill rises. This is the *only* durability growth.
- Real progression is **changing careers** — different access and standing, not more power.

**Advance triggers** (Warlock Compendium 2) rather than XP: one for learning something new,
one for **following your Passion even when it cost you**, and one per career-specific
condition ("mark an advance when you stir people up against authority"). Checkable, so
Claude cannot be generous by accident.

**Reputation** is a score with a *label* that changes with recent deeds — `reputation 7
(swindler)`. Claude rolls it when the character meets someone; passing means recognised,
"which may or may not be beneficial". Notoriety is a threat vector, not a reward.

---

## 7. Scenario scaling

Scenarios are written once with a **Threat rating `T`** used as a multiplier inside the
content (Scarlet Heroes): a trap doing `Td4` does `6d4` in a T6 scenario; enemy counts and
skill values scale from it.

This is how a chronicle stays interesting for years **without escalating the fiction**. The
same village mystery runs in year one or year eight. Danger scales; scope need not. It is
the mechanical expression of constraint 6.

---

## 8. The 40k overlay

The same engine with different data, plus one rules overlay:

- Careers → 40k careers (Dark Heresy supplies the list)
- casual/martial → civilian/military; the social constraint is *stronger* in the Imperium
- The existing **blast** critical table covers energy weapons
- Magic → psychic powers; **Wrath of the Otherworld becomes Perils of the Warp with no
  structural change** — reskin the miscast table, keep the mechanism
- Corruption stays exactly as-is; only its vocabulary changes
- Warlock Compendium 2's firearms rules (Readiness / Misfire / Boom!) port directly

Fantasy first. The overlay is a data exercise once the engine is proven.
