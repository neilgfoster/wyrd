# Feature Specification: Full-campaign simulated playtest across every subsystem

**Feature Branch**: `144-full-campaign-simulated-playtest`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Full-campaign simulated playtest across every subsystem (closes
#376, child of epic #220). Script a representative multi-session arc for one character —
creation through several sessions of downtime, conflict, harm, recovery, economic advancement,
and at least one solo-procedure-driven scene — and grade the transcript against docs/design/,
separately reporting functional correctness versus behavioral fidelity per #90's Definition of
Done."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One character's full arc, played straight through, across every subsystem (Priority: P1)

Someone who has read the individually-scoped playtests (#208-#219: resolution, combat/harm,
solo procedures, career, companions, and the rest) wants to see all of it play out together, the
way an actual chronicle would — one character, several sessions, creation through downtime,
conflict, harm, recovery, economic advancement, and a solo-procedure-driven scene, in one
continuous transcript rather than scoped fragments.

**Why this priority**: This is #220's own purpose for this feature — the first full-campaign-
scale playtest, proving the subsystems compose across a real multi-session arc rather than only
individually.

**Independent Test**: Read the new section; confirm one character is created, carried through
creation, at least three sessions (each closing at Rally or downtime), a conflict producing harm,
a recovery step, at least one economic-advancement event, and at least one solo-procedure-driven
scene (an oracle consultation, a companion beat, or a journey leg), with real seeded dice
throughout.

**Acceptance Scenarios**:

1. **Given** a freshly created character, **When** the scripted arc runs end to end, **Then** it
   executes without crashing and produces a legal state transition at every step.
2. **Given** a conflict that resolves with harm to the character, **When** the following downtime
   or Rally is played, **Then** the recovery mechanic that fires (Rally's Stamina/Strain
   recovery, or a downtime Mend) matches `docs/design/`'s stated rule exactly.
3. **Given** the full transcript, **When** it is graded against `docs/design/`, **Then**
   functional correctness (did each step produce a legal outcome) and behavioral fidelity (did
   pacing, difficulty, and outcome shape match what the design prose says should happen) are
   reported as two distinct, separately-verdicted sections — never folded into one verdict.

### User Story 2 - A real behavioral gap is raised as a follow-up, never fixed inline or silently absorbed (Priority: P2)

Following specs/055 and specs/059's established pattern, if the full-campaign transcript surfaces
a genuine mismatch between what a mechanic's design prose promises and what it actually produced
across this longer, composed run, that mismatch becomes its own tracked issue rather than being
patched inside this playtest or quietly noted and forgotten.

**Why this priority**: The issue's own scope is explicit that fixing every finding inline is out
of scope; the value of this playtest depends on findings actually surfacing as follow-up work,
not disappearing into a passing transcript.

**Independent Test**: If the graded transcript's behavioral-fidelity section names a real gap,
confirm a follow-up GitHub issue exists referencing it; if no real gap is found, confirm the
report states that plainly rather than manufacturing one.

**Acceptance Scenarios**:

1. **Given** a behavioral-fidelity finding that represents a genuine design/behavior mismatch,
   **When** the playtest is reported, **Then** a follow-up issue is raised referencing the
   finding, following specs/055/059's pattern.
2. **Given** no real gap surfaces, **When** the playtest is reported, **Then** the report states
   there is no follow-up to raise, rather than inventing one to fill the section.

### Edge Cases

- Is every subsystem from #208-#219 exercised? No — the issue scopes this to a *representative*
  arc (creation, downtime, conflict, harm, recovery, economic advancement, one solo-procedure
  scene), not an exhaustive tour of every mechanic; anything the arc doesn't organically touch is
  recorded as untested, not forced in, matching specs/053's established precedent for this same
  question.
- What happens if the arc's dice would produce character death or retirement? Played straight —
  neither manufactured nor avoided; if it happens organically it is played through, if it
  doesn't the arc completes without it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching the discipline
  established by prior scoped playtests (specs/046, specs/047, specs/053, and others).
- **FR-002**: The playtest MUST script one character across multiple sessions spanning creation,
  downtime, conflict, harm, recovery, economic advancement, and at least one solo-procedure-driven
  scene, in one continuous arc rather than separate fragments.
- **FR-003**: The playtest MUST grade its own transcript against `docs/design/`, per the
  convention in `docs/design/30-playtest-transcript.md`.
- **FR-004**: The report MUST separate functional correctness (did each step produce a legal
  outcome) from behavioral fidelity (did pacing/difficulty/outcome shape match design prose) as
  two distinct sections with independent verdicts, per #90's Definition of Done — never folded
  into a single verdict.
- **FR-005**: Any real behavioral gap the playtest surfaces MUST be raised as its own follow-up
  issue, following specs/055/059's existing findings-synthesis pattern, rather than fixed inline
  or silently absorbed.
- **FR-006**: The scripted run MUST execute without crashing.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering one character's
  full multi-session arc — creation, downtime, conflict, harm, recovery, economic advancement,
  and a solo-procedure-driven scene — following the existing document's established structure and
  tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, seeded, in a
  stated fixed order.
- **SC-003**: Functional correctness and behavioral fidelity are reported as two distinct,
  separately-verdicted sections.
- **SC-004**: Any real behavioral gap found is named as a follow-up issue reference; if none is
  found, the report states that explicitly.
- **SC-005**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-006**: `python3 -m pytest -q`, `python3 -m ruff check .`, and
  `python3 -m ruff format --check .` all pass with no regression.

## Assumptions

- This feature carries no ADR — nothing found requires a design decision; it is a worked playtest
  record, the same shape as specs/046, specs/047, and specs/053.
- Documentation-only: no engine code changes are expected unless the transcript surfaces a real
  gap, in which case that gap is raised as its own follow-up issue (FR-005) rather than fixed
  here.
- The roll-generation/scripting used to produce the transcript is scratch tooling, not committed,
  matching the precedent in specs/053 and other prior playtests — the committed artifact is the
  graded transcript section itself.
