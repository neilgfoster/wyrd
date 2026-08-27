# Wyrd — the ruleset

Percentile, narrative, and light enough to run one beat in a few lines of text.

Every label here is a **default**. A setting renames or disables what it likes
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)); nothing mechanical changes.

| Engine label | What it measures | Typical setting names |
|---|---|---|
| **Taint** | permanent accrual that transforms you at thresholds | Corruption · Shadow · Sin · Humanity |
| **Trauma** | long-term mental accrual, breaking into Afflictions | Insanity · Scars · Sanity |
| **Strain** | short-term pressure, recovered at a Rally | Stress · Fatigue · Wear |
| **Resolve** | the spendable counterweight to Taint | Hope · Faith · Nerve |
| **Fate** | the death valve | Fate · Destiny · Providence |
| **Transformation** | the permanent change at a Taint threshold | Mutation · Gift · Mark |
| **Affliction** | the lasting condition at a Trauma threshold | Derangement · Disorder |
| **Dread** | how frightening your changes make you to others | Fear points |
| **Standing** | an open-ended count of social position — what a character is owed by who they
  are and who they know | Reputation · Renown · Rank |
| **Ill Omen / Fair Omen** | the two Wyrd-die faces | Chaos Star / Comet · Peril / Grace |

---

**Naming rule.** An engine label must be *descriptive English*, not a term borrowed from a
source system. "Downtime" rather than a named phase from one game; "Ill Omen" rather than a
named die face from another. If a label only makes sense to someone who has read a
particular book, it belongs in that setting's `rename:` block, not here.

---

**One shared shape, used twice.** Taint/Resolve and Fate/Fortune are the same mechanism, applied
to two different domains: a scarce or near-permanent resource, paired with a renewable
counterweight that spends against it. Taint accrues and only falls when a Transformation spends
it down; Resolve is the spendable counterweight, renewing at a Rally and a downtime, capped by
how much Taint there currently is to counter. Fate is spent, rarely, to buy off the worst
possible outcome and does not come back; Fortune is its daily-renewable counterweight, spent far
more freely, on smaller stakes. Neither pair was designed as an instance of the other — they were
each settled on their own terms, for corruption and for mortality respectively — but the shape
underneath is identical, and naming it here means a third instance of the same pattern, if one is
ever added, reads as completing something already established rather than inventing a new idea.

---

**Before the ruleset uses them: Skill and Stamina.** Two terms this document assumes from its
first line, defined in full in [`10-the-character.md`](10-the-character.md) —

- **Skill** — a percentage, under a name the setting supplies (10-the-character.md §2). This is
  what every roll below tests against. **Engine-fixed**: the mechanism (a percentage, tested
  against `d100`) is not a setting choice; the skill *list* and its *names* are.
- **Stamina** — current and maximum, spent in an exchange and restored at a Rally or a downtime
  (§2 below, and 10-the-character.md). **Engine-fixed**: the starting value, cap and recovery
  rule are the engine's; a setting may retune the starting figure, never the mechanism.

Everything above the line (Taint, Trauma, Strain, Resolve, Fate, Transformation, Affliction,
Dread, Standing, the Wyrd die) is **renamable presentation, engine-fixed mechanism** in the same
sense — the table only lists the ones a setting typically has reason to rename.

---

## 1. Resolution

> **Roll `d100`. Succeed at or under your `skill%`.**
> - **Degrees of success** — tens digit of the skill minus tens digit of the roll — give
>   magnitude.
> - **The units digit of the natural roll** is the **Wyrd die**: what else happened.

One roll, three independent axes, no extra dice. Rationale and rejected alternatives are in
[ADR 0001](../adr/0001-resolution.md).

**Difficulty** modifies the *skill*, never the roll — which is what keeps the Wyrd die clean:

| Easy | Average | Challenging | Difficult | Hard | Very Hard |
|---|---|---|---|---|---|
| +20 | +0 | −10 | −20 | −30 | −40 |

**One step up, four steps down, on purpose.** A task easier than Easy is not rolled at all — "only
roll when it is dramatic" (below), and the Declaration table's "so well-judged it removes the
risk" row already covers a plan good enough to remove the risk entirely. There is no *Very Easy*
tier because the tier below Easy is *no roll, it simply works*. The steps below Average, by
contrast, are where most of the dramatic range actually lives — genuinely hard-but-attemptable
tasks span a wide band, from "harder than usual" to "at the edge of possible," and that band is
where the difficulty ladder is doing its real work.

**Untrained — a skill you do not have** is tested at a flat **10%**, before difficulty and
declaration. Anyone may try to shoot; almost nobody hits. The engine has no characteristics to fall
back on ([ADR 0013](../adr/0013-the-engine-names-no-skill.md)), so this base is stated rather than
derived, and it sits inside the *you would be guessing* band
([`13-diegesis.md`](13-diegesis.md)).

Untrained attempts stack the same two modifiers as any other roll — difficulty (above) and
declaration (below) — so a combined figure is never one hidden number, always two named ones added
to the 10% base:

| Attempting | Base | + Difficulty | + Declaration | At |
|---|---|---|---|---|
| average, said briefly | 10% | Average +0 | brief, no bonus | **10%** |
| easy, said briefly | 10% | Easy +20 | brief, no bonus | **30%** |
| easy, specific and leveraging something established | 10% | Easy +20 | Specific *and* leveraging, +20 | **50%** |
| hard | 10% | Hard −30 | brief, no bonus | impossible — the modifier takes it below zero |

Trained, at average difficulty said briefly, opens at **25%** and up — see Declaration below for
what "specific and leveraging something established" means, and §3 for a skill's cap.

Having the skill is worth at least 15 points over not having it, at every difficulty. A setting may
mark a skill as **requiring training**, and then there is no untrained attempt at all — a language
you do not speak is not a 10% chance ([`10-the-character.md`](10-the-character.md)).

### Opposed tests

When a player character or companion is opposed by an NPC/opponent — a lock picked while a guard
listens, a bluff run past a suspicious gatekeeper, breaking free of a captor's grip — the test
resolves as a single player-facing roll, exactly as combat's attack and defence rolls already do
(§2, [ADR 0027](../adr/0027-combat-rolls-belong-to-the-player.md)):

1. **The player rolls once**, against `effective% = clip(50 + (skill −
   opponent_skill_or_baseline), 5, 95)` — an even match is a coin flip, no skill gap reaches
   certainty or impossibility. **The opponent's dice are never consulted.**
2. **Degrees** are read `tens(effective%) − tens(roll)`, using `effective%` as the skill value —
   the same formula this section has always used, fed the same input combat already feeds it.
3. **A failure simply fails the action.** There is no resisting-side roll and no degrees
   comparison to have skipped.
4. **The Wyrd die always belongs to the player** making the roll — there is no roll on the
   opponent's side for it to belong to instead.
5. **Assistance** (below), declaration and the untrained-10% rule apply exactly as they do to any
   other roll; nothing about this shape treats them differently.
6. **An Omen also carries a ±10 modifier on the roller's own next roll** — an Ill Omen −10, a
   Fair Omen +10 — on top of the narrative framing above (§1's "something also goes wrong /
   breaks your way" still applies; this adds a measured cost or gain to it, not a replacement for
   it). **The roller's own next roll**, since the opponent never rolls and the die always belongs
   to the player: the very next roll of any kind that character makes, whether another opposed
   test or a combat roll (§2), in the order play actually produces them. **Does not stack** — a
   second Omen before the pending modifier is spent replaces it, never adds to it — and **lapses
   unused** if the scene or fight ends first. Scoped to opposed tests and combat, where the same
   roll shape governs both; an ordinary (non-opposed) test's Omen stays narrative-only
   ([ADR 0042](../adr/0042-opposed-and-combat-omens-carry-a-plus-minus-10-modifier.md),
   [`check_omen_effect.py`](../../specs/049-combat-omen-mechanical-effect/check_omen_effect.py)).

**A contest between two player-controlled entities** — a player character and a companion, or two
companions, in genuine tension with no NPC/opponent side — has no opponent skill to set
`effective%` against. The GM either names which side is acting and calls one ordinary test, or
treats it as two ordinary tests. This is not the shape above; it is not resolved by a roll on each
side compared against the other's, and it does not need to be — it comes up rarely, and an
ordinary test already answers it.

**This generalises what combat already did.** [ADR 0027](../adr/0027-combat-rolls-belong-to-the-player.md)
converted combat's attack and defence rolls to this shape; [ADR 0035](../adr/0035-opposed-tests-generalise-to-the-player-facing-roll.md)
extends it to every opposed test where one side is an NPC/opponent, which was every remaining live
use of the two-sided roll-both shape this section once described. That earlier shape — both sides
roll, the acting side first and must succeed, ties to the resister — is recorded in
[ADR 0016](../adr/0016-opposed-tests-need-a-successful-actor.md) as the mechanic it replaced; it
governs nothing in the current ruleset.

**Only roll when it is dramatic** — when failure is interesting and the outcome is in doubt.
Everything else simply happens.

### The Wyrd die

Read from the **units digit of the natural roll**:

| Units | Result |
|---|---|
| 0 | **Ill Omen** — something also goes wrong |
| 9 | **Fair Omen** — something also breaks your way |
| 1–8 | nothing |

20% frequency. Widen to `0–1` / `8–9` (adding minor Bane and Boon) via `houserules.yaml` if
play proves it sparse.

The units digit is uniform within both the success and failure sets, so the axes are
genuinely independent: a success carrying an Ill Omen and a failure carrying a Fair Omen are
equally possible at any difficulty.

**The natural roll rule.** The Wyrd die is read from the dice as they first fell — never
modified, never rerolled. Fortune buys the *result*, never the world's reaction to the first
attempt.

> You can change what happened. You cannot change what it cost.

**Taint bends the die**, so the world turns against you more often as you accrue it, while
your competence is untouched:

| Taint | Ill Omen on units |
|---|---|
| 0–2 | 0 |
| 3–5 | 0–1 |
| 6+ | 0–2 |

### Declaration

The same action declared well is a different action:

| Declaration | Effect |
|---|---|
| So well-judged it removes the risk | **no roll** — it works |
| Specific and in character | **+10** |
| Specific *and* leveraging something established | **+20** |
| Brief or unelaborated | no bonus, **no penalty** |
| Against the character's established nature | the GM may invoke a Drive for **−20** |

**Never reward length; never penalise brevity.** Six specific words earn the bonus; a
paragraph of generic atmosphere does not. Terse play must stay viable — sessions happen on a
phone. And prefer *no roll* to a large bonus: a plan good enough to remove the risk should
simply succeed.

### Assistance

A companion may help. One does.

- **The helper must be able to do the task.** Someone who could not attempt it alone cannot
  improve someone who is attempting it.
- **The help must be specific** — what they actually do, in the fiction. Encouragement is not
  assistance.
- **The helper does not roll.** One test, one natural roll, one omen.
- **The bonus is a tenth of the helper's own skill**, rounded down, to a ceiling of **+10**.

| Helper's skill | Worth |
|---|---|
| 30% | **+3** |
| 45% | **+4** |
| 65% | **+6** |
| 100% | **+10** |

**Further hands do not add.** A second, third and fourth companion change the fiction, and may
change the *difficulty the GM sets*, but they never accumulate a bonus. This is the rule that keeps
the ladder meaning something: at a Hard test a practised character sits at 15%, and four companions
adding +10 each would put them at 55% — the rung the GM chose, deleted by turning up with friends.
Computed in [`check_assistance.py`](../../specs/011-assistance-and-group-tests/check_assistance.py) and
recorded in [ADR 0017](../adr/0017-assistance-group-tests-and-extended-tasks.md).

A helper who is barely competent is worth almost nothing, which is the point. Help from someone who
cannot do the task is not help.

### Group tests

**A group acts, a group rolls once.** The party's composition shows in the *skill tested*, never in
the number of dice. Which skill depends on a question about the fiction:

| The fiction | Test |
|---|---|
| the thing must get done | the **most capable** member's skill, with assistance |
| everyone must get through | the **least capable** member's skill, with assistance |

Hauling a cart from a ditch is the first: one strong pair of arms and willing hands. Crossing a
courtyard unseen is the second — the party is as quiet as its noisiest member, and the scout can
only do so much for them.

A member with no relevant skill at all is tested at the untrained 10%, and in a test everyone must
get through, that is who is tested. Leaving them behind is a decision available to the party, and
usually the interesting one.

### Extended tasks

Some work does not resolve in a beat. Forging a blade, deciphering a dead language, nursing someone
through a fever — these accumulate.

- **The target is a count of degrees.** Reach it and the work is done.
- **One test per interval**, and the interval is named by the fiction: a night, a week, a season.
- **A success adds its degrees, minimum 1.** A bare success never stalls the work.
- **A failed interval is spent and gains nothing.** The time is gone; the work is where it was.
- **The Wyrd die is read every interval**, from that interval's natural roll, as in any test.

| Scope | Target |
|---|---|
| a night's work | **2** |
| a season's work | **4** |
| a great labour | **6** |

At a competent 45% those are roughly two, four and six intervals. At 25% the largest is nearly
eighteen, and the rule does not hide that: **an extended task at a skill you barely have is not a
long task, it is a wall.** Bring a helper, lower the difficulty, or do not attempt it.

**An interval must be worth a beat of prose**, or it is not worth a roll. Work that produces no
scene worth writing is not an extended task; it is a single test, or it simply happens.

**Invoking a system of power** — a setting's declared mechanism for supernatural or extraordinary
effort — is an ordinary test governed entirely by this section; see
[`09-systems-of-power.md`](09-systems-of-power.md) for the schema, the cost a setting
declares, and the Ill Omen consequence.

---

## 2. Combat

### The exchange

What is on the other side of the roll — what an opponent carries, and which of these rules reads
each field — is in [`12-the-adversary.md`](12-the-adversary.md).

- **The opponent never rolls.** Its capability is a static number
  ([`12-the-adversary.md`](12-the-adversary.md)), and every roll in combat belongs to a player
  character or companion ([ADR 0027](../adr/0027-combat-rolls-belong-to-the-player.md)).
- **Attack:** the attacker rolls once against `effective% = clip(50 + (attack_skill −
  defender_skill_or_baseline), 5, 95)` — an even match is a coin flip, and no skill gap reaches
  certainty or impossibility. On success, roll the weapon's damage.
- **Defence:** when the target is a player character or companion, the player rolls once against
  `effective%` computed the other way round — `clip(50 + (defence_skill −
  attacker_skill_or_baseline), 5, 95)` — instead of the opponent rolling an attack. Failure means
  the blow lands; success means it does not.
- **Degrees, on the attack roll**, are read from the roll exactly as in §1 —
  `tens(effective%) − tens(roll)` — using `effective%` as the skill value; the attack roll must
  succeed for the hit to land at all, so degrees are always available.
- **Degrees, on a failed defence roll**, are read from a virtual roll rather than the natural
  one — the roll that lands the blow is a *failure* of the defender, which has no degrees of its
  own to read under §1's success-only convention. Reflect it: `virtual_eff = 100 − eff_def`,
  `virtual_roll = 101 − r` (where `r` is the natural failed roll), then apply §1's same formula —
  `tens(virtual_eff) − tens(virtual_roll)` — to the virtual inputs
  ([ADR 0044](../adr/0044-telling-blow-via-a-failed-defence-roll-is-symmetric.md)). A blow landed
  via a badly-missed defence roll is exactly as capable of being telling as a decisively-won
  attack.
- **The Wyrd die always belongs to the player** making the roll, attack or defence — there is no
  roll on the opponent's side for it to belong to instead.
- **An Omen carries the same ±10 next-roll modifier here as §1's opposed tests** — combat's
  attack and defence rolls are that same shape ([ADR 0027](../adr/0027-combat-rolls-belong-to-the-player.md)),
  so the modifier rule is the same rule, not a second one
  ([ADR 0042](../adr/0042-opposed-and-combat-omens-carry-a-plus-minus-10-modifier.md)).
- **Assistance** (§1) applies identically to the attack roll and the defence roll.
- **Stamina is not meat.** It is cuts, bruises, and losing control of the fight.
- **Armour subtracts dice:** light `1d3`, modest `1d6`, heavy `2d6`. A shield raises one rank.
  A minimum of 1 always gets through.
- **Telling blow:** win by 6 or more degrees and **the damage rolled doubles**, and then armour
  subtracts. The order matters: it is where almost every large critical comes from
  ([`05-criticals.md`](05-criticals.md)). Computed against the roll this section actually
  produces, not carried over from the shape it replaced — telling blows stay a minority of hits
  at every realistic pairing
  ([`check_conversion.py`](../../specs/018-player-facing-combat/check_conversion.py),
  [ADR 0028](../adr/0028-the-telling-blow-threshold-and-the-damage-finding.md)).
- **Damage has a type** — **slashing**, **piercing**, **blunt** or **searing**. The set is closed,
  and a setting renames one it has no fiction for
  ([ADR 0022](../adr/0022-four-damage-types-named-for-the-wound.md)).
- **Critical** when damage takes a combatant **below 0 Stamina**. Roll `1d6 + points below
  zero` on the table for the damage type ([`05-criticals.md`](05-criticals.md)). High results
  are lethal — the worst row marks the blow **mortal**, and a mortal blow is answered when the fight
  ends, like every other death in this ruleset
  ([ADR 0023](../adr/0023-a-critical-never-kills-during-the-fight.md)).
- Weapons are **casual** or **martial**. Martial weapons mark the bearer and are illegal in
  most civilised places, and being seen carrying one there **costs 1 Standing** the moment it
  becomes visible in a scene — not a fine, not automatic violence, a real and immediate social
  cost. Where the fiction supports it, the GM may also treat it as a trigger for an encounter (a
  patrol, a challenge) rather than a Standing loss, but not both for the same sighting.

### Gear and coin

A setting's `gear.yaml` declares what a weapon or armour piece is
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)), validated against a closed schema
([`check_gear.py`](../../tools/check_gear.py)): a weapon states its damage, damage type,
casual/martial class, price and availability; armour states its rank, price and availability.

**Wealth is coin: a small number the player can state a total for, not a ledger.** Nothing in
this ruleset asks a player to itemize what they bought or when. A character has some coin; they
spend it against a `gear.yaml` price, or at Upkeep ([`16-session.md`](16-session.md)), and the
total simply changes.

**Standing and coin are two sides of one material position, not one resource.** Standing is what
a character is *owed* by their position — who they are, who they know, what door that opens.
Coin is what they *have on hand*. Upkeep is the one place they convert: away from home, a
character pays in whichever one they still have. Standing also moves outside Upkeep, as a direct
consequence of a scene — the martial-weapon rule above is one such case, and the GM may apply
others where the fiction plainly calls for it, the same way Taint or Trauma can move outside
their own triggers.

**Encumbrance is a question asked of the fiction, not a number.** There is no weight table and no
carrying-capacity score — consistent with [`13-diegesis.md`](13-diegesis.md)'s existing "realistic,
not logistic" rule for inventory generally. When it matters whether a character is plausibly
carrying something, the GM asks the same question that document already asks about what a
character has and what's missing, and answers it from the fiction: what they're wearing, where
they came from, what they've said they packed.

### Rounds and turn order

A **round** is the span in which every combatant acts once. It has no fixed length in the fiction;
it is as long as the exchange needs.

> **Whoever started the exchange acts first.** That side takes the whole first round, then the other
> side takes theirs.

Order costs no dice and needs no roll, which matters twice over: it keeps a round cheap in prose,
and the engine names no skill and has no characteristics
([ADR 0013](../adr/0013-the-engine-names-no-skill.md)), so there is nothing an initiative roll could be
made against without inventing an attribute for the purpose.

Within a side, order is the fiction's and carries no mechanical weight — companions act where they
make sense, and nothing depends on which of them goes first.

**Where neither side started it** — a mutual encounter, both parties seeing each other at once — the
side already holding a weapon acts first. If both are armed, or neither is, the player's side acts
first. That last clause is the one rule here decided from outside the fiction, and it is stated
plainly rather than dressed up ([ADR 0018](../adr/0018-combat-sequencing.md)).

### A turn is one action

On their turn a combatant does **one** thing:

| Action | Effect |
|---|---|
| **Attack** | in close engagement, or at range |
| **Close** | enter close engagement with someone |
| **Break off** | leave close engagement, at the cost of a parting blow |
| **Ready or use** | draw, reload, drink, brace, work something |
| **Act on the fiction** | anything else the scene affords |

One action, no second action and no free action. Anything that would need two is two turns.

### Engagement

The engine records **one** fact about position: two combatants are **in close engagement**, or they
are not. There are no distances, no ranges and no map — a chronicle can record a state and cannot
record a battlefield.

**Closing costs the closing combatant their action.** They arrive; they do not also swing.

**Being closed with is not refusable.** Once someone has closed, the engagement exists, and leaving
it means breaking off.

That single exchange rate is what holds ranged and close combat in tension. A fighter spends a turn
to reach an archer; the archer spends a parting blow to get clear again. Neither is free, and
neither is impossible.

### Ranged attacks

A ranged attack is an ordinary attack. What makes one harder is what the fiction already carries,
read on the difficulty ladder in §1 — never a distance, because there is not one:

| The shot | Difficulty |
|---|---|
| clear sight, target unaware or standing still | **Easy** |
| ordinary | **Average** |
| target has cover, or the light is poor | **Challenging** |
| **the shooter is in close engagement** | **Difficult** |
| **the target is in close engagement with someone else** | **Challenging** |
| target has hard cover and knows the shot is coming | **Hard** |

Two of those rows do work worth naming. Shooting **while engaged** is hard enough that an archer
would usually rather break off — which is what stops a fight collapsing into everyone shooting at
arm's length. Shooting **into someone else's fight** is the situation that arises constantly and
that no rule covered until it was played: it is one rung harder, and an **Ill Omen** on the shot
means the ally is hit instead.

### Breaking off, and getting away

Leaving a fight is two things, and they cost separately.

**Breaking close engagement always works, and always costs a parting blow.** Every opponent still
engaged with the departing combatant attacks them as they go. There is no roll to leave.

**Getting away from the scene is a group test**, in the *everyone must get through* shape from §1 —
the party escapes as fast as its slowest member, and the fastest can only do so much for them. The
pursuit sets the difficulty:

| Pursuit | Difficulty |
|---|---|
| one pursuer | **Challenging** |
| each further pursuer | one rung harder |
| no one able or willing to follow | no test — you simply go |

On a failure the fight resumes, and it resumes **where the slowest member is**.

Flight is therefore never impossible — retreat stays the right answer to a fight going badly, and
the engine lets a player take it — and never free.

### Surprise and ambush

> **A surprised side does not act in the first round at all.**

This is the ordinary turn-order rule taken to its limit: the exchange began and one side did not
know it.

**A surprised combatant still defends.** They lose their turn, not their reflexes. Without that
sentence surprise is worth roughly twice what it is meant to be.

**Ambush is surprise that was prepared** rather than stumbled into — a position chosen, a weapon
already drawn, a moment waited for. It eases the first round's attacks by **+20**, and nothing
after. Preparing an ambush is therefore worth more than being handed one, and worth no more than a
perfectly judged declaration (§1).

A free round is decisive without being deciding: computed across realistic pairings it moves the
surprising side's odds by 4 to 8 points and never past 83%, so an ambush wins fights and does not
end them before they start
([`check_sequencing.py`](../../specs/012-combat-sequencing/check_sequencing.py)).

### Crowds

A fight against twenty people cannot be run one roll at a time. This is the rule that lets a
character and their companions face a crowd without a `d100` per body — and it is a rule, with
numbers, not a licence for the GM to decide when a fight stops mattering.

> **At the start of their turn, a character in close engagement with a crowd clears one crowd
> member, without a roll and without spending their action.**

Each character **and companion** clears one, on their own turn. A cleared body is *out of action*
and does not act that round; the character then takes their turn as normal, against whatever the
crowd was in the way of. A character who is not engaged with the crowd — shooting from across the
yard — clears nobody.

**Who is a crowd member** is a lookup, and nothing else. All three tests must hold:

| Read from | Qualifies when |
|---|---|
| the opponent's **maximum Stamina** | **1** |
| the opponent's **armour** | **none** |
| the **character's** relevant skill against **theirs** | ahead by **20 or more** |

The first two are the whole of what used to be called *petty*, and they are not a judgement about
what an opponent is worth — they are the statement that **one connecting blow removes them**. Across
the whole plausible span of weapon damage, a single ordinary hit takes a body of Stamina 1 in no
armour below zero between **67% and 100%** of the time; the same body in the lightest armour drops
as low as **11%**, and a body of Stamina 2 as low as **33%**. The line sits exactly where one blow
stops being enough
([`check_mobs.py`](../../specs/013-the-mob-rule/check_mobs.py),
[ADR 0019](../adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md)).

The third is the whole of what used to be called *weaker*. Untrained is a flat 10% (§1), so against
an untrained crowd the rule opens at **30%** — one advance past a newly opened skill. A character
who is themselves untrained has no gap and clears nobody.

**The clear is worth about what rolling it out would be, and slightly more.** Against a qualifying
body, attacking and rolling for it removes 0.55 to 0.80 bodies a round across the skills characters
actually have; the free clear removes 1. That discount — **1.25× to 1.82×** — is what buying out a
roll per body costs, and it is bounded by the character's own turn: nobody clears two.

**The crowd answers once, not once per body.**

> **A crowd engaged with a character makes one attack on them each round**, at whatever skill its
> members have, eased by **+10 for each body on that character beyond the first**, to a ceiling of
> **+20**.

**A crowd's parting blow is one attack on the same terms**, not one per body. Breaking off from a
crowd otherwise costs a blow from every opponent still engaged (above), which would put back exactly
the rolls this rule removes.

The ceiling is the top of the difficulty ladder, and it is reached at **three bodies on one
target**. A crowd's numbers past that buy nothing against that character — what they buy is
reaching more of the party at once. A party of four is facing a full-strength crowd from twelve
bodies on.

That leaves the fight where it should be:

| | Rounds to clear | Rounds to be dropped |
|---|---|---|
| one character, no armour, six bodies | 6 | **5.7** |
| one character, modest armour, six bodies | 6 | 12.9 |
| four characters, no armour, twelve bodies | 3 | 5.7 each |
| one character, no armour, twenty bodies | 20 | 5.7 |

**A lone unarmoured character loses to six people.** The rule is not a way to win a crowd fight
alone; it is a way not to roll sixty times. Armour and companions are what actually answer a crowd,
which is the right answer for both to be.

**The Aftermath table is not rolled for a crowd.** It is rolled once per character and companion who
dropped (below), and a crowd is neither — twenty Aftermath rolls is the same fault as twenty attack
rolls. What became of the crowd is the fiction's to say.

### Death is deferred

Nothing resolves during the fight; a combatant who drops is *out of
action*. Afterwards, roll `d100 + 5 × points below zero` on the **Aftermath** table
([`06-aftermath.md`](06-aftermath.md)) — once per combatant who dropped, companions
included. Most results are a lasting mark rather than death. Deferred resolution is how a
single-character chronicle survives lethal combat.

### Getting back up

Stamina is spent in the exchange and restored on the clocks the engine already has. There is no
third clock, and no roll.

> **At each Rally, recover 1 Stamina.** At the end of a **downtime** phase, Stamina returns to
> maximum. A combatant who dropped below 0 wakes at **0 when the fight ends**, and recovers from
> there.

**Companions recover on the same rule.** They roll on the same Aftermath table and drop on the same
numbers; there is no companion rate.

**The rate is Strain's rate, at Strain's trigger** (§5). One number covers both, and a second
restoration rate at the same pause would be two numbers doing one job.

**Downtime costs no undertaking.** Weeks or a season of rest mending cuts and bruises needs no
mechanic to explain it — Stamina is not meat — and putting it on the undertaking list would make
every downtime after a real fight resolve to the same choice, which is the trade
[`16-session.md`](16-session.md) exists to pose. What downtime cannot mend is a lasting wound, and
that is what **Mend** is for.

**Waking at 0 is not a second penalty.** The Aftermath table has already priced dropping; this says
only where the track restarts. Waking at any fraction of maximum would soften the same event twice,
in two places that would eventually disagree.

The road back is short enough to keep playing and long enough to be felt:

| | Rallies to full |
|---|---|
| dropped, Stamina 6 | **6** |
| dropped, Stamina 7 (a completed career) | 7 |
| one ordinary fight against an even opponent, won | 4.0 |
| one ordinary fight at a 20-point advantage, won | 2.1 |

An even fight costs most of the track — and that is the road back *including* being dropped, since
a combatant who dropped wakes at 0 however far below it they went. That is the rule's real weight: a character who fights
an equal every beat never sees full Stamina again until a downtime, and one who picks their fights
recovers between them.

**Entering a fight short is the cost, and it is steep.** Against an opponent 20 points below them, a
character drops **14.8%** of the time at full Stamina and **48.6%** at 2 — the same fight, three
times as dangerous. Against an equal, dropping is near a coin flip whatever they walked in with,
which is a property of the damage scale rather than of this rule
([`check_recovery.py`](../../specs/014-stamina-recovery/check_recovery.py),
[ADR 0020](../adr/0020-stamina-recovers-on-the-clocks-the-engine-has.md)).

**A consumable healing item — a potion, a draught, battlefield medicine — has no mechanical effect
on Stamina.** It is flavour a setting is free to describe, but it does not advance a recovery
clock, restore a point outright, or otherwise shortcut Rally, downtime, or Mend. Recovery lives
entirely on the clocks the engine already has ([ADR 0020](../adr/0020-stamina-recovers-on-the-clocks-the-engine-has.md));
an item that bypassed them would be the third clock that decision explicitly rejected. This is a
position, not a silence: **Stamina is not meat**, so there is nothing for a potion to mend that the
existing rule does not already answer.

## 3. Fate and Fortune

- **Fate** — few, permanent, spent to **avoid death**. Gone when spent; new ones are rare.
- **Fortune** — renewable daily, equal to the Fate score. Spend to reroll, defend again, act
  sooner, dodge a misfortune, or break a tie. Always the player's choice.

**Fortune, Resolve and the Bargain (§4) compose freely on the very same failed roll — nothing
bounds how many a character spends chasing one result.** A character with the resources to spare
may fail, take the Bargain, fail again, spend Resolve, fail again, and spend every remaining
Fortune point, all against the same original test. This is deliberate, not an unexamined gap: a
character throwing everything they have at one make-or-break moment is a real story beat, and it
is not a guaranteed win — spending every resource still leaves the character subject to the same
odds every other roll uses
([ADR 0046](../adr/0046-reroll-resources-stack-unbounded-on-one-roll.md)).

When Fate is spent the character **survives and is not better off**. The blow was glancing;
everything goes black; they wake later — tended by companions, or imprisoned, or stripped and
left in a ditch. The GM chooses where they wake, which makes Fate the chronicle's
course-correction tool as well as its anti-frustration valve.

Mechanically, spending Fate **closes the death rows** of the Aftermath table: the result is
re-read on the worst row that is not death, and that is what the character carries away
([`06-aftermath.md`](06-aftermath.md), [ADR 0009](../adr/0009-fate-closes-the-death-rows.md)).
Fate is spent only against a death result, and never to improve any other.

### Spending Fate for someone else

A Fate point may be spent to save a **companion** from death, on the same terms as saving
yourself: they survive, and they are not better off.

Two conditions:

- **The character must be present and able to act.** Fate is not spent at a distance. If a
  companion dies while the player is elsewhere, that death stands.
- **Fate buys against dice, never against agendas.** A companion killed by a critical can be
  saved. A companion who walks out because Tension broke, who betrays the player, or who is
  claimed by their own objective, cannot — those are not accidents, and Fate does not argue
  with them ([`16-session.md`](16-session.md)).

That boundary is what keeps both designs intact. Fate remains a **death valve**, not a plot
valve; and companions remain the engine's reliable source of loss, because the losses that
matter most are the ones no resource can prevent.

It also puts the player's scarcest resource into a genuine dilemma. Two Fate left, a
companion bleeding out, and a long road still ahead is a better decision than any the
character sheet can pose alone — and **choosing not to spend is itself a decision the
chronicle should remember**, and record.

Companions have no Fate of their own; their mechanical layer is deliberately thin. They
rely on the player's, which is precisely what makes it cost something.

`mortality` in the setting's tone contract sets starting Fate.

---

## 4. Taint and Resolve

Two paired scores, because a one-way meter is a worse model than a balance.

- **Resolve** — spendable, renewable. Spend **1** for a **+20 bonus to an immediate reroll** of
  the failed test — distinct from Fortune's plain reroll (§3): Fortune buys a fresh roll at the
  same odds, Resolve buys a better one, and costs the resource that measures how much fight is
  left rather than the one that measures luck.
- **Taint** — accrues and sticks.

**Resolve recovers at the same cadence Strain already uses: +1 at a Rally, and back up to its
cap at a downtime** — the same rate ADR 0020 already fixed for Stamina and Strain, reused rather
than a third number invented for a third track. **Resolve's cap is the character's current Taint
plus 3** — one threshold-interval of headroom, the same spacing that already governs
Transformations (§4 below), so a fully-rested character always has real Resolve to spend down
before reaching Taint, not a cap that sits exactly on the Spent line it is meant to measure the
distance to
([ADR 0043](../adr/0043-resolve-recovers-at-a-rally-capped-by-taint.md),
[`check_resolve.py`](../../specs/052-resolve-recovery-mechanic/check_resolve.py)).

**When Resolve falls to equal Taint, the character is Spent** — they will not press a
struggle and will withdraw from danger. **At Taint 0 they can never be Spent, however tired** —
stated as its own rule, not derived from the cap formula: a character who has accrued no Taint
at all has nothing yet for Resolve to be a counterweight *to*, so the state is exempted outright
rather than left to a formula that would otherwise make it reachable at Taint 0 too.

The same Taint score therefore means different things at different times, and recovery is
part of the loop rather than an afterthought.

### Gaining Taint

Three routes, deliberately in both directions:

1. **The Bargain** — you failed something that mattered and have no Fortune left. You may
   **choose** to take 1 Taint to reroll. Always the player's choice; the GM may mention the
   option exists and never applies it. **May compose with Resolve and Fortune (§3) on the same
   failed roll, without limit** — see §3's own statement of this
   ([ADR 0046](../adr/0046-reroll-resources-stack-unbounded-on-one-roll.md)).
2. **Exposure** — resist with a test. Minor `1`, moderate `2`, major `3`, reduced by degrees
   of success. Sources are a setting matter, and should include **moral** ones as well as
   supernatural — giving in to despair or cruelty is exposure.

   **When the source runs with the grain of the character's Fault Line** — the GM's call,
   grounded in the fiction, the same judgment already used to invoke a Drive below — a failed
   resistance gains Taint **one tier worse**: minor `1` becomes `2`, moderate `2` becomes `3`,
   major stays at `3`. This never touches the resolution roll itself, only the Taint number
   consumed on a failure, so it does not compound invisibly with the way Taint already bends
   the Wyrd die. It applies **at most once per Exposure event**, and is independent of an
   Invocation drawn against the same roll — one changes what is gained on failure, the other
   changes the difficulty of the roll that produced it, and applying both does not compound
   either beyond its own step
   ([`tools/check_fault_line.py`](../../tools/check_fault_line.py)).
3. **Invocation** — before a roll, the GM may **spend one of the character's Taint points** to
   impose a penalty, narrating how it surfaces. Maximum one per check, and it *consumes* the
   point, so it cannot be leaned on.

### Fault Line

Taint is **specific, not generic**. Each character has a Fault Line derived at creation from
their Drives and Misfortune. It names *how* they fall — the direction, not only the quantity —
and it is not only descriptive: it is what the GM reads against Exposure sources above to decide
whether a failure gains Taint at its stated tier or one tier worse. Two characters at equal Taint
with different Fault Lines therefore accrue Taint at different rates once the fiction starts
drawing on each of their directions, without any change to the transformation table itself
([`07-transformations.md`](07-transformations.md)) or to any resolution roll
([ADR 0031](../adr/0031-fault-line-biases-exposure-not-the-transformation-table.md)).

### Thresholds and the hidden count

**A Taint threshold always forces a Transformation (body). It never forces an Affliction (mind).**
Afflictions are Trauma's business alone — they arise at 6+ Trauma, a separate track (§5) — and a
Taint threshold never produces one. The thresholds sit at every multiple of 3 (3, 6, 9, …), the
same interval the Wyrd-die bands above already use for the first two. Crossing one forces a roll
on the transformation table ([`07-transformations.md`](07-transformations.md)). The result
consumes Taint equal to its severity, dropping the character back below the threshold; if still
over, roll again — a loop that terminates by construction
([`07-transformations.md`](07-transformations.md),
[`check_transformation.py`](../../tools/check_transformation.py)).

On the **first** Transformation the engine **secretly rolls the hidden threshold** — how many
this character can endure. **The player never sees it.** Written to state once, so later
Transformations are narrated against a real countdown.

When it runs out the character is **lost**, and becomes a character the GM controls. They do not
leave the chronicle; they join the opposition.

Transformations carry **Dread** — Taint's cost is social as well as mechanical. The
transformed character's problem is being seen. Full detail —
the table, the threshold's roll and range, and Dread's magnitude and effect — lives in
[`07-transformations.md`](07-transformations.md).

---

## 5. Trauma, Fear and Strain

Three tiers of mental harm, distinguished by how long they last.

- **Strain** — today. From failed mental tests, terror, exhaustion. Recovered at a Rally.
- **Trauma** — long-term and sticky. **1 per critical taken**, 1 per failed Terror test, **1 per
  multiple of the character's maximum Stamina a failed system-of-power invocation's accumulated
  Strain now contains** — read against Strain's *current* total, which keeps accumulating through
  any run of successes without being checked or reduced; a success costs nothing extra at the
  moment it is rolled, but does not erase what it silently carried Strain past — the next failure
  settles the whole outstanding total, not only the span since that failure's own last point.
  Strain carries forward at its remainder past the highest multiple charged, not reset to zero
  ([`09-systems-of-power.md`](09-systems-of-power.md),
  [ADR 0047](../adr/0047-strain-threshold-crossing-checks-cumulative-strain.md)), more at the
  GM's discretion for genuinely terrible events.
- **Afflictions** — permanent. At **6+ Trauma**, test on every further point (a fiction-chosen
  skill, pass/fail only — [`08-afflictions.md`](08-afflictions.md)); on a failure take an
  Affliction and **lose 6 Trauma**. The track sawtooths, so a character can break many times
  across years — the same Affliction may recur, which is ordinary rather than a defect. Computed
  in [`08-afflictions.md`](08-afflictions.md): the long-run cadence is exactly 1 Affliction
  per 6 Trauma-adding events, independent of the test's skill, because the floor and the drop are
  the same number.

**Fear** prevents pressing an attack; **Terror** routs, and costs a Trauma point on a failure.
An Affliction is never described as an Affliction — it is described as behaviour.

---

## 6. Experience and advancement

The rate and ceiling are set by the setting's `power_curve`. The economy below is the same
either way.

### Advances are the currency

**1–3 per session**, awarded against **triggers**, never an XP total — so the engine can
verify an award rather than the GM being generous by accident.

| Trigger | Awarded when |
|---|---|
| **Learned** | you discovered something true about the world you did not know |
| **Drove** | you acted on a Drive **even though it cost you** |
| **Practised** | you met your career's own declared condition |
| **Endured** | you survived something that should have finished you |

One of each per session at most.

### Spending

| Cost | Buys |
|---|---|
| 1 | **+5%** to a skill your career grants, to that career's cap |
| 1 | **open** a new skill your career grants, at 25% |
| 1 | **change career**, to any entry career, or to a non-entry career whose prerequisites you satisfy, given a fictional reason |

That is the entire economy. No talent trees, no feats — their absence is deliberate
([ADR 0002](../adr/0002-source-material.md)).

### Careers

Careers form a **directed graph** — each entry career is choosable freely, and each non-entry
career declares the prerequisite career(s) completing any one of grants eligibility for it
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)). **Changing career is a free choice of
any entry career, or a legal move to a non-entry career you are currently eligible for** — a
character's own history of what they completed shapes what a non-entry career they can reach,
but never traps them: abandoning a career path entirely and starting over from a fresh entry
point is always legal, and the engine cannot grant a non-entry career your past does not permit.

**Every career caps its skills at 70%** — the top of the *expert* band ([`13-diegesis.md`](13-diegesis.md))
— one figure applied to every skill that career grants. No advance may raise a skill past its
career's cap; a career alone never buys the 75%+ band, "it is part of who you are."

**Completing a career** — every skill it grants at that 70% cap — is the only durable toughening:
**+1 maximum Stamina** and a permanent **Mark**, one small benefit that persists across every
later career. Depth is rewarded over breadth, and this is the whole power curve. Completion is
tracked **per career-instance**: a character who leaves a career unfinished and re-enters it
later starts a fresh instance and grants nothing for the one abandoned, but a career finished
twice across a lifetime — legal, since eligibility for a career, once earned, never expires —
grants its Stamina and Mark each time.

**Maximum Stamina stops climbing at 10.** Creation fixes the starting value at 6 because a further
+1 there is a 16.7% gain, and states directly that "much above 10 [...] the sentence stops being
true" ([`11-character-creation.md`](11-character-creation.md)) — a gain below 10% no longer
reads as durable toughening. Ten is exactly that boundary (1⁄10 = 10%), computed and asserted in
[`check_advancement.py`](../../tools/check_advancement.py). A career completed after maximum Stamina
reaches 10 still grants its Mark; it grants no further Stamina.

### What actually grows

Over a long chronicle these dominate, and none improves a die roll: **Reputation** (a score
with a label, rolled when you meet someone — being recognised may or may not help),
**Allegiances**, **Holdings**, **Knowledge**, **Bonds**.

A character ten years in is not harder to kill. They are harder to replace.

### Companions and succession

A companion's mechanical layer ([`16-session.md`](16-session.md)) advances rarely and simply —
one competence gained or limitation lost at a downtime, landing on that layer (typically `career`
widening what a test legally covers, or a wound's effect lessening — Mend already covers that
case). No career graph, no Marks.

A successor inherits none of the competence and all of the position
([`19-campaign.md`](19-campaign.md)): the new companion's mechanical layer starts at its own
baseline (no `wounds`, `bond: 0`, `taint: 0`, `strain: 0`) and their narrative layer is written
fresh, same as any new companion.

---

## 7. Danger scaling

Content is written once with a **danger rating** used as a multiplier inside it: a trap
written `Nd4` does `6d4` at danger 6, and enemy counts and skill values scale from the same
number. It is also written for a party of a stated size — `written_for`, a head count and never
a gate ([`26-corpus-index.md`](26-corpus-index.md)). Counts scale below; skill values scale in
points, further down. An opponent's own record never changes — what a written opponent carries is in
[`12-the-adversary.md`](12-the-adversary.md), and it is absolute.

Effective danger accounts for the party actually present:

> `danger_effective = danger × (party_effective / written_for)`

This is how a chronicle stays interesting for years **without escalating the fiction**. The
same village mystery runs in year one or year eight; the danger scales, the scope need not.

### What a party counts for

A head count is not an effective size, because the second body in a room is worth less than the
first and the tenth is worth less again.

> **The k-th body is worth `1/k`.** A party of `p` bodies has an effective size of
> `1 + 1/2 + 1/3 + … + 1/p`.

| Bodies | Effective size |
|---|---|
| 1 | 1.000 |
| 2 | 1.500 |
| 3 | 1.833 |
| 4 | 2.083 |
| 5 | 2.283 |
| 6 | 2.450 |

The sum is order-independent, so no roster order has to be invented and two people counting the
same party in different orders reach the same number.

**Both sides of the ratio are read through that same function.** `party_effective` is the
effective size of the party present; the denominator is the effective size of a party of
`written_for` bodies. Comparing an effective size with a raw head count would be comparing two
different things, and the identity case would never land: as it stands, **a table of four bodies
runs content written for four exactly as written**, which is what makes the equation a ratio
rather than a discount.

**The party is a query, not a roster.** It is the player character, who counts as one body, plus
every companion at `status: with-party` ([`22-state.md`](22-state.md)). A companion who is away,
dead, lost or departed counts for nothing, and no companion counts for more or less than any
other — the engine holds no capability score for a companion and this rule does not invent one.
Scaling happens when content is prepared, not when a door opens, so who is standing in a
particular room is never consulted.

**Where `written_for` is missing or zero, the content runs as written.** A record that never
stated a party size is not a record claiming a party of none.

### Rounding happens at the point of use

`danger_effective` is **never rounded**. It is carried exact, and each quantity built from it
rounds separately:

> **Round half up, and never below 1 where the written quantity was at least 1.**

A trap written `Nd4` always throws at least one die. Rounding `danger_effective` itself would
throw away precision that the multiplications afterwards need, and it goes wrong first at the
largest count in a piece of content — which is generally the fight.

A worked case: a danger-3 arc written for four, run by one character and two companions, is
three bodies against four. The ratio is `1.833 / 2.083`, or **0.88**, and `danger_effective` is
**2.64** — six cultists become five, three watchmen stay three.

### The skill values scale too, in points

A percentage cannot be multiplied by a ratio: 45 × 2.64 is not a skill. So the second quantity this
section scales resolves to a **points adjustment added to the opponent's percentage**, which is how
every other modifier in this engine works — the difficulty ladder in §1 is +20 to −40, not a
multiplier.

> **The adjustment is `15.5 × log₂(ratio)`, rounded to the nearest 5 and clipped to ±20.**

| party \ `written_for` | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| **1** | +0 | −10 | −15 | −15 | −20 | −20 |
| **2** | +10 | +0 | −5 | −5 | −10 | −10 |
| **3** | +15 | +5 | +0 | −5 | −5 | −5 |
| **4** | +15 | +5 | +5 | +0 | +0 | −5 |
| **5** | +20 | +10 | +5 | +0 | +0 | +0 |
| **6** | +20 | +10 | +5 | +5 | +0 | +0 |

Three properties, and none of them was chosen:

**The diagonal is +0.** Content written for four, run by four bodies, meets opponents at exactly
their written percentages. That is the identity case the ratio exists to preserve, and it now holds
on both quantities rather than on the count alone.

**The coefficient is fitted, not picked.** Across every party and `written_for` from one to six the
ratio runs `0.408` to `2.450` — exactly antisymmetric, because swapping the two inverts it. Require
the extreme of that computed range to land on the ladder's top rung and the coefficient falls out:
`20 / log₂(2.45)`. It was derived before it was written down, which is the only way a round number
in this repo means anything ([`27-tooling.md`](27-tooling.md)).

**The clip is symmetric at ±20**, not the ladder's −40, because the adjustment must negate when
party and `written_for` swap. A −40 floor against a +20 ceiling would break exactly that.

**An adjusted percentage floors at 0.** An opponent already at the untrained 10, in content written
for six, met by a lone character, takes the full −20 and would land below zero. A percentage is not
a negative number, and §1 already says what a test at or below zero is: it is not attempted.

The rounding step is **5** because that is the finest unit the engine moves a skill by at all (§6).
Rounding to the ladder's 10 preserves the identity case too, but discards a rung the engine can
express. Computed in
[`check_adversary.py`](../../specs/017-adversary-model/check_adversary.py).

### The retinue is not a difficulty setting

Effective size grows like a logarithm, so gathering bodies buys steadily less. Against content
written for four:

| Bodies | Ratio |
|---|---|
| 1 | 0.48 |
| 3 | 0.88 |
| 5 | 1.10 |
| 10 | 1.41 |
| 20 | 1.73 |

Five times the head count does not buy double the danger. The first companion buys 0.24; the
fifth buys 0.08.

**The curve is not overridable.** With the same function on both sides of the ratio, replacing it
on one side alone would break the identity case, and replacing it on both would cancel out. A
setting's levers over difficulty are the companions it grants and the `danger` its content
carries.
