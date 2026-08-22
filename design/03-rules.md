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

**Opposed tests:** both roll; the higher degree of success wins; ties to the defender. The acting side reads the
Wyrd die.

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

### Luck

A percentage the player *may choose* to test to dodge a misfortune or break a tie. Testing
Luck costs 1 Luck for the rest of the arc, pass or fail. Always the player's choice.

---

## 2. Combat

- Attacks are opposed tests. The winner rolls the weapon's damage.
- **Stamina is not meat.** It is cuts, bruises, and losing control of the fight.
- **Armour subtracts dice:** light `1d3`, modest `1d6`, heavy `2d6`. A shield raises one rank.
  A minimum of 1 always gets through.
- **Telling blow:** win by 3 or more degrees and the damage doubles.
- **Critical** when damage takes a combatant **below 0 Stamina**. Roll `1d6 + points below
  zero` on the table for the damage type. High results are lethal.
- Weapons are **casual** or **martial**. Martial weapons mark the bearer and are illegal in
  most civilised places — a social constraint that does real work.

**Mobs.** Each round a character also clears petty opponents weaker than themselves, so one
character plus companions can face a crowd without a roll per body.

**Death is deferred.** Nothing resolves during the fight; a combatant who drops is *out of
action*. Afterwards, roll on the **Aftermath** table. Most results are a lasting mark rather
than death — a permanent wound, a new enemy, capture, a disfigurement that frightens people,
a wound that recurs before every future fight. Deferred resolution is how a single-character
chronicle survives lethal combat.

---

## 3. Fate and Fortune

- **Fate** — few, permanent, spent to **avoid death**. Gone when spent; new ones are rare.
- **Fortune** — renewable daily, equal to the Fate score. Spend to reroll, defend again, or
  act sooner.

When Fate is spent the character **survives and is not better off**. The blow was glancing;
everything goes black; they wake later — tended by companions, or imprisoned, or stripped and
left in a ditch. The GM chooses where they wake, which makes Fate the chronicle's
course-correction tool as well as its anti-frustration valve.

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

Crossing a Taint threshold forces a **Transformation** (body) or an **Affliction** (mind).
The result consumes Taint equal to its severity, dropping the character back below the
threshold; if still over, roll again.

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
  take an Affliction and **lose 6 Trauma**. The track sawtooths, so a character can break
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
