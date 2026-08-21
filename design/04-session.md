# Wyrd — session structure

How twenty minutes on a train becomes a legitimate unit of play, and how the party works
when every companion is an NPC.

Structure adapted from prior art; provenance is recorded in the private research repo.

---

## Where a beat sits

```
Chronicle          years of play
 └ arc             recursive, to whatever depth the material warrants
   └ arc           (campaign · adventure · scenario · scene are labels, not levels)
     └ beat        one goal. THE ATOMIC UNIT.
```

Arcs nest freely ([`14-entities.md`](14-entities.md)); only the beat is structurally special.

A **beat** is the smallest complete thing: a single goal, attempted, resolved, persisted.
Searching the crypt is a beat. Fighting what was in it is a second. Getting out with the
ledger is a third.

**A session is one or more beats.** Two beats is a real session. One beat is a real session.

**This entire structure is internal.** The player never hears the words beat, rally or arc.
They are how the engine knows when to persist, when to offer a stopping point, and when to
compact — the equivalent of a page break, not a plot point. See the GM contract in
[`01-principles.md`](01-principles.md).

## The two modes

From 3e:

- **Story mode** — zoomed out, narrated broadly. Travel, a week of work, a search that has
  no real opposition. Used when order and detail don't matter.
- **Scene mode** — zoomed in. Opposed actions, sequence matters, the player wants to speak
  in character.

Claude switches explicitly and says so. One session can cover a fortnight of travel in two
paragraphs and then spend fifteen minutes in a cellar.

## The Rally — the save point

Between beats comes a **Rally**: a short pause with mechanical weight.

On a Rally:
- recover **1 Stress** and **1 Fatigue**
- posture drifts one step toward neutral
- Claude assesses the beat and may award an advance
- **state is written and the chronicle is committed**

This is the answer to "I have to get off the train." Every Rally is a clean stopping point
with fiction attached for why you caught your breath. Claude should offer one whenever a
beat closes and always accept `stop` there.

**No session ever ends mid-beat.** If the player must stop mid-beat, Claude persists state
and writes a `pending:` marker naming the unresolved action, so resumption is exact.

## The session loop

```
1. LOAD      chronicle.yaml, pc.yaml, party.yaml, recap.md, threads.yaml, contract
2. ELAPSE    wyrd advance-time — the world moved since last session (see 05-campaign)
3. RECAP     three sentences. Where you are, what is unresolved, what has changed.
4. BEAT      situation → player choice → roll → narrate → persist → Rally
5. REPEAT    until the player stops
6. CLOSE     compaction, recap regeneration, commit
```

Step 2 matters more than it looks. The elapsed-time pass runs *before* the recap so that the
recap can say "you have been three weeks in a town; word came that the mill at Grenzstadt
burned" — the world having moved is the first thing the player learns.

## Session shapes

Not every session is an adventure. Four legitimate shapes:

| Shape | Length | What it is |
|---|---|---|
| **Beat** | 10-20 min | One goal in an ongoing scenario. The default. |
| **Interlude** | 10 min | Pure character. A conversation, a meal, a companion's problem. No dice, or one. |
| **Downtime** | 15 min | A Fellowship phase (below). Advances the calendar. |
| **Long session** | 45+ min | A whole episode, or a scenario's climax. Rare. |

The Interlude is important and easy to neglect. Constraint 7 says most sessions are small;
a session that is *only* a companion telling you something over bad beer is a good session
and the engine should say so.

Note that shape is Claude's internal read of what the session is likely to be, used for
pacing. It is not announced either — the player does not get told they are in an Interlude,
they get told the beer is bad.

## The Fellowship phase

From another source system, where downtime is a phase with its own rules rather than a skip.

Triggered at the end of a scenario or arc, or when the player asks. Structure:

| Step | What happens |
|---|---|
| **Destination** | Where you spend it. Companions may disperse to their own affairs. |
| **Upkeep** | Time costs something. Away from home: lose 1 Standing, or spend coin equal to Standing. |
| **Advances** | Spend earned advances (see [`03-rules.md`](03-rules.md)). |
| **Undertaking** | Choose **one** activity for the period. |

Undertakings include: **Recover** (reduce Taint or Stress), **Mend** (treat a lasting
wound), **Pursue** (advance a personal thread), **Sectivate** (build a relationship or a
holding), **Learn** (open a new career), **Ask** (gather information on a Threat).

The constraint is that you choose **one**. Recovering from taint means *not* pursuing
the thing that corrupted you. That trade is the whole point.

A Fellowship phase **advances the calendar** — typically weeks to a season — which means
Threats activate. Downtime is when the world gets ahead of you.

## The party

The player runs one character. Claude runs everyone else. Companions are the primary
mechanism for pacing, exposition and cost — because Wyrd cannot meaningfully threaten the
player's character without consent, but it can absolutely break a companion.

### Companions are people

Each companion in `party.yaml` carries:

```yaml
- name: Grete Vollen
  career: labourer
  agenda: "get her brother out of the debt he owes the Meisters"
  flaw: "cannot leave a wrong alone"
  bond: 3            # to the PC; -3..+3
  taint: 1
  stress: 0
  secret: "she already knows what happened to the brother"  # PC does not know this
  arc: "will have to choose between the debt and the party"
```

**Claude never asks the player to decide for a companion.** Companions act on their agendas,
including against the player's interest, and may refuse, leave, lie, or act while the player
sleeps.

### Party Tension

From 3e — the mechanism that makes an NPC party feel alive on a schedule rather than
arbitrarily.

A single **Tension** track, 0-6. It rises when:
- the player overrules a companion on something touching their agenda
- a companion is hurt by the player's choice
- the party goes hungry, unpaid, or unrested
- a secret surfaces
- taint shows

At **3**, friction is visible — sniping, reluctance, a companion holding something back.
At **6**, something breaks: a departure, a betrayal, a confession, a refusal at the worst
moment. **Then Tension resets to 0.**

It falls by 1 at a Fellowship phase, and by 1 when the player spends a beat on a companion's
problem rather than their own.

This gives Claude a principled, visible, self-resetting licence to generate inter-party
drama driven by what actually happened — and it makes the Interlude session mechanically
worthwhile.

### Bonds

Each companion's `bond` (-3..+3) to the PC modifies Tension gain, whether they follow into
danger, and whether they tell you the truth. It moves slowly and it is the closest thing
Wyrd has to a relationship score.

A companion at bond -3 is still travelling with you. That is more interesting than one who
left.
