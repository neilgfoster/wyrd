# Aftermath

The table a combatant rolls on **after** the fight, once they have dropped. It is what
[`03-rules.md`](03-rules.md) means by *death is deferred*: nothing resolves while the fight is
running, and what dropping actually cost is settled when it is over.

This is the load-bearing table in the ruleset. Deferred resolution is how a single-character
chronicle survives lethal combat, and most of what this table says is a lasting mark rather than
death.

It is a family of the kind [`03a-tables.md`](03a-tables.md) defines, and everything below is declared
within those conventions.

---

## The roll

| | |
|---|---|
| **key** | `aftermath` |
| **die** | `d100` |
| **modifier** | `+ (5 × points below zero)` |
| **lowest possible total** | `6` |
| **uniqueness** | repeatable |
| **extra row fields** | none |

**The modifier is the number the ruleset has already computed.** A critical happens when damage takes
a combatant below 0 Stamina, and the critical table reads `1d6 + points below zero`
([`03-rules.md`](03-rules.md)). That same count of points below zero modifies this roll, so a
combatant who dropped by one reads a different part of the table from one who was nearly cut in half.
The alternative — a flat roll — would make every knockdown equally survivable and would throw away a
distinction the ruleset already draws.

**The lowest possible total is 6**, not 1: the die's lowest face is 1, and a critical means at least
one point below zero, so the smallest modifier is 5. The first row starts at 6 because
[`03a-tables.md`](03a-tables.md) requires a family's ranges to begin at its lowest possible total,
and 6 is that total.

**The last row is open at the top** because the modifier is unbounded. A hard enough blow runs off
the end of any table with a highest row, and the worst row absorbs everything above it.

**The family is repeatable.** Being left for dead twice across a decade is being left for dead twice;
nothing here is a slot that can only be filled once. Because it is repeatable, the *when a unique
family runs out* clause of [`03a-tables.md`](03a-tables.md) does not apply to it, and this family
declares no exhaustion outcome.

**The family declares no extra row field.** Transformations and Afflictions carry a severity because
a rule consumes Taint equal to it; nothing consumes anything equal to an Aftermath severity, and a
field no rule reads is how a table goes quietly stale.

---

## When it is rolled

**After the fight, never during it.** A combatant who drops is *out of action* and stays that way
until the fighting stops. This is the whole content of deferred death: the fight resolves as a fight,
and its cost is counted afterwards.

**Once per combatant who dropped**, however many times they went down in that fight. The roll answers
what the fight cost them, not how many times it knocked them over.

**Order does not matter.** Where several combatants are down, they may be resolved in any order; no
result depends on another's.

**Everyone who dropped rolls** — the player's character and companions alike, on this table, with
this modifier, against these rows.

### The boundary with criticals

Two tables answer one blow, and they answer different questions:

| | Criticals | Aftermath |
|---|---|---|
| **When** | during the fight, the moment a combatant goes below 0 | after the fight ends |
| **How many** | one per critical taken | one per combatant who dropped |
| **Which table** | one per damage type | one, for everyone |
| **Answers** | what the blow did | what it cost |

A critical describes the wound as it lands. Aftermath describes what the character is left carrying.

**A critical never kills during the fight.** The worst row of every critical table marks the blow
**mortal**, and a combatant carrying a mortal blow has their result here **read on the `death` row**,
whatever the dice said — the mirror of the re-read a spent Fate point performs (below). Nothing about
that changes this table's die, its modifier, or when it is rolled
([`03a-1-criticals.md`](03a-1-criticals.md),
[ADR 0023](adr/0023-a-critical-never-kills-during-the-fight.md)).

---

## The table

| Range | Key | Effect | Description |
|---|---|---|---|
| **6–30** | `out-of-action` | nothing lasting | You wake when it is over. |
| **31–52** | `lasting-wound` | one wound record | Something did not mend. |
| **53–66** | `left-for-dead` | one wound record; the character wakes elsewhere, without what they carried | You wake somewhere else, and your belongings are gone. |
| **67–78** | `new-enemy` | one wound record; a `character` entity with `role: nemesis` | Someone made a point of you. |
| **79–88** | `taken` | captured; a `thread` entity opens | You wake held. |
| **89–98** | `disfigured` | one wound record, effect `dread: +1` | Your face is not what it was. |
| **99–110** | `recurring-wound` | one wound record with `recurring: true`, effect `skill: -10` | It wakes before every fight after this one. |
| **111+** | `death` | death | You do not get up. |

The **key** is what a recorded outcome names, so a reader years later can resolve a log line to a
row. It is engine vocabulary and never rendered to the player; the description is what is said at
the table.

Descriptions are the engine's defaults and say only what happened. What it *feels* like is the
setting's ([`13-authoring-a-setting.md`](13-authoring-a-setting.md)) — a setting may rewrite every
word of this column without touching what any row does.

### Reading a result

1. Roll `d100`. Add `5 ×` the points below zero the combatant dropped by.
2. Find the row whose range contains the total.
3. Apply the row's effect. Say its description.
4. Record the outcome with the table's key.

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "table": "aftermath",
 "roll": 74, "modifier": 25, "total": 99, "row": "recurring-wound", "fate_spent": false}
```

`fate_spent` is recorded because Fate changes which row is *applied* without changing what was
*rolled*, and because declining to spend is itself a decision the chronicle should remember
([`03-rules.md`](03-rules.md)).

### What the rows weigh

[`03-rules.md`](03-rules.md) claims most results are a lasting mark rather than death. Computed
against the rows above, across drops of one to twelve points below zero:

| Dropped by | A lasting mark | Death | Nothing lasting |
|---|---|---|---|
| 1 | 75% | 0% | 25% |
| 3 | 80% | 5% | 15% |
| 6 | 80% | 20% | 0% |
| 9 | 65% | 35% | 0% |
| 12 | 50% | 50% | 0% |

Unweighted across that range: **a lasting mark 71%, death 23%**. The claim holds.

Two things follow that are worth stating rather than leaving to be discovered:

- **A combatant dropped by one or two points cannot die on this table at all.** The highest totals
  they can reach are 105 and 110, and death begins at 111. A light knockdown is survivable by
  construction rather than by luck — which is what deferred death is for.
- **Death overtakes marks past a drop of twelve** — a blow that beat a typical character's whole
  remaining Stamina twice over. Death is uncommon on this table; it is not rare at every blow, and
  saying so would be false.

These numbers are computed, not asserted. Probability claims in this ruleset have been wrong before
and were caught only by computing them.

---

## The lasting wound

Several rows leave a **wound record** — an entry in the character's `wounds` list
([`06-state.md`](06-state.md)). It is what makes a permanent mark a thing state holds rather than a
sentence somebody said once.

```yaml
wounds:
  - id: the-knee-that-never-set   # kebab-case, unique on this character, stable forever
    from: {table: aftermath, beat: 412}
    effect: {skill: -10}
    recurring: false
    description: "the knee never set right"
```

| Field | Holds |
|---|---|
| `id` | identifies this wound for the life of the chronicle, so a later rule can name exactly one |
| `from` | the table and beat that produced it — a wound outlives the log line that recorded it |
| `effect` | the mechanical consequence, applicable without reading the prose |
| `recurring` | whether the wound fires again at the start of every fight |
| `description` | what is said at the table; never reaches state as a mechanic |

**Effects come from a closed set.** Every one names a mechanic the engine already knows:

| `effect` | Applies |
|---|---|
| `stamina_max: -N` | a permanent reduction to maximum Stamina |
| `skill: -N` | a penalty to the skill the wound bears on — to the *skill*, never to the roll ([`03-rules.md`](03-rules.md)) |
| `dread: +N` | the Dread track — this is a wound other people can see |

An effect naming anything else is a load error, not a row quietly ignored.

**A wound record carries no duration and no severity**, and it does not need them: a wound lasts
until something mends it, and what mends it is the **Mend** undertaking
([`04-session.md`](04-session.md)), which moves one named wound's effect one grade per downtime
spent. A wound whose effect reaches nothing gains `closed:` — the record is kept and marked, never
deleted, because history is never recomputed ([`09-evolution.md`](09-evolution.md)).

**A recurring wound is the exception, and never closes** (below).

**Wounds are rendered diegetically** ([`10-diegesis.md`](10-diegesis.md)). The knee never set right;
never `skill: -10`.

---

## The recurring wound

One row is not a result at all but an ongoing condition: a wound record with `recurring: true`.

| | |
|---|---|
| **Fires** | when a fight begins, before the first roll |
| **Effect** | `−10` to the skill the wound bears on, for that fight |
| **Between fights** | nothing |
| **Duration** | the rest of the chronicle. Mend cannot reach it |
| **Stacking** | the family is repeatable, so a character may carry more than one; each fires |

**`−10` is not a new number.** It is the *Challenging* step the difficulty table already publishes,
and difficulty modifies the skill rather than the roll ([`03-rules.md`](03-rules.md)) — so a
recurring wound makes the character worse at fighting and leaves the Wyrd die clean. Nothing new has
to be learned to apply it.

It fires without a test, deliberately. A wound flaring for the two-hundredth time is not dramatic,
and the ruleset only rolls when it is.

**It is the one wound the Mend undertaking cannot touch.** Every other wound steps toward nothing
over enough seasons; this one does not, because re-reading a `death` result onto it is precisely
what a spent Fate point buys (below). A rule that let a downtime erase it would price Fate's promise
at one season and quietly undo the argument the death rows close on
([ADR 0021](adr/0021-mending-steps-and-the-recurring-wound-does-not.md)).

---

## Closing the death rows

Two things can take death off this table for a character. Both work the **same way**, and the way is
deterministic — no second roll, no judgement call:

> A `death` result is re-read on the **worst non-death row**, and that row's effect is applied
> instead.

In practice that is the recurring wound. The character survives, and carries something that wakes
before every fight for the rest of their life.

A mortal critical arrives at the same rows from the other direction, and Fate answers it the same
way: a mortal blow fixes the result at `death`, and a spent Fate point re-reads that `death` onto the
worst non-death row. A mortal blow is not a way around Fate; it is a way into the row Fate answers
([`03a-1-criticals.md`](03a-1-criticals.md)).

| Closed by | Condition |
|---|---|
| **A spent Fate point** | the player spends one. For a companion, the player's character must be **present and able to act**, and spends their own ([`03-rules.md`](03-rules.md)). |
| **`mortality: low`** | the setting's tone contract. The death rows are closed for everyone, always. |

**This is what makes Fate's promise mechanical.** [`03-rules.md`](03-rules.md) already says a
character who spends Fate survives and is **not better off**. If Fate simply cancelled the roll, that
promise would be prose with nothing under it. Re-reading on the worst row is the promise, applied.

**Fate may only be spent against a `death` result.** It does not improve any other row, it is never
spent at a distance, and it buys against dice rather than against agendas — the boundaries
[`03-rules.md`](03-rules.md) already draws. A character with no Fate, or a player who declines to
spend, takes the row as rolled.

**`mortality` does not modify the roll.** The tone contract governs how this table is *applied*
([`01-principles.md`](01-principles.md)), and closing the death rows is an application rule. Making
it an adjustment to the total instead was tried and fails twice over: at `mortality: low` the lowest
possible total drops below the first row, so the table no longer loads, and at `mortality: high` a
combatant who dropped by a single point can reach the death row — destroying the exact property
deferred death exists to provide. The decision and its rejected alternatives are in
[ADR 0009](adr/0009-fate-closes-the-death-rows.md).

---

## Companions

**Companions roll on this table**, with the same modifier, against the same rows. There is no
companion table, no companion row, and no companion modifier.

The asymmetry the engine wants is already there and does not need helping: **companions have no Fate
of their own**. A death result stands for them unless the player's character is present, able to act,
and spends a Fate point on their behalf. That is what makes companions the chronicle's reliable
source of loss — they lack the valve, not because the dice are weighted against them.

Weighting the dice as well would count the same fragility twice, and the two would eventually
disagree.

A companion's outcome moves their existing `status` ([`06-state.md`](06-state.md)): `dead` where a
death result stands, `away` while they are held. No new status value is introduced.

---

## What this table does not touch

**Trauma.** A critical already costs 1 Trauma when it is taken ([`03-rules.md`](03-rules.md)).
Awarding more here would charge the same blow twice.

**Stamina recovery.** How a character gets back up is [`03-rules.md`](03-rules.md) §2's: a
combatant who dropped wakes at 0 and recovers 1 at each Rally, or to maximum at a downtime. This
table says what the fight cost, never how long the bruises take.

---

## What a setting may replace

The **rows** — their ranges, effects and descriptions — by naming the table under
`overrides.tables:` in `setting.yaml` ([`13-authoring-a-setting.md`](13-authoring-a-setting.md)):

```yaml
overrides:
  tables: {aftermath: setting/rules/tables/aftermath.yaml}
```

A setting may **not** change the die, the modifier, the uniqueness, the row schema, or how the death
rows close. The last of those is a mechanism Fate depends on, and a setting that moved it would
change what a Fate point buys. Lethality is already a setting's to set, through `mortality`.

**Table changes apply forward.** A result already rolled stands as it was rolled, and no history is
recomputed ([`09-evolution.md`](09-evolution.md)).
