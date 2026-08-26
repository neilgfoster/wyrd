# Research: Loyalty and party eligibility

**Feature**: 009-loyalty-and-party-eligibility | **Date**: 2026-08-25

## 1. Why this is engine work and not setting data

`13-authoring-a-setting.md` is explicit: a setting may extend, retune, rename or disable what the
engine provides, and **may never add a mechanism**. A rule constraining who may be in a party is a
mechanism. A setting cannot supply it, so the engine must.

It also matters more here than it would at a table with several players. The player runs one
character and **the GM runs everyone else** (`04-session.md`), so "who may join this party" is a
question the engine answers dozens of times across a chronicle, unprompted. Left to judgement it
drifts, and the drift is invisible.

## 2. The vocabulary is nearly all taken

| Candidate | Status |
|---|---|
| **Allegiance** | **taken** — `03-rules.md` §6 uses it for organisational standing a character *accumulates*, one of the things that grows over a long chronicle |
| **Faction** | **taken** — `14-entities.md` makes it an entity type (an `organisation`) |
| **Bond** | **taken** — `04-session.md`, a companion's −3..+3 feeling toward the player |
| **Drive** | **taken** — what a character wants; invocable for −20 |
| **Standing** | claimed by #55 in Stage 9 |
| **Loyalty** | **free** — zero uses anywhere in `design/` |

*Alignment* is unusable: it is a specific published system's term and would fail the naming rule in
`CLAUDE.md` on sight. *Creed* was considered and rejected as leaning religious, which is a register,
and registers belong to settings ([ADR 0004](../../doc/adr/0004-tone-belongs-to-the-setting.md)).

**Loyalty** is plain, unused, carries no genre, and covers both the chosen kind (a sworn servant) and
the imposed kind (born to a side). Settings rename it anyway; renames are presentation-only.

## 3. A boolean relation is too weak, and a full matrix is too much

Two characters can stand in three useful relations, not two:

| Relation | Meaning | Evidence it is needed |
|---|---|---|
| *(default)* | nothing to say | most pairs, in most settings |
| **strained** | they will travel together, badly | a pious knight and a thief is a party; a tense one |
| **irreconcilable** | they will not travel together at all | a witch hunter and what they hunt |

A boolean forces the middle case into one of the extremes: either the tense pair is forbidden, which
is wrong and makes most settings unplayable, or it is unremarkable, which throws away the friction
that is the point.

A full N×N matrix expresses everything and costs a setting O(n²) declarations, nearly all of them
default. **Declaring only the non-default pairs** gives the same expressiveness at the size of the
interesting part.

## 4. `strained` should not need a new mechanism

`04-session.md` already has **Party Tension** — a 0–6 track that rises on friction, becomes visible
at 3, breaks at 6 with a departure or betrayal, then resets. Its listed causes are already exactly
this kind of thing: overruling a companion on their agenda, a secret surfacing, taint showing.

A strained pairing is friction of precisely that shape, so it feeds the existing track rather than
introducing a parallel one. That also gives the outcome for free: sustained strain eventually
*breaks*, and breaking is already defined.

## 5. A Loyalty that changes mid-chronicle already has an outcome

Some settings make conversion or corruption possible, so a party can become invalid without anyone
joining or leaving. The engine needs no new event for this: an irreconcilable pairing inside an
existing party is exactly what Tension breaking describes — a departure, a betrayal, a refusal at
the worst moment.

So the rule is *when Loyalty changes, re-check the party*, and the consequence is machinery that
already exists.

## 6. What this does not decide

**Whether a setting attaches Loyalty to careers.** It may — a career that only servants of one side
can hold — but the engine does not require it, because plenty of settings have careers open to
everyone and one dividing line elsewhere.

**Capacity gates of other kinds.** Whether a character can work magic at all is a different question
and belongs to #26 (Stage 10). Loyalty is about who will travel with whom, not what a character can
do.
