# Feature Specification: Engine scaffolding

**Feature Branch**: `075-engine-scaffolding`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Engine scaffolding: CLI skeleton, dice tool, state read/write — stand up engine/ with a CLI entry point, a deterministic d100 dice primitive, and persist-before-narrate save/load plumbing, per docs/design/01-principles.md and docs/design/02-architecture.md. Part of #208/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM rolls dice through code, never through the model (Priority: P1)

Whenever a rule requires a die roll, the GM (an LLM acting as game master) invokes a CLI command
rather than inventing a result. The command returns a deterministic, verifiable outcome the GM
narrates from.

**Why this priority**: This is principle 1 from `docs/design/01-principles.md` — "the dice bind
the GM" — and the reason the whole engine build starts here. Every later rule (opposed tests,
combat, tables) is narration hung on this roll; without it nothing downstream can be trusted.

**Independent Test**: Can be fully tested by invoking the dice command directly, with a fixed
seed, and confirming the same seed always reproduces the same roll — deliverable and checkable
with no other engine feature in place.

**Acceptance Scenarios**:

1. **Given** the CLI is installed, **When** a d100 roll is requested, **Then** it returns a value
   from 1-100 and the process exits successfully.
2. **Given** a fixed random seed, **When** the same roll is requested twice, **Then** both calls
   return the identical result.
3. **Given** no seed is supplied, **When** a roll is requested, **Then** the result is drawn from
   a source of real randomness (not the same value every time).

---

### User Story 2 - State survives before the scene is described (Priority: P2)

Whenever the engine changes chronicle state (a roll result, a stat change, anything), that change
is written to disk before any narration is produced. If the process is interrupted right after a
write, the saved state reflects it; nothing is lost to a crash mid-scene.

**Why this priority**: This is principle 2 — "persist before narrate" — the guarantee that a
crash, a context reset, or a closed phone never loses the fiction. It is the second load-bearing
guarantee the rest of the engine depends on, after the dice.

**Independent Test**: Can be fully tested by invoking a save operation, killing the process
immediately after it returns, and confirming the on-disk state reflects the change — independent
of any specific game rule.

**Acceptance Scenarios**:

1. **Given** a chronicle state file, **When** the engine records a change, **Then** the file on
   disk reflects the new state before any narration text is emitted.
2. **Given** a saved state file, **When** the engine loads it, **Then** it recovers a value
   identical to what was written (a round trip).
3. **Given** a state write is interrupted (e.g. process killed mid-write), **When** the file is
   next read, **Then** it is either the old, fully-valid state or the new, fully-valid state —
   never a corrupted partial write.

---

### User Story 3 - A person can invoke the engine directly (Priority: P3)

Someone at a terminal (a developer, or the GM's own tool layer) can run a single command to
confirm the engine is present and working, without yet needing any specific rule to be
implemented.

**Why this priority**: Lowest priority because it's a convenience/diagnostic surface, not a
guarantee anything else depends on — but every later feature needs *some* CLI entry point to
attach its own commands to, so standing up the shape now avoids every subsequent feature
re-deciding it.

**Independent Test**: Can be fully tested by running the CLI with no arguments or a version
flag and confirming it exits successfully with identifiable output.

**Acceptance Scenarios**:

1. **Given** the engine is installed, **When** the CLI is invoked with a version/status command,
   **Then** it prints identifying output and exits with a success code.

### Edge Cases

- What happens when the dice command is asked for a roll outside its defined range (e.g. a
  non-positive number of sides)? The command must reject it with a clear error rather than
  returning a nonsensical value.
- What happens when the state file does not yet exist (first-ever save)? The engine must create
  it rather than failing.
- What happens when the state file exists but is not valid (hand-edited into a broken shape)?
  The engine must fail loudly on load rather than silently discarding or guessing at the data.
- What happens when two processes attempt to write state at the same time? Out of scope for this
  feature (single chronicle, single active session, per `02-architecture.md`'s "two chronicles
  never share a repository" guarantee) — no concurrent-write handling is required here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a command that rolls a d100 (1-100 inclusive) and reports
  the result.
- **FR-002**: The engine MUST support an explicit seed for a roll, such that the same seed always
  produces the same result.
- **FR-003**: The engine MUST default to a genuinely random source when no seed is supplied.
- **FR-004**: The engine MUST reject an invalid roll request (e.g. zero or negative sides) with a
  clear error rather than a silent or nonsensical result.
- **FR-005**: The engine MUST provide a way to write chronicle state to disk such that the write
  completes (old or new state fully intact) before any narration step runs.
- **FR-006**: The engine MUST provide a way to read chronicle state back from disk, recovering
  exactly what was last written.
- **FR-007**: A state write MUST be atomic — an interruption during the write MUST NOT leave a
  partially-written, unparseable file on disk.
- **FR-008**: Loading a state file that fails to parse or fails schema validation MUST raise a
  clear, specific error rather than being silently ignored or defaulted.
- **FR-009**: The engine MUST expose a single CLI entry point that a later feature's commands can
  attach to (e.g. `wyrd roll`, `wyrd <future-command>`), plus a minimal command (e.g. version or
  status) usable to confirm the entry point works with no other feature implemented yet.
- **FR-010**: The engine MUST introduce no dependency on any external package, daemon, or
  database — Python 3.11+ standard library only, per `docs/design/27-tooling.md`.
- **FR-011**: Nothing under `engine/` may name a specific setting, system, or source text — it
  must read as setting-agnostic per `CLAUDE.md`'s engine rule.

### Key Entities

- **Chronicle state**: the on-disk record this feature can read and write a round trip of. Its
  full schema (character, companions, threads, etc.) belongs to later features; this feature only
  needs a minimal state shape sufficient to prove the persist-before-narrate read/write guarantee.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A d100 roll with a fixed seed produces the identical result across 100 repeated
  invocations, with zero deviation.
- **SC-002**: A save-then-load round trip recovers state identical to what was saved, verified
  across at least one automated test per state field exercised.
- **SC-003**: An interrupted write (simulated by killing the process mid-write in a test) never
  leaves a file that fails to parse as either the prior or the new valid state.
- **SC-004**: A cold run of the CLI's minimal command succeeds with no setup beyond a standard
  Python 3.11+ interpreter — no package install step.

## Assumptions

- Language and runtime are settled by `docs/design/27-tooling.md`: Python 3.11+, standard library
  only. Not treated as an open question for this spec.
- The chronicle state schema used to demonstrate the read/write round trip is minimal and
  provisional — later features (the character model, #209, etc.) will extend it; this feature is
  not responsible for the full eventual schema.
- "Atomic write" is satisfied by the standard write-to-temp-file-then-rename pattern; no stronger
  durability guarantee (e.g. fsync ordering across a power loss) is required.
- No CLI framework dependency is assumed; `argparse` (standard library) is sufficient for the
  minimal entry point this feature needs.
- This feature does not implement any opposed-test, combat, or table-lookup logic — those are
  separate children of #208 (#222, #223, #224) and build on top of what this feature provides.
