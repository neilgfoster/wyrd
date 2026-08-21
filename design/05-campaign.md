# Wyrd — the meta-campaign

The layer that makes a chronicle run for years: how the world moves while you are away, how
arcs are selected rather than scripted, and how a losing struggle is shaped.

Provenance for the ideas here is recorded in the private research repo.

---

## Threats

A **threat** is a campaign-length antagonist that acts on its own schedule whether or not the
player is present.

It is **not an entity type**. It is an *aspect* attached to a `character`, `organisation` or
`place` ([`14-entities.md`](14-entities.md)), because such an antagonist may be a person, a
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

### Threats are personal

Every active Threat must have **at least one connection to the player or a companion** —
a birthplace, a debt, a relative, an old employer. Derived at chronicle creation from the
PC's Drive and Misfortune. The thing threatening the world is already the thing that
marked you.

---

## Elapsed time — the rule that makes this practical

Real sessions are weeks apart. Wyrd does **not** simulate every intervening week.

**Abstract it.** Take the **expected value** over the
elapsed period. A Threat at Imminence 4 activates roughly once per three weeks — so a
five-week gap produces about two activations. Roll those, apply them, and generate the
resulting world-state.

`wyrd advance-time <days>` does this deterministically and writes the results. It runs at
the **start** of every session, before the recap, so the first thing the player learns is
what changed while they were gone.

This is what makes "dip in and out over years" actually work. The world moved; it did not
wait; and computing that costs one command.

---

## Threads

The connective tissue that makes a sequence of scenarios feel authored rather than
episodic.

A **thread** is an open loop: a debt, an enemy who escaped, a promise, a name you should not
know, a companion's unresolved arc.

```yaml
- id: the-escaped-patron
  opened: 2512-Nachexen
  summary: "the man who paid the zealots walked away; you saw his ring"
  hooks: [nobility, altdorf, jewellery, the-rot-beneath-the-town]
  heat: 2        # 0-5. rises when touched, decays slowly when ignored
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
six-pager about a corrupt miller are equally valid inputs. See
[scenarios.md](https://github.com/neilgfoster/wyrd-research/blob/main/reference/scenarios.md) and
[library-triage.md](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library-triage.md).

**Prefer short-form.** The magazine and fanzine archives are the richest seam precisely
because a six-page adventure about a corrupt miller has no ambition to be a finale.

---

## Arcs and eras

An **arc** is 5-10 scenarios around one Threat, ending with a real change to the world —
usually not a victory.

A chronicle is divided into named **eras** that state the shape of the decline, as in *The
Darkening of Mirkwood*:

> The Quiet Years → The First Signs → The Bad Winter → What Came After

> A losing struggle is a legitimate shape for a chronicle, and settings that declare one
> should say so in their tone contract. The engine's part is only to hold the line the
> setting draws — see [`01-principles.md`](01-principles.md).


And:

> Where a setting declares a losing struggle, the emphasis belongs on personal stakes: the
> region may be lost, but can this character save the people in front of them?

So: **the world's darkness escalates; the player's power does not.** Scope stays personal
while stakes rise around it. Victory is holding the line one more year, and saving
something specific and small.

This is the mechanical answer to constraint 5 and constraint 6 together.

## Holdings

Over years the player accumulates something — a cottage, a boat, a workshop, a
name in a guild, a family. It is recorded in the chronicle and it is **leverage**:

> "If Spiders attack a Woodman village, that's a tragedy for the heroes to avenge — but if
> the village includes a farm that is part of a hero's holding, then it's personal."

And it manufactures the dilemma that a long campaign needs: remain on the quest, or go home
and defend your own.

## Succession

A chronicle running years may outlast one labourer. When the PC dies, is lost, or
retires, the default is **succession, not replacement** — but succession is inherited
**through the thread, not the bloodline**.

"Your son takes up the sword" is the weakest available version. It is sentimental, it is
not how the world works, and it makes the chronicle about a family when it should be
about a rot that outlives everyone who touches it.

### The successor is already in the chronicle

The next PC is someone **already in the chronicle** — a name that has appeared, however
briefly. The engine selects from the chronicle's `character` entities by *entanglement*, not affection. Strong
candidates, roughly in order of how well they carry a story:

- **Someone the old PC wronged.** The debt they never repaid; the family they failed to
  warn; the witness they left in the cellar. They inherit the consequences and the grudge.
- **Someone who was investigating them.** A witch hunter, a bailiff's clerk, a rival
  agitator who had a file on you and now has to finish what you started, hating it.
- **A bystander whose life the old PC's actions changed.** The miller's daughter, after the
  mill. She never chose this.
- **A rival.** Someone who wanted what you had and now has your enemies as well.
- **Whoever found what you left behind.** The ledger, the body, the thing in the cellar.
  Possession of the evidence is itself an inheritance.
- **A companion** — still permitted, but the *least* interesting option, because the bond is
  already established and nothing has to be re-earned.

The successor need not have liked the old PC. They may have been hunting them. A witch
hunter who took the case, and now carries the taint they were sent to burn out, is a
better second act than any heir.

### What is actually inherited

**Not property. Unfinished business.**

| Inherited | Not inherited |
|---|---|
| Open **threads**, at their current heat | Skills, careers, advances |
| The **enemies** the old PC made | Stamina, Luck, Fate |
| Active **Threats** and their Imminence | Reputation *(a new label starts, possibly hostile)* |
| What the world **believes** about the old PC | Taint, transformations, afflictions |
| The **rot** itself, still growing | Any assumption of goodwill |

**Holdings are not automatically passed on.** A cottage may be seized for debt, burned,
occupied by squatters, or fall to someone else entirely. If it does reach the successor it
should arrive encumbered — with the debt, the obligation, or the thing living under it.
Losing the holding is often the better story, and it is a legitimate outcome of the old PC's
death rather than a punishment.

Reputation is the sharpest inheritance. `reputation 6 (a notorious killing)` does not
die with the person it described. The successor may spend years being mistaken for what
their predecessor was, or condemned for it.

### The old PC does not leave

If they were **lost**, they became a character the GM controls — and the successor may meet
them. If they **died**, what they did persists in the entity store as fact and in the world as
rumour, and the two need not match. If they **retired**, they are somewhere, and can be
found, and may not want to be.

This is the mechanism that makes an era boundary meaningful: the chronicle continues, the
protagonist does not, and the thing they were fighting is still there — larger, and now
partly their fault.

### At the table

Succession is offered, never imposed. On a character's end the GM proposes **two or three
candidates from the chronicle's characters** with a line each on how they are entangled, and the player
chooses — or declines and starts clean. Declining is legitimate; the threads simply stay
open and go cold in their own time.
