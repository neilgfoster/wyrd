# Feature Specification: Player-facing combat rolls

**Feature Branch**: `018-player-facing-combat`

**Created**: 2026-08-25

**Status**: Draft

**Input**: Issue [#69](https://github.com/neilgfoster/wyrd/issues/69) — convert combat to
player-facing rolls: the opponent never rolls, their capability is a static number the player
rolls against, attacking and defending alike.

## Why this exists

**Combat is a double gate, and no skill escapes it.** An attack is an opposed test
([`03-rules.md`](../../docs/design/03-rules.md) §1, [ADR 0016](../../docs/adr/0016-opposed-tests-need-a-successful-actor.md)):
the attacker must succeed, then beat the defender's degrees. Computed across realistic pairings,
**61-84% of the player's rolls do nothing at all** — the roll that was meant to be the moment of
play most often resolves to nothing happening. Alternatives that keep the two-roll structure
(a static defence number, a defence that costs a resource) shave rolls off one side of the gate and
leave most of them blank regardless.

**#44 decided the direction and nothing owns it.** [#44](https://github.com/neilgfoster/wyrd/issues/44)
(Stage 5 — Conflict) recorded, in a review comment, that combat should become player-facing: the
opponent's capability becomes a static number, and the player rolls against it for both attack and
defence. Its only children are [#11](https://github.com/neilgfoster/wyrd/issues/11) (sequencing,
ranged combat, flight, surprise) and [#13](https://github.com/neilgfoster/wyrd/issues/13) (the mob
rule) — neither performs the conversion. A decision recorded only as an epic comment is the fault
class the design programme exists to close.

**The calibration is already computed and is not re-litigated here.** From
[`specs/012-combat-sequencing/check_mapping.py`](../012-combat-sequencing/check_mapping.py):

```
effective% = clip(50 + (player_skill - opponent_skill), 5, 95)
```

Checked against two contest models that assume no linearity — a margin contest and a degrees
contest with the success gate and ties rerolled:

| S vs O | margin | degrees | `50+(S-O)` | `50+(S-O)/2` |
|---|---|---|---|---|
| 40 v 40 | 49.5% | 50.0% | 50% | 50% |
| 55 v 40 | 63.4% | 62.3% | 65% | 57% |
| 60 v 30 | 75.1% | 78.2% | **80%** | 65% |
| 100 v 50 | 87.2% | 89.4% | 95% | 75% |

Slope 1 has a worst deviation of 8.3 points from either model; the half-difference variant has
16.2, and is flat exactly where play happens. **Clipped to 5-95%** because neither certainty nor
impossibility may be reachable: a roll that cannot fail is not worth making, one that cannot
succeed removes the reason to try, and the Wyrd die is read from the units digit of the natural
roll, so a fixed outcome still owes the fiction a reaction it can no longer earn.

This feature settles what the mapping is *for* — the attack roll, the defence roll, what happens
to two-sided opposed tests, and the knock-on decisions #44 named — not the mapping's shape.

## Clarifications

### Session 2026-08-25

- **Q: Does the telling blow's degree threshold change under the new mapping, and how are degrees
  computed from a single player-facing roll?** → **Degrees are computed exactly as today —
  `tens(effective%) − tens(roll)` on the one roll the player makes — and the telling-blow threshold
  is recomputed numerically as part of this feature, not carried over unexamined.** The mechanism
  (a roll's degrees drive the telling blow) is unchanged; only the number feeding it changes, from
  a raw skill to the clipped effective percentage. The actual threshold is not guessed here: it is
  computed by a committed script against the new roll's distribution (FR-014), the same way ADR
  0016 computed the opposed-test rate rather than asserting it. Rejected: inventing a new margin
  measure (e.g. reading margin from the raw skill gap rather than from degrees) — that would be a
  second measure of the same quantity the degree scale already provides
  ([ADR 0001](../../docs/adr/0001-resolution.md)), which is the drift class this repo is
  corrected for most often.
- **Q: Does the assistance rule (§1, a helper's bonus of up to +10) apply to the new defence roll
  the same way it applies to an attack?** → **Yes, identically.** Nothing in the assistance rule is
  attack-specific — it is stated as a bonus to *a* roll from a companion who can do the task and
  acts specifically in the fiction. A companion calling a warning or angling a shield fits that
  description as well for a defence as a companion lending a hand fits an attack. Rejected: exempting
  defence, which would need a new carve-out with no textual basis and would make combat the one
  place assistance behaves differently depending on which of the two rolls it is a player is making.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A player attacks, and the opponent never rolls (Priority: P1)

A player declares an attack. They roll once, against a single percentage derived from their attack
skill and the opponent's relevant skill (or `baseline`, [`03d-the-adversary.md`](../../docs/design/06-the-adversary.md)
§3). The opponent's dice never come out.

**Why this priority**: This is the conversion. Nothing else in the feature is meaningful until an
attack resolves on one roll.

**Independent Test**: Take a written character and a written opponent (from
[specs/017-adversary-model](../017-adversary-model/spec.md)'s schema) and resolve an attack from a
fixed seed, entirely from the player's roll and published values.

**Acceptance Scenarios**:

1. **Given** a player's attack skill and the opponent's relevant skill or baseline, **When** the
   attack is declared, **Then** the engine computes one effective percentage, the player rolls once
   against it, and the opponent's own dice are never consulted.
2. **Given** an even match (equal skills), **When** the attack roll is made, **Then** it succeeds
   50% of the time.
3. **Given** any skill gap, **When** the effective percentage is computed, **Then** it never reaches
   0% or 100% — the floor and ceiling are 5% and 95%.

---

### User Story 2 - A player defends against an incoming attack, on the same terms (Priority: P1)

When an opponent's turn would attack a player character (or companion), the game does not roll for
the opponent. Instead the player rolls a defence, against a percentage derived from their defensive
skill and the opponent's attacking skill.

**Why this priority**: Attack and defence are named as separate acts with separate skills in the
issue's acceptance criteria; a conversion that resolves attacks but leaves defence as an opposed
test against opponent dice is only half done.

**Independent Test**: Resolve an opponent's turn against a written character, entirely from the
player's defence roll — no die is ever rolled for the opponent's side.

**Acceptance Scenarios**:

1. **Given** an opponent's turn against a player character, **When** the attack is resolved,
   **Then** the player rolls a defence against an effective percentage computed from the two
   relevant skills, and the opponent never rolls.
2. **Given** the defence roll fails, **When** damage is resolved, **Then** the existing damage,
   armour, telling-blow and critical rules apply exactly as they do to a player attack today.
3. **Given** the defence roll succeeds, **When** the opponent's turn ends, **Then** no damage is
   applied and the fiction reflects a defended attack, not a missed one.

---

### User Story 3 - Degrees and the telling blow still mean something at the new scale (Priority: P2)

Degrees of success drive the telling blow and (via Aftermath) the severity of a drop below zero
Stamina. The player-facing roll must still produce degrees that quantise sensibly, and the telling
blow threshold must be reconsidered now that the roll's distribution has changed.

**Why this priority**: The issue's acceptance criteria call out degrees quantising on the tens
digit as a currently-invisible problem — half of all +5% advances change nothing about the tens
digit of an effective percentage that is itself derived, not authored. This is a correctness
question about a mechanic already in play, not a new capability, but it must be answered before the
conversion can be called complete.

**Independent Test**: Compute the distribution of degrees (and telling-blow frequency) produced by
the player-facing roll across a representative span of skill gaps, and compare it to the
opposed-test distribution it replaces.

**Acceptance Scenarios**:

1. **Given** the effective-percentage mapping, **When** degrees are computed from a player-facing
   roll, **Then** the rule for how they are computed is stated explicitly and its consequence for
   the telling-blow rate is computed, not assumed.
2. **Given** the new roll structure, **When** ADR 0016's provisions are reviewed, **Then** each is
   either reaffirmed for the surviving single-roll case or explicitly retired, and the ADR's status
   is updated accordingly (a new ADR, since an accepted ADR is never edited in place).

---

### Edge Cases

- What happens when a player's attack or defence skill is untrained (flat 10%, §1) against a
  high-baseline opponent — does the 5% floor still leave a roll worth making?
- What happens to an opposed test that is not combat (a two-sided contest of wills, a chase) now
  that combat's opposed test is gone — does ADR 0016 keep governing those, or does the conversion
  reach them too?
- What happens to assistance (§1) and the group-test rules once combat rolls belong entirely to one
  side — does a helper's bonus still apply to the player's single roll?
- What happens at the extremes of the clip (5% and 95%) to the Wyrd die's units-digit read, given
  that a clipped percentage no longer corresponds to the raw skill gap?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST resolve a player-character (or companion) attack in combat as a
  single roll against an effective percentage, never a second roll for the opponent.
- **FR-002**: The effective percentage for an attack MUST be computed as
  `clip(50 + (attacker_skill - defender_skill_or_baseline), 5, 95)`, using the calibration already
  computed in `specs/012-combat-sequencing/check_mapping.py`.
- **FR-003**: The engine MUST resolve an opponent's attack against a player character (or
  companion) as a single defence roll by the player, against an effective percentage computed the
  same way, with the opponent's dice never consulted.
- **FR-004**: Attack and defence MUST remain separate acts naming separate skills — an attack skill
  is never substituted for a defensive one or vice versa.
- **FR-005**: The engine MUST state explicitly how degrees are computed from the player-facing
  roll, and the telling-blow threshold (currently "win by 3 or more degrees") MUST be reconsidered
  against the new roll's distribution rather than carried over unexamined.
- **FR-006**: Degrees for the player-facing roll MUST be computed as `tens(effective%) −
  tens(roll)`, and the telling-blow threshold MUST be recomputed against this roll's distribution by
  the committed script (FR-014) rather than carried forward from the opposed-test figure unexamined.
- **FR-007**: The design MUST state whether two-sided opposed tests survive outside combat (a
  contest where both parties genuinely act, e.g. a tug-of-war of wills) or whether the conversion
  removes two-sided opposed tests from the engine entirely.
- **FR-008**: [ADR 0016](../../docs/adr/0016-opposed-tests-need-a-successful-actor.md)'s status
  MUST be resolved: reaffirmed as still governing whatever opposed tests remain, or superseded by a
  new ADR — never edited in place.
- **FR-009**: Starting Stamina MUST be re-settled or explicitly reaffirmed, computed against the
  new expected fight length under player-facing rolls (fight length is a live lever once every
  round produces a result rather than 61-84% doing nothing).
- **FR-010**: The design MUST face explicitly the consequence #44 named: a player-rolled defence
  (as opposed to the opponent needing to beat a static defence number) raises incoming damage by a
  factor of 1.4x-3.1x over the current opposed-test structure. The design MUST either accept this
  and revise Stamina/armour/danger accordingly, or state what offsets it.
- **FR-011**: The Wyrd die MUST always be read from the acting player's own roll — attack or
  defence — never from a die the engine simulates for the opponent, consistent with "the Wyrd die
  now always belongs to the player" (issue #69).
- **FR-012**: The assistance rule (§1, a helper's bonus of up to +10) MUST apply identically to
  both the player's attack roll and their new defence roll — nothing in its wording is
  attack-specific, and combat MUST NOT become the one place assistance behaves differently by
  which of the two rolls a player is making.
- **FR-013**: `docs/design/03-rules.md` §1 and §2 MUST be updated in place to describe the player-facing
  mechanic as the current rule; the two-sided opposed test description is removed or narrowed to
  match FR-007's decision, and the spec is not left as the only record of current behaviour.
- **FR-014**: The calibration and any newly computed thresholds (telling blow, damage-multiplier
  offset, Stamina) MUST be reproducible from a committed script under `specs/018-player-facing-combat/`,
  consistent with "check the maths" (`CLAUDE.md`) and the assert-prior-numbers convention already
  used by `specs/012-combat-sequencing` and `specs/017-adversary-model`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an even match, an attack (and separately, a defence) succeeds on exactly 50% of
  rolls.
- **SC-002**: No skill gap, however large, produces a certain success or a certain failure — the
  computed effective percentage stays within 5-95% for every input.
- **SC-003**: An opponent's dice are never rolled during combat resolution — every roll in a
  combat round belongs to a player character or companion.
- **SC-004**: The share of a player's combat rolls that resolve to "nothing happens" (a plain
  miss, with no defence roll following it) drops from the current 61-84% to a figure computed and
  stated for the new structure, not assumed to have improved.
- **SC-005**: The telling-blow rate and the damage-multiplier consequence for a player-rolled
  defence are both stated as computed numbers, each checkable by re-running the committed script.

## Assumptions

- The adversary model ([specs/017-adversary-model](../017-adversary-model/spec.md), landed) already
  supplies what a static opponent number *is* — a listed skill or the block's `baseline` — so this
  feature consumes that model rather than redefining it.
- Combat sequencing, ranged combat, flight and surprise ([#11](https://github.com/neilgfoster/wyrd/issues/11),
  landed) are out of scope; this feature only changes *who rolls*, not *when* or *in what order*.
- The mob rule ([#13](https://github.com/neilgfoster/wyrd/issues/13), landed) is out of scope and is
  not revisited even though it currently reads a skill-gap test that itself depends on opposed-test
  machinery — any incompatibility surfaced there is a follow-up issue, not blocking work here.
