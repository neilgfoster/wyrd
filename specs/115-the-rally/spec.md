# Feature Specification: The Rally: recovery, advance award and commit

**Feature Branch**: `310-the-rally`

**Created**: 2026-09-10

**Status**: Draft

**Input**: GitHub issue #310 — The Rally: recovery, advance award and commit

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fixed recovery at a Rally (Priority: P1)

Whenever a beat closes, the engine applies the Rally's fixed recovery: the character's Strain
drops by 1 (never below 0) and Stamina rises by 1 (never above the character's current maximum).
This is the mechanism `docs/design/16-session.md` names as the answer to "I have to get off the
train" — a Rally always has this effect, with no roll and no GM discretion over the amount.

**Why this priority**: Every other part of a Rally (the advance award, the commit) presupposes
that the fixed recovery step itself exists and is correct — it is the part of the Rally that is
never optional.

**Independent Test**: Apply a Rally to a character sitting below Stamina maximum and above 0
Strain; confirm Strain drops by exactly 1 and Stamina rises by exactly 1. Apply a Rally to a
character already at 0 Strain or at Stamina maximum; confirm neither track goes out of range.

**Acceptance Scenarios**:

1. **Given** a character with Strain 3 and Stamina 4 of a maximum 6, **When** a Rally is applied,
   **Then** Strain becomes 2 and Stamina becomes 5.
2. **Given** a character with Strain 0, **When** a Rally is applied, **Then** Strain stays 0 (it
   does not go negative).
3. **Given** a character with Stamina already at its maximum, **When** a Rally is applied,
   **Then** Stamina stays at the maximum (it does not exceed it).

---

### User Story 2 - The advance award is optional (Priority: P1)

At the same Rally, the GM may assess the beat just closed and award an advance against one of
`engine/wyrd/advancement.py`'s existing triggers. A Rally with no award is a completely valid
outcome — nothing about applying a Rally requires an award to have happened, and the fixed
recovery in User Story 1 happens identically whether or not one is claimed.

**Why this priority**: This is the mechanism that ties a Rally to the campaign's advancement
economy, but it must not become a second, competing way to award advances — it wires the
existing hook rather than inventing new award logic.

**Independent Test**: Apply a Rally with no award claimed; confirm the recovery still applies and
the advancement record is unchanged. Apply a Rally with an award claimed against a valid trigger;
confirm the existing `award_advance` behaviour (including its refusals) is the only path an award
can take.

**Acceptance Scenarios**:

1. **Given** a beat has just closed, **When** a Rally is applied with no advance claimed, **Then**
   the Rally succeeds and the session's advancement record is unchanged.
2. **Given** a beat has just closed and the GM assesses it against a valid trigger, **When** a
   Rally is applied with that trigger, **Then** the advancement record reflects exactly what
   `advancement.award_advance` would have recorded for that trigger on its own.
3. **Given** a trigger already awarded this session, **When** a Rally is applied claiming that
   same trigger again, **Then** the award is refused exactly as `award_advance` already refuses
   it, and the Rally's fixed recovery still applies regardless.

---

### User Story 3 - State is written and committed only at a Rally (Priority: P1)

A Rally is the point at which state is written and the chronicle is committed
(`docs/design/16-session.md`). Outside a Rally (or the mid-beat `pending:` marker introduced by
#309), nothing silently persists — a caller driving the session loop can rely on a Rally (or an
explicit pending marker) as the only moments state hits durable storage.

**Why this priority**: This is the property the issue's own Definition of Done names explicitly,
and it is what makes a Rally the answer to "I have to get off the train" rather than merely a
recovery calculation — the character sheet is safe to close the laptop on only once this has
run.

**Independent Test**: Drive a Rally end-to-end and confirm the persist/commit step runs exactly
once, in order after the recovery and award steps. Confirm no other function in this feature
writes state on its own.

**Acceptance Scenarios**:

1. **Given** a beat has closed, **When** a Rally is applied, **Then** the recovery and any award
   are computed first, and the persist/commit step runs exactly once afterward.
2. **Given** a Rally that computes no award, **When** it completes, **Then** the persist/commit
   step still runs — persistence does not depend on an award having happened.

---

### Edge Cases

- What happens when a Rally is applied and the character has no `stamina_max` field, or an
  advancement record has never been opened for the session? The Rally function operates on the
  values it is given; a caller that has not yet opened a session's advancement record uses
  `advancement.new_record()` before the first Rally, the same as any other caller of that module.
- What happens when an award is claimed against an unknown trigger, or past the session's
  ceiling? `advancement.award_advance`'s existing refusal shapes (`unknown_trigger`,
  `already_awarded`, `session_ceiling`) are surfaced unchanged; this feature does not add a
  fourth reason an award can fail.
- What happens at a mid-beat stop, where `session.set_pending` applies instead of a Rally? Out of
  scope here — #309 already defines the `pending:` marker as the other point state may be
  written; this feature only concerns the Rally itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a Rally function that, given a character's current Strain
  and Stamina (and Stamina maximum), returns Strain reduced by exactly 1 (floored at 0) and
  Stamina raised by exactly 1 (capped at the maximum).
- **FR-002**: The Rally function MUST accept an optional advance-award trigger and, when one is
  given, apply it via `advancement.award_advance` against the session's advancement record —
  never a parallel or reimplemented award check.
- **FR-003**: The Rally function MUST succeed and apply its fixed recovery whether or not an
  advance is claimed, and whether or not a claimed award is accepted or refused.
- **FR-004**: The engine MUST provide a Rally step that, given the results of FR-001 through
  FR-003, runs a caller-supplied persist/commit step exactly once, after recovery and any award
  are computed — mirroring `session.run_close`'s existing "ordering guaranteed, content injected"
  shape rather than inventing a second convention for the same idea.
- **FR-005**: The Rally step MUST NOT write or commit state anywhere outside that single
  persist/commit call — every other function this feature adds is a pure computation over the
  values it is given.
- **FR-006**: A refused advance award (per `advancement.award_advance`'s existing refusal
  reasons) MUST be reported back to the caller rather than silently discarded, so the GM can see
  why an assessed trigger did not pay out.

## Key Entities *(include if feature involves data)*

- **Rally result**: the outcome of applying a Rally — the character's recovered Strain and
  Stamina, and (when an award was claimed) the `award_advance` outcome and updated advancement
  record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A Rally applied to a character below Stamina maximum and above 0 Strain changes
  Strain by exactly -1 and Stamina by exactly +1, matching `docs/design/03-rules.md` §2's stated
  amounts, on every input checked by the feature's automated tests.
- **SC-002**: A Rally with no advance claimed leaves the advancement record byte-for-byte
  unchanged from its input.
- **SC-003**: Across every acceptance scenario above, the persist/commit callable runs exactly
  once per Rally — never zero, never more than once.

## Assumptions

- Stamina and Strain are represented as the plain integer fields already named in
  `engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS` (`stamina`, `strain`) and read/written by
  the caller driving the session loop; this feature does not introduce a new state shape for
  them.
- The advancement record this feature reads and writes is exactly the one
  `engine/wyrd/advancement.py` already defines (`new_record`/`award_advance`/`begin_session`) —
  no new record shape is introduced.
- "A beat closing," and the exact point at which a Rally becomes available to the caller, is
  defined by #309's session loop (`engine/wyrd/session.py`); this feature is invoked by that
  caller and does not itself decide when a beat has closed.
- The persist/commit step's actual content (what "write state" and "commit the chronicle" mean
  concretely) depends on the chronicle/campaign state layer under #300, which does not exist yet
  — the same scoping `session.run_close` already applies. This feature guarantees the step runs,
  exactly once, at the right point, taking it as an injected callable rather than implementing it.
