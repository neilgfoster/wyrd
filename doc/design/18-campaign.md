# Wyrd — the meta-campaign

The layer that makes a chronicle run for years: how the world acts when the character is not
looking, how arcs are selected rather than scripted, and what happens when a chronicle outlives its
character.

Provenance for the ideas here is recorded in the private research repo.

---

## Threats

A **threat** is a campaign-length antagonist that acts on its own schedule whether or not the
player is present.

It is **not an entity type**. It is an *aspect* attached to a `character`, `organisation` or
`place` ([`27-entities.md`](27-entities.md)), because such an antagonist may be a person, a
conspiracy or a poisoned valley — and forcing a choice between them loses information.

```yaml
# in the frontmatter of whichever entity carries it
threat:
  imminence: 3
  clues:                      # the ordered discovery path
    - <the first thing anyone notices>
    - <what that leads to>
    - <the thing at the centre>
  effects:                    # rolled when it activates
    1: "grows stronger — imminence +1"
    2: "its reach permanently worsens"
    3-6: "spreads to an adjacent place"
    7: "a named character is taken or turned"
    8: "an open, public calamity — everyone knows"
  ambient:                    # true while within its reach
    - "<a standing cost of being here>"
  counters:                   # how it can actually be fought
    - "<the thing that would undo it>"
  weakness: "<its limit>"
  connection: "why this touches the player"
  known_to_player: none       # none | rumoured | partial | understood
```

The active set is a query — entities with a `threat` block and `imminence > 0` — not a file.

### Imminence

| Rating | Meaning |
|---|---|
| 1-2 | Interacts rarely and randomly. A rumour, an occasional body. |
| 3-4 | An active force, a growing concern. Named people start disappearing. |
| 5-6 | Serious concern for everyone; troubles the region constantly. |
| 7+ | An almost constant source of trouble — "perhaps spelling its ultimate ruin". |

### Activation

At the start of each in-game week, roll **`d100` per threat**. If the result is
**≤ imminence × 10**, it activates: roll on its effects table. Imminence is therefore a
chance-per-week in tens of percent, which keeps the whole engine percentile.

The GM chooses *when in the week* it lands — while the player is present (a scene) or while
they are elsewhere (they hear about it later, late and partially).

**If a Threat acts and the player was not there, they must still find out.** A peddler
brings word; a companion's family writes; the market is talking. Information should arrive **late, incomplete, and sometimes wrong**.

### Where threats come from

A threat is an **aspect**, not a type ([`27-entities.md`](27-entities.md)) — so **any entity
may acquire one at any time**, and most of the interesting ones are not there at the start.

| Origin | How it arises |
|---|---|
| **Seeded** | written at chronicle creation from the character's Drives and Misfortune |
| **Inherited** | already active in the setting; the character simply walks into it |
| **Provoked** | the character intervened, and something that had no interest in them now has one |
| **Made** | someone the character wronged, abandoned or failed acquires an objective about it |

The last two are the ones that make a chronicle feel like consequence rather than content.
A conspiracy the player disrupted does not shrug; it acquires a `threat` block, an imminence,
and an objective naming *them*. A companion left for dead becomes a `character` whose role
changes to nemesis, whose archetype is **fallen-ally** — the one that knows you — and whose
connection is not a birthplace or a debt but the thing that actually happened.

**Promotion is the mechanism.** Nothing is created: an existing entity gains a `threat`
block, and its objective is rewritten to point at the player. That is why the archetypes are
behavioural rather than thematic — they say how something acts once it has decided to act
against you.

Threats also **fade**. An imminence may fall when the player addresses a cause, and a threat
whose objective is satisfied or foreclosed stops being one, keeping its entity and its
history.

### Threats are personal

Every active threat must have **at least one connection to the player or a companion** —
a birthplace, a debt, a relative, an old employer, or an event. A threat with no connection
is scenery, and belongs in the setting rather than in a chronicle's active set.

For seeded and inherited threats that connection is written. For provoked and made ones it
*is* the history, which is the strongest kind — the thing threatening the world is the thing
the player did.

Note that a provoked threat escalating is **scale drift**, which some settings suppress
([`01-principles.md`](01-principles.md)). Under `scale_drift: suppressed` a provoked threat
grows more *personal* rather than more powerful: it comes for you specifically, rather than
for the region.

---

## Elapsed time — game time, never real time

**Game time advances only when the fiction advances it.** Real-world gaps between sessions
are irrelevant to the world clock.

This matters more than it sounds. If a beat ends with the character standing in a cellar with
a blade drawn, and the player returns three weeks later, **no game time has passed at all**.
They are still in the cellar, and the blade is still drawn. A world clock tied to the wall
clock would have aged the world three weeks between two consecutive heartbeats.

The inverse holds too: two beats played back to back in one sitting may sit a season apart in
the fiction, if a downtime phase separates them.

### What advances the clock

| Source | Typical span |
|---|---|
| A summarised beat covering a span | hours to days |
| Narrated travel | days to weeks |
| An explicit wait — until morning, until the boat, until the fever breaks | as stated |
| **Downtime** ([`16-session.md`](16-session.md)) | weeks to a season |
| The gap between arcs, where the fiction implies one | as stated |

Nothing else. In particular, **closing the session advances nothing.**

### Advancing it

When the clock does move, the world moves with it — and Wyrd does not simulate every
intervening week.

**Take the expected value over the span.** A threat at imminence 4 activates roughly once
per three weeks, so a five-week jump produces about two activations. Roll those, apply them,
and generate the resulting state.

```
wyrd advance-time <game-days>
```

Deterministic, and it writes its results. It is called **when the fiction says time passed**
— most often at the end of a downtime phase — not at the start of a session.

A journey's summarised legs advance the clock this same way — see
[`30-journeys.md`](30-journeys.md) for the setting-configurable subsystem that plays travel
rather than only narrating it.

### Returning after a long absence

A real-world gap changes nothing about the world. It changes what the **recap** has to do:
re-establish where the character is, what was unresolved, and what was about to happen
([`19-state.md`](19-state.md)). If the session stopped mid-beat, the `pending:` marker
restores the exact moment.

That distinction is what makes "dip in and out over years" work. The player's absence is a
fact about the player, not about the world.

---

## Threads

The connective tissue that makes a sequence of scenarios feel authored rather than
episodic.

A **thread** is an open loop: a debt, an enemy who escaped, a promise, a name you should not
know, a companion's unresolved arc.

```yaml
- id: the-one-who-paid
  opened: {year: 0, month: null}
  summary: "whoever funded it walked away, and you would know them again"
  hooks: [money, influence, the-thing-they-funded]
  heat: 2        # 0-5; rises when touched, decays slowly when ignored
```

Every scenario **consumes** threads (it needs hooks that match live ones) and **emits** new
ones. Selecting the next scenario means finding one whose hooks match threads that are
currently hot.

**This is the piece Wyrd cannot borrow.** An authored year-by-year campaign fixes what
happens when; a procedural threat generator never sequences at all. Wyrd must *select and
sequence*, which is exactly the judgment an LLM is good at — provided the state is written
down.

Threads decay. A thread untouched for a year of game time drops in heat and eventually
closes as "never resolved" — which is itself true to the setting. Not everything gets an
answer.

---

## Scenario selection

At the start of an arc, or when a scenario closes, the GM picks the next by:

1. Reading live threads by heat
2. Matching against `scenarios/*/scenario.yaml` hooks, filtered by setting
3. Scaling it to the current **danger rating** (see [`03-rules.md`](03-rules.md))
4. Rewriting names, places and faction to fit the chronicle
5. Recording `source:` — what it was adapted from and what changed

**Sourcing is by theme, not system.** An investigation written for another world and a *a periodical*
six-pager about a corrupt official are equally valid inputs. See
[scenarios.md](https://github.com/neilgfoster/wyrd-research/blob/main/reference/scenarios.md) and
[library-triage.md](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library-triage.md).

**Prefer short-form.** The magazine and fanzine archives are the richest seam precisely
because a six-page adventure about a corrupt official has no ambition to be a finale.

---

## Eras

A chronicle is divided into named **eras**: periods with their own ambient register, marking
where the world's condition changed.

An era does four jobs, all of them structural:

- it **names a period**, so the chronicle's history is navigable years later
- it **sets the ambient register**, which the GM reads as context for every beat inside it
- it is a **natural seam for rules changes**, since "the world works differently now" is
  absorbed far more gracefully between eras than mid-arc
  ([`22-evolution.md`](22-evolution.md))
- it is **git-tagged**, giving a decade of play navigable checkpoints

**The direction is the setting's business, not the engine's.** A sequence of eras may
describe a decline, a recovery, a cycle of seasons, or simply a succession of different
problems. What the engine requires is only that eras are *named in advance* and that
crossing one is *recorded*.

Under a tone contract with `scale_drift: suppressed`, eras change the *character* of the
world rather than its scale — what is at stake stays local, but what it costs to live there
changes ([`01-principles.md`](01-principles.md)).

### Top-level arcs

Arcs recurse ([`27-entities.md`](27-entities.md)), so there is no fixed number of anything.
But the arcs directly under a chronicle have a job the deeper ones do not: **each should end
with a real change to the world**, recorded in the overlay, and that change is what an era
boundary is eventually drawn around.

An arc that ends with nothing altered was a sequence of beats, not an arc.

## Holdings

Over years a character accumulates **things that can be taken**: a dwelling, a boat, a
workshop, a standing in some organisation, a household, a debt owed to them.

A holding is recorded as an entity like anything else, and its purpose is mechanical rather
than decorative: **it converts accumulated investment into stakes.** A threat to a settlement
is a problem; a threat to a settlement where the character owns the mill is *personal*, and
requires no invention on the GM's part to make it so.

It also manufactures the dilemma a long chronicle needs: **stay with what you were doing, or
go back and defend your own.** That choice is only available to a character who has something
to lose, which is why holdings accrue quietly for years before they matter.

Holdings are distinct from **allegiances**. An allegiance is standing within an organisation;
a holding is a thing that can be burned, seized, occupied or ruined.

## Succession

A chronicle running years may outlast the character who began it. When the player's
character dies, is lost, or retires, the default is **succession, not replacement** — and
succession passes **through the thread, not the bloodline**.

"Your son takes up the sword" is the weakest available version. It is sentimental, it
assumes an inheritance most settings do not grant, and it makes the chronicle about a family
when it should be about **the situation that outlives everyone who touches it**.

### The successor is already in the chronicle

The successor is someone **already in the chronicle** — a name that has appeared, however
briefly. The engine selects from the chronicle's `character` entities by *entanglement*, not
affection. Strong candidates, roughly in order of how well they carry a story:

- **Someone the predecessor wronged.** The debt they never repaid; the family they failed to
  warn; the witness they left in the cellar. They inherit the consequences and the grudge.
- **Someone who was investigating them.** An official, an inquisitor, a rival who kept a
  file — and now has to finish what the predecessor started, hating it.
- **A bystander whose life the predecessor's actions changed.** Someone who was simply
  present, and is now the only one who knows. They never chose this.
- **A rival.** Someone who wanted what you had and now has your enemies as well.
- **Whoever found what you left behind.** The ledger, the body, the thing in the cellar.
  Possession of the evidence is itself an inheritance.
- **A companion** — still permitted, but the *least* interesting option, because the bond is
  already established and nothing has to be re-earned.

The successor need not have liked the predecessor. They may have been hunting them. An
investigator who took the case and now carries the thing they were sent to end is a better
second act than any heir.

### What is actually inherited

**Not property. Unfinished business.**

| Inherited | Not inherited |
|---|---|
| Open **threads**, at their current heat | Skills, careers, advances |
| The **enemies** the predecessor made | Stamina, Luck, Fate |
| Active **Threats** and their Imminence | Reputation *(a new label starts, possibly hostile)* |
| What the world **believes** about the predecessor | Taint, transformations, afflictions |
| The **unresolved situation** itself | Any assumption of goodwill |

**Holdings are not automatically passed on.** A dwelling may be seized for debt, burned,
occupied, or fall to someone else entirely. If one does reach the successor it should arrive
encumbered — with the debt, the obligation, or whatever made it worth taking.
Losing the holding is often the better story, and it is a legitimate outcome of the predecessor's
death rather than a punishment.

Reputation is the sharpest inheritance. `reputation 6 (a notorious killing)` does not
die with the person it described. The successor may spend years being mistaken for what
their predecessor was, or condemned for it.

### The predecessor does not leave

If they were **lost**, they became a character the GM controls — and the successor may meet
them. If they **died**, what they did persists in the entity store as fact and in the world as
rumour, and the two need not match. If they **retired**, they are somewhere, and can be
found, and may not want to be.

This is what can make an era boundary meaningful: the chronicle continues, the protagonist
does not, and what they were contending with is still there — now partly their doing.

### At the table

Succession is offered, never imposed. On a character's end the GM proposes **two or three
candidates** with a line each on how they are entangled, and the player chooses — or declines and starts clean. Declining is legitimate; the threads simply stay
open and go cold in their own time.
