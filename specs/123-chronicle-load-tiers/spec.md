# Feature Specification: Chronicle load-tier resolution and recap.md

**Feature Branch**: `123-chronicle-load-tiers`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Chronicle load-tier resolution (always / on-demand / archival) and recap.md" (issue #326)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Always-tier resolves without a manifest (Priority: P1)

A GM starting a session needs to know exactly which entities to read into context before play
begins, without maintaining or consulting any curated list.

**Why this priority**: This is the feature's entire point (#326's goal) — everything else
(recap.md, regeneration) depends on this query existing and being correct.

**Independent Test**: Given a chronicle's entity set, running the always-tier query returns the
player character, every companion with `status: with-party`, every thread with `heat >= 3`,
`chronicle.yaml`, and `recap.md` — and nothing else — with no separate list to maintain.

**Acceptance Scenarios**:

1. **Given** a chronicle with a player character, two with-party companions, one former
   companion at `status: departed`, and threads at `heat` 2, 3 and 5, **When** the always-tier
   query runs, **Then** it returns the player character, the two with-party companions, the two
   threads with `heat >= 3`, `chronicle.yaml` and `recap.md` — and excludes the departed
   companion and the `heat: 2` thread.
2. **Given** an entity's `status` changes from `with-party` to `departed` (or a thread's `heat`
   drops below 3) between two queries, with no other write, **When** the always-tier query runs
   again, **Then** that entity is absent from the second result — tier membership tracked current
   state, not a stale prior answer.

---

### User Story 2 - On-demand entities are reachable by id or search (Priority: P2)

During play, a GM needs to pull in an entity that isn't in the always-tier set — a place visited
once, an NPC referenced in passing — without that entity ever needing to be pre-declared.

**Why this priority**: Without this, the always tier is complete but the session has no way to
reach the rest of the chronicle at all.

**Independent Test**: Given any entity not in the always tier, it can be fetched by its id, and
found by a text/grep search over the entity set, without appearing in the always-tier query.

**Acceptance Scenarios**:

1. **Given** an entity that is not the player character, not a with-party companion, and not a
   `heat >= 3` thread, **When** it is looked up by its id, **Then** it is returned in full.
2. **Given** a search term that matches text in an on-demand entity's body or frontmatter,
   **When** a grep-style search runs over the entity set, **Then** that entity is among the
   results.

---

### User Story 3 - recap.md regenerates at session close (Priority: P1)

A player returning to a chronicle after time away needs a short, current summary of where things
stand, without reading raw entity files.

**Why this priority**: `recap.md` is itself in the always-tier set (#326's goal, and
`22-state.md` § Load policy) — the always tier is incomplete as a feature until it is a
regenerated document rather than a stale one.

**Independent Test**: Given a chronicle at session close, regenerating `recap.md` produces a
document of roughly 200 words covering where and when, the three hottest threads, what changed,
body/mind state, and who's present — replacing whatever `recap.md` held before.

**Acceptance Scenarios**:

1. **Given** a session that changed a thread's heat, moved a companion's status, and changed the
   player character's location, **When** the session closes, **Then** `recap.md` is regenerated
   and reflects all three changes.
2. **Given** a chronicle with more than three open threads, **When** `recap.md` regenerates,
   **Then** it names exactly the three highest-heat threads, not all of them.
3. **Given** a freshly regenerated `recap.md`, **When** its word count is measured, **Then** it
   is close to 200 words (not, say, double or half that) — a soft budget, not an exact count.

### Edge Cases

- A chronicle with no with-party companions and no thread at `heat >= 3`: the always tier still
  returns the player character, `chronicle.yaml` and `recap.md` — an empty companion/thread set
  is valid, not an error.
- A chronicle with zero open threads: `recap.md`'s "three hottest threads" section names as many
  as exist (zero, one, two), never fabricates placeholders to fill three slots.
- Regenerating `recap.md` when no session actually ran (called out of sequence): the query layer
  itself does not need to guard against this — session-close sequencing is `session.py`'s
  existing responsibility, not new scope here.
- An entity with `status: with-party` but no `heat`/`threat` block at all (an ordinary companion):
  included in the always tier by status alone, independent of any thread scoring.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an always-tier query over the current entity set that
  returns exactly: the player character, every companion entity with `status: with-party`, every
  thread entity with `heat >= 3`, plus `chronicle.yaml` and `recap.md`.
- **FR-002**: The always-tier query MUST be re-derivable purely from current entity state (status
  fields, `heat` values, entity kind) — no separate manifest, cache, or list of ids that could
  fall out of sync with the entities themselves.
- **FR-003**: The system MUST support fetching any entity not in the always tier by its id
  (on-demand tier).
- **FR-004**: The system MUST support finding on-demand entities by a text search (grep-style)
  over the entity set.
- **FR-005**: The system MUST treat `log/` as archival — reachable but not surfaced by either the
  always-tier or on-demand queries described above.
- **FR-006**: The system MUST regenerate `recap.md` at session close, replacing its prior
  content.
- **FR-007**: A regenerated `recap.md` MUST include: where and when the player character is,
  the three hottest open threads (by `heat`, fewer if fewer exist), what changed during the
  session just closed, the player character's body and mind state in one sentence each, and who
  is currently present (with-party companions).
- **FR-008**: A regenerated `recap.md` MUST stay close to a 200-word budget (a soft target, not
  an exact count enforced as a hard failure).
- **FR-009**: Changing an entity's `status` or a thread's `heat` MUST change always-tier
  membership on the very next query, with no other state requiring an update.

### Key Entities *(include if feature involves data)*

- **Always-tier result**: the set of items a session loads unconditionally — player character,
  with-party companions, `heat >= 3` threads, `chronicle.yaml`, `recap.md`. Not a stored object;
  the output of a query run fresh each time.
- **recap.md**: a regenerated markdown document, not hand-authored, summarising chronicle state
  at the moment of the last session close.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The always-tier query, run against a chronicle's current entity set, returns the
  correct set (per FR-001) with no manual curation step.
- **SC-002**: A change to a single entity's `status` or `heat` field changes the always-tier
  query's result on the next call, with zero additional writes.
- **SC-003**: `recap.md`, regenerated at session close, lands within roughly 150-250 words in
  ordinary cases (a soft band around the ~200-word target, not a hard cutoff).
- **SC-004**: `ruff check` and `ruff format --check` both pass repo-wide after the change.

## Assumptions

- This feature is a pure query/generation layer over entities already loadable via
  `engine/wyrd/entity.py`'s existing `load_set`/`resolve_entity` — it does not change entity
  schema or storage.
- Out of scope, per issue #326: invariant enforcement on writes, and the pending/transaction
  lifecycle — both later children of epic #300.
- "On demand by id/grep" is satisfied by exposing a lookup-by-id function and relying on the
  entity set already being plain text/YAML files a grep-style search can run over; no new index
  structure is assumed necessary unless investigation during planning shows otherwise.
- `chronicle.yaml`'s schema and load/save (#325) are already in place and used as-is.
- The "session close" trigger point is `engine/wyrd/session.py`'s existing close/loop machinery;
  this feature adds a step there rather than inventing a new lifecycle hook.
