# Feature Specification: The crowd rule

**Feature Branch**: `013-the-mob-rule`

**Created**: 2026-08-25

**Status**: Implemented

**Input**: GitHub issue #13 (R1.8), under Stage 5 — Conflict (#44). Depends on #11, which landed as
ADR 0018. Out of scope: combat sequencing itself (#11); the adversary model (#54); harm, recovery
and the critical tables (Stage 6, #45); setting-specific crowd content.

## Context

The mob rule in `docs/design/03-rules.md` §2 was one sentence:

> Each round a character also clears petty opponents weaker than themselves, so one character plus
> companions can face a crowd without a roll per body.

It carries no numbers, and it defines neither *petty* nor *weaker* — the two terms the whole rule
turns on. As written it cannot be applied without the GM inventing the missing half at the table,
which is what [`docs/design/27-tooling.md`](../../docs/design/27-tooling.md) and ADR 0005 exist to prevent.

Two further silences are load-bearing and were not named in the issue. **The rule says nothing about
what the crowd does back** — and a crowd that cannot hurt anyone is scenery, which makes the rule
free rather than useful. And **it says nothing about the GM's side of the roll budget**: a rule that
spares the player sixty `d100` rolls and leaves the GM rolling sixty has not removed the cost, it has
moved it.

Two pressures shape every answer, and they pull against each other. **The rule exists to delete
rolls**, so anything it adds per body defeats it. And **the rule must not delete the fight**: an
engine in which crowds are safe has made the numbers on the other side meaningless.

The stage's live constraint from #11 still binds: combat is moving to **player-facing rolls**, the
opponent's capability becoming a static number, at slope 1 clipped to 5–95%. Nothing here may deepen
combat's dependence on the opponent throwing dice, and every number here is computed under **both**
today's opposed test and that mapping.

## Clarifications

### Session 2026-08-25

- Q: Does *petty* survive the naming rule in `CLAUDE.md`? → A: No. It is a judgement about an
  opponent's worth, not a description of capability. Replaced by the mechanic it was standing in
  for: a body one blow removes.
- Q: What statistic defines a qualifying opponent? → A: Maximum Stamina and armour, both on their
  own sheet — computed to the point where one ordinary hit stops removing them.
- Q: What defines *weaker*? → A: A stated skill gap against the opposing side, anchored to the
  untrained 10% and the 25% a skill opens at.
- Q: How many are cleared per round? → A: One, free of the action, bounded by what rolling it out
  would average under the mapping.
- Q: What does the crowd do back? → A: One attack per character it is engaged with, with extra
  bodies converting into the existing difficulty ladder to a stated ceiling.

## Computed findings

All produced by [`check_mobs.py`](check_mobs.py), at real party and crowd sizes rather than at a
midpoint.

**There is no Stamina cliff, and that is what fixes the threshold.** A single ordinary hit takes a
body below zero:

| Stamina | armour | worst weapon in the band | best |
|---|---|---|---|
| 1 | none | **66.7%** | 100% |
| 1 | light | 11.1% | 90.7% |
| 2 | none | 33.3% | 97.2% |
| 3 | light | 0% | 71.3% |

Only *Stamina 1, no armour* is removed by one blow under every weapon in the plausible band. The
first drafted threshold — Stamina 3 in light armour — was rejected by the script at **16.7%** on a
mid-band weapon.

**The free clear's discount is bounded.** Under the mapping, attacking a qualifying body and rolling
for it removes **0.55 to 0.80** bodies a round across skills of 25–55%. A free clear of 1 is a
discount of **1.25× to 1.82×**. Under today's opposed test the same figure reads up to **5.04×**,
which is an artefact of a test in which a competent character misses an untrained one two times in
three — reported, and deliberately not designed around.

**The crowd's threat saturates at three bodies on a target**, where +10 per extra body meets the
ladder's top rung. Rounds to put a competent, Stamina-6 character below zero, under the mapping:
**5.7** unarmoured, **12.9** in modest armour. A lone unarmoured character clears six bodies in 6
rounds and is dropped by them in 5.7 — they lose.

**The damage scale agrees with what #44 established.** A mid-band weapon through modest armour is
**1.56** points and **4.5** hits to drop, which is what specs/012 is calibrated to. An earlier draft
of the script used the weapon band's mean and computed 2.15 and 3.26 — internally tidy, and
disagreeing with a merged figure.

## Requirements

### FR-1 — *Petty* is answered explicitly, either way

The naming question the issue raises is decided and recorded, not left. Whatever term results
carries no genre or moral register, per `CLAUDE.md`.

### FR-2 — A qualifying opponent is a lookup on their own statistics

Whether a given opponent qualifies is read from numbers on their sheet. No clause requires an
assessment of what they are, what they are worth, or how the scene feels.

### FR-3 — *Weaker* is a stated comparison against the opposing side

A number, not an adjective, and anchored to values the engine already fixes rather than invented.

### FR-4 — The clear has a number, and the number is bounded by what rolling would give

How many bodies are cleared per round is stated. The rate is computed against what attacking and
rolling for the same bodies would average, under both resolution models, and the discount is
reported rather than assumed.

### FR-5 — The crowd's own attacks are specified, and cost no more rolls than the player's side

What a crowd does on its turn is stated, and it does not reintroduce a roll per body on the GM's
side. Extra bodies resolve through the existing difficulty ladder, never a parallel mechanic.

### FR-6 — Nothing added here is a parallel mechanic

Every rule resolves through the core roll and the existing ladder: modifiers apply to the skill,
never the roll (ADR 0001). No new die, no new track, no new scale.

### FR-7 — Nothing added here obstructs the player-facing conversion

Each number holds under both today's opposed test and the recorded mapping, and no rule works only
because the opponent rolls.

### FR-8 — The numbers are computed at real party and crowd sizes

Not at a midpoint. Party sizes 1–4, crowd sizes 4–20, skills 25–55%. Two probability claims in this
repository have been wrong and both were caught only by computing them.

### FR-9 — The script asserts agreement with figures earlier issues computed

The damage scale underneath this rule must be the merged one. A rule computed on its own private
damage model would be internally consistent and wrong.

### FR-10 — Every figure the design document publishes is asserted by the script

Tables are where staleness hides: each row reads as a small factual claim and nothing about a wrong
one looks wrong. Changing the model must fail the script rather than silently disagree with the
prose.

### FR-11 — The rule is played before it is settled

At least one complete crowd fight is run end to end against the drafted rule and its outcome
recorded. Prefer playing a rule over arguing about it.

### FR-12 — The design document, not the spec, is left as the record

`docs/design/03-rules.md` §2 is rewritten in place, with no "previously we…" note. An ADR records the
decision and the workable alternatives rejected.

## Constraints

- Setting-agnostic: no setting or system name, no tone baked into a mechanic's description.
- The core roll, the difficulty ladder and the degree scale are not replaced.
- No threshold belonging to the adversary model (#54) or to Stage 6 is set here. The rule may
  *require* an adversary to state a maximum Stamina and an armour rating; it may not specify how.
- Python 3.11+, stdlib only, exact arithmetic (`Fraction`).
- `check_docs.py` and `backlog.py check` stay green.

## Assumptions

- **Combat still resolves as an opposed test while this lands**, per ADR 0016, and moves to the
  player-facing mapping later. Both are modelled.
- **Weapon damage is setting data**, so every conclusion is taken across the same plausible band
  `specs/008-character-creation` used, and none is allowed to hold at only one point of it.
- **A realistic fight is one character plus companions against a small number of opponents**, and a
  realistic crowd is 4 to 20 bodies.

## Success criteria

- **SC-001**: Given any group and any opposing side, a reader determines whether the rule applies
  from `docs/design/03-rules.md` alone, exercising no judgement.
- **SC-002**: The rule states how many bodies are cleared, by whom, and at what cost.
- **SC-003**: The crowd's own attacks are resolvable in one roll per engaged character.
- **SC-004**: Every number in the rule is reproducible by running one script.
- **SC-005**: The script fails if the design document's published figures drift from the model.
- **SC-006**: No term in the result carries a moral or genre register.
- **SC-007**: One worked crowd fight is recorded, and the rules it found are folded back in.

## Acceptance criteria

- [x] `docs/design/03-rules.md` states the crowd rule with concrete numbers, not prose alone.
- [x] The qualifying threshold is defined on a creature's own statistics.
- [x] *Weaker* is defined by a checkable comparison against the opposing side.
- [x] Whether the rule applies is a lookup, not a judgement call.
- [x] The *petty* rename question is answered explicitly, and the chosen terms carry no register.
- [x] The numbers were computed at real party and crowd sizes, and the working is recorded.
- [x] The script asserts agreement with the damage scale #44 established.
- [x] A worked crowd fight is recorded in `specs/013-the-mob-rule/`.
- [x] An ADR records the decision and the alternatives rejected.
- [x] `check_docs.py` and `backlog.py check` pass.
