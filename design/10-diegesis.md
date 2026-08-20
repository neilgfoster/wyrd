# Wyrd — the character sheet you never see

The player must be able to know their character without reading their statistics. Wendel
does not know he has 2 stamina left; he knows he is not going to win another fight today. He
does not know he is Blunt 5; he knows a mace feels honest in his hand in a way a sword never
has.

This is not decoration. A player who reads numbers optimises against numbers, and the
register collapses. A player who reads their own body makes decisions the way the character
would.

---

## Three visibility classes

| Class | Examples | Rendered as |
|---|---|---|
| **Never shown** | doom clock, thread heat, party tension, bond values, NPC stats, difficulty numbers, Threat imminence | nothing — these are engine state |
| **Diegetic only** | stamina, skills, corruption, insanity, stress, reputation, wounds, inventory | prose, from the character's own perspective |
| **Countable** | Fate, Fortune, Luck | prose that is still *countable*, because the player must decide whether to spend them |

The countable class is the only compromise, and it is forced: a resource you must choose to
spend has to be legible. It can still be said in the character's idiom — *"there is one more
turn of luck in you today"* — but the player must be able to count it. Never obscure a
number the player is required to make a decision with.

Mechanical detail is always available **on request**. A player who asks "what's my actual
stamina?" gets the number. The default is prose; the raw sheet is a query, not a habit.

---

## Bands

Defined so the engine renders them consistently rather than Claude improvising a new
vocabulary every session.

### Stamina — as a fraction of max

| Fraction | The character knows |
|---|---|
| 100% | unmarked |
| 75-99% | winded; a bruise coming up |
| 50-74% | hurt, and favouring something |
| 25-49% | badly used; everything costs more than it should |
| 1-24% | barely standing; the next one might do it |
| ≤0 | out of the fight |

Fractions, not absolutes, so it holds as max stamina grows.

### Skills — Warlock's ladder

| Level | The character knows |
|---|---|
| 4 | never really done this; you'd be guessing |
| 5 | you've tried it; it didn't go well |
| 6 | trained. You know the shape of it |
| 7-8 | practised. It feels natural now |
| 9-10 | expert. People ask you about this |
| 11-12 | it is part of who you are |

So Wendel "has held a book of prayer since he was fourteen" (Incantation 6) but "has swung a
mace exactly twice, both times badly" (Blunt 5).

### Corruption — felt as wrongness, never as a score

| Corruption | The character knows |
|---|---|
| 0 | nothing |
| 1-2 | a thought that wasn't yours, once, and it hasn't fully left |
| 3-5 | you avoid mirrors at certain hours. You have started explaining things to yourself |
| 6-8 | it is company now. It has opinions |
| 9+ | you are no longer the only one deciding |

**The doom clock is never rendered at all**, in any form. Not even as dread. The player finds
out where it was when it runs out.

### Insanity and Stress

Stress is *today* — "your hands won't settle", "you keep checking the door". Insanity is
*permanent* and shows as accumulated tells the character has stopped noticing, which other
people notice for them. A derangement is never described as a derangement; it is described
as behaviour.

### Hope and being Beset

Hope is rendered as capacity to keep going, not as a bar. Beset — Hope fallen to Corruption
— is the one state that *should* be unmistakable, because it changes what the character is
willing to do: "you cannot make yourself care what happens next."

### Inventory — realistic, not logistic

No encumbrance table. No item list unless asked. The character recalls what they are
carrying the way a person does — the things that matter, in the order they matter:

> Your robes, still stinking of last night. The mace on your belt, which you have never
> used on anything that could hit back. The shield of the faith, in the vestry where it
> always is. The book of prayer. And the key, which is the problem.

The character also knows what is **missing** without being told, because people do.

---

## The character as a knowledge source

The character knows things the player does not. Wendel knows Hemmelfurt — who drinks where,
which magistrate is bribable, what the Verenan liturgy says about a damaged record. The
player does not, and should not have to.

So the player can ask **in character** — *"what do I know about the Overseer?"* — and get an
answer scaled to the character's competence, not the player's. That is a legitimate move, it
costs nothing, and it usually does not need a roll: it is recall, not research.

Where the character *wouldn't* know, say so plainly and in their voice. Absence of knowledge
is information too.

---

## Engine support

```
wyrd status                 # diegetic prose: body, mind, soul, carried
wyrd status --raw           # the actual sheet, on request
wyrd knows <topic>          # what this character would know, at their competence
```

Band lookup is deterministic and lives in `engine/tables/bands.py` — the *mapping* is a
table, only the sentence is written. This is the tooling rule in
[`07-tooling.md`](07-tooling.md) applied to prose: the model chooses the words, never the
band.

Bands are per-setting where the idiom differs. A Reikland rat-catcher and an Imperial Guard
trooper describe exhaustion differently; the thresholds are the same.
