# Warlock! — rules digest

Working notes on the candidate base system for Wyrd. Source: Greg Saunders / Fire Ruby
Designs — *Warlock! Traitor's Edition* (146pp), *Warlock!* (1st printing, 146pp),
*Compendium* (94pp), *Compendium 2* (107pp). All in `onedrive:Games/Tabletop/Warlock!`.

Mechanics summarised for implementation. Not a substitute for the books.

## Why this system

Explicitly designed as a rules-light engine for old-school British fantasy, and the book
says outright it "does not contain lots of explicit setting information, so you can use it
with your favourite published or home-made settings." Its basic careers are WFRP 1e's
careers barely disguised (Agitator, Boatman, Rat catcher, Road warden, Grave robber,
Militiaman, Pedlar, Bounty hunter). Reikland drops on with almost no conversion.

## Core resolution

- **Basic test:** `1d20 + skill level >= 20` to succeed.
- **Opposed test:** both roll `1d20 + skill`, highest wins. Draw = draw (re-roll if that
  makes no sense).
- **Difficulty:** GM applies a penalty of **2 or 4** to skill. That is the whole
  difficulty system.
- **Luck:** a skill-like score. Player *may choose* to test Luck to dodge a misfortune, or
  to break a tie in an opposed test. **Testing Luck costs 1 Luck for the rest of the
  adventure, pass or fail.** Always the player's choice.

## Advancement — lateral, not vertical

- GM grants **1-3 advances** per session.
- An advance raises one skill **in the current career only**, up to that career's cap.
- **Career skill** = the *lowest* of the skill levels the career grants, so it rises slowly.
- **Max Stamina +1 each time the career skill rises by 1.** This is the only growth in
  durability, and it is slow.
- Real progression is **changing careers** (basic -> advanced), which changes access and
  social position rather than power.

This is the flat power curve the low-fantasy constraint needs, already built in.

## Combat

- Melee/ranged are opposed tests. Winner rolls the weapon's damage dice.
- **Stamina is not meat.** Explicitly "cuts, bruises, and the tiring effects of physical
  exertion... losing the ability to control the fight."
- **Armour subtracts dice:** light `1d3`, modest `1d6`, heavy `2d6`. Shield raises armour
  one rank (precludes two-handed weapons). Minimum 1 stamina loss always gets through.
- **Mighty strike:** beat the defender's roll by more than 3x -> double stamina loss.
- **Critical hit:** taking damage that puts you **below 0 stamina**. Roll
  `1d6 + total negative stamina` on the table for the weapon's damage type.
- Damage types: **slashing / piercing / crushing / blast**, each with its own d6 table.
- On the slashing table: `7` = 1d3 fingers sliced off; `8` = ear slashed, permanent -2 to
  hearing tests; **`10+` = cut through an artery, dead.**

Weapons are **casual** or **martial** — martial weapons are banned in most civilised areas
and mark the bearer as a soldier. A social constraint doing real work, very WFRP.

Sample damage: unarmed `1d6-2` crushing, dagger `1d6+2` piercing, arming sword `2d6`
slashing, mace `2d6+2` crushing, bow `2d6+1` piercing, crossbow `2d6+2` piercing.

## Magic

- Priests and wizards share one spell list; only the flavour of the otherworld contact
  differs. Spells cost stamina (the number in brackets).
- Spells live on **scrolls that must be kept to hand** and can be stolen. Practitioners
  carry decoys.
- **Miscast:** on a failed second incantation test, roll `1d20` on the miscast table.
- The miscast table is a **mutation table in all but name**: horns grow from the head, an
  eye turns milky white, fingers elongate, skin bleaches white, hair falls out, an
  otherworldly being notices the caster and arrives in 1d3 rounds.

## Compendium 1 — corruption material (NPC-facing)

Part 4 "Corrupted" covers demonkind, cultists and fallen knights as **antagonists**, for
the GM to build. Includes a `1d20` **Mark of Darkness** table rolled per *year* of demonic
service: pallid skin, fangs, white eyes, rat's tail, cloven hooves, surrounded by flies,
extra eyes, featureless face.

Also: necromancy with its own **necromantic miscast** table, demonic spells, dark gifts.

**Gap:** these are GM tools for building corrupted NPCs. There is no player-facing
corruption *track* that accrues. Wyrd must add that — but the tables to draw from exist.

## Compendium 2 — the solo-play goldmine

**Cruel Misfortune** (`1d20`, at character creation): a built-in personal hook, each one
a standing instruction to the GM. Death hunts you; a disaster sibling; born under a dark
star; a rival in love; a mistake you live with; a revenge you are owed; *you have seen
things* (GM decides what triggers the memory); one big joke (GM reveals a cosmic joke
against you once per session).

**Passions:** two per character, negative (Vice/Hate/Fear) or positive
(Desire/Loyalty/Love/Uphold/Respect/Devotion), each attached to an object — e.g.
hate (elves), vice (gambling). Once per session the **player** may invoke a passion for
**+5** to a related test; once per session the **GM** may invoke one against the character
for **-5**. Passions can flip at end of session when the fiction warrants — Devotion
becomes Hatred on discovering the church is rotten.

**Reputation:** starts at 0. Awarded on goal completion — `1` minor/local, `2` significant,
`5` major. Carries a *label* that changes with recent deeds: reputation 7 (swindler),
reputation 6 (the Gottleburg murders). **In play the GM asks for a Reputation test when
the character meets someone** — pass means recognised, "with whatever consequences that
brings. This may or may not be beneficial to the character, such is fame."

**Per-career advance triggers:** each career lists 2 concrete conditions.
Agitator: "mark an advance when you stir people up to act against authority." Assassin:
"when you get away scot-free." Plus one advance for learning something new, and one for
following your traits/passions **even when it got you into trouble**.

Also adds firearms (Readiness / Shooting / Misfire / Boom!) — relevant to both a
gunpowder Empire and, extended, to the 40k conversion.

## Assessment for Wyrd

**Fit: strong.** Every roll is one line of arithmetic. No grid, no positioning, no
hit locations. The Stamina-then-criticals model delivers grim lethality with almost no
bookkeeping, and damage-typed crits make injuries specific for free.

**What Wyrd must add:**

1. **Fate points** — *the essential one*. Warlock has no death-cheat; Luck is a
   test-modifier resource, not a survival valve. With `10+ = dead` on the crit tables, a
   single roll can end a multi-year single-PC chronicle. WFRP's Fate points (small,
   hard to replenish, convert death into maimed-and-worse-off) are required for this
   format. This makes the game *more* grim, not less.
2. **Corruption track** — player-facing and cumulative, triggered by exposure (warpstone,
   daemonic presence, unforgivable acts) as well as miscasting. Draw effects from the
   existing miscast and Mark of Darkness tables.
3. **Insanity track** — with **Fear/Terror tests** as the main trigger. Warlock has no
   fear rules at all; `Fear` exists only as a spell.

**What Wyrd should adopt as-is:** Cruel Misfortune, Passions, Reputation, and the
per-career advance triggers. All four are unusually well suited to an LLM GM running one
player — they are explicit, checkable, and they hand the GM standing licence to apply
pressure without inventing it.

## Sci-fi conversion (later)

Near-mechanical, on this base:

- Careers -> 40k careers (structure identical; Dark Heresy supplies the list)
- Casual/martial -> civilian/military weapons; the social constraint gets *stronger* in
  the Imperium
- Damage types -> existing `blast` table already covers energy weapons
- Magic -> psychic powers; **Wrath of the Otherworld becomes Perils of the Warp with no
  structural change** — reskin the miscast table, keep the mechanism
- Compendium 2's firearms rules (Readiness / Misfire / Boom!) port directly

## Editions and other notes

**Which book is canonical:** *Traitor's Edition* (2022) is the fuller revision of the 2020
first printing — same 146pp, same structure, ~18% more text. Content differences are
minor. **Use Traitor's Edition.** The Compendia are additive, not replacements.

**Scenario guidance is thin.** The "Mastery" chapter's *Scenario Forms* section is general
GM advice — it names the scripted-vs-freeform tension and recommends a blend, but offers no
scenario format or structure. Wyrd must design its own. Worth noting the tension it
identifies is exactly the one Wyrd has to resolve: scripted scenarios railroad and get
abandoned when the player deviates; pure freeform makes players "lose focus... if they
think the games master is making it up." **Situation-with-agendas, not script** is the
answer to both.

**Warhammer Fighting Fantasy Roleplay** (`Advanced Fighting Fantasy/03 - Warhammer Fighting
Fantasy Roleplay`) is a 43-page fan conversion of Warhammer to Advanced Fighting Fantasy 2e
(SKILL / STAMINA / LUCK / MAGIC). It has races, skills, equipment, settlement tables and
good Old World name lists — but **no careers, corruption, insanity, fate or fear rules**.
Useful as a naming and flavour resource; not as a mechanical source.
