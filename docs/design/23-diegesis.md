# Wyrd — the character sheet you never see

The player must be able to know their character without reading their statistics. the player character
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
| **Never shown** | hidden threshold, thread heat, party tension, bond values, character stats, difficulty numbers, Threat imminence | nothing — these are engine state |
| **Diegetic only** | stamina, skills, taint, trauma, strain, reputation, wounds, inventory | prose, from the character's own perspective |
| **Countable** | Fate, Fortune, Luck | prose that is still *countable*, because the player must decide whether to spend them |

The countable class is the only compromise, and it is forced: a resource you must choose to
spend has to be legible. It can still be said in the character's idiom — *"there is one more
turn of luck in you today"* — but the player must be able to count it. Never obscure a
number the player is required to make a decision with.

Mechanical detail is always available **on request**. A player who asks "what's my actual
stamina?" gets the number. The default is prose; the raw sheet is a query, not a habit. The
request mechanism itself — how a player steps out of the fiction to ask, and how the answer
stays out of the chronicle — is specified in
[`17-out-of-character-mode.md`](17-out-of-character-mode.md).

---

## Bands

Defined so the engine renders them consistently rather than the GM improvising a new
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

### Skills

Read as a percentage, per [`03-rules.md`](03-rules.md):

| Skill | The character knows |
|---|---|
| ≤25% | never really done this; you would be guessing |
| 30–40% | trained. You know the shape of it |
| 45–55% | practised. It feels natural now |
| 60–70% | expert. People ask you about this |
| 75%+ | it is part of who you are |

So a character at 35% "has done this since he was fourteen", and the same character at 25%
in another skill "has tried it exactly twice, both times badly".

### Taint — felt as wrongness, never as a score

| Taint | The character knows |
|---|---|
| 0 | nothing |
| 1-2 | a thought that wasn't yours, once, and it hasn't fully left |
| 3-5 | you avoid mirrors at certain hours. You have started explaining things to yourself |
| 6-8 | it is company now. It has opinions |
| 9+ | you are no longer the only one deciding |

**The hidden threshold is never rendered at all**, in any form. Not even as unease. The player finds
out where it was when it runs out. Taint itself is Diegetic-only, not Never-shown ("Three
visibility classes" above): "never as a score" describes the default, in-fiction narration — the
general on-request rule still applies, the same as Stamina or a skill
([`17-out-of-character-mode.md`](17-out-of-character-mode.md)). Only the hidden threshold is
withheld even then.

### Trauma and Strain

Strain is *today* — "your hands won't settle", "you keep checking the door". Trauma is
*permanent* and shows as accumulated tells the character has stopped noticing, which other
people notice for them. An Affliction is never described as an Affliction; it is described as behaviour.

### Resolve and being Spent

Resolve is rendered as capacity to keep going, not as a bar. Spent — Resolve fallen to Taint
— is the one state that *should* be unmistakable, because it changes what the character is
willing to do: "you cannot make yourself care what happens next."

### Inventory — realistic, not logistic

No encumbrance table. No item list unless asked. The character recalls what they are
carrying the way a person does — the things that matter, in the order they matter:

> The coat, still wet. The knife on your belt, which you have never used on anything that
> could hit back. The lamp, out of oil. And the key, which is the problem.

The character also knows what is **missing** without being told, because people do.

**Encumbrance is the same question asked the other way round.** There is no weight table and no
carrying-capacity score ([`03-rules.md`](03-rules.md) §2). When it matters whether a character is
plausibly carrying something, the GM asks it of the fiction the same way — what they're wearing,
where they came from, what they've said they packed — and answers from that, not from a sum.

---

## The character as a knowledge source

The character knows things the player does not: who drinks where, which official is
bribable, what the local law says about a damaged record. The player does not, and should
not have to.

So the player can ask **in character** — *"what do I know about this place?"* — and get an
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
[`20-tooling.md`](20-tooling.md) applied to prose: the model chooses the words, never the
band.

Bands are per-setting where the idiom differs — a farmhand and a void-sailor describe
exhaustion differently. **The thresholds are the same; only the words change**, which is the
same rule renames follow everywhere ([`20-tooling.md`](20-tooling.md)).
