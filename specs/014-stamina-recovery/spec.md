# Feature Specification: Stamina recovery and the fate of lasting wounds

**Feature Branch**: `014-stamina-recovery`

**Created**: 2026-08-25

**Status**: Implemented

**Input**: GitHub issue #10 (R1.2), under Stage 6 — Harm, recovery and death (#45). Depends on #6,
which landed as the Aftermath table. Out of scope: the Aftermath table's own contents (#6); the
adversary model (#54); the player-facing conversion (#69); setting-specific healing content.

## Context

Two silences, and they are the same silence read at two timescales.

**Nothing in `design/` restores Stamina.** Every other track has an answer: Strain recovers 1 at a
Rally ([`doc/design/03-rules.md`](../../doc/design/03-rules.md) §5), Taint and Strain both have the
**Recover** undertaking, Trauma sawtooths through Afflictions. Stamina — the resource the whole of
§2 spends — has nothing at all.
[`doc/design/09-aftermath.md`](../../doc/design/09-aftermath.md) explicitly declines to answer it
("How a character gets back up, and over how long, is not this table's business"), which was correct
scoping there and leaves the question homeless.

The consequence is not a rounding error. A starting character has **Stamina 6**
([`doc/design/05-character-creation.md`](../../doc/design/05-character-creation.md)), and an ordinary
telling blow drops a full-Stamina character. Without a recovery rule, that character is at 0 for the
rest of the chronicle. The combat loop has no bottom half.

**And nothing says whether a lasting wound ever mends.** The Aftermath table hands out wound records
on five of its eight rows, and says outright that a wound record "carries no healing field, no
duration and no severity… whether a wound ever mends is not settled here". Meanwhile
[`doc/design/16-session.md`](../../doc/design/16-session.md) already lists **Mend** — "treat a lasting
wound" — as a downtime undertaking. So the engine has a named undertaking whose effect is undefined,
pointing at a record shaped to refuse the question. One of those two has to move.

Three pressures shape every answer here.

**Recovery must not undo the fight.** The Aftermath table's whole argument is that dropping costs
something durable. A rule that returns a character to full between beats makes the table's 71% chance
of a lasting mark the only thing combat ever leaves behind, and makes Stamina a per-scene resource
rather than a state the chronicle carries.

**Recovery must not stall the chronicle either.** A character who cannot get back to fighting shape
without a season of downtime will spend the chronicle avoiding the engine's own combat rules — and
the register this engine is built for is attritional, not paralytic.

**No new cadence, no new number.** The engine already has exactly two clocks for restoring anything:
the **Rally** (between beats, restores 1 Strain) and **downtime** (weeks to a season, one undertaking
chosen). Answering Stamina on a third clock would be a parallel mechanic, and two clocks describing
one thing is the fault class this repo keeps being corrected for.

## Clarifications

### Session 2026-08-25

- **Q: What restores Stamina, at what rate?** → **1 at every Rally, and full at the end of a downtime
  phase, automatically.** The Rally rate is Strain's rate at Strain's trigger — no new number and no
  new clock. Downtime restores without spending the one undertaking: charging Mend-or-Recover for
  something weeks of rest would do anyway would make the undertaking choice a formality after every
  real fight, and the choice is the point.
- **Q: What does a combatant who dropped below 0 come back at?** → **0, climbing by the normal rule.**
  The Aftermath roll has already said what the fight cost; this says only where the track restarts.
  A dropped starting character is six Rallies from full, which is the longest road the rule offers and
  is meant to be.
- **Q: Do lasting wounds mend?** → **Yes, one grade per downtime spent on Mend, except a recurring
  wound, which never closes.** Mend moves one named wound's effect one step toward zero within the
  closed effect set; the record is kept and marked closed rather than deleted. The recurring wound is
  exempt because re-reading a `death` row onto it is exactly what a spent Fate point buys — a mending
  rule that erased it would price Fate's promise at one season.

## Requirements

### FR-1 — Stamina has a stated recovery trigger and rate

`design/` states, unambiguously and in one place, what restores Stamina, at what rate, and gated on
what. A reader must be able to apply it without inventing the missing half at the table
([`doc/design/20-tooling.md`](../../doc/design/20-tooling.md)).

### FR-2 — The rule hangs off a clock the engine already has

Recovery is triggered by the **Rally**, by **downtime**, or by both — not by a new phase, a new
track, or a new per-session allowance. Where a rate is given, it is justified against a number the
engine already publishes rather than chosen freely.

### FR-3 — Dropping is distinguished from being hurt

A combatant who went **below 0** and rolled on the Aftermath table does not re-enter play on the same
terms as one who ended the fight at 2 Stamina. The rule states what a dropped combatant comes back
at, and when.

### FR-4 — The fate of lasting wounds is settled explicitly, either way

Either wounds never mend — stated in `design/`, with the reasoning — or a mending mechanism is
defined: what triggers it, what it costs, what it changes, and what it cannot touch.

### FR-5 — Mend stops being an undertaking with no effect

`doc/design/16-session.md`'s **Mend** undertaking either gains a defined effect or is removed. An
undertaking a player can choose and the engine cannot resolve is a hole in the same document that
lists it.

### FR-6 — The recurring wound's permanence is answered against what Fate bought

`doc/design/09-aftermath.md` says a recurring wound lasts "the rest of the chronicle, unless a later
rule says otherwise". This is that later rule, and it must state its position deliberately: whether
mending can reach a recurring wound, given that re-reading a `death` row onto the recurring wound is
what a spent Fate point buys. A mending rule that erases it prices Fate's promise at one downtime.

### FR-7 — Whatever state changes are additive

Any new field on a wound record or on the character is an **additive** change
([`doc/design/22-evolution.md`](../../doc/design/22-evolution.md)), and
[`doc/design/19-state.md`](../../doc/design/19-state.md) is updated to hold it. A closed wound's record is
not deleted — history is never recomputed.

### FR-8 — Effects step only through values the closed set already permits

`doc/design/09-aftermath.md` declares a closed set of wound effects (`stamina_max: -N`, `skill: -N`,
`dread: +N`), and an effect naming anything else is a load error. Any mending rule that changes an
effect must leave it inside that set at every step.

### FR-9 — The numbers are computed at real character values, not asserted

Time-to-recover, and the attrition a real chronicle actually sees, are computed at the Stamina and
skill values characters actually have — Stamina 6 (7 after a completed career), skills 25/35/45/55 —
never at a midpoint. A committed script does the computing (CLAUDE.md).

### FR-10 — The script asserts agreement with figures earlier issues computed

The check script asserts, not eyeballs, that its model reproduces the merged figures it depends on:
an ordinary hit puts **1.56** points through modest armour and takes **4.5** hits to drop a starting
character (`specs/013-the-mob-rule/check_mobs.py`), and the Aftermath table's lasting-mark/death
weights are unchanged by anything here.

### FR-11 — Every figure the design document publishes is asserted by the script

No number reaches `design/` that the script does not compute and assert. A figure in prose that
nothing recomputes is how a table goes stale.

### FR-12 — The rule survives the player-facing conversion

Nothing specified here may deepen combat's dependence on the opponent rolling dice, or on any number
the player-facing mapping (#69, slope 1 clipped 5–95%) removes.

### FR-13 — The design document, not the spec, is left as the record

`design/` is rewritten in place to describe present behaviour. Decisions where a real alternative was
rejected are recorded as ADRs, which are never edited afterwards.

## Constraints

- Rules changes apply **forward only**; history is never recomputed
  ([`doc/design/22-evolution.md`](../../doc/design/22-evolution.md)).
- Setting-agnostic: descriptive English labels, no borrowed system vocabulary, no tone baked into the
  mechanic's description. What recovery *feels* like is the setting's.
- The engine **names no skill** ([ADR 0013](../../doc/adr/0013-the-engine-names-no-skill.md)), so
  no rule here may turn on a healing skill by name.
- A setting may already disable tracks and rename mechanics; nothing here may assume Stamina recovery
  is the same in every setting beyond what `13-authoring-a-setting.md` allows.
- `specs/014-stamina-recovery/` is committed alongside the change.

## Assumptions

- The Rally and downtime remain the engine's only restoration clocks; no third is introduced.
- Companions recover on the same rule as the player's character, as they roll on the same Aftermath
  table. Nothing here introduces a companion-specific rate.
- Maximum Stamina is changed only by a completed career (+1) and by a `stamina_max: -N` wound;
  recovery restores *current* Stamina toward that maximum and never raises the maximum.

## Success criteria

- A GM reading `design/` can answer "how much Stamina do I have back?" at any point in a chronicle
  without a judgement call.
- A character dropped in a fight has a defined, finite path back to full, and the path is long enough
  that the fight is remembered and short enough that play continues.
- Whether a given wound can ever be removed is answerable from the wound record and one rule.
- Every published figure is reproduced by `python3 specs/014-stamina-recovery/check_recovery.py`.

## Acceptance criteria

- [ ] A Stamina recovery rule exists in `design/`, unambiguous about trigger and rate.
- [ ] The fate of lasting wounds is settled — never healing (with reasoning) or a defined mechanism.
- [ ] `doc/design/16-session.md`'s Mend undertaking resolves to a defined effect, or is removed.
- [ ] Both decisions are recorded as ADRs where a real alternative was rejected.
- [ ] `doc/design/19-state.md` holds any new field, additively.
- [ ] `check_recovery.py` computes every published figure and asserts agreement with prior issues'.
- [ ] `python3 tools/check_docs.py` and `python3 tools/backlog.py check` pass.
