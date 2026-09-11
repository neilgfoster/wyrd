# Feature Specification: End-to-end functional test suite across the whole engine

**Feature Branch**: `143-end-to-end-functional-test-suite`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "End-to-end functional test suite across the whole engine (GitHub issue #375)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A single run proves the subsystems hand off correctly (Priority: P1)

A contributor changing one engine module wants to know, in one test run, whether their change
broke a handoff into a neighbouring subsystem (e.g. a combat outcome that should feed into harm,
harm that should feed into recovery) -- something the existing per-module unit suites cannot see,
since each is scoped to its own module.

**Why this priority**: This is the entire point of the feature (#375): no integration test
currently exercises more than one or two subsystems together, so a broken handoff between two
correctly-unit-tested modules currently ships silently.

**Independent Test**: Run the new suite alone (`python3 -m pytest tests/engine/test_integration.py`
with `PYTHONPATH=engine`, or the repo's existing unittest convention). It constructs one character
and drives it through every subsystem listed in the acceptance criteria, asserting on state at
each handoff, and passes.

**Acceptance Scenarios**:

1. **Given** a freshly created character, **When** the suite runs creation through to chronicle
   bootstrap in sequence, **Then** every subsystem in the sequence executes without error and the
   suite reports a single pass/fail result for the whole run.
2. **Given** a combat resolution that inflicts a wound, **When** the suite proceeds to the harm and
   recovery subsystems, **Then** the wound recorded by combat is the one harm/recovery act on --
   asserted by identity (wound id), not merely "recovery ran without raising."

---

### User Story 2 - A reviewer trusts the suite is checking handoffs, not just calling functions (Priority: P2)

A reviewer reading the new test file wants to see, for each subsystem boundary, an assertion tied
to a concrete value that crossed that boundary -- not just that a sequence of calls didn't raise.

**Why this priority**: The issue's own acceptance criteria distinguish "asserted" from "exercised"
explicitly; a suite that only calls every module without checking the handoff values would satisfy
a naive reading of "drives it through every subsystem" while missing the actual requirement.

**Independent Test**: Read the suite's assertions against the sequence diagram in `plan.md`; each
listed handoff has a corresponding assertion whose expected value is derived from the *previous*
subsystem's actual output, not a value hard-coded independently of it.

**Acceptance Scenarios**:

1. **Given** the adversary subsystem selects a specific adversary trait value, **When** the
   condition-tracks subsystem applies a consequence keyed on that trait, **Then** the test asserts
   the condition-track state reflects that specific trait's value.

---

### User Story 3 - The suite runs clean under the repo's existing lint and test conventions (Priority: P3)

A maintainer wants the new suite to look and behave like every other suite already in `tests/`, so
it doesn't need special-case tooling or exceptions in CI-equivalent checks.

**Why this priority**: Explicit Definition of Done in #375: "Suite is green under the repo's ruff
config and existing pytest/unittest convention." Lower priority only because it's a constraint the
other two stories must satisfy anyway, not a separable slice of value.

**Independent Test**: `python3 -m ruff check .` and `python3 -m ruff format --check .` both report
the new file(s) clean; `PYTHONPATH=engine python3 -m pytest tests/engine/test_integration.py -q`
passes with the same invocation pattern the repo's other suites use.

**Acceptance Scenarios**:

1. **Given** the new test file(s) under `tests/engine/`, **When** ruff and the test runner are
   invoked exactly as documented in CLAUDE.md, **Then** both exit clean/passing with no
   suite-specific configuration added.

---

### Edge Cases

- What happens when a subsystem call in the middle of the sequence legitimately has no
  observable state to hand off (e.g. a step that only validates)? The test still asserts something
  concrete about that step's own postcondition (e.g. "no exception, and the returned value matches
  the documented shape") rather than skipping it silently.
- How does the suite handle randomness in subsystems that roll dice (adversary/danger resolution,
  oracle-style rolls)? A seeded/deterministic RNG (or a fixed die-roll injection point the modules
  already expose for their own unit tests) is used so the run is reproducible and its handoff
  assertions are exact, not probabilistic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The suite MUST construct a single player character via the engine's own creation
  path (`engine/wyrd/creation.py`) and reuse that one character across every subsequent subsystem
  step, rather than constructing a fresh character per step.
- **FR-002**: The suite MUST drive that character through, in sequence: creation, action
  resolution, conflict (combat), harm/recovery, adversaries, condition tracks, economies,
  specialist subsystems (systems of power / supernatural mechanism), solo procedures
  (oracle/scenario/journey), session/campaign structure (rally, downtime, advancement), and
  chronicle bootstrap.
- **FR-003**: For each adjacent pair of subsystems in that sequence, the suite MUST assert that the
  later subsystem's observed state reflects a specific value produced by the earlier subsystem
  (e.g. the wound id combat records is the wound id recovery closes), not merely that the call
  sequence completed without raising.
- **FR-004**: The suite MUST run as a single test run (one pytest/unittest invocation, one
  pass/fail result), consistent with the rest of `tests/engine/`.
- **FR-005**: The suite MUST use only the Python 3.11+ standard library plus the engine's own
  modules -- no new third-party test dependency.
- **FR-006**: The suite MUST be green under this repo's ruff configuration (`ruff check .` and
  `ruff format --check .`) with no ruleset exception added for it.
- **FR-007**: The suite MUST NOT add any new engine capability; it exercises existing module
  surfaces exactly as they exist today (out of scope per #375).
- **FR-008**: The suite MUST NOT grade playtest quality or narrative/behavioral output -- that is
  #220's second child, explicitly out of scope here.
- **FR-009**: Any randomness a driven subsystem needs (e.g. combat/adversary/oracle rolls) MUST be
  made deterministic for the run, using each module's own existing seam for injecting or seeding
  randomness (no new randomness-control mechanism invented for this suite alone).

### Key Entities

- **Integration test suite**: one new test module (or a small number of them) under
  `tests/engine/`, holding the single end-to-end sequence and its handoff assertions.
- **Driven character**: the one player-character construct the whole sequence is built around;
  its evolving state (wounds, stamina, taint, coin, etc.) is what each handoff assertion reads.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One test invocation exercises all eleven subsystem areas named in FR-002 and
  reports a single pass.
- **SC-002**: Every one of the ten adjacent-subsystem handoffs in that sequence has at least one
  assertion tied to a value produced by the prior step (not a hard-coded independent value).
- **SC-003**: `ruff check .` and `ruff format --check .` report zero findings against the new
  file(s), and the existing full test run (`PYTHONPATH=engine python3 -m pytest -q`, or the repo's
  unittest equivalent) still passes in full alongside the new suite.
- **SC-004**: The suite's own run is deterministic -- run twice, it produces the same pass/fail
  result and the same asserted values both times.

## Assumptions

- "Specialist subsystems" (#375's phrase) maps to the systems-of-power / supernatural-mechanism
  module set (`overrides.py` and the power-cost/Ill Omen path through `entity.py`/`state.py`),
  since that is the one specialist mechanism epic #90 shipped that isn't already covered by one of
  the other named sequence steps.
- "Solo procedures" maps to the oracle, scenario-selection, and journey modules
  (`corpus_scenario.py`, `scenario_selection.py`, `arc_selection.py`, `journey.py`), consistent with
  epic #218's own scope.
- Where a subsystem module exposes multiple entry points, the suite calls the one realistic for a
  single character's session-level flow (the same call shape its own unit test suite already
  uses), rather than every possible entry point.
- No new fixtures/helpers module is required beyond the standard library and the engine's own
  test-support patterns already used elsewhere in `tests/engine/`.
- Schema versioning/migration and any other engine capability gap uncovered while wiring the
  sequence together is out of scope for this feature (#375 explicitly excludes new engine
  capability) and is reported as a follow-up rather than fixed inline.
