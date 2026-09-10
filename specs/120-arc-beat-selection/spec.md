# Feature Specification: Beat/arc entry and exit conditions, and thread-matched selection

**Feature Branch**: `321-arc-beat-selection`

**Created**: 2026-09-10

**Status**: Draft

**Input**: GitHub issue #321 — Beat/arc entry and exit conditions, and thread-matched selection

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A beat or arc declares what it needs and what it leaves behind (Priority: P1)

A GM (or another engine module) attaches an `entry` block (`requires_threads`, `requires_state`,
`hooks`) and an `exit` block (`emits_threads`, `changes`, `leads_to`) to an arc or beat, so its
place in a story can be judged from its own declared fit rather than from an author's fixed
sequence.

**Why this priority**: Every other story here — selection, fallback, recursion — reads these two
blocks. Without a validated shape for them, nothing downstream has solid ground to stand on.

**Independent Test**: Construct an arc and a beat each carrying a full `entry`/`exit` block, and
confirm both validate; corrupt one required sub-field at a time and confirm each is rejected.

**Acceptance Scenarios**:

1. **Given** an arc or beat with `entry.requires_threads`, `entry.requires_state`, and
   `entry.hooks`, **When** it is validated, **Then** it is accepted.
2. **Given** an arc or beat with `exit.emits_threads` (each entry optionally carrying an `if`
   condition), `exit.changes`, and `exit.leads_to`, **When** it is validated, **Then** it is
   accepted.
3. **Given** an arc or beat with no `entry`/`exit` block at all, **When** it is validated,
   **Then** it is still accepted — both blocks are optional, not a new required field on every
   entity (a stub, per #299's sibling feature, may carry neither yet).

---

### User Story 2 - The engine picks the next beat by matching live threads (Priority: P1)

Given a set of threads currently live in a chronicle, the engine selects candidate arcs/beats
whose `entry.requires_threads` are satisfied by that set — the mechanism that lets a decade-long
chronicle draw on a library-wide pool instead of a single author's order.

**Why this priority**: This is the feature's reason for existing — the entry/exit schema in
User Story 1 only matters because something reads it to make a selection decision.

**Independent Test**: Build a small pool of candidates with varied `requires_threads`, run
selection against a chosen live-thread set, and confirm exactly the candidates whose requirements
are a subset of the live threads come back.

**Acceptance Scenarios**:

1. **Given** a pool of candidates and a live-thread set that satisfies two of them,
   **When** selection runs, **Then** exactly those two are returned.
2. **Given** a candidate with an empty or absent `requires_threads`, **When** selection runs
   against any live-thread set (including empty), **Then** that candidate is always eligible —
   an empty requirement is never treated as unsatisfiable.
3. **Given** a candidate whose `requires_threads` is only partially covered by the live-thread
   set, **When** selection runs, **Then** it is excluded.

---

### User Story 3 - `leads_to` is a fallback, never an equal-weight candidate source (Priority: P1)

When no candidate's `requires_threads` matches the live threads, the engine falls back to
whatever a prior beat's `exit.leads_to` suggests, but only then — a live thread match always wins
over a hinted sequence.

**Why this priority**: The design doc calls this out specifically ("`leads_to` is consulted only
when nothing better is live"); getting the ordering backward would silently turn Wyrd's emergent,
thread-matched selection into a rail.

**Independent Test**: Construct a case where a `leads_to` target and a thread-matched candidate
both exist and confirm the thread-matched one is what selection returns; then remove the
thread-matched candidate and confirm the `leads_to` target is returned instead.

**Acceptance Scenarios**:

1. **Given** both a thread-matched candidate and a `leads_to` target, **When** selection runs,
   **Then** the thread-matched candidate is returned and the `leads_to` target is not consulted.
2. **Given** no thread-matched candidate but a `leads_to` target naming a valid candidate,
   **When** selection runs, **Then** the `leads_to` target is returned.
3. **Given** neither a thread-matched candidate nor a `leads_to` target, **When** selection runs,
   **Then** the engine returns no selection (an empty result), not an error — no fit found is a
   legitimate outcome the caller must handle, not a defect.

---

### User Story 4 - Selection works at every nesting level, including an undecomposed stub (Priority: P2)

Because arcs contain arcs, entry/exit conditions exist at every level, not just at the leaves —
the engine can match threads against a whole campaign, a single arc inside it, or a beat, and an
arc that has never been decomposed into children is still selectable purely on its own entry/exit.

**Why this priority**: This is what makes lazy conversion (the sibling feature under #299)
actually lazy — a stub earns its place in a story before anyone has spent effort decomposing it.

**Independent Test**: Include an arc still at `status: stub` (no children) in the candidate pool
alongside fully-decomposed arcs and beats, and confirm it is selected on the same footing when its
own `requires_threads` matches.

**Acceptance Scenarios**:

1. **Given** a candidate pool mixing beats, decomposed arcs, and an undecomposed stub arc,
   **When** selection runs, **Then** the stub is evaluated purely on its own `entry` block, with
   no requirement that it have children to be selectable.
2. **Given** a live-thread set matched by an arc containing further arcs and beats, **When**
   selection runs at the arc's own level, **Then** the arc itself is returned without descending
   into its children — descent, when wanted, is a separate call at the next level.

---

### Edge Cases

- What happens when a candidate's `entry.requires_state` names a state condition (not a thread) —
  is it evaluated by this feature? Out of scope: this feature covers `requires_threads` matching
  only; `requires_state` is validated as a shape (User Story 1) but its evaluation against actual
  chronicle state depends on the chronicle-state layer (#300, not built yet) and is deferred to
  it.
- What happens when two or more candidates satisfy `requires_threads` equally? The engine returns
  all of them — this feature does not rank or pick among ties; a caller (or a later feature)
  decides.
- What happens when `exit.emits_threads[].if` references a condition this feature cannot itself
  evaluate? The `if` field's shape is validated (User Story 1); evaluating whether the condition
  held is the caller's responsibility once the beat resolves — this feature only carries the
  field through, it does not interpret it.
- What happens when a `leads_to` target does not exist in the candidate pool at all (dangling
  reference)? Treated the same as "no `leads_to` target" for User Story 3's fallback purposes —
  selection returns no selection rather than raising, though a caller may separately choose to
  surface it as a data-integrity problem (out of scope here; `entity.unresolved_references`
  already covers dangling wikilinks generally).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST support an optional `entry` block on an arc or beat, holding
  `requires_threads` (list of thread tags), `requires_state` (list of state conditions, shape
  only), and `hooks` (list of narrative hook strings).
- **FR-002**: The engine MUST support an optional `exit` block on an arc or beat, holding
  `emits_threads` (list of `{tag, if}` entries, `if` optional), `changes` (list of strings), and
  `leads_to` (a reference to another arc/beat).
- **FR-003**: An arc or beat carrying neither block MUST still validate — `entry`/`exit` are
  optional, consistent with a `status: stub` entity that has not yet been decomposed.
- **FR-004**: The engine MUST expose a selection function that, given a live-thread set and a
  pool of candidate arcs/beats, returns every candidate whose `entry.requires_threads` is a
  subset of the live-thread set.
- **FR-005**: A candidate with an empty or absent `requires_threads` MUST always be eligible,
  regardless of the live-thread set.
- **FR-006**: When the thread-match in FR-004 returns at least one candidate, the engine MUST
  return only those matches — `leads_to` MUST NOT be consulted.
- **FR-007**: When the thread-match in FR-004 returns no candidates, the engine MUST fall back to
  resolving `leads_to` from whatever beat/arc the caller names as the current one, returning that
  target if it names a valid candidate in the pool.
- **FR-008**: When neither a thread match nor a valid `leads_to` target exists, the engine MUST
  return an empty result rather than raising.
- **FR-009**: Selection MUST operate on any given nesting level's own candidates without
  requiring that a candidate have children, so an arc at `status: stub` is selectable on its own
  entry/exit alone.
- **FR-010**: Selection MUST NOT itself descend into a selected arc's children — recursion to a
  deeper level is a separate call the caller makes, not an implicit side effect of one selection
  call.
- **FR-011**: `entry`/`exit` field names and shapes MUST match `docs/design/26-corpus-index.md`'s
  beat schema exactly (the index is a projection of the entities, not a parallel vocabulary).

### Key Entities *(include if feature involves data)*

- **Entry block**: What must already be true (live threads, state, narrative hooks) for an arc or
  beat to be reachable.
- **Exit block**: What an arc or beat leaves behind once resolved — threads it emits (optionally
  conditional on outcome), changes to the world, and a hinted next step (`leads_to`).
- **Live-thread set**: The plain input this feature consumes — a set of thread tags currently
  live in a chronicle. This feature does not store or track it; that is the chronicle/campaign
  state layer (#300/#301), not built yet.
- **Candidate pool**: The arcs/beats a given selection call considers, at whatever single nesting
  level the caller is currently working at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given any arc/beat with a well-formed `entry`/`exit` block, validation accepts it
  100% of the time; a malformed required sub-field is rejected 100% of the time.
- **SC-002**: In a scripted pool where exactly N of M candidates satisfy the live-thread set,
  selection returns exactly those N, with zero false positives or negatives, across repeated
  runs.
- **SC-003**: In a scripted case with both a thread match and a `leads_to` target present,
  selection returns the thread match 100% of the time; with the thread match removed, it returns
  the `leads_to` target 100% of the time.
- **SC-004**: An undecomposed stub arc included in a candidate pool is selected under the same
  conditions as a fully-decomposed arc or beat, with no code path that excludes it for lacking
  children.

## Assumptions

- This feature builds on the entity file format (#296, closed) and the containment/session-loop
  work (#309, merged) — it adds a new, optional schema layer and a pure selection function, it
  does not change how containment or the session loop themselves work.
- Where "live threads" are stored, tracked, or updated as play proceeds is explicitly out of
  scope — this feature takes that set as a plain argument, matching the existing engine module
  pattern (setting-supplied/caller-supplied data passed in, no hidden state).
- The lazy-conversion status lifecycle (`stub` → `drafted` → `complete`) and provenance
  (`sources`) fields are a sibling feature under the same parent epic (#299 → the other linked
  feature) and are not touched here.
- Danger scaling (`danger_effective`, already implemented in `engine/wyrd/adversary.py`) is
  unrelated to selection itself and is not invoked by this feature; a caller applies it
  separately once a beat/arc is selected.
- This module holds no persistent state of its own, matching `wyrd.entity`/`wyrd.session`'s
  pure-function style.
