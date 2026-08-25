# Wyrd — session structure

How twenty minutes on a train becomes a legitimate unit of play, and how the party works
when every companion is played by the GM.

Structure adapted from prior art; provenance is recorded in the private research repo.

---

## Where a beat sits

```
Chronicle          years of play
 └ arc             recursive, to whatever depth the material warrants
   └ arc           (campaign · adventure · scenario · situation — labels, not levels)
     └ beat        one goal. THE ATOMIC UNIT.
```

Arcs nest freely ([`14-entities.md`](14-entities.md)). The distinction that matters is not
depth but kind:

> **Arcs organise. Beats are played.**

An arc is a container — it has entry and exit conditions, and children. A **beat** is where
play actually happens: a single goal, attempted, resolved, persisted. Searching the crypt is
a beat. Fighting what was in it is a second. Getting out with the ledger is a third.

That is why a beat is not simply "an arc with no children". An arc of one beat is still an
arc, and a beat is never a container.

**A session is one or more beats.** Two beats is a real session. One beat is a real session.

**This entire structure is internal.** The player never hears the words beat, rally or arc.
They are how the engine knows when to persist, when to offer a stopping point, and when to
compact — the equivalent of a page break, not a plot point. See the GM contract in
[`01-principles.md`](01-principles.md).

## The two modes

A beat is either **played** or **summarised**.

- **Summarised** — zoomed out. Travel, a week of work, a search with no real opposition.
  Used when order and detail do not matter.
- **Played** — zoomed in. Opposed actions, sequence matters, the player wants to speak in
  character.

The GM switches by *changing how it narrates*, never by announcing a mode — one session can
cover a fortnight of travel in two paragraphs and then spend fifteen minutes in a cellar.

The choice is the GM's and it is not a property of the content: the same beat may be played
in one chronicle and summarised in another.

## The Rally — the save point

Between beats comes a **Rally**: a short pause with mechanical weight.

On a Rally:
- recover **1 Strain**
- recover **1 Stamina** ([`03-rules.md`](03-rules.md) §2)
- The GM assesses the beat and may award an advance
- **state is written and the chronicle is committed**

This is the answer to "I have to get off the train." Every Rally is a clean stopping point
with fiction attached for why you caught your breath. The GM should offer one whenever a
beat closes and always accept `stop` there.

**No session ever ends mid-beat.** If the player must stop mid-beat, the GM persists state
and writes a `pending:` marker naming the unresolved action, so resumption is exact.

## The session loop

```
1. LOAD      chronicle.yaml, the player character, present companions, hot threads, recap, contract
2. ORIENT    where and when the character is; the clock has not moved since you stopped
3. RECAP     three sentences. Where you are, what is unresolved, what has changed.
4. BEAT      situation → player choice → roll → narrate → persist → Rally
5. REPEAT    until the player stops
6. CLOSE     compaction, recap regeneration, commit
```

Step 2 matters more than it looks. The elapsed-time pass runs *before* the recap so that the
recap can say "you have been three weeks away; word came that a mill burned" — the world having moved is the first thing the player learns.

## Session shapes

Not every session is an adventure. Four legitimate shapes:

| Shape | Length | What it is |
|---|---|---|
| **Single beat** | 10-20 min | One goal in an ongoing arc. The default. |
| **Interlude** | 10 min | Pure character. A conversation, a meal, a companion's problem. No dice, or one. |
| **Downtime** | 15 min | A downtime phase (below). Advances the calendar. |
| **Extended** | 45+ min | Several beats, or an arc's climax. Rare. |

The Interlude is important and easy to neglect. Where a setting declares a personal scope
([`01-principles.md`](01-principles.md)), most sessions *should* be small — and a session
that is only a companion telling you something over bad beer is a real one. The engine
should say so rather than padding it into an adventure.

Note that shape is the GM's internal read of what the session is likely to be, used for
pacing. It is not announced either — the player does not get told they are in an Interlude,
they get told the beer is bad.

## Downtime

Downtime is a phase with its own rules, not a skip between adventures.

Triggered at the end of a scenario or arc, or when the player asks. Structure:

| Step | What happens |
|---|---|
| **Destination** | Where you spend it. Companions may disperse to their own affairs. |
| **Upkeep** | Time costs something. Away from home: lose 1 Standing, or spend coin equal to Standing. |
| **Advances** | Spend earned advances (see [`03-rules.md`](03-rules.md)). |
| **Undertaking** | Choose **one** activity for the period. |
| **Rest** | Stamina returns to maximum. Automatic; it costs no undertaking. |

Undertakings include: **Recover** (reduce Taint or Strain), **Mend** (treat a lasting
wound), **Pursue** (advance a personal thread), **Cultivate** (build a relationship or a
holding), **Learn** (open a new career), **Ask** (gather information on a Threat).

The constraint is that you choose **one**. Recovering from taint means *not* pursuing
the thing that corrupted you. That trade is the whole point.

**Stamina is not on that list**, deliberately. It returns to maximum whether or not the period is
spent on it ([`03-rules.md`](03-rules.md) §2) — otherwise every downtime after a real fight would
resolve to the same choice, and the trade above would be a formality rather than a decision.

### Mend

**Mend treats one named lasting wound, and moves its effect one grade.**

| | |
|---|---|
| **Names** | one wound, by its `id` ([`06-state.md`](06-state.md)) |
| **Moves** | that wound's effect one step toward nothing: `skill: -10` → `-5` → closed; `stamina_max: -1` → closed; `dread: +1` → closed |
| **Leaves alone** | everything else on the record — a mended wound keeps its `id`, its origin and its description |
| **Costs** | the downtime's one undertaking |
| **Cannot touch** | a **recurring** wound, ever |

Every step lands on a value the wound record's closed effect set already permits
([`03a-2-aftermath.md`](03a-2-aftermath.md)) — `−10` and `−5` are the difficulty ladder's own rungs
(`03-rules.md` §1), so nothing new has to be learned to apply a half-mended wound. A wound whose
effect reaches nothing is **closed, not deleted**: the record stays, marked, because history is
never recomputed ([`09-evolution.md`](09-evolution.md)).

**A recurring wound never closes.** Re-reading a `death` result onto the recurring wound is exactly
what a spent Fate point buys ([`03a-2-aftermath.md`](03a-2-aftermath.md)); a mending rule that
erased it would price that promise at one season
([ADR 0021](adr/0021-mending-steps-and-the-recurring-wound-does-not.md)).

A drop leaves **0.61** wound records on average, costing **0.62** downtimes of Mend to clear — so a
character who fights hard about as often as they rest keeps pace, and one who fights harder than
that accumulates ([`check_recovery.py`](../specs/014-stamina-recovery/check_recovery.py)).

Downtime **advances the calendar** — typically weeks to a season — which means
Threats activate. Downtime is when the world gets ahead of you.

## The party

The player runs one character. The GM runs everyone else.

**The player's character can be threatened, and the engine is built to do it.** Criticals are
lethal, death is deferred to the Aftermath table rather than softened, Fate points are few
and permanent, and a chronicle that outlives its protagonist has succession rules waiting
([`05-campaign.md`](05-campaign.md)). Any setting can raise or lower that with `mortality`.

What differs is **rationing**. Threat to the player's character is real but expensive — it
costs a Fate point, or it ends a character the chronicle has been building for years.
Companions carry no such cost, so they can be broken *often*, and that is why they are the
engine's primary lever for pacing and consequence.

There is a second reason, and it matters more than the first: **loss lands harder when the
player could not have prevented it by playing better.** A companion acts on their own
objective, refuses, lies, or dies while the player is elsewhere. That is a kind of cost a
character sheet cannot deliver.

The player may spend Fate to save a companion from death, but only from *death*, and only
when present to act ([`03-rules.md`](03-rules.md)). A companion lost to their own agenda —
who leaves, betrays, or is claimed by what they wanted — cannot be bought back. That is the
line that keeps companions meaningful rather than merely fragile.

### Companions are people

Each companion is a `character` entity carrying:

```yaml
role: companion
status: with-party
career: <career-id>
objective:
  wants: "<what they are actually here for>"
  next_step: "<what they will do about it next>"
flaw: "<the thing that gets them into trouble>"
bond: 3                    # -3..+3, toward the player
taint: 1
strain: 0
secret: "<something the player does not know>"
arc: "<the choice this companion is heading toward>"
```

**The GM never asks the player to decide for a companion.** Companions act on their agendas,
including against the player's interest, and may refuse, leave, lie, or act while the player
sleeps.

### Loyalty — who will travel with whom

Some settings divide their world so deeply that two people from opposite sides of the line would
never share a road, whatever else they had in common. The engine has to know that, because the GM
assembles the party and the question comes up constantly.

Every character carries a **Loyalty**: what they serve, or what they are. The engine fixes nothing
about what Loyalties exist — a setting declares them, and names them
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)). Most settings need two or three; a
setting with one dividing line and a setting with none are both legal.

Between any two Loyalties the setting declares one of three relations. Only the interesting ones are
written down; anything undeclared is the first:

| Relation | Effect |
|---|---|
| *(undeclared)* | nothing. They travel together like anyone else. |
| **strained** | They travel together **badly**. Tension rises **twice as fast** while both are in the party. |
| **irreconcilable** | They do not travel together. A companion of an irreconcilable Loyalty **cannot join**, and the engine refuses rather than asking. |

`strained` needs no machinery of its own: Party Tension below already measures exactly this kind of
friction, and already says what happens when it accumulates. A strained party is not forbidden — it
is a party on a shorter fuse, and the fuse is the one that already exists.

**A Loyalty can change.** Conversion, corruption, a revelation about someone's birth — settings that
allow it will use it. When a character's Loyalty changes, the party is re-checked. If that makes an
existing pairing irreconcilable, **Tension breaks immediately**: a departure, a betrayal, a refusal
at the worst possible moment, exactly as at 6. The engine needs no new event for this, because the
one it already has says the right thing.

The player's character is not exempt. A player whose Loyalty changes may find the party they built
will no longer ride with them, and that is a consequence the chronicle should record rather than
soften.

### Party Tension

The mechanism that makes a GM-played party feel alive on a schedule rather than
arbitrarily.

A single **Tension** track, 0-6. It rises **twice as fast** while the party holds a strained pairing
of Loyalties (above). It rises when:
- the player overrules a companion on something touching their agenda
- a companion is hurt by the player's choice
- the party goes hungry, unpaid, or unrested
- a secret surfaces
- taint shows

At **3**, friction is visible — sniping, reluctance, a companion holding something back.
At **6**, something breaks: a departure, a betrayal, a confession, a refusal at the worst
moment. **Then Tension resets to 0.**

It falls by 1 during downtime, and by 1 when the player spends a beat on a companion's
problem rather than their own.

This gives the GM a principled, visible, self-resetting licence to generate inter-party
drama driven by what actually happened — and it makes the Interlude session mechanically
worthwhile.

### Bonds

Each companion's `bond` (-3..+3) to the player character modifies Tension gain, whether they follow into
danger, and whether they tell you the truth. It moves slowly and it is the closest thing
Wyrd has to a relationship score.

A companion at bond -3 is still travelling with you. That is more interesting than one who
left.
