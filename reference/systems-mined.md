# Systems mined — findings from the reading list

Worked through the reading order in [library-triage.md](library-triage.md). Mechanics
summarised for implementation; not a substitute for the books.

---

## 1. Dragon Age / AGE — the stunt system

**Confirmed as read.** `3d6 + ability vs TN`, one die (the **Dragon Die**) a different
colour.

> "If you make a successful attack roll and get **doubles on any of the dice**, you can
> perform one or more stunts in addition to dealing your normal damage. You receive a number
> of **stunt points (SP) equal to the Dragon Die** and must use them right away."

Stunts are bought from a **costed menu**, once each per round, and then — importantly —
**the player narrates how they pulled it off**. Worked example from the book: dice read
3, 5, 5 with a 5 as the Dragon Die, total 18; hit, doubles, so 5 SP, spent as
skirmish (1) + skirmish (1) + lightning attack (3).

Sample costs: Rapid Reload 1 · Knock Prone 2 · Disarm 2 · Mighty Blow 2 (extra 1d6) ·
Pierce Armour 2 (halve armour) · Lightning Attack 3 (second attack) · Dual Strike 4 ·
Seize the Initiative 4. Parallel menus exist for **spell stunts**, and later sets add
roleplaying and exploration stunts.

Anti-cascade rule worth keeping: if a stunt grants another roll and *that* rolls doubles,
**it generates no further SP**.

### The limitation Wyrd must fix

**AGE stunts only trigger on a success.** There is no failure-side stunt, and no bane —
stunts are purely beneficial. So AGE supplies the *trigger* (doubles, orthogonal to the
total) and the *magnitude* (the coloured die), but not the bidirectionality Wyrd needs.
Wyrd's extension — reading direction off the Wyrd die so doubles can produce a bane on a
success or a boon on a failure — is genuinely additional. See [dice-design.md](dice-design.md).

The costed SP menu is a good model for text play: deterministic, checkable, and it turns
"what else happened" into a lookup rather than an invention. The stunt lists are effectively
a pre-written boon table.

---

## 2. Beyond the Wall: *Further Afield* — Threat Packs

**The meta-campaign engine.** Better suited to Wyrd than TOR's authored Tale of Years,
because it *generates* rather than scripts.

### Structure of a Threat Pack

Read *The Blighted Land* in full — the whole thing is one page:

- **Imminence rating** — how active and dangerous the Threat is
- **Threat Effects table** — what happens when it activates, escalating by roll:
  `1` grows stronger (+1 Imminence) · `2` encounter chance permanently rises ·
  `3-6` creeps outward into adjacent hexes · `7` grows one hex in a random direction ·
  `8` all adjacent hexes fall
- **Clues List** — the ordered discovery path: Forgotten Village → Haunted Library → Folk
  Tale → This Blighted One's Story → Blighting Ritual → The Artifact at the Centre
- **Encounters table** (d6)
- **Ambient effects** — while inside the Blight: daily save vs poison or lose 1 HP (those
  who die return as undead), no healing from rest, no safe water
- **Denizens** — stat blocks, including the boss with a weakness (*True Name: +5 against it
  when uttered*) and an immortality clause (*if destroyed, reforms at the artifact*)
- **Counters** — the specific spells/means that can undo it

### How Threats run

**Imminence bands:**

| Rating | Meaning |
|---|---|
| 1-2 | Interacts rarely and randomly — a new bandit group, a dragon that occasionally emerges |
| 3-4 | An active force, a growing cause for concern — a Goblin King raising armies |
| 5-6 | Serious concern for everyone; growing daily, frequently troubling the land |
| 7+ | An almost constant source of trouble, "perhaps spelling its ultimate doom" |

**The weekly roll:** at the start of every in-game week, roll **d12 per Threat**. If the
result is ≤ its Imminence, the Threat activates that week; roll on its effects table.

**The GM chooses when in the week it lands** — while the player is home (a session) or while
they are away (they learn of it later). And explicitly:

> "If a Threat manifests in a way that does not directly involve the characters, make sure
> they know about it... you might have a traveling peddler come to town and tell them about
> the dangers faced by their neighbors."

That is TOR's *News from Afar* mechanised.

### The rule that solves Wyrd's biggest practical problem

> **Abstracting Weekly Threat.** "If the characters are engaging in a long period of
> downtime... simply figure out how often a Threat is likely to come up and then use the
> **expected value**. If the Vengeful Wyrm has an Imminence Rating of 4, then it can be
> expected to activate roughly once every three weeks."

This is exactly how Wyrd should handle real-world gaps between sessions. Don't simulate
every week — take expected value over the elapsed in-game time and generate the resulting
events. Computationally trivial, narratively correct, and it means a three-week absence
produces a world that has genuinely moved.

### Threats are personal from character creation

Every active Threat must have **at least one character with an attached history**. Players
roll on a table tying them to a Threat, taking an ability penalty plus a bonus or skill.
Pairs directly with Warlock's **Cruel Misfortune** and TOR's **Shadow Weakness** — the thing
that threatens the world is already the thing that marked you.

**Library also contains** 5 ready Threat Packs (Blighted Land, Grey Prince, Imperial City,
Vengeful Wyrm, Risen Dead), 4 blank Threat Worksheets, and 10 Scenario Packs.

---

## 3. Crowns 2e — fear and conditions

Lighter than hoped, but two useful things.

**Conditions as the universal currency.** *Panic* and *exhausted* are conditions applied by
failed saves, monster attacks, infection and critical damage — e.g. "if a bloodied character
takes fear-related [damage] gains the panic condition"; "Critical damage: give player panic".
Conditions are tracked on cards.

**Monsters use MOR (morale) in place of all saves** — a single number replacing the whole
save suite for NPCs. That asymmetry is worth copying: Wyrd's NPCs (including companions in
mass scenes) do not need the player's full state model.

The setting framing — humanity has lost the war, scattered refuges in ruin-haunted
wilderness — is tonally right but adds nothing mechanical beyond the above.

---

## 4. Mordheim — the D66 serious injuries chart

**The best single table found for Wyrd's post-combat consequences**, because most results
generate *story* rather than a penalty.

Rolled **after** the battle for any warrior taken out of action:

| D66 | Result |
|---|---|
| 11-15 | **Dead** — body abandoned in the dark alleys, all equipment lost |
| 16-21 | Multiple Injuries — roll D6 more times |
| 22 | Leg Wound — permanent -1 Movement |
| 23 | Arm Wound — 1 in 6 amputated (one-handed weapons only), else miss next game |
| 24 | **Madness** — stupidity or frenzy, permanently |
| 25 | Smashed Leg — may never run again (may still charge) |
| 26 | Chest Wound — permanent -1 Toughness |
| 31 | Blinded in One Eye — -1 BS; blinded in both = retire |
| 32 | Old Battle Wound — roll D6 before *every* future battle; on a 1 you cannot fight |
| 33 | Nervous Condition — permanent -1 Initiative |
| 34 | Hand Injury — permanent -1 Weapon Skill |
| 35 | Deep Wound — miss D3 games |
| 36 | Robbed — survives, loses all equipment |
| 41-55 | **Full Recovery** |
| 56 | **Bitter Enmity** — psychologically scarred; now *hates* (D6) the individual who did it / their leader / their whole warband / all warbands of that type |
| 61 | **Captured** — held by the enemy; may be ransomed, exchanged, sold to slavers at D6×5gc, sacrificed, or turned into a zombie |
| 62-63 | **Hardened** — immune to fear from now on |
| 64 | **Horrible Scars** — *causes* fear from now on |
| 65 | Sold to the Pits — wakes in the fighting pits and must fight a Pit Fighter |
| 66 | Survives Against the Odds — +1 Experience |

Distribution: **Dead ~14%**, **Full Recovery ~42%**, everything else a lasting mark.

Why this matters for Wyrd:

- **Deferred resolution.** You do not know the outcome during the fight; it is rolled
  afterwards. This is how a single-PC campaign survives lethal combat without either
  softening it or ending — and it pairs with Fate points rather than competing.
- **Bitter Enmity is a relationship result, not a stat penalty** — it creates a named enemy.
- **Captured is a scenario hook**, not an ending.
- **Old Battle Wound is a recurring dread beat** that fires on its own schedule forever.
- **Horrible Scars** makes the survivor frightening — the same social-cost idea as WFRP's
  mutation Fear Points.

Sellswords adds a complementary idea: when a character falls, **you do not learn whether
they are dead until someone reaches them**, then roll on an Out-of-Action table. Deferred
death resolution, again.

---

## 5. Scarlet Heroes — running one PC against party content

Built explicitly for a single hero, and it solves the scaling problem two ways.

**The Fray die.** Every hero has one (d8 fighter, d6 default, d4 magic-user); *only* heroes
have them. Each round, in addition to their normal attack, a hero rolls the Fray die to
automatically kill or injure petty enemies with **fewer hit dice than the hero has levels**.
Magic-users are the exception — their d4 Fray die "can affect any target, even one stronger
than the wizard."

This is the mechanism that lets one character face a mob written for a party without
inflating the character. Directly applicable: Wyrd's PC plus NPC companions still needs a
way to handle six thugs without six rounds of individual rolls.

**Asymmetric stats.** Heroes have hit points; "monsters and normal people have hit dice
instead." NPCs are cheaper to model than the PC — the same asymmetry Crowns uses with MOR.

**The Threat score (T).** Each adventure carries a Threat from 1 to 10+, and it is used as a
**multiplier inside the content**: "if a trap does `Td4` damage and the Threat of the
adventure is 6, the trap does `6d4`." Enemy hit dice and attack bonuses scale from it too.
One adventure template therefore serves any level.

That is the answer to scaling Wyrd's scenarios across a multi-year chronicle **without**
escalating the fiction — a scenario is written once with `T`-scaled numbers, and the same
village mystery can be run in year one or year eight. It keeps the low-fantasy constraint
intact: the *danger* scales, the *scope* need not.

**Solo tooling:** urban / wilderness / dungeon adventure generators, a Yes-or-No oracle with
"yes, but" and "no, but" bands, and Oracular Adjectives tables. The book explicitly defers to
Mythic for deeper solo technique. Note the honest framing — the tables "provide the basic
narrative bones... Each adventure scene is meant to be fleshed out with your own
imagination", which is precisely the division of labour Wyrd inverts (Claude supplies the
imagination, the tables supply the constraint).

---

## 6. Sellswords & Spellslingers / Rangers of Shadow Deep

Both are **miniatures games on a measured table** (36×36 inches, movement in inches, terrain
placement), so far less transferable than the triage assumed. Rangers is a solo/co-op
campaign game with recruitable, progressing **companions**, which is structurally the right
shape for Wyrd's NPC party, but its companion rules are stat-and-equipment bookkeeping
rather than behaviour or agency.

Salvageable ideas:

- **Spawn points.** "Any terrain feature large enough to hide a creature may be a spawning
  point for foes popping up at the worst moment." A useful default for how encounters
  arrive in a described space without a map.
- **Deferred death** (above).
- **Hard caps on the PC.** Sellswords PCs start at 3 hp and "no PC may ever have more than
  6" — an explicit refusal to let the protagonist outgrow the world. Very much the flat
  power curve Wyrd wants, stated as a rule.

Lower value than expected. Recorded so it is not re-read.

---

## 7. BareBones Fantasy

Roll-under percentile, doubles as crits/fumbles, eight skills. The generators the reviews
praised are **not in the core rulebook** — likely in *Of Towns and Heroes* (7MB) or the
*Decahedron* magazines (5 issues), both unread. The core book's own value to Wyrd is low;
Warlock does this job better.

One asset worth noting regardless: **`1000 Descriptors`** (a reference PDF) — a bulk
adjective/detail list of exactly the kind useful for keeping NPC and location description
varied over years of play.

---

## What changed as a result

**Adopt:**

- **Threat Packs** as Wyrd's arc format — Imminence, effects table, clue path, ambient
  effects, denizens, counters. Weekly d12 activation, expected-value abstraction across
  real-world gaps.
- **Mordheim's D66 injury chart** (reskinned) as post-combat resolution, keeping the
  narrative results — Bitter Enmity, Captured, Hardened, Horrible Scars, Old Battle Wound.
- **Scarlet Heroes' `T` scaling** so scenarios are written once and stay usable for years.
- **The Fray die** (or an equivalent) so one PC can face a mob.
- **AGE's costed stunt menu** as the model for what boons and banes actually *do*.
- **Asymmetric NPC stats** (Crowns' MOR, SH's hit dice) — companions and enemies are cheap
  to model; only the PC carries the full state.

**Reject:** Sellswords/Rangers tactical layer, BareBones core, Crowns' setting material.

**Still unread and worth it:** Beyond the Wall's other four Threat Packs and the blank
worksheets; Dragon Age's roleplaying/exploration stunts (Sets II-III); Mordheim's
*Border Town Burning* campaign (58MB) and the *Town Cryer* run.
