# Wyrd — character creation

The procedure that turns a setting's declared options into a playable character. It is run once
per chronicle, at bootstrap ([`29-chronicle-bootstrap.md`](29-chronicle-bootstrap.md)), and it must
produce the same character shape every time — two runs that disagree are a bug, not a flourish.

**The procedure is the engine's. The options are the setting's.** There is one procedure, not an
engine one and a setting one.

---

## 1. The steps, in order

| | Step | Where the content comes from |
|---|---|---|
| 1 | **Choose a career.** Any the setting marks as an entry point. | the setting's career graph ([`26-authoring-a-setting.md`](26-authoring-a-setting.md)) |
| 2 | **Spend 8 advances** inside that career, opening and raising skills. This is the character's background. | §3 |
| 3 | **Choose a Loyalty**, from those the setting declares. | the setting's Loyalties ([`16-session.md`](16-session.md)) |
| 4 | **Set Stamina** to 6, current and maximum. | engine, §2 |
| 5 | **Set Luck** to 40, current and maximum. | engine, §2 |
| 6 | **Set Fate** from the setting's `mortality`. Fortune equals it. | engine, §2 |
| 7 | **Set the tracks** the setting has not disabled to zero. | [`03-rules.md`](03-rules.md) §4–5 |
| 8 | **Name them, and place them.** Name, a Drive, a Misfortune, a Bond, and where they are from. | the setting's name, Drive and Misfortune tables |
| 9 | **Write the Fault Line** — one sentence naming the direction Taint pulls this character, from the Drive and Misfortune chosen above. | engine, §1 below |

Steps 4–7 are fixed. Steps 1, 2, 3, 8 and 9 read setting data or the choices already made and cannot
be completed without them.

**Nothing is rolled.** No characteristics exist to roll ([ADR 0013](../adr/0013-the-engine-names-no-skill.md)),
Stamina and Luck are flat, and skills come from the career. A character is *chosen*, not generated —
see [ADR 0014](../adr/0014-character-creation-is-chosen-not-rolled.md).

Of step 8, the **Drive**, the **Misfortune** and the **Bond** carry mechanical weight — a Drive can be
invoked for −20 ([`03-rules.md`](03-rules.md) §1), a Misfortune feeds the Fault Line (step 9) and
seeds a Threat at chronicle creation ([`18-campaign.md`](18-campaign.md)), and a Bond is a real
relationship ([`16-session.md`](16-session.md)). The name and the place of origin are fiction, and
the engine never reads them. Where a character is *from* shows up mechanically in step 3, not here.

**The Fault Line (step 9) is written, not chosen from a list.** It names the direction Taint pulls
this character — how they fall, not how much ([`03-rules.md`](03-rules.md) §4) — and it is one
sentence combining the Drive and the Misfortune just chosen: what they want, and what already works
against them, read together. No roll and no table decide it; the GM and player agree the sentence at
the table, the same judgment call the GM already makes to invoke a Drive. A setting may replace the
free sentence with a lookup from its own taxonomy — deriving the Fault Line from a culture rather
than a Drive, say — as a **retune**, since the mechanism the Fault Line feeds does not change
([`26-authoring-a-setting.md`](26-authoring-a-setting.md)).

## 2. The starting values

| | Value | Why |
|---|---|---|
| **Skills** | **8 advances**, spent inside the starting career, opening at least two skills | creation uses the same doors play uses ([`03-rules.md`](03-rules.md) §6) and invents none |
| **Stamina** | **6**, current and maximum | derived; see below |
| **Luck** | **40**, current and maximum | a test must fail more often than it succeeds, and still have something to erode |
| **Fate** | by `mortality`: `low` **2**, `standard` **3**, `high` **4** | the tone contract sets it ([`01-principles.md`](01-principles.md)) |
| **Fortune** | equal to Fate, renewed daily | [`03-rules.md`](03-rules.md) §3 |
| **Taint, Trauma, Strain, Resolve, Dread** | 0 | nothing has happened yet |
| **Loyalty** | chosen from the setting's | what decides who will travel with them ([`16-session.md`](16-session.md)) |

A setting may **retune** any of these ([`26-authoring-a-setting.md`](26-authoring-a-setting.md)) —
altering starting Fate is named there as a permitted override. These are the engine's defaults, not
a constraint on the setting.

### Why Stamina is 6

Four things already fixed it, and it was computed rather than chosen
([`../specs/008-character-creation/check_creation.py`](../../specs/008-character-creation/check_creation.py)):

- A completed career grants **+1 maximum Stamina**, called "the only durable toughening"
  ([`03-rules.md`](03-rules.md) §6). At 6 that is a **16.7%** gain. Much above 10 and the sentence
  stops being true. A career is **complete** once every skill it grants has been opened and
  raised to that career's cap — the terminal state of the advance mechanics in §3, not a separate
  event. The same completed state is what makes a character **eligible** for any career naming
  it as a prerequisite ([`26-authoring-a-setting.md`](26-authoring-a-setting.md)).
- An **ordinary** telling blow — a mid-band weapon against modest armour — drops a full-Stamina
  character **2.4 points** below zero, inside the 1–3 that the Aftermath family treats as ordinary.
  Deferred death stays routinely survivable.
- The **worst** case — a martial weapon, telling blow, no armour — overshoots by **8.8**, grim but
  inside the range the Aftermath table has rows for. A martial weapon is illegal in most civilised
  places for exactly this reason ([`03-rules.md`](03-rules.md) §2).
- An armoured exchange resolves in about **4.5** hits, and an unarmoured one in **2**. Armour roughly
  doubles endurance, and a fight still fits the twenty-minute session that
  [`01-principles.md`](01-principles.md) requires.

Values from 5 to 10 satisfy the overshoot constraint; 6 is the largest at which the career gain stays
unambiguous and a fight stays short.

### Why Fate rises with mortality

Fate is the anti-frustration valve as much as the death valve
([`03-rules.md`](03-rules.md) §3). A deadlier setting reaches for it more often, so it starts with
more. Under `mortality: low` the Aftermath table's death rows are closed already
([ADR 0009](../adr/0009-fate-closes-the-death-rows.md)), so Fate's death function is nearly idle and 2
is enough — and because Fortune equals Fate, it never falls to zero, or a character would have no
daily resource at all.

## 3. The background is how the advances are spent

A new character is not at the start of their first career. They have been doing it a while, and
**how far and in which direction is their background.**

**Eight advances**, spent under the ordinary rules ([`03-rules.md`](03-rules.md) §6) and constrained
to the **starting career's** skills:

| Cost | Buys |
|---|---|
| 1 | **open** a skill that career grants, at 25% |
| 1 | **+5%** to a skill already open, to the career's cap |

These are the only doors, and they are the same ones play uses. **A career grants a list of skills
the character *may* learn — not skills they already have.** Nothing may exceed the career's cap, and
no advance may be spent outside the career; that constraint is what makes the result a *background*
rather than a shopping trip.

**At least two skills must be opened.** A career is not one thing, and without the floor eight
advances on a single skill would open it at 60% — *expert*
([`23-diegesis.md`](23-diegesis.md)) before the chronicle has begun.

Two characters entering the same career therefore differ, and differ in a way that says something:

| Spent | Reads as |
|---|---|
| open 2, everything into one | **55%** and 25% — one real strength, and a thing they have barely touched |
| open 2, split evenly | **40% / 40%** — a narrow, solid pair |
| open 3 | **35% / 35% / 30%** — a working spread, all *trained* |
| open 4 | **30% × 4** — a journeyman who has done a bit of everything |

**Everything the career grants but the character never opened, they are simply untrained at** — the
flat 10% of [`03-rules.md`](03-rules.md) §1. That is the honest answer, and it is why the untrained
base matters: a character genuinely lacks most skills rather than owning them all at a token value.

The pool is computed in
[`check_creation.py`](../../specs/008-character-creation/check_creation.py) rather than picked: eight
puts every opened skill in the *trained* band at every legal spread, and cannot reach *expert*.

**This is the only allocation in creation, and it buys no advantage the fiction does not.** Depth
costs breadth; there is no optimum, only a shape.

## 4. What a setting must provide

Creation cannot run without these. A setting missing any of them fails to load, rather than being
filled in by the GM's judgement.

| | Requirement |
|---|---|
| **Entry careers** | at least one career marked as an entry point, each declaring the skills it grants |
| **Names** | enough to name a person of this world |
| **Places** | somewhere to be from |
| **Drives** | the things a character wants, in this world's terms |
| **Misfortunes** | the things already working against a character, in this world's terms — what step 9 draws on to write the Fault Line |
| **Loyalties** | at least one, and the relations between any that are strained or irreconcilable. A setting with a single Loyalty is legal, and means the question never arises |

Everything else a character carries starts empty: no wounds, no Marks, no career history, no
Reputation, no Allegiances, no Holdings, no Bonds beyond the one chosen at step 7.

## 5. Where creation hands off

The character leaves creation as an ordinary `character` entity
([`19-state.md`](19-state.md)) with `role: player`. Advancement takes over from there and uses the
same doors creation used: an advance opens a career-granted skill at 25%, or raises one by +5% toward
the career's cap ([`03-rules.md`](03-rules.md) §6).

There is no separate "starting character" state and no creation-only rule that later stops applying.

**A successor runs this same procedure.** When a chronicle continues through a new character
([`18-campaign.md`](18-campaign.md)), they inherit the world's situation — open threads, live
Threats, the enemies the predecessor made — and none of the predecessor's skills, Stamina, Luck or
Fate. Those come from here, exactly as they did the first time.
