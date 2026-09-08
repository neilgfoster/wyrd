# Feature Specification: Oracle prompts engine support

**Feature Branch**: `109-oracle-prompts-engine-support`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "Oracle prompts: engine support — implement docs/design/15-oracle-
prompts.md as engine code: the four prompt families (NPC objective, situation truth, thread turn,
complication), each a repeatable 1d100 table (10 rows, 1-100 contiguous, no modifier), looked up
by family key and returning (roll, effect, description). Expose it as a new verb in the TOOLS
catalog. Fix tools/check_oracle_prompts.py's stale DOC path. Issue #290."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rolling a prompt table (Priority: P1)

A GM has reached a point in play where one of the four scoped gaps — an NPC's real motive, why a
situation isn't as presented, a thread's next turn, or a scene's complication — needs inventing,
and nothing has already established it. The GM asks the engine to roll the matching prompt table
and gets back the natural roll, the row's effect key, and its description, ready to narrate.

**Why this priority**: This is the entire mechanism. Every one of the four families shares this
same lookup shape; nothing else in this feature exists without it.

**Independent Test**: Call the lookup for each of the four family keys with a range of rolls
spanning 1-100 and confirm every roll returns exactly the row the design document's table
declares for that range.

**Acceptance Scenarios**:

1. **Given** a roll of 34, **When** the `oracle-prompt-npc-objective` table is rolled, **Then**
   the engine returns effect `prove_worth` with its declared description.
2. **Given** a roll of 100, **When** any of the four tables is rolled, **Then** the engine returns
   that table's last row (91-100) — the top of the range is never open past 100, since no modifier
   applies.
3. **Given** a roll of 1, **When** any of the four tables is rolled, **Then** the engine returns
   that table's first row (1-10).

---

### User Story 2 - An unrecognized family is a load error (Priority: P2)

A caller asks the engine to roll a family key that isn't one of the four declared in the design
document (a typo, or a setting mistakenly inventing a fifth family). The engine refuses rather
than silently returning nothing or crashing uninformatively.

**Why this priority**: Matches this engine's existing convention (`resolution.py`'s
`_critical_band`: "an unrecognized damage type is a load error, not a table quietly skipped") —
consistency with sibling table lookups already landed, not new behaviour this feature invents.

**Independent Test**: Call the lookup with a family key not in the closed set of four and confirm
it raises a clear, catchable error rather than returning a value or an unhandled exception.

**Acceptance Scenarios**:

1. **Given** a family key of `"oracle-prompt-weather"` (not one of the four), **When** it is
   rolled, **Then** the engine raises an error naming the closed set of valid keys.

---

### Edge Cases

- A roll must be a natural 1d100 result in the range 1-100 inclusive; a value outside that range
  is a caller error (same convention as other table lookups in this engine — the die tool itself
  only ever returns 1-100 for `1d100`).
- This feature does not write to any entity's state (no companion `objective.wants`, no thread
  record) — per the design document, applying a rolled result to state is the GM's own act,
  tracked separately under #292. The roll/effect/description triple is the entire contract.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a lookup, keyed by one of the four family keys declared in
  docs/design/15-oracle-prompts.md (`oracle-prompt-npc-objective`, `oracle-prompt-situation-
  truth`, `oracle-prompt-thread-turn`, `oracle-prompt-complication`), that maps a natural 1d100
  roll to that table's row: its effect key and description, exactly as the design document's
  tables declare them.
- **FR-002**: Each table's ten rows MUST cover 1-100 contiguously with no gaps and no overlaps,
  matching the design document exactly (this is a property of the shipped data, verified by a
  check script — not something the lookup itself needs to re-validate at call time beyond
  rejecting an out-of-range roll).
- **FR-003**: The lookup MUST reject a family key outside the closed set of four with a clear
  error, rather than returning an empty/null result or an unhandled exception.
- **FR-004**: The engine MUST expose this lookup as a callable verb (matching this engine's
  existing verb-catalog pattern in `catalog.py`/`client.py`), accepting a family key and a
  seed/roll, and returning the natural roll, the row's effect key, and its description.
- **FR-005**: The verb MUST use this engine's existing deterministic dice tool for the roll
  (`1d100`, no modifier), the same as every other table-driven mechanic in this engine — never a
  bare `random` call.
- **FR-006**: This feature MUST NOT write to any entity's persisted state; the verb is read-only,
  returning content for the caller (the GM) to apply.
- **FR-007**: `tools/check_oracle_prompts.py`'s stale reference to `docs/design/13-oracle-
  prompts.md` MUST be corrected to the document's actual current path (`docs/design/15-oracle-
  prompts.md`), so the existing check script runs instead of failing on a missing file.

### Key Entities

- **Oracle prompt table**: one of the four family keys; ten (range, effect key, description) rows
  covering 1-100 contiguously. Data only — this feature adds no new persisted entity type.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For all four family keys, every integer roll 1-100 resolves to exactly the row the
  design document declares for that range — verified exhaustively, not sampled.
- **SC-002**: `tools/check_oracle_prompts.py` runs to completion and passes against the corrected
  document path.
- **SC-003**: `python3 -m pytest -q` (under `PYTHONPATH=engine`), `python3 -m ruff check .`,
  `python3 -m ruff format --check .`, `python3 tools/check_docs.py`, and `python3
  tools/backlog.py check` are all clean after this feature lands.
