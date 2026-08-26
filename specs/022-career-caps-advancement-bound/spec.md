# Feature Specification: Career caps and the advancement bound

**Feature Branch**: `022-career-caps-advancement-bound`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "R1.5 — Career caps and the advancement bound" (issue #12)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A skill stops rising at a stated, known point (Priority: P1)

A player spending an advance to raise a career-granted skill needs to know, without asking the
GM, whether the skill can still rise — and by how much room is left before it can't.

**Why this priority**: Every advance spent under §6 ("+5% to a skill your career grants, to that
career's cap") already names the cap; without a stated number the rule cannot be executed, and
this is the only growth mechanic in the game.

**Independent Test**: Given a character with a skill open in their current career, raising it by
successive advances always lands on a value that is either below the stated cap or exactly at it,
never above it, and the engine can state the cap for any (career, skill) pair without asking the
GM.

**Acceptance Scenarios**:

1. **Given** a skill open at a value below its career's cap, **When** an advance is spent to raise
   it by +5%, **Then** the new value is `min(old value + 5%, cap)`.
2. **Given** a skill already at its career's cap, **When** the player attempts to spend an advance
   raising it further, **Then** the advance is refused as illegal — there is nothing left to buy.
3. **Given** any career the setting declares, **When** its granted skills are enumerated,
   **Then** each has a stated, positive cap no advance can exceed.

---

### User Story 2 - Completing a career pays out a stated, permanent grant (Priority: P1)

A player who has raised every skill their career grants to that career's cap needs to know what
they get for it, so "completing a career" is a real, checkable event rather than a vague
milestone.

**Why this priority**: §6 already calls this "the only durable toughening" and names its two
components (+1 maximum Stamina, a Mark) but the interaction between multiple completions and the
Stamina creation numbers (§03c, "much above 10 and the sentence stops being true") is unresolved —
this is the actual gap the issue exists to close.

**Independent Test**: Given a character whose current career has every granted skill at that
career's cap, the engine recognises completion and applies the grant exactly once for that
career-instance, independent of how many advances it took to get there or in what order the
skills were raised.

**Acceptance Scenarios**:

1. **Given** a character with every skill their career grants sitting at that career's cap,
   **When** the last such skill reaches its cap, **Then** the career is marked complete, maximum
   Stamina increases by 1, and a Mark is recorded.
2. **Given** a career already completed once, **When** the character re-enters the same career
   later in a legal career history, **Then** completing it again grants the same +1 Stamina and a
   further Mark — completion is a repeatable event per career-instance, not a one-time flag.
3. **Given** a character who opens a skill their career grants but never raises every such skill
   to the cap, **When** the character changes career, **Then** no completion grant is made for the
   career left behind.

---

### User Story 3 - The advancement bound is stated and holds up over a long chronicle (Priority: P2)

A GM running a chronicle across years of played time needs to know where advancement actually
stops — not because a cap on paper, but because a character's Stamina and skills genuinely cannot
climb without limit, and the game stays the "harder to replace, not harder to kill" shape §6
already claims.

**Why this priority**: this is the requirement's own acceptance criterion ("computed numbers, not
asserted") and the reason a spec is being written at all — a bound nobody has checked is not a
bound.

**Independent Test**: Running the numbers for a character who completes careers back-to-back over
a long chronicle (using the skill list and career caps this spec defines) shows maximum Stamina
converging to a stated ceiling, and skill values across a lifetime of careers staying inside a
stated envelope — checked by a script against the same constraint §03c already used to fix
Stamina at 6 ("much above 10 and the sentence stops being true").

**Acceptance Scenarios**:

1. **Given** a character who completes career after career for the rest of a long chronicle,
   **When** maximum Stamina is tracked across each completion, **Then** it approaches a stated
   ceiling and does not grow without bound.
2. **Given** the same long chronicle, **When** the character's skill portfolio is examined after
   many completed careers, **Then** no skill exceeds 100% and the spread across skills matches the
   "depth over breadth" claim in §6 — a character with many completed careers is not simply
   expert at everything.

### Edge Cases

- A career the setting declares grants zero skills, or only skills already at their cap for a
  different reason (a Mark, say) — completion must still be well-defined and reachable.
- A character changes career mid-way and later re-enters the same career: does progress toward
  completion persist, or restart? (Resolved as part of this spec — see Requirements.)
- A companion (§6 "Companions and succession") never runs the career graph or accrues Marks —
  the cap and completion mechanic in this spec applies to player characters only, and that
  boundary must stay explicit so it isn't read as a companion oversight.
- A setting's career graph contains a cycle (a career is its own legal exit, directly or via a
  loop) — completion must still terminate as a per-instance event, not be blocked by the cycle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST define a numeric cap, expressed as a skill percentage, for every
  skill a career grants, such that no advance can raise that skill (via that career) above it.
- **FR-002**: A career's cap MUST be a single value applied uniformly to every skill that career
  grants — the engine does not define a separate cap per (career, skill) pair, matching how §6
  already writes "to that career's cap" as one number per career.
- **FR-003**: The engine MUST set every career's cap to **70%**, the top of the *expert* band
  (`10-diegesis.md`, 60–70%) — the highest band a career, as opposed to a permanent Mark or other
  durable grant, can buy on its own.
- **FR-004**: The engine MUST refuse an advance that would raise a skill beyond its career's cap;
  such an advance is not a legal spend under §6.
- **FR-005**: The engine MUST recognise a career as **complete** for a given career-instance the
  moment every skill that career grants is at that career's cap (70%) for that character.
- **FR-006**: On completing a career, the engine MUST grant exactly **+1 maximum Stamina** and
  record one **Mark**, applied once per career-instance completed — completing the same career a
  second time (a legal re-entry via the career graph) grants the same rewards again.
- **FR-007**: The engine MUST NOT grant completion rewards for a career the character leaves
  without every granted skill reaching the cap; leaving early forfeits the pending completion for
  that instance.
- **FR-008**: The engine MUST track completion progress per career-instance (a single continuous
  span of holding that career), not per career-name-for-life — re-entering a career after leaving
  it starts a fresh instance, with its skills wherever the character's Marks and prior training
  left them, and any skill already at or above the cap from a past instance counts toward this
  instance's completion immediately.
- **FR-009**: Maximum Stamina MUST have a stated ceiling, computed rather than asserted, that
  bounds how many completions matter mechanically — the engine MUST state this ceiling as an
  explicit ADR-recorded number, not leave it open-ended, consistent with `03c-character-creation.md`'s
  own reasoning that Stamina gains "much above 10" break the "16.7% gain" sentence that fixed the
  starting value.
- **FR-010**: The advancement bound MUST be justified by a script that computes, for a character
  completing careers back-to-back over a chronicle of at least 10 career-instances, the resulting
  maximum Stamina and skill spread — committed under `specs/022-career-caps-advancement-bound/`
  alongside this spec, in the same style as `check_creation.py` and `check_transformation.py`.
- **FR-011**: This spec's cap and completion mechanic MUST apply to player characters only; the
  engine's existing companion advancement (§6, "one competence gained or limitation lost at a
  downtime, no career graph, no Marks") is unchanged by this feature.
- **FR-012**: No career name, skill name, or advancement-vocabulary label introduced by this
  feature may be setting- or system-specific — all of it stays descriptive English, per
  `CLAUDE.md`.

### Key Entities *(include if feature involves data)*

- **Career**: a setting-declared node in the career graph (`14-entities.md`); grants a list of
  skills and now a single numeric cap (70%) applied to all of them; tracks legal entries and
  exits.
- **Career-instance**: one continuous span of a character holding a given career, from entry to
  exit; the unit completion is tracked and granted against — a character may hold the same career
  in more than one instance across a lifetime.
- **Mark**: a permanent, small benefit recorded on a character at career completion; already named
  in §6 as persisting across every later career; this feature adds the trigger (career completion)
  and confirms it accrues once per completed instance, not once per lifetime.
- **Skill**: a career-granted capability held at a percentage value (`10-diegesis.md` bands);
  this feature adds the ceiling (the owning career's cap) that bounds it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any (career, skill) pair the engine can state a cap without consulting the GM,
  and that cap is the same number (70%) for every skill a given career grants.
- **SC-002**: An advance that would push a skill past its career's cap is rejected 100% of the
  time; the pure function governing an advance spend never returns a post-advance value above the
  cap.
- **SC-003**: Completing a career is a deterministic, checkable event: given a character's skill
  values and the career's grant list, the engine agrees with a human GM's reading of "every
  granted skill at the cap" without needing judgement calls.
- **SC-004**: A computed run of 10+ career-instances back-to-back shows maximum Stamina converging
  to a stated ceiling (not growing linearly with career count) and no skill exceeding 100%,
  matching the "harder to replace, not harder to kill" claim in §6 with numbers rather than
  assertion.
- **SC-005**: `doc/design/03-rules.md` states the cap value, the completion trigger, and the
  Stamina ceiling in the same place the existing "career's cap" and "completing a career" language
  already lives, so a reader never has to consult the spec to know current behaviour.

## Assumptions

- The cap is a flat 70% for every career, not a per-skill or per-setting-tunable value — matching
  how §6 already writes "to that career's cap" as a single figure per career, and keeping the
  mechanic setting-agnostic (a setting cannot smuggle in system-specific caps per skill).
- 70% (the top of the *expert* band) is the right ceiling for what a career alone can buy: it
  reserves "it is part of who you are" (75%+, `10-diegesis.md`) for something beyond ordinary
  career advancement — consistent with the existing "depth over breadth" framing and with no
  contrary evidence found in `design/`. If playtesting later shows this boundary wrong, a
  superseding ADR corrects it forward per `09-evolution.md`.
- Maximum Stamina's ceiling is a computed, stated number (not "unbounded, but slow") — this is
  the crux the issue exists to resolve, and is worked out numerically in this feature's plan/check
  script rather than guessed here.
- Career-instance tracking (FR-008) resolves the "re-enter a career" edge case by treating each
  span as independent, which is consistent with `09-evolution.md`'s "rules changes apply forward
  only" posture: nothing about a past instance is recomputed when a new one begins.
- This feature does not touch the skill list itself (already settled by #5) or any setting's
  actual career graph (setting data, out of scope per the issue).
