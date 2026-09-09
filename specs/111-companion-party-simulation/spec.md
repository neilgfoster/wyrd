# Feature Specification: Companion and party simulation engine support

**Feature Branch**: `111-companion-party-simulation`

**Created**: 2026-09-09

**Status**: Draft

**Input**: GitHub issue #292 — Companion and party simulation: engine support

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bring a companion into the party (Priority: P1)

A GM adds a companion to the party record: a person with a narrative layer (what they want, what
their flaw is, what secret they hold, what choice they're heading toward) and a mechanical layer
(career, Bond, Taint, Strain, wounds) exactly as `docs/design/16-session.md` specifies.

**Why this priority**: Without a representable companion, nothing else in this feature has
anything to act on.

**Independent Test**: Create a companion record with both layers populated; the engine accepts it,
rejects a mechanical layer with a sixth field or a missing one of the five, and rejects a
narrative-layer field bleeding into the mechanical layer's five.

**Acceptance Scenarios**:

1. **Given** a new companion with `career`, `bond`, `taint`, `strain`, `wounds` all present and no
   others, **When** the party record is validated, **Then** it is accepted.
2. **Given** a companion record missing `bond`, **When** validated, **Then** the engine reports
   which field is missing rather than accepting a partial record.
3. **Given** a companion record carrying an extra mechanical field not in the closed five,
   **When** validated, **Then** the engine rejects it.

---

### User Story 2 - Tension and Bond interact the way the rule specifies (Priority: P1)

A companion-naming event that would raise Party Tension has its actual Tension gain computed from
that companion's Bond, per the offset table in `docs/design/16-session.md` (`ADR 0034`): Bond
below 0 adds an extra point per point below; Bond above 0 subtracts a point per point above,
floored at 0.

**Why this priority**: This is the mechanical payoff the design commits to; without it Bond is
inert data and Tension does not behave as documented.

**Independent Test**: Compute the Tension delta for a base-1 event against companions at Bond +3,
+1, 0, and -2 in isolation, and compare each to the table in the design document.

**Acceptance Scenarios**:

1. **Given** a companion at Bond +3, **When** an event naming them would add 1 Tension, **Then**
   the actual delta applied is 0.
2. **Given** a companion at Bond -2, **When** an event naming them would add 1 Tension, **Then**
   the actual delta applied is 3.
3. **Given** an event that names no specific companion, **When** Tension would rise, **Then** the
   stated delta applies unmodified, regardless of any companion's Bond.
4. **Given** Tension at 5, **When** an event adds enough to reach or exceed 6, **Then** Tension
   resolves as a break and resets to 0 (per `docs/design/16-session.md`'s "at 6, something
   breaks... then Tension resets to 0").

---

### User Story 3 - Loyalty gates who can join, and strain doubles Tension gain (Priority: P2)

The GM asks whether a candidate companion may join the current party. The engine answers using the
setting's declared Loyalty relations: undeclared pairs travel normally, `strained` pairs are
allowed but double the party's Tension gain while both are present, and `irreconcilable` pairs are
refused outright.

**Why this priority**: This is a hard gate (a party the engine must refuse to assemble) plus a
Tension-rate modifier, both load-bearing for session play, but the party is usable without it if
built with compatible Loyalties by hand.

**Independent Test**: Attempt to add a companion whose Loyalty is `irreconcilable` with an existing
party member's Loyalty; the engine refuses and states why. Attempt to add one whose Loyalty is
merely `strained` with an existing member's; the engine allows it and the party's Tension-gain rate
doubles while both remain present.

**Acceptance Scenarios**:

1. **Given** two Loyalties the setting declares `irreconcilable`, **When** a companion of one is
   added to a party already containing a character of the other, **Then** the engine refuses the
   join and identifies the conflicting pair.
2. **Given** two Loyalties the setting declares `strained`, **When** both are present in the party,
   **Then** an event that would add N Tension instead adds 2N (before any Bond offset).
3. **Given** two Loyalties with no declared relation, **When** both are present, **Then** the party
   forms normally and Tension accrues at the stated rate.
4. **Given** a party member whose Loyalty changes to one `irreconcilable` with another current
   member, **When** the change is applied, **Then** the party is re-checked and Tension breaks
   immediately (resolves as a 6-break and resets to 0), per `docs/design/16-session.md`.

---

### User Story 4 - The GM plays the whole rest of the party (Priority: P2)

Given the current party's companions, their narrative-layer objectives, and the situation, the
engine surfaces what each companion's stated objective and next step already commit them to acting
on — including refusing, lying, leaving, or acting while the player character is elsewhere — rather
than the GM inventing it from nothing each time or the player being asked to decide for them.

**Why this priority**: This is `docs/design/16-session.md`'s "the GM runs everyone else" and "the
GM never asks the player to decide for a companion" made operable, but it is GM-support tooling
layered on top of User Stories 1-3's data model, not a gate on them.

**Independent Test**: Given a companion record with `objective.wants` and `objective.next_step`
populated, request that companion's current disposition; the engine returns the recorded objective
and next step rather than silently defaulting or requiring the caller to already know them.

**Acceptance Scenarios**:

1. **Given** a companion with a populated `objective`, **When** the GM asks what that companion is
   currently oriented toward, **Then** the engine returns `wants` and `next_step` verbatim — it
   does not generate new narrative content (that stays the GM's job; `docs/design/16-session.md`:
   "nothing on it is consulted by a die roll").
2. **Given** a party of up to five companions, **When** the GM requests the full party roster,
   **Then** every companion's narrative and mechanical layers are returned together, keyed so a
   beat needs no lookup beyond what is already there.

### Edge Cases

- A party at the design's stated maximum size (five companions plus the player character): adding
  a sixth companion is refused, not silently truncated.
- A companion's Bond sits exactly at 0: the offset table's baseline (no change) applies.
- Tension is already at 6 when the increment is computed (e.g. two stacking events in the same
  beat): the break resolves once, Tension does not go negative or accumulate past the reset.
- A companion has `wounds: []` (none yet): this is a valid record, not an error.
- A Loyalty relation is queried in both directions (A-to-B and B-to-A): the relation is symmetric
  and the engine returns the same answer either way.
- A companion's Loyalty is undeclared entirely by the setting (no career/skills tie-in beyond
  Loyalty membership): treated as the "undeclared" relation to everything, per the design's
  explicit default.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST represent a companion as a `character` entity carrying exactly two
  layers: a narrative layer (`objective` with `wants`/`next_step`, `flaw`, `secret`, `arc`) and a
  mechanical layer closed at exactly five fields (`career`, `bond`, `taint`, `strain`, `wounds`),
  per `docs/design/16-session.md` and ADR 0034.
- **FR-002**: The engine MUST reject a companion record whose mechanical layer is missing any of
  the five closed fields, or that carries a mechanical field outside that set.
- **FR-003**: The engine MUST compute a companion-naming Tension event's actual delta from the
  named companion's `bond`, using the stated offset (delta = max(0, base + (0 - bond)) when bond is
  negative or zero contributes base as today; concretely: an extra +1 Tension per point Bond sits
  below 0, and -1 Tension per point Bond sits above 0, floored at 0), matching the worked values in
  `docs/design/16-session.md`'s table (+3→0, +1→0, 0→1, -2→3) for a base-1 event.
- **FR-004**: The engine MUST leave a Tension event that names no specific companion unmodified by
  any companion's Bond.
- **FR-005**: The engine MUST resolve Party Tension reaching or exceeding 6 as a single break and
  reset Tension to 0, regardless of how much the triggering increment overshot 6.
- **FR-006**: The engine MUST reduce Tension by 1 during downtime and by 1 when the player spends a
  beat on a companion's problem, per `docs/design/16-session.md`, without letting it go below 0.
- **FR-007**: The engine MUST look up the declared relation between any two Loyalties from the
  setting's data, defaulting to "undeclared" (no effect) when the setting states no relation for a
  given pair.
- **FR-008**: The engine MUST refuse to add a companion to a party when doing so would place an
  `irreconcilable` Loyalty pairing in the party, and MUST report which two Loyalties conflict.
- **FR-009**: The engine MUST double the party's Tension-gain rate (before any Bond offset) for as
  long as a `strained` Loyalty pairing is present in the party.
- **FR-010**: The engine MUST re-check the party's Loyalty pairings whenever a character's Loyalty
  changes, and MUST resolve an existing pairing that becomes `irreconcilable` as an immediate
  Tension break (reset to 0), per `docs/design/16-session.md`.
- **FR-011**: The engine MUST enforce a maximum party size of five companions alongside the player
  character, refusing to add a companion beyond that bound.
- **FR-012**: The engine MUST provide a way to read a single companion's or the full party's
  narrative and mechanical layers together, without requiring the caller to separately assemble
  them from multiple lookups.
- **FR-013**: The engine MUST NOT generate, infer, or alter narrative-layer content (`objective`,
  `flaw`, `secret`, `arc`) on a companion's behalf — that content is authored and played by the GM;
  the engine's role is to surface what is already recorded, per `docs/design/16-session.md`'s "the
  GM never asks the player to decide for a companion" and the narrative layer's own "nothing here
  is ever read by a resolution rule."

### Key Entities

- **Companion**: a `character` entity representing a party member other than the player character.
  Narrative layer: `objective` (`wants`, `next_step`), `flaw`, `secret`, `arc` — free text, never
  read by a resolution rule. Mechanical layer, closed at five fields: `career`, `bond` (-3..+3),
  `taint`, `strain`, `wounds` (list of lasting-wound entries, same table as the player character).
- **Party**: the current set of companions (and the player character) travelling together;
  tracks a single **Tension** value (0-6) shared across the whole party.
- **Loyalty relation**: a pairwise relation the setting declares between two Loyalty values —
  `strained` or `irreconcilable` — with "undeclared" (no effect) as the default for any pair the
  setting does not name.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM can create, validate, and read back a full five-companion party using only
  engine calls, with no hand-assembly of a companion's two layers from separate sources.
- **SC-002**: Every Tension-delta value in `docs/design/16-session.md`'s Bond-offset table is
  reproduced exactly by the engine's computation for the corresponding Bond value, verified by a
  script that reads the table from the design document rather than a hand-copied literal.
- **SC-003**: An attempt to assemble a party containing an `irreconcilable` Loyalty pairing is
  refused 100% of the time, with the conflicting pair identified in the refusal.
- **SC-004**: `python3 -m ruff check .` and `python3 -m ruff format --check .` report the new code
  clean, and `python3 tools/check_companion_layers.py` continues to pass unchanged (the closed
  five-field mechanical layer is not altered by this feature).

## Assumptions

- This feature implements engine mechanics only; it does not add narrative-content generation
  (e.g. an LLM authoring a companion's objective) — that remains a GM/table activity the engine
  surfaces data for, per FR-013.
- "NPC-played party simulation" in scope here means: representing companions, computing Tension
  and Bond interactions, enforcing Loyalty gating, and surfacing each companion's recorded
  objective/next-step for the GM to play — not an autonomous decision-making agent that chooses
  actions on a companion's behalf. `docs/design/16-session.md` places that judgment with the GM.
- The setting supplies Loyalty names and their pairwise relations as data (per
  `docs/design/24-authoring-a-setting.md`); this feature consumes that data and does not define
  what Loyalties any particular setting has.
- Adversary and named-antagonist handling (`docs/design/12-the-adversary.md`) is unaffected and out
  of scope — this feature only touches the companion/party model.
- Party membership and Tension state persist using the same `state.py` persistence primitives the
  player character already uses, rather than a new storage mechanism.
