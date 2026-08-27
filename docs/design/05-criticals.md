# Criticals

The table a combatant rolls **the moment a blow takes them below 0 Stamina**. It is what
[`03-rules.md`](03-rules.md) means by *high results are lethal*, and it is the only place in the
ruleset where the **damage type** of a blow does any work.

There is one table per damage type, because a puncture and a bruise are not the same injury and the
ruleset has been telling the GM to roll "on the table for the damage type" since it was written.

It is a family of the kind [`04-tables.md`](04-tables.md) defines, and everything below is
declared within those conventions.

---

## The roll

| | |
|---|---|
| **key** | `critical-<type>` — one table per damage type |
| **die** | `1d6` |
| **modifier** | `+ points below zero` |
| **lowest possible total** | `2` |
| **uniqueness** | repeatable |
| **extra row fields** | none |

**The modifier is how far the blow overshot.** A combatant driven to −1 reads the top of the table;
one driven to −11 reads most of the way down it. The same count of points below zero, multiplied by
five, is what modifies the Aftermath roll ([`06-aftermath.md`](06-aftermath.md)) — one measured
quantity, read twice, rather than two measurements of the same blow that could disagree.

**The lowest possible total is 2**, not 1: the die's lowest face is 1, and a critical means at least
one point below zero. Every table's first row starts at 2, because
[`04-tables.md`](04-tables.md) requires a family's ranges to begin at its lowest possible total.

**The last row of every table is open at the top** because the modifier is unbounded above. The
largest modifier the rules can produce is **24** — a doubled telling blow from the heaviest weapon in
the band, against an unarmoured combatant with nothing left — and a table with a highest row would
run off the end well before that.

**The family is repeatable.** Taking the same wound twice across a decade is taking it twice. Because
it is repeatable, the *when a unique family runs out* clause of [`04-tables.md`](04-tables.md) does
not apply, and this family declares no exhaustion outcome.

**The family declares no extra row field.** No rule consumes a critical's severity — Taint is
consumed by transformations and afflictions, not by wounds — and a field nothing reads is how a table
goes quietly stale.

---

## The damage types

The engine ships **four**, named for the **shape of the wound** rather than for a weapon or an
element:

| Type | Key | The wound is |
|---|---|---|
| **Slashing** | `critical-slashing` | opened along its length — it bleeds, and it shows |
| **Piercing** | `critical-piercing` | narrow and deep — it reaches what is behind the surface |
| **Blunt** | `critical-blunt` | crushed — nothing is opened, and something is broken |
| **Searing** | `critical-searing` | burned — the tissue is destroyed rather than parted |

Naming by wound shape is what keeps the set setting-agnostic. A taxonomy of weapons would need
extending for every setting's armoury; a taxonomy of elements would carry a genre in with it. A wound
shape is a fact about a body, and every setting has bodies.

**Searing is the flexible one, on purpose.** It is fire in one setting, a beam weapon in another,
acid or cold or a current in a third. A setting whose fiction has none of those renames it to the
one thing it does have, or declares no weapon of that type and never rolls on the table
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)). A setting may not add a fifth type: the
set is closed, and a weapon declaring a type the engine does not publish is a load error rather than
a table quietly skipped.

The decision and the sets rejected are in
[ADR 0022](../adr/0022-four-damage-types-named-for-the-wound.md).

---

## What the tables differ in

They share the die, the modifier and the row schema. They differ in **where each becomes mortal and
what each leaves behind** — and that difference is the reason the family holds four tables instead of
one:

| | Kills at | Leaves behind |
|---|---|---|
| **Piercing** | soonest | least — it reaches deep and disturbs little on the way |
| **Slashing** | readily | what can be seen, and what will not close |
| **Searing** | less readily | what is looked at afterwards |
| **Blunt** | last | most — it breaks what it lands on |

If the four carried identical ranges and differed only in wording, damage type would be a rename
wearing a mechanic's costume, and the ruleset's instruction to roll *on the table for the damage
type* would mean nothing. Computed at the modifiers that actually occur, the four differ by a factor
of seven in how often they are mortal and by twenty points in how often they leave nothing at all
(below).

---

## The tables

Every row carries **range**, **key**, **effect** and **description**, per
[`04-tables.md`](04-tables.md). The key is engine vocabulary and never rendered to the player. The
descriptions say only what happened; what it *feels* like is the setting's
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)).

### `critical-slashing`

| Range | Key | Effect | Description |
|---|---|---|---|
| **2–5** | `slashing-glancing` | nothing lasting | It opens skin and no more. |
| **6–9** | `slashing-scored` | one wound record, effect `dread: +1` | It will be seen for the rest of your life. |
| **10–13** | `slashing-opened` | one wound record, effect `skill: -5` | It is deep, and it does not close cleanly. |
| **14–17** | `slashing-hamstrung` | one wound record, effect `skill: -10` | Something that moved you was cut. |
| **18–20** | `slashing-maimed` | one wound record, effect `stamina_max: -1` and `dread: +1` | Part of you is gone. |
| **21+** | `slashing-mortal` | **mortal** | You are opened, and it will not stop. |

### `critical-piercing`

| Range | Key | Effect | Description |
|---|---|---|---|
| **2–4** | `piercing-grazed` | nothing lasting | It goes past you. |
| **5–8** | `piercing-punctured` | one wound record, effect `skill: -5` | It went in, and it aches when you use it. |
| **9–12** | `piercing-transfixed` | one wound record, effect `stamina_max: -1` | It went through. |
| **13–15** | `piercing-organ` | one wound record, effect `stamina_max: -1` and `skill: -5` | It reached something you need. |
| **16–18** | `piercing-collapsed` | one wound record, effect `stamina_max: -2` | You do not draw a full breath again. |
| **19+** | `piercing-mortal` | **mortal** | It found the middle of you. |

### `critical-blunt`

| Range | Key | Effect | Description |
|---|---|---|---|
| **2–6** | `blunt-winded` | nothing lasting | You lose the wind and the next moment. |
| **7–11** | `blunt-cracked` | one wound record, effect `skill: -5` | Something is cracked, and you will feel it turning over. |
| **12–15** | `blunt-broken` | one wound record, effect `skill: -10` | A bone is broken. |
| **16–19** | `blunt-shattered` | one wound record, effect `stamina_max: -1` and `skill: -5` | It did not break cleanly, and it will not set. |
| **20–23** | `blunt-concussed` | one wound record, effect `stamina_max: -2` | You lose time, and some of it does not come back. |
| **24+** | `blunt-mortal` | **mortal** | Something inside gave way. |

### `critical-searing`

| Range | Key | Effect | Description |
|---|---|---|---|
| **2–5** | `searing-scorched` | nothing lasting | It hurts far more than it harms. |
| **6–9** | `searing-blistered` | one wound record, effect `dread: +1` | The skin does not grow back the same. |
| **10–13** | `searing-seared` | one wound record, effect `skill: -5` | It reaches under the skin, and stays reached. |
| **14–17** | `searing-scarred` | one wound record, effect `dread: +2` | People will look, and then stop looking. |
| **18–21** | `searing-charred` | one wound record, effect `stamina_max: -1` and `dread: +1` | It burned down to something that does not regrow. |
| **22+** | `searing-mortal` | **mortal** | Too much of you is burned. |

### Reading a result

1. Roll `1d6`. Add the points below zero the blow drove the combatant to.
2. Find the row whose range contains the total, **on the table for the damage type**.
3. Apply the row's effect. Say its description.
4. Record the outcome with the table's key.

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "table": "critical-slashing",
 "roll": 4, "modifier": 11, "total": 15, "row": "slashing-hamstrung"}
```

**Effects come from a closed set** — the same one [`06-aftermath.md`](06-aftermath.md) already
declares, so a critical writes the wound record every other rule already knows how to read, and the
**Mend** undertaking ([`16-session.md`](16-session.md)) already knows how to step it:

| `effect` | Applies |
|---|---|
| `stamina_max: -N` | a permanent reduction to maximum Stamina |
| `skill: -N` | a penalty to the skill the wound bears on — to the *skill*, never to the roll |
| `dread: +N` | the Dread track — this is a wound other people can see |
| `mortal` | the blow was a killing one. It is answered after the fight (below) |

An effect naming anything else is a load error, not a row quietly ignored. **No row charges Trauma**
(below).

---

## When it is rolled

**The moment the blow lands**, during the fight — which is what separates this table from Aftermath.
A critical says what the blow *did*; nothing about it waits.

**Once per critical taken.** A combatant who is taken below zero twice in one fight rolls twice, on
whatever table the blow that did it calls for.

**Everyone rolls on these tables** — the player's character, companions, and opponents alike. There
is no separate table for an opponent, and the rows answer for them without a special case.

**A critical costs 1 Trauma**, by [`03-rules.md`](03-rules.md) §5, charged once for the critical
itself. **No row on any of these tables charges Trauma**, because a row that did would price one blow
twice, and the two counts would eventually disagree.

---

## The mortal blow

The worst row of every table is `mortal`. It does **not** kill during the fight.

> A combatant carrying a mortal blow has their **Aftermath result read on the `death` row**, whatever
> the dice said.

This is the mirror of the re-read [`06-aftermath.md`](06-aftermath.md) already publishes for a
spent Fate point — one mechanism, running in both directions — and it is what lets *high results are
lethal* be true without a second, quieter way to die mid-fight:

| | Says | When |
|---|---|---|
| **The critical** | what the blow did | as it lands |
| **The mortal row** | that it was a killing blow | as it lands |
| **Aftermath** | what it cost | after the fight |

**Everything that closes a death still closes this one.** A spent Fate point re-reads it onto the
worst non-death row — the recurring wound — and `mortality: low` closes the death rows for everyone,
always. A mortal critical is not a way around Fate; it is a way *into* the row Fate answers.

**A mortal blow adds nothing to the Aftermath roll.** Aftermath declares one modifier and keeps it. A
bonus to the total was the obvious alternative and was rejected: it would give a one-modifier family
a second modifier, and it would make a mortal blow *probably* fatal rather than fatal, which is a
different rule wearing the same name.

The decision and its rejected alternatives are in
[ADR 0023](../adr/0023-a-critical-never-kills-during-the-fight.md).

---

## What the numbers actually are

Computed across the whole weapon band (`1d3`, `1d6`, `1d8`, `2d6`), all four armour ranks, the
telling blow's doubling, and every remaining Stamina a real character has — not at a midpoint
([`check_criticals.py`](../../specs/015-damage-type-criticals/check_criticals.py)).

**The modifier is small far more often than it is large.** Half of all criticals carry a modifier of
**4 or less**, and the median is **4**:

| Points below zero | Share of criticals | Cumulative |
|---|---|---|
| 1 | 23.3% | 23.3% |
| 2 | 12.9% | 36.2% |
| 4 | 9.4% | 56.7% |
| 8 | 4.6% | 81.3% |
| 12 | 2.2% | 93.2% |
| 20 or more | 0.5% | — |

That distribution is why every table's first two rows are the wide ones. A critical is an ordinary
event in this ruleset, and a table that only reads well at its bottom would be a table nobody
reaches.

**What each table weighs**, over the modifiers that actually occur:

| Table | Nothing lasting | A lasting mark | Mortal |
|---|---|---|---|
| `critical-piercing` | 17.8% | 78.6% | **3.6%** |
| `critical-slashing` | 27.2% | 70.9% | 1.8% |
| `critical-searing` | 27.2% | 71.5% | 1.3% |
| `critical-blunt` | **38.0%** | 61.5% | 0.5% |

Piercing is seven times likelier to be mortal than blunt; blunt is more than twice as likely to leave
nothing behind. That is the difference between four tables and one table said four ways, and it is
computed rather than asserted.

**What criticals do to lethality overall.** A drop already ends in death some of the time, through
Aftermath. Adding the mortal row moves that by **under a single percentage point**:

| | Chance a drop ends in death |
|---|---|
| Aftermath alone | 16.3% |
| …with `critical-blunt` | 16.3% |
| …with `critical-piercing` | 17.2% |

**16.3% is not a correction to the 23% Aftermath publishes**; it is a different question about the
same table. That 23% is unweighted across drops of one to twelve, and this figure weights each drop
by how often it actually happens — and light drops dominate. Both are computed in
[`check_criticals.py`](../../specs/015-damage-type-criticals/check_criticals.py), which fails if either
moves.

**A combatant dropped by one point cannot be killed by any of these tables.** The highest total they
can reach is 7, and the earliest mortal row begins at 19. As with Aftermath, a light knockdown is
survivable by construction rather than by luck.

---

## What this table does not touch

**Trauma.** Charged once by [`03-rules.md`](03-rules.md) §5, per critical taken. Not by a row.

**Being out of action.** A combatant below 0 Stamina is out of action until the fight ends, by
[`03-rules.md`](03-rules.md) §2. That is the drop, not the critical, and it happens whether the
critical rolls a 2 or a 24.

**Stamina recovery.** How a character gets back up is [`03-rules.md`](03-rules.md) §2's — 1 at each
Rally, full at a downtime. A critical says what the blow did, never how long it takes to walk it off.

**What the fight cost.** That is Aftermath's, and only Aftermath's.

---

## What a setting may replace

The **rows** — their ranges, effects and descriptions — by naming a table under `overrides.tables:`
in `setting.yaml` ([`24-authoring-a-setting.md`](24-authoring-a-setting.md)):

```yaml
overrides:
  tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}
```

A setting may **not** change the die, the modifier, the uniqueness, the row schema, the closed set of
damage types, or the mortal blow's composition with Aftermath. The last of those is a mechanism Fate
depends on, and a setting that moved it would change what a Fate point buys. Lethality is already a
setting's to set, through `mortality`.

**A setting renames a type it has no fiction for**, and the rename is presentation-only: the key and
the effect are what reach state, and a rename never touches either
([`04-tables.md`](04-tables.md)).

**Table changes apply forward.** A result already rolled stands as it was rolled, and no history is
recomputed ([`29-evolution.md`](29-evolution.md)).
