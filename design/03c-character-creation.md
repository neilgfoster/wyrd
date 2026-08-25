# Wyrd — character creation

The procedure that turns a setting's declared options into a playable character. It is run once
per chronicle, at bootstrap ([`16-chronicle-bootstrap.md`](16-chronicle-bootstrap.md)), and it must
produce the same character shape every time — two runs that disagree are a bug, not a flourish.

**The procedure is the engine's. The options are the setting's.** There is one procedure, not an
engine one and a setting one.

---

## 1. The steps, in order

| | Step | Where the content comes from |
|---|---|---|
| 1 | **Choose a career.** Any the setting marks as an entry point. | the setting's career graph ([`14-entities.md`](14-entities.md)) |
| 2 | **Take every skill that career grants, at 25%.** | the career's own declaration |
| 3 | **Set Stamina** to 6, current and maximum. | engine, §2 |
| 4 | **Set Luck** to 40, current and maximum. | engine, §2 |
| 5 | **Set Fate** from the setting's `mortality`. Fortune equals it. | engine, §2 |
| 6 | **Set the tracks** the setting has not disabled to zero. | [`03-rules.md`](03-rules.md) §4–5 |
| 7 | **Name them, and place them.** Name, a Drive, a Bond, and where they are from. | the setting's name and place tables |

Steps 3–6 are fixed. Steps 1, 2 and 7 read setting data and cannot be completed without it.

**Nothing is rolled.** No characteristics exist to roll ([ADR 0013](adr/0013-the-engine-names-no-skill.md)),
Stamina and Luck are flat, and skills come from the career. A character is *chosen*, not generated —
see [ADR 0014](adr/0014-character-creation-is-chosen-not-rolled.md).

## 2. The starting values

| | Value | Why |
|---|---|---|
| **Skills** | every skill the starting career grants, at **25%** | 25% is what an advance opens a skill at ([`03-rules.md`](03-rules.md) §6); creation uses the same door |
| **Stamina** | **6**, current and maximum | derived; see below |
| **Luck** | **40**, current and maximum | a test must fail more often than it succeeds, and still have something to erode |
| **Fate** | by `mortality`: `low` **2**, `standard` **3**, `high` **4** | the tone contract sets it ([`01-principles.md`](01-principles.md)) |
| **Fortune** | equal to Fate, renewed daily | [`03-rules.md`](03-rules.md) §3 |
| **Taint, Trauma, Strain, Resolve, Dread** | 0 | nothing has happened yet |

A setting may **retune** any of these ([`13-authoring-a-setting.md`](13-authoring-a-setting.md)) —
altering starting Fate is named there as a permitted override. These are the engine's defaults, not
a constraint on the setting.

### Why Stamina is 6

Four things already fixed it, and it was computed rather than chosen
([`../specs/008-character-creation/check_creation.py`](../specs/008-character-creation/check_creation.py)):

- A completed career grants **+1 maximum Stamina**, called "the only durable toughening"
  ([`03-rules.md`](03-rules.md) §6). At 6 that is a **16.7%** gain. Much above 10 and the sentence
  stops being true.
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
([ADR 0009](adr/0009-fate-closes-the-death-rows.md)), so Fate's death function is nearly idle and 2
is enough — and because Fortune equals Fate, it never falls to zero, or a character would have no
daily resource at all.

## 3. What a setting must provide

Creation cannot run without these. A setting missing any of them fails to load, rather than being
filled in by the GM's judgement.

| | Requirement |
|---|---|
| **Entry careers** | at least one career marked as an entry point, each declaring the skills it grants |
| **Names** | enough to name a person of this world |
| **Places** | somewhere to be from |
| **Drives** | the things a character wants, in this world's terms |

Everything else a character carries starts empty: no wounds, no Marks, no career history, no
Reputation, no Allegiances, no Holdings, no Bonds beyond the one chosen at step 7.

## 4. Where creation hands off

The character leaves creation as an ordinary `character` entity
([`06-state.md`](06-state.md)) with `role: player`. Advancement takes over from there and uses the
same doors creation used: an advance opens a career-granted skill at 25%, or raises one by +5% toward
the career's cap ([`03-rules.md`](03-rules.md) §6).

There is no separate "starting character" state and no creation-only rule that later stops applying.

**A successor runs this same procedure.** When a chronicle continues through a new character
([`05-campaign.md`](05-campaign.md)), they inherit the world's situation — open threads, live
Threats, the enemies the predecessor made — and none of the predecessor's skills, Stamina, Luck or
Fate. Those come from here, exactly as they did the first time.
