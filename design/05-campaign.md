# Wyrd — the meta-campaign

The layer that makes a chronicle run for years: how the world moves while you are away, how
scenarios are selected rather than scripted, and how a long defeat is shaped.

Sources: Beyond the Wall's Threat Packs, The One Ring's Tale of Years, WFRP 3e's Progress
Tracker. See [systems-mined](../reference/systems-mined.md) and
[tor-concepts](../reference/tor-concepts.md).

---

## Threats

A **Threat** is a campaign-length antagonist that acts on its own schedule whether or not
the player is present. Format from Beyond the Wall, which had the best one found.

```yaml
name: The Rot Beneath Grenzstadt
imminence: 3
clues:                    # the ordered discovery path
  - the miller's cough
  - the well that tastes of iron
  - the Weissbruck ledger
  - what the physician buried
  - the cellar under the shrine
  - the thing that is still growing
effects:                  # rolled when the Threat activates
  1: "grows stronger — imminence +1"
  2: "the tainted district permanently worsens"
  3-6: "spreads to an adjacent location"
  7: "a named NPC is taken or turned"
  8: "an open, public horror — the town knows"
ambient:                  # true while inside its reach
  - "corruption exposure: minor, weekly"
  - "no restful sleep"
denizens: [...]
counters:                 # how it can actually be fought
  - "the ledger names the patron"
  - "the shrine cellar can be flooded"
weakness: "it cannot cross running water"
```

### Imminence

| Rating | Meaning |
|---|---|
| 1-2 | Interacts rarely and randomly. A rumour, an occasional body. |
| 3-4 | An active force, a growing concern. Named people start disappearing. |
| 5-6 | Serious concern for everyone; troubles the region constantly. |
| 7+ | An almost constant source of trouble — "perhaps spelling its ultimate doom". |

### Activation

At the start of each in-game week, roll **d12 per Threat**. If the result is **≤ Imminence**,
that Threat activates: roll on its effects table.

Claude chooses *when in the week* it lands — while the player is present (a scene) or while
they are elsewhere (they hear about it later, late and partially).

**If a Threat acts and the player was not there, they must still find out.** A peddler
brings word; a companion's family writes; the market is talking. This is TOR's *News from
Afar* — and information should arrive **late, incomplete, and sometimes wrong**.

### Threats are personal

Every active Threat must have **at least one connection to the player or a companion** —
a birthplace, a debt, a relative, an old employer. Derived at chronicle creation from the
PC's Passion and Cruel Misfortune. The thing threatening the world is already the thing that
marked you.

---

## Elapsed time — the rule that makes this practical

Real sessions are weeks apart. Wyrd does **not** simulate every intervening week.

From Beyond the Wall's *Abstracting Weekly Threat*: take the **expected value** over the
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
  summary: "the man who paid the cultists walked away; you saw his ring"
  hooks: [nobility, altdorf, jewellery, the-rot-beneath-grenzstadt]
  heat: 2        # 0-5. rises when touched, decays slowly when ignored
```

Every scenario **consumes** threads (it needs hooks that match live ones) and **emits** new
ones. Selecting the next scenario means finding one whose hooks match threads that are
currently hot.

**This is Wyrd's genuinely original piece.** TOR's Tale of Years is authored — year 2953 has
a fixed adventure. Beyond the Wall's Threats are procedural but not sequenced. Wyrd must
*select and sequence*, which is exactly the judgment an LLM is good at, provided the state
is written down.

Threads decay. A thread untouched for a year of game time drops in heat and eventually
closes as "never resolved" — which is itself true to the setting. Not everything gets an
answer.

---

## Scenario selection

At the start of an arc, or when a scenario closes, Claude picks the next by:

1. Reading live threads by heat
2. Matching against `scenarios/*/scenario.yaml` hooks, filtered by setting
3. Scaling it to the current **Threat rating `T`** (see [`03-rules.md`](03-rules.md))
4. Rewriting names, places and faction to fit the chronicle
5. Recording `source:` — what it was adapted from and what changed

**Sourcing is by theme, not system.** A Deadlands investigation and a *White Dwarf*
six-pager about a corrupt miller are equally valid inputs. See
[scenarios.md](../reference/scenarios.md) and
[library-triage.md](../reference/library-triage.md).

**Prefer short-form.** The magazine and fanzine archives are the richest seam precisely
because a six-page adventure about a corrupt miller has no ambition to be a finale.

---

## Arcs and eras

An **arc** is 5-10 scenarios around one Threat, ending with a real change to the world —
usually not a victory.

A chronicle is divided into named **eras** that state the shape of the decline, as in *The
Darkening of Mirkwood*:

> The Quiet Years → The First Signs → The Bad Winter → What Came After

Eras are named in advance and set the ambient register. They are also the honest statement
of the campaign's thesis: **things get worse.**

## The long defeat

The register, from TOR, stated better than I can restate it:

> "Even heroes can hardly avert this fate — all the odds are against them. But there is
> something they can certainly do: they can fight to hold back the darkness for another day,
> another month, maybe another year... they will at least save something from the inevitable
> doom."

And:

> "The emphasis should be on personal tragedy. The forest may be lost, but can the heroes
> save their own families and friends?"

So: **the world's darkness escalates; the player's power does not.** Scope stays personal
while stakes rise around it. Victory is holding the line one more year, and saving
something specific and small.

This is the mechanical answer to constraint 5 and constraint 6 together.

## Holdings

From TOR. Over years the player accumulates something — a cottage, a boat, a workshop, a
name in a guild, a family. It is recorded in the chronicle and it is **leverage**:

> "If Spiders attack a Woodman village, that's a tragedy for the heroes to avenge — but if
> the village includes a farm that is part of a hero's holding, then it's personal."

And it manufactures the dilemma that a long campaign needs: remain on the quest, or go home
and defend your own.

## Succession

A chronicle running years may outlast one rat-catcher. When the PC dies, is damned, or
retires, the default is **succession, not replacement**: an apprentice, a child, a
companion. They inherit the holdings, the threads, the enemies, and the reputation —
and none of the competence.

"Your daughter inherits the ledger and the enemies" keeps a decade of history live in a way
a fresh character never can.
