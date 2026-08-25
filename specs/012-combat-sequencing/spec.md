# Feature Specification: Combat sequencing, ranged combat, flight and surprise

**Feature Branch**: `012-combat-sequencing`

**Created**: 2026-08-25

**Status**: Clarified

**Input**: GitHub issue #11 (R1.4), under Stage 5 — Conflict (#44). Out of scope: the mob rule,
which is #13 and depends on this landing; harm, recovery and the critical tables, which are Stage 6
(#45); the adversary model, which is #54.

## Context

**The word *initiative* appears in no design document.** `design/03-rules.md` §2 specifies what an
attack *is* — an opposed test, armour subtracting dice, a telling blow, a critical below zero
Stamina — and says nothing about when anyone does it. There is no round, no turn order, no
statement of who swings first. There is no ranged combat at all. There is no fleeing, no
disengaging, no surprise and no ambush.

Per [`design/07-tooling.md`](../../design/07-tooling.md), a gap here is not a neutral silence. Every
question the rules decline to answer becomes a judgement call at play time, made differently each
session, by an engine whose whole premise is that anything with a correct answer is computed rather
than inferred. An unsequenced exchange is a rule delegated to improvisation.

Two pressures shape every answer below, and they pull against each other.

**The medium has no positions.** Text play has no map, no facing, no measured distance. A rule that
needs to know how many metres apart two combatants are cannot be run, because nothing in the
chronicle records it. Anything imported from a tactical game — a grid, movement rates, ranges in
metres — is unusable here even where it is well designed.

**A round costs prose.** *Only roll when it is dramatic* still binds. A sequencing rule that adds a
roll per combatant per round turns one beat into a page, and sessions happen on a phone. The
acceptance bar runs in both directions: under-specified leaves a GM judgement call, over-specified
imports a wargame the medium cannot support.

There is also a live constraint from the parent stage. **#44 has set a direction — combat moves to
player-facing rolls, the opponent's capability becoming a static number rather than a roll** — and
recorded it as this stage's to implement. That conversion is not this feature's work, but no rule
this feature adds may make it harder: nothing here may deepen combat's dependence on the opponent
throwing dice.

## Clarifications

### Session 2026-08-25

- Q: How should #11 handle the player-facing conversion #44 set the direction for? → A: Stay
  compatible with it, and raise it as a sibling issue under #44 carrying the computed slope and clip.
- Q: What shape does turn order take? → A: Whoever started the exchange acts first; surprise and
  ambush are the extreme case of the same rule. No roll.
- Q: How much spatial state does the engine carry for ranged combat? → A: One binary state —
  engaged in close combat, or not.
- Q: What does surprise do to the first round? → A: The surprised side does not act in it at all;
  ambush additionally makes the first attacks easier. Gated on the computation.
- Q: How is disengaging and fleeing resolved? → A: Breaking engagement costs a parting blow from
  each engaged opponent, no roll; getting away is a group test in the everyone-must-get-through shape.


## Computed finding — the player-facing mapping's slope

#44 sets the direction and records the mapping `effective% = 50 + (player_skill − opponent_skill)`,
calibrated so an even match is a coin flip. It does not settle the **slope**, and a half-difference
variant, `50 + (S − O) / 2`, reads as the more cautious choice. It is not. Computed, in
[`check_mapping.py`](check_mapping.py), against two contest models that assume no linearity at all —
a margin contest (both roll, higher `skill − roll` wins) and a degrees contest with the success gate
and ties rerolled:

| S vs O | margin | degrees | `50+(S−O)` | `50+(S−O)/2` | opposed today |
|---|---|---|---|---|---|
| 40 v 40 | 49.5% | 50.0% | 50% | 50% | 30.1% |
| 35 v 30 | 54.4% | 53.4% | 55% | 52% | 27.6% |
| 55 v 40 | 63.4% | 62.3% | 65% | 57% | 43.0% |
| 60 v 30 | 75.1% | 78.2% | **80%** | 65% | 54.0% |
| 70 v 35 | 78.5% | 82.5% | 85% | 67% | 63.9% |
| 100 v 50 | 87.2% | 89.4% | 95% | 75% | 85.0% |

**Slope 1 tracks both models across the whole realistic band; the worst deviation is 8.3 points
against the half-difference mapping's 16.2.** The half-difference version is flat exactly where play
happens: a master against a competent professional reads 75% where both models say 87–89%, and it
needs a 90-point gap to reach the top of the scale at all, against slope 1's 45.

Two things follow that are this spec's to record rather than #44's to rediscover.

**Neither mapping reproduces the current opposed test, and that is the point.** Today 60 v 30 gives
the actor 54% and an even 40 v 40 gives 30% — the actor mostly whiffs. The mapping is a
*replacement* for that curve, not a model of it, which is the whole substance of #44's direction.

**The mapping is clipped to 5–95%.** Slope 1 otherwise reaches certainty at a 50-point gap, where
both contest models say 87–89%, and reaches impossibility going the other way. Neither may be
reachable: a roll that cannot fail is a roll not worth making, and one that cannot succeed removes
the player's reason to try. The clip also keeps the Wyrd die live at every skill gap — the omen is
read from the units digit of the natural roll, so an outcome fixed in advance would still owe the
fiction a reaction it can no longer earn.


## Requirements

### FR-1 — A round is defined

The rules state what a round is: the unit of time in which each combatant acts once, and what it
represents in the fiction. Everything else in this feature is measured in rounds.

### FR-2 — Turn order is decided by a stated rule

**Whoever started the exchange acts first.** The side that initiated takes the first round; the
other responds. Order is therefore determined by a fact the fiction already carries, never by a GM's
choice and never by a roll. Within a side, order is the fiction's and carries no mechanical weight.
Surprise and ambush (FR-8) are the extreme case of this same rule, not a separate system.

The rule states what happens when neither side initiated — a mutual encounter — and that answer is
also a rule, not a judgement call.

### FR-3 — Turn order costs no rolls

Ordering adds **zero dice**. This is a stronger bound than "at most one per round" and it is
available because FR-2 reads the order off the fiction. It also sidesteps a constraint the engine
genuinely has: ADR 0013 names no skill and the engine has no characteristics, so there is no
attribute an initiative roll could be made against without inventing one.

### FR-4 — A combatant's turn has a stated content

What a combatant may do on their turn is specified: how many actions, and what an action may be.
The rule must be answerable without reference to distance or movement.

### FR-5 — Ranged attacks are resolvable without positional geometry

Ranged combat is specified, and specified without a grid, metres, movement rates or facing. What
makes a ranged attack easier or harder is expressed in terms the fiction already carries — cover,
visibility, and the engagement state of FR-5a — and resolves through the existing difficulty ladder
rather than a parallel mechanic.

### FR-5a — Engagement is one binary state

The only spatial fact the engine records is whether two combatants are **in close engagement or
not**. There are no bands, no distances and no positions. Shooting while engaged is harder by a
stated amount. One bit is the whole spatial model, and it is chosen because it is the least the
engine can carry and still answer FR-6 — a band would be positioning in English clothes, and a
chronicle cannot record one anyway.

### FR-6 — Closing and being closed with is stated

Closing to engagement is something a combatant does on their turn. Being closed with is not
refusable except by disengaging (FR-7), which is what gives a shooter a reason to ever stop
shooting. The rules state what closing costs the combatant who does it, and what changes for both
sides once engagement exists.

### FR-7 — Disengaging and fleeing resolve in two steps, each with a stated cost

Leaving a fight is two distinct things, and the rules separate them.

**Breaking close engagement costs a parting blow.** Each opponent still engaged with the departing
combatant attacks as they go. There is no roll to leave — leaving always works, and always costs.

**Getting away from the scene is a group test**, in the *everyone must get through* shape already
specified in `03-rules.md` §1, against the pursuit. On a failure the fight resumes, and it resumes
where the least capable member is. Reusing the existing group-test shape is deliberate: flight is
the case that rule was written for, and a second escape mechanic would be a parallel one.

Flight is therefore never impossible — retreat stays the correct answer to a fight going badly —
and never free.

### FR-8 — Surprise costs the surprised side its first round; ambush is prepared surprise

**A surprised side does not act in the first round at all.** This is FR-2 taken to its extreme: the
exchange began and one side did not know it. The rules state what establishes surprise and who has
it.

**Ambush is surprise that was prepared**, and it additionally makes the first attacks easier by a
stated amount — so setting an ambush buys something over stumbling into an advantage.

Both effects are **gated on FR-14's computation**. A free round is worth a great deal in an engine
where roughly 4.5 hits drop a combatant, and the value of one must be computed before this is
settled. If it proves to end fights before they begin, the fallback is stated in the ADR rather than
discovered in play.

### FR-9 — No positioning of any kind enters the design documents

No grid, no ranges in metres, no movement rates, no facing appears anywhere in the result. This
bound is part of the requirement, not an oversight, and is checkable by grep.

### FR-10 — Nothing added here is a parallel mechanic

Every rule this feature adds resolves through the core roll and the existing difficulty ladder:
modifiers apply to the **skill**, never to the roll, preserving the independence of success, degrees
and the Wyrd die (ADR 0001). One test raises one omen, read from the units digit of the natural
roll, unmodified and unrerolled.

### FR-11 — Nothing added here obstructs the player-facing conversion

Each rule is stated so it survives the direction set on #44 — the opponent's capability becoming a
static number the player rolls against. A rule that only works because the opponent rolls must be
avoided or flagged as needing rework when that conversion lands.

### FR-11a — The mapping's slope and clip are recorded for #44

Where this feature touches the player-facing mapping, it records the computed answer rather than
leaving it open: the slope is **1** — `effective% = 50 + (player_skill − opponent_skill)` — and the
result is **clipped to 5–95%**, so no skill gap ever produces a certainty or an impossibility. This
is recorded as a finding with its computation, for #44 to adopt when the conversion lands; this
feature does not perform the conversion.

### FR-11b — The conversion is given an owner

The player-facing conversion is raised as a **sibling issue under #44**, carrying FR-11a's computed
slope and clip. #44 currently records the direction in a comment and has only #11 and #13 as
children, so nothing owns it — which is the fault the design programme exists to close. This feature
raises that issue; it does not perform the conversion.

### FR-12 — R1.8 has the footing it depends on

The mob rule (#13) reads *petty* and *weaker* against a turn order. This feature leaves a turn order
concrete enough for that rule to be written against, without writing it.

### FR-13 — An exchange is played out by hand before the rule is settled

At least one complete exchange is run end to end against the drafted rules — two sides, a ranged
opening, a close engagement, an attempt to flee — and its outcome recorded. The single playtest this
engine has had corrected the resolution mechanic three times inside two rolls, none of it visible on
paper.

### FR-14 — Round counts are computed, not asserted

Any claim about how long a fight runs, or how much surprise or a first-round advantage is worth, is
produced by a check script at the skills characters actually have, not stated from intuition. Two
probability claims in this repo have been wrong, and both were caught only by computing them.

### FR-15 — The design documents are updated, not merely the spec

`design/03-rules.md` §2 carries the rules as the engine's description, rewritten in place with no
"previously we…" notes. An ADR records any decision with a workable rejected alternative. The spec
is not left as the only record of current behaviour.

## Constraints

- Setting-agnostic: no setting or system name in `design/` or `README.md`; engine labels are
  descriptive English, and tone stays a setting property.
- The core roll, the difficulty ladder and the degree scale from ADR 0001 are not replaced.
- No threshold belonging to Stage 6 (harm, recovery, death) or to the adversary model (#54) is set
  here.
- Python 3.11+, stdlib only, exact arithmetic (`Fraction`) for any computation.
- `check_docs.py` and `backlog.py check` stay green.

## Assumptions

- **The player-facing conversion is not this feature's work.** #44 records the direction and names
  this stage as its owner, but #11's scope is sequencing, ranged combat, flight and surprise. This
  feature is written to be compatible with the conversion rather than to perform it; anything it
  finds about the conversion is reported as a finding for #44.
- **Combat still resolves as an opposed test while this lands**, per `03-rules.md` §1 and ADR 0016.
- **Engagement is a state, not a distance** (settled as FR-5a).
- **Realistic combat skills run roughly 25–55%**, and a realistic fight is one character plus
  companions against a small number of opponents.

## Success criteria

- **SC-001**: A reader can run a complete exchange start to finish from `design/03-rules.md` alone,
  making no judgement call about who acts when.
- **SC-002**: Turn order for a round of any size is determined with zero rolls.
- **SC-003**: A ranged attack is resolvable from one bit of spatial state — engaged or not — with
  no distance recorded anywhere.
- **SC-004**: An attempt to flee has a stated resolution and a stated cost or risk.
- **SC-005**: Surprise costs the surprised side its first round, and the value of that free round
  is computed rather than asserted.
- **SC-006**: A grep for grid, metre, movement rate and facing vocabulary across `design/` returns
  nothing this feature added.
- **SC-007**: The mapping finding is reproducible by running one script, and its conclusion is
  produced by computation rather than asserted in prose.
- **SC-008**: One worked exchange is recorded, and its outcome matches what the drafted rules
  predict.

## Acceptance criteria

- [ ] `03-rules.md` §2 defines the round, turn order and the content of a turn.
- [ ] `03-rules.md` §2 specifies ranged attacks and what changes when engagement closes.
- [ ] `03-rules.md` §2 specifies disengaging and fleeing, with its cost or risk.
- [ ] `03-rules.md` §2 specifies surprise and ambush and their effect on the first round.
- [ ] An ADR records the sequencing decision and the alternatives rejected.
- [ ] A check script computes round counts and the value of acting first, at realistic skills.
- [ ] A worked exchange is recorded in `specs/012-combat-sequencing/`.
- [ ] No positioning vocabulary appears in the result.
- [ ] A sibling issue for the player-facing conversion exists under #44, carrying the computed
      slope and clip.
- [ ] The player-facing mapping's slope and 5–95% clip are recorded as a computed finding for #44,
      with a script that reproduces it.
- [ ] `check_docs.py` and `backlog.py check` pass.
