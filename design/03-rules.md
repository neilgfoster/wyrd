# Wyrd — the ruleset

Percentile, narrative, and light enough to run one beat in a few lines of text.

Every label here is a **default**. A setting renames or disables what it likes
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)); nothing mechanical changes.

| Engine label | What it measures | Typical setting names |
|---|---|---|
| **Taint** | permanent accrual that transforms you at thresholds | Corruption · Shadow · Sin · Humanity |
| **Trauma** | long-term mental accrual, breaking into Afflictions | Insanity · Scars · Sanity |
| **Strain** | short-term pressure, recovered at a Rally | Stress · Fatigue · Wear |
| **Resolve** | the spendable counterweight to Taint | Hope · Faith · Nerve |
| **Fate** | the death valve | Fate · Luck · Destiny |
| **Transformation** | the permanent change at a Taint threshold | Mutation · Gift · Mark |
| **Affliction** | the lasting condition at a Trauma threshold | Derangement · Disorder |
| **Dread** | how frightening your changes make you to others | Fear points |
| **Ill Omen / Fair Omen** | the two Wyrd-die faces | Chaos Star / Comet · Peril / Grace |

---

**Naming rule.** An engine label must be *descriptive English*, not a term borrowed from a
source system. "Downtime" rather than a named phase from one game; "Ill Omen" rather than a
named die face from another. If a label only makes sense to someone who has read a
particular book, it belongs in that setting's `rename:` block, not here.

---

## 1. Resolution

> **Roll `d100`. Succeed at or under your `skill%`.**
> - **Degrees of success** — tens digit of the skill minus tens digit of the roll — give
>   magnitude.
> - **The units digit of the natural roll** is the **Wyrd die**: what else happened.

One roll, three independent axes, no extra dice. Rationale and rejected alternatives are in
[ADR 0001](adr/0001-resolution.md).

**Difficulty** modifies the *skill*, never the roll — which is what keeps the Wyrd die clean:

| Easy | Average | Challenging | Difficult | Hard | Very Hard |
|---|---|---|---|---|---|
| +20 | +0 | −10 | −20 | −30 | −40 |

**Untrained — a skill you do not have** is tested at a flat **10%**, before difficulty and
declaration. Anyone may try to shoot; almost nobody hits. The engine has no characteristics to fall
back on ([ADR 0013](adr/0013-the-engine-names-no-skill.md)), so this base is stated rather than
derived, and it sits inside the *you would be guessing* band
([`10-diegesis.md`](10-diegesis.md)).

| Attempting | At |
|---|---|
| untrained, average difficulty, said briefly | **10%** |
| untrained, easy, said briefly | **30%** |
| untrained, easy, specific and leveraging something established | **50%** |
| untrained, hard | impossible — the modifier takes it below zero |
| trained, average difficulty, said briefly | **25%** and up |

Having the skill is worth at least 15 points over not having it, at every difficulty. A setting may
mark a skill as **requiring training**, and then there is no untrained attempt at all — a language
you do not speak is not a 10% chance ([`03b-the-character.md`](03b-the-character.md)).

### Opposed tests

When someone resists, both roll — but not symmetrically.

1. **The acting side rolls first, and must succeed.** If they fail, the action fails. There is no
   comparison and the other side need not roll at all.
2. **Degrees exist only on a success.** A failed roll has no degrees, not negative ones.
3. **If the resisting side also succeeds, compare degrees.** The higher wins; **ties go to the
   resisting side**.
4. **The margin** is the difference in degrees, and it is what a rule like the telling blow reads.
5. **Only the acting side reads the Wyrd die.** One roll, one omen, however many dice were thrown.

The **acting side** is whoever is trying to change the situation; the other is resisting it. Where
neither is — two people racing for the same thing — it is not an opposed test, and the GM either
names an actor or calls for two ordinary tests.

Rule 2 is not a detail. Degrees are `tens(skill) − tens(roll)`, so a failure computes as a negative
number, and subtracting one *inflates* the margin. Left that way, roughly three quarters of
successful attacks would be telling blows — doubled damage as the ordinary case, invisible in the
prose. Recorded in [ADR 0016](adr/0016-opposed-tests-need-a-successful-actor.md) and computed in
[`check_opposed.py`](../specs/010-opposed-tests/check_opposed.py).

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
Computed in [`check_assistance.py`](../specs/011-assistance-and-group-tests/check_assistance.py) and
recorded in [ADR 0017](adr/0017-assistance-group-tests-and-extended-tasks.md).

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

### Luck

A percentage the player *may choose* to test to dodge a misfortune or break a tie. Testing
Luck costs 1 Luck for the rest of the arc, pass or fail. Always the player's choice.

---

## 2. Combat

### The exchange

- Attacks are opposed tests. The winner rolls the weapon's damage.
- **Stamina is not meat.** It is cuts, bruises, and losing control of the fight.
- **Armour subtracts dice:** light `1d3`, modest `1d6`, heavy `2d6`. A shield raises one rank.
  A minimum of 1 always gets through.
- **Telling blow:** win by 3 or more degrees and the damage doubles.
- **Critical** when damage takes a combatant **below 0 Stamina**. Roll `1d6 + points below
  zero` on the table for the damage type ([`03a-tables.md`](03a-tables.md)). High results are
  lethal.
- Weapons are **casual** or **martial**. Martial weapons mark the bearer and are illegal in
  most civilised places — a social constraint that does real work.

### Rounds and turn order

A **round** is the span in which every combatant acts once. It has no fixed length in the fiction;
it is as long as the exchange needs.

> **Whoever started the exchange acts first.** That side takes the whole first round, then the other
> side takes theirs.

Order costs no dice and needs no roll, which matters twice over: it keeps a round cheap in prose,
and the engine names no skill and has no characteristics
([ADR 0013](adr/0013-the-engine-names-no-skill.md)), so there is nothing an initiative roll could be
made against without inventing an attribute for the purpose.

Within a side, order is the fiction's and carries no mechanical weight — companions act where they
make sense, and nothing depends on which of them goes first.

**Where neither side started it** — a mutual encounter, both parties seeing each other at once — the
side already holding a weapon acts first. If both are armed, or neither is, the player's side acts
first. That last clause is the one rule here decided from outside the fiction, and it is stated
plainly rather than dressed up ([ADR 0018](adr/0018-combat-sequencing.md)).

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
([`check_sequencing.py`](../specs/012-combat-sequencing/check_sequencing.py)).

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
([`check_mobs.py`](../specs/013-the-mob-rule/check_mobs.py),
[ADR 0019](adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md)).

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
([`03a-2-aftermath.md`](03a-2-aftermath.md)) — once per combatant who dropped, companions
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
[`04-session.md`](04-session.md) exists to pose. What downtime cannot mend is a lasting wound, and
that is what **Mend** is for.

**Waking at 0 is not a second penalty.** The Aftermath table has already priced dropping; this says
only where the track restarts. Waking at any fraction of maximum would soften the same event twice,
in two places that would eventually disagree.

The road back is short enough to keep playing and long enough to be felt:

| | Rallies to full |
|---|---|
| dropped, Stamina 6 | **6** |
| dropped, Stamina 7 (a completed career) | 7 |
| one ordinary fight against an even opponent | 5.4 to 5.7 |
| one ordinary fight at a 20-point advantage | 2.3 to 3.6 |

An even fight costs nearly the whole track. That is the rule's real weight: a character who fights
an equal every beat never sees full Stamina again until a downtime, and one who picks their fights
recovers between them.

**Entering a fight short is the cost, and it is steep.** Against an opponent 20 points below them, a
character drops **14.8%** of the time at full Stamina and **48.6%** at 2 — the same fight, three
times as dangerous. Against an equal, dropping is near a coin flip whatever they walked in with,
which is a property of the damage scale rather than of this rule
([`check_recovery.py`](../specs/014-stamina-recovery/check_recovery.py),
[ADR 0020](adr/0020-stamina-recovers-on-the-clocks-the-engine-has.md)).

## 3. Fate and Fortune

- **Fate** — few, permanent, spent to **avoid death**. Gone when spent; new ones are rare.
- **Fortune** — renewable daily, equal to the Fate score. Spend to reroll, defend again, or
  act sooner.

When Fate is spent the character **survives and is not better off**. The blow was glancing;
everything goes black; they wake later — tended by companions, or imprisoned, or stripped and
left in a ditch. The GM chooses where they wake, which makes Fate the chronicle's
course-correction tool as well as its anti-frustration valve.

Mechanically, spending Fate **closes the death rows** of the Aftermath table: the result is
re-read on the worst row that is not death, and that is what the character carries away
([`03a-2-aftermath.md`](03a-2-aftermath.md), [ADR 0009](adr/0009-fate-closes-the-death-rows.md)).
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
  with them ([`04-session.md`](04-session.md)).

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

- **Resolve** — spendable, renewable. Spend for a bonus after a failed roll.
- **Taint** — accrues and sticks.

**When Resolve falls to equal Taint, the character is Spent** — they will not press a
struggle and will withdraw from danger. At Taint 0 they can never be Spent, however tired.

The same Taint score therefore means different things at different times, and recovery is
part of the loop rather than an afterthought.

### Gaining Taint

Three routes, deliberately in both directions:

1. **The Bargain** — you failed something that mattered and have no Fortune left. You may
   **choose** to take 1 Taint to reroll. Always the player's choice; the GM may mention the
   option exists and never applies it.
2. **Exposure** — resist with a test. Minor `1`, moderate `2`, major `3`, reduced by degrees
   of success. Sources are a setting matter, and should include **moral** ones as well as
   supernatural — giving in to despair or cruelty is exposure.
3. **Invocation** — before a roll, the GM may **spend one of the character's Taint points** to
   impose a penalty, narrating how it surfaces. Maximum one per check, and it *consumes* the
   point, so it cannot be leaned on.

### Fault Line

Taint is **specific, not generic**. Each character has a Fault Line derived at creation from
their Drives and Misfortune. It names *how* they fall — the direction, not only the quantity.

### Thresholds and the hidden count

Crossing a Taint threshold forces a **Transformation** (body) or an **Affliction** (mind),
rolled on the tables for each ([`03a-tables.md`](03a-tables.md)). The result consumes Taint equal
to its severity, dropping the character back below the threshold; if still over, roll again.

On the **first** Transformation the engine **secretly rolls the hidden threshold** — how many
this character can endure. **The player never sees it.** Written to state once, so later
Transformations are narrated against a real countdown.

When it runs out the character is **lost**, and becomes a character the GM controls. They do not
leave the chronicle; they join the opposition.

Transformations carry **Dread** — Taint's cost is social as well as mechanical. The
transformed character's problem is being seen.

---

## 5. Trauma, Fear and Strain

Three tiers of mental harm, distinguished by how long they last.

- **Strain** — today. From failed mental tests, terror, exhaustion. Recovered at a Rally.
- **Trauma** — long-term and sticky. **1 per critical taken**, 1 per failed Terror test, more
  at the GM's discretion for genuinely terrible events.
- **Afflictions** — permanent. At **6+ Trauma**, test on every further point; on a failure
  take an Affliction ([`03a-tables.md`](03a-tables.md)) and **lose 6 Trauma**. The track
  sawtooths, so a character can break
  many times across years.

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
| 1 | **change career**, to a legal exit, given a fictional reason |

That is the entire economy. No talent trees, no feats — their absence is deliberate
([ADR 0002](adr/0002-source-material.md)).

### Careers

Careers form a **directed graph**: each declares its entries and exits
([`14-entities.md`](14-entities.md)). You may only move to a legal exit, so a career history
is a biography, and the engine cannot grant a career your past does not permit.

**Completing a career** — every granted skill at its cap — is the only durable toughening:
**+1 maximum Stamina** and a permanent **Mark**, one small benefit that persists across every
later career. Depth is rewarded over breadth, and this is the whole power curve.

### What actually grows

Over a long chronicle these dominate, and none improves a die roll: **Reputation** (a score
with a label, rolled when you meet someone — being recognised may or may not help),
**Allegiances**, **Holdings**, **Knowledge**, **Bonds**.

A character ten years in is not harder to kill. They are harder to replace.

### Companions and succession

Companions advance rarely and simply — one competence gained or limitation lost at a
downtime. No career graph, no Marks.

A successor inherits none of the competence and all of the position
([`05-campaign.md`](05-campaign.md)).

---

## 7. Danger scaling

Content is written once with a **danger rating** used as a multiplier inside it: a trap
written `Nd4` does `6d4` at danger 6, and enemy counts and skill values scale from the same
number.

Effective danger accounts for the party actually present:

> `danger_effective = danger × (party_effective / written_for)`

This is how a chronicle stays interesting for years **without escalating the fiction**. The
same village mystery runs in year one or year eight; the danger scales, the scope need not.
