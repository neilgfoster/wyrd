# Feature Specification: Scenario selection by thread heat and hooks

**Feature Branch**: `131-scenario-selection`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Scenario selection by thread heat and hooks" (issue #339)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM is offered the scenario whose hooks match the hottest threads (Priority: P1)

At the start of an arc, or when a scenario closes, the chronicle needs its next scenario picked
rather than scripted (docs/design/19-campaign.md). The engine ranks live threads by heat, finds
which candidate scenarios' declared `hooks` match those threads, and proposes the
best-matching one.

**Why this priority**: this is the entire mechanical content of "Scenario selection" — without
it, nothing connects a chronicle's accumulated threads (#335) to what plays next.

**Independent Test**: given a set of threads at different heat levels and a set of candidate
scenarios each declaring their own `hooks`, confirm the scenario whose hooks match the hottest
thread(s) is selected over one matching only cold or unmatched threads.

**Acceptance Scenarios**:

1. **Given** two candidate scenarios, one whose hooks match a thread at heat 4 and one whose
   hooks match only a thread at heat 1, **When** selection runs, **Then** the first is proposed.
2. **Given** a candidate scenario whose hooks match no live thread at all, **When** selection
   runs, **Then** it is never proposed over one that matches something, even at low heat.
3. **Given** two candidate scenarios that tie on total matched heat, **When** selection runs,
   **Then** the earlier one in the candidate list is proposed — a deterministic, stable
   tie-break, never an arbitrary one.
4. **Given** no candidate scenario matches any live thread, **When** selection runs, **Then**
   nothing is proposed (`None`) rather than an arbitrary pick.

---

### User Story 2 - The selected scenario is scaled to the current danger rating (Priority: P1)

A scenario is written for a given party size; the chronicle's actual party may be larger or
smaller, and its danger rating may have shifted. The selected scenario's encounter counts are
scaled through the engine's existing danger-scaling machinery (docs/design/03-rules.md section
7, `adversary.scaled_count`) before being handed to the GM.

**Why this priority**: an unscaled scenario either trivialises or overwhelms the actual party —
the design document is explicit that content is written once and scaled, never rewritten per
chronicle.

**Independent Test**: given a selected scenario with a declared `written_for` party size and one
or more encounters with a `written_count`, confirm each encounter's scaled count matches what
`adversary.scaled_count` already computes for the same inputs.

**Acceptance Scenarios**:

1. **Given** a selected scenario's encounter with `written_count: 4`, `written_for: 4`, and a
   chronicle `danger_rating`/party matching what it was written for, **When** the scenario is
   scaled, **Then** the encounter's count is unchanged (a ratio of 1).
2. **Given** a selected scenario's encounter with a smaller actual party than `written_for`,
   **When** the scenario is scaled, **Then** the encounter's count is exactly what
   `adversary.scaled_count` returns for those same inputs — no separate scaling formula is
   introduced.

---

### User Story 3 - Provenance is recorded on the selected scenario (Priority: P2)

Selecting a scenario rewrites names, places and factions to fit the chronicle; `source:` records
what it was adapted from and what changed, so a reader coming back later can tell content from
consequence.

**Why this priority**: without it, a converted scenario is indistinguishable from one authored
from scratch, losing exactly the "sourcing is by theme, not system" provenance the design
document treats as load-bearing.

**Independent Test**: given a selected scenario, an `adapted_from` label and a `changed`
description, confirm the returned scenario carries a `source: {adapted_from, changed}` block.

**Acceptance Scenarios**:

1. **Given** a selected scenario and provenance details, **When** `source:` is recorded,
   **Then** the returned scenario carries `source: {adapted_from, changed}` and every other
   field unchanged.

### Edge Cases

- An empty candidate-scenario list, or an empty threads list, yields `None` selected — never an
  error.
- A scenario declaring `hooks: []` (no hooks at all) never matches any thread and is never
  selected over one that does.
- A scenario with no encounters (`encounters: []`, e.g. a purely social one) scales to an empty
  encounter list — never an error, never a spurious minimum-1 count.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to rank a list of threads by `heat`, descending,
  stable on ties.
- **FR-002**: The engine MUST provide a way to select, from a list of candidate scenarios each
  declaring a `hooks` list, the one whose hooks match the greatest total heat across live
  threads — summing the heat of every live thread whose id or hook appears in a scenario's
  `hooks`.
- **FR-003**: Selection MUST break a tie in matched heat by earliest position in the candidate
  list — deterministic, never arbitrary (FR from User Story 1's Acceptance Scenario 3).
- **FR-004**: Selection MUST return `None` (not raise, not an arbitrary pick) when no candidate
  scenario matches any live thread, or when either input list is empty.
- **FR-005**: The engine MUST provide a way to scale a selected scenario's declared encounters
  through the engine's existing `adversary.scaled_count` — no new scaling formula is introduced.
- **FR-006**: The engine MUST provide a way to attach a `source: {adapted_from, changed}` block
  to a selected scenario, returning every other field unchanged.

### Key Entities

- **Candidate scenario** (read from `scenarios/*/scenario.yaml` in a setting repo, out of
  scope's file layer — this feature takes an already-loaded list of scenario dicts): a plain
  dict with `hooks: list[str]`, `written_for: int`, and `encounters: list[{written_count: int,
  ...}]`. This feature does not define or validate the full scenario schema, only the fields it
  reads.
- **Selection result**: the chosen scenario dict, or `None`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The highest-matched-heat scenario is selected over any lower-matching alternative
  in every tested combination — verified by exact-input tests.
- **SC-002**: A tie in matched heat always resolves to the earlier candidate, verified
  explicitly, not left to dict/set ordering.
- **SC-003**: Every scaled encounter count exactly equals `adversary.scaled_count`'s own output
  for the same inputs — no drift between this feature's scaling and the existing formula.
- **SC-004**: A recorded `source:` block is present on every scenario this feature attaches one
  to, with every other field of the scenario unchanged.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no file
  I/O — matching every sibling module in this epic. `scenarios/*/scenario.yaml` files
  themselves, and the setting-specific catalogue they form, live in a setting repo (per this
  repo's own CLAUDE.md: "no catalogue of a personal library" enters the engine repo) — this
  feature operates on an already-loaded list of scenario dicts a caller supplies, the same
  boundary `threat.py`/`thread.py` keep for entity data.
- "Match" between a scenario's `hooks` and a thread is exact string membership — a scenario hook
  matches a thread when that hook string appears in the thread's own `hooks` list (both declared
  in the same vocabulary per docs/design/19-campaign.md's example: `hooks: [money, influence,
  the-thing-they-funded]`). No fuzzy or partial matching is introduced.
- Danger-rating scaling reuses `adversary.scaled_count` exactly as it already exists (#98,
  epic-#8's danger-scaling work) — this feature adds no new formula, only the plumbing that
  applies it to a selected scenario's declared encounters.
- Filtering candidate scenarios "by setting" (docs/design/19-campaign.md) is assumed already
  done by the caller before this feature's candidate list is supplied — which setting's
  scenarios are eligible is a setting-repo/session concern, not this feature's.
