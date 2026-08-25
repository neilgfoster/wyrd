# Implementation Plan: Combat sequencing, ranged combat, flight and surprise

**Branch**: `012-combat-sequencing` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Rewrite `03-rules.md` §2 so a fight can be run end to end: a round, a turn order that costs no dice,
one bit of spatial state, a ranged attack, a way out, and surprise. Record the decision as one ADR,
compute the two numbers that decide whether the harshest rule in it is survivable, and play an
exchange by hand before any of it is settled.

## The load-bearing decisions

**Turn order is read off the fiction, not off a number the engine does not have.** ADR 0013 says the
engine names no skill and there are no characteristics, so an initiative roll has nothing to roll
against without inventing an attribute — and inventing one to solve a sequencing problem is exactly
the parallel mechanic FR-10 forbids. *Whoever started the exchange acts first* costs nothing, is
never ambiguous, and makes surprise the same rule taken to its extreme rather than a second system
bolted alongside.

The rule has one genuine hole: **a mutual encounter, where neither side started it.** Left open it
is a judgement call every session. The plan closes it with a diegetic first test and a deterministic
fallback: the side already holding a weapon acts first; if both or neither, the player's side does.
The fallback is a metagame rule and the ADR should say so plainly rather than dress it up.

**One bit of space, and closing costs a turn.** Engagement is binary because a chronicle can record
a bit and cannot record a distance. The whole ranged/melee tension then rests on one exchange rate:
**closing to engagement is a combatant's action for that round**, so a melee fighter spends a turn
to reach the shooter, and the shooter who wants clear air spends a parting blow to get it (FR-7).
Neither side is free. If closing were free, ranged combat would have no cost; if it were impossible,
a shooter would never stop shooting. This is the only place in the feature where the balance is
carried by a single choice, and it is the one most worth playing rather than arguing.

**A free round for surprise is the harshest rule here, and it is gated on a computation.** At the
skills characters actually have, roughly 4.5 hits drop a combatant and a fight runs 5–14 rounds.
Whether a free round is a decisive advantage or a modest one is a number, not an intuition, and this
repo has been wrong about a combat probability twice. The rule ships only if the computed win rate
for the surprising side stays short of a foregone conclusion; the ADR records the fallback either
way.

**Nothing here deepens the dependence on the opponent rolling.** Every rule above is stated in terms
of turns, states and costs rather than contested rolls — which is what lets #44's conversion land on
top of it without rework. The one exception is the flight group test, which reads the pursuit's
capability; that is stated as a difficulty, so it converts cleanly.

## What the check script has to settle

`check_sequencing.py`, stdlib only, exact arithmetic (`Fraction`), no sampling:

1. **Fight length in rounds**, at realistic pairings (25–55%), under the current opposed rule and
   the turn order this feature adds. The one number in this area that already exists was wrong, and
   was corrected on #44; this one gets computed rather than quoted.
2. **The value of acting first** — the win rate of the side that takes the first round against an
   otherwise identical opponent. This is what FR-2's rule is actually worth, and it has never been
   quantified.
3. **The value of a free round** (surprise), same comparison. This is the gate on FR-8: if the
   surprising side's win rate is effectively total, the rule ends fights before they start and the
   fallback applies.
4. **The value of the ambush bonus** on top of the free round, across candidate sizes, so the number
   chosen is a rung of the existing ladder rather than a new one.
5. **The cost of fleeing** — expected damage from parting blows at realistic opponent counts — so
   FR-7's "never free" is a quantity rather than an assertion.

Anything the script reveals about the player-facing conversion is **reported to the new sibling
issue, not asserted here** (FR-11b).

## The rules, as planned

**A round** is the span in which every combatant acts once. It has no fixed duration in the fiction;
it is as long as the exchange needs.

**Turn order.** The side that started the exchange acts first, then the other. Within a side the
order is the fiction's and carries no mechanical weight. On a mutual encounter, the side already
holding a weapon acts first; if both or neither, the player's side does.

**A turn is one action.** Attack in close combat, shoot, close to engagement, break engagement,
ready or use something, or act on the fiction. One action, no action economy, no bonus actions — the
prose budget will not carry more and FR-10 will not carry a second currency.

**Engagement** is binary. Closing costs the closing combatant their action. Being closed with is not
refusable except by breaking engagement, which costs a parting blow.

**Ranged attacks** resolve as any attack, on the existing difficulty ladder. Shooting while engaged
in close combat is harder by a stated rung; cover and poor visibility are further rungs. No distance
is recorded anywhere, because the engine cannot record one.

**Flight** is two steps. Breaking engagement always works and always costs: each opponent still
engaged attacks as you go. Getting away is then a group test in the *everyone must get through*
shape (§1) against the pursuit's difficulty; on a failure the fight resumes where the least capable
member is.

**Surprise** costs the surprised side its first round entirely. **Ambush** is surprise that was
prepared, and eases the first round's attacks by a stated rung.

## Steps

1. `check_sequencing.py` — settle the free-round gate, the ambush rung and the cost of flight;
   assert only what this feature owns, report the rest.
2. `worked-exchange.md` — one complete exchange played by hand: a ranged opening, a closing, an
   attempt to flee, resolved against the drafted rules, with its outcome checked against what the
   script predicts (FR-13).
3. `03-rules.md` §2 — rewritten in place: round, turn order, the turn, engagement, ranged attacks,
   flight, surprise and ambush.
4. ADR 0018 — the sequencing decision and the alternatives rejected.
5. Raise the sibling issue under #44 for the player-facing conversion, carrying `check_mapping.py`'s
   slope and clip (FR-11b).
6. `check_docs.py` and `backlog.py check` green.

## Constitution Check

| Gate | How this satisfies it |
|---|---|
| Nothing unpublishable enters the repo | No source text, no quotation; every rule is derived from this engine's own constraints |
| No setting or system vocabulary in `design/` | Round, turn, engagement, parting blow, surprise, ambush — descriptive English throughout; checked by grep |
| Tone is a setting property | No register is baked in; the rules describe sequence and cost, never how a fight feels |
| Computed, not inferred | The free-round gate, the ambush rung and the cost of flight are all script output; nothing about probability is asserted in prose |
| Rules apply forward only | New rules; no history is recomputed |
| Design docs rewritten in place | §2 is replaced, not appended to; no "previously we…" notes |
| Capability change goes through Spec Kit | `specs/012-combat-sequencing/` is committed |
| A rejected alternative earns an ADR | ADR 0018 records initiative rolls, range bands and free disengagement as the rejected options |

No violations, so no Complexity Tracking entries.

## Project structure

```text
specs/012-combat-sequencing/
├── spec.md
├── plan.md                  # this file
├── tasks.md
├── check_mapping.py         # the #44 slope finding, already computed
├── check_sequencing.py      # the free-round gate, the ambush rung, the cost of flight
├── worked-exchange.md       # FR-13
└── checklists/requirements.md

design/
├── 03-rules.md              # §2 rewritten
├── adr/0018-combat-sequencing.md
└── README.md                # ADR index row
```

**Structure decision**: this repository is a design corpus, not an application. There is no `src/`
and no test suite in the usual sense — the check scripts under `specs/` *are* the tests, each
asserting the claims its own feature makes, and `tools/check_docs.py` is the integration test over
the documents. This feature follows that shape exactly.

## Technical context

**Language**: Python 3.11+, standard library only. **Dependencies**: none. **Testing**: the feature's
own check script, plus `tools/check_docs.py` and `tools/backlog.py check`. **Arithmetic**: exact
(`Fraction`), never sampled — a Monte Carlo answer to a question with a closed form is the inference
ADR 0005 rules out.

## Risks

**Closing-costs-a-turn is the rule most likely to be wrong on paper.** It is the single exchange
rate holding ranged and close combat in tension, and its failure mode — a shooter who can kite
forever, or a melee fighter who can never arrive — will not show up in a probability table. The
mitigation is FR-13: play it, with a ranged opening and a closing, before it is settled.

**A free round may be worth more than it looks.** It is not one extra attack; it is an extra attack
*and* a round in which the other side cannot reduce your side's numbers. The script must model the
whole fight, not one exchange, or it will understate it — and understating it is precisely how the
last combat number in this repo went wrong.

**The mutual-encounter fallback is a metagame rule** inside an engine that otherwise keeps its rules
diegetic. It is small and it is honest, but it should be named as a compromise in the ADR rather
than left to be discovered.
