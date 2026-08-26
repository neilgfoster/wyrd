# Feature Specification: Journeys as a subsystem

**Feature Branch**: `024-journeys-as-a-subsystem`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Journeys as a subsystem — a travel-centred setting can run a
journey as played content, through one configurable engine subsystem (issue #56, Stage 10 of
the design programme)."

## Clarifications

### Session 2026-08-26

- Q: How is a hazard's per-leg trigger chance determined? → A: Mirrors the Threat activation
  roll (`docs/design/18-campaign.md`) — a per-journey hazard rating × 10, rolled once per leg.
- Q: What decides whether a leg is played (a beat) versus summarised? → A: Author-declared,
  via the existing `mode: played | summarised` field beats already carry
  (`docs/design/28-arcs-and-beats.md`) — set when the journey/leg is authored or converted.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a journey as played content (Priority: P1)

The GM needs to run a stretch of travel as a sequence of scenes the player actually plays —
choices, rolls, consequences — rather than a single sentence of narrated summary, because the
setting's whole story is the road.

**Why this priority**: This is the gap the issue exists to close. Without it, a
travel-centred setting has nothing to run, and it degrades every session to narration.

**Independent Test**: Start a journey between two known places with a defined pace and at
least one hazard entry. Play it to arrival. Every leg of the journey either resolves through
the core roll or is explicitly a narrated skip, and the chronicle's elapsed time and
consequences (Standing, condition, supply) reflect what happened.

**Acceptance Scenarios**:

1. **Given** a journey between two places with a known distance and pace, **When** the GM
   starts it, **Then** the journey produces a sequence of legs, each resolving through play
   (a beat) or through summary (elapsed time and expected-value events), matching
   `docs/design/18-campaign.md`'s existing split.
2. **Given** a journey in progress, **When** a leg's hazard roll (`d100` against the
   journey's hazard rating × 10) succeeds, **Then** the triggered hazard entry resolves
   through the core percentile roll, using an existing skill and difficulty, exactly as any
   other test in the engine.
3. **Given** a journey completes, **When** the GM checks chronicle state, **Then** elapsed
   time has advanced by the journey's stated span and any consequences (harm, Standing,
   supply, thread changes) are recorded as ordinary chronicle state — no journey-specific
   ledger.

---

### User Story 2 - Configure or disable the subsystem per setting (Priority: P2)

A setting author whose stories are not about travel needs journeys to cost nothing —
no fields to fill in, no table to maintain, no rule the GM has to remember to ignore.

**Why this priority**: The engine is setting-agnostic (`CLAUDE.md`); a subsystem that cannot
be turned off cleanly becomes a tax on every setting that doesn't want it, which the
`docs/design/26-authoring-a-setting.md` "a setting may never add a mechanism" rule is meant to
prevent from being worked around by leaving it half-used instead.

**Independent Test**: Take a setting with journeys left at their default (off, or minimally
configured), and confirm nothing about ordinary play — narrated travel, elapsed-time
advancement, scenario selection — requires touching journey configuration or produces
journey-specific output.

**Acceptance Scenarios**:

1. **Given** a setting that does not configure journeys, **When** the character travels in
   play, **Then** travel is narrated exactly as `docs/design/18-campaign.md` already describes,
   with no journey subsystem invoked.
2. **Given** a setting that does configure journeys, **When** an author reads its
   configuration, **Then** every field is optional beyond the minimum needed to place a
   journey on the map, and omitting a field (hazards, roles, supply) degrades to a sensible
   default rather than an error.

---

### User Story 3 - Author a journey from source material (Priority: P3)

A setting author converting a stub arc that is a journey (a road, a river, a trek across
open country) needs journey structure to fit the same lazy-conversion pipeline as any other
arc, so a journey is not a special case to hand-author outside the arc/beat tree.

**Why this priority**: Keeps the subsystem load-bearing rather than parallel machinery;
lower priority because it depends on User Story 1 existing first.

**Independent Test**: Take a stub arc tagged as a journey and decompose it, confirming the
result is an arc whose children are the journey's legs, addressable and selectable the same
way any other arc's children are.

**Acceptance Scenarios**:

1. **Given** a stub arc tagged as a journey, **When** it is converted, **Then** its children
   are legs expressed as ordinary beats or nested arcs (per `docs/design/28-arcs-and-beats.md`),
   not a separate journey-only file shape.

### Edge Cases

- What happens when the player abandons or reroutes a journey partway through? The engine
  must be able to close out a journey early — apply elapsed time and consequences for the
  distance actually covered, and let the remainder either lapse or be resumed later as a
  fresh journey — rather than requiring it to run to its declared end.
- What happens when a journey's hazard table has no entries (a setting configures roles and
  pace but skips hazards)? The journey still runs — legs resolve as travel/summary per
  `docs/design/18-campaign.md` — it simply never rolls on an empty table.
- What happens when the party composition changes mid-journey (a companion joins or is
  lost)? Any per-character consequence (supply draw, harm) applies to whoever is present at
  that leg, consistent with how the rest of the engine already treats a changing party.
- How does a journey interact with an active Threat whose reach the route passes through?
  The route is exposure like any other passage through a Threat's reach — its `ambient` cost
  applies, it does not require a separate journey-vs-threat resolution rule.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST define a journey as a structural extension of the existing
  arc/beat shape (`docs/design/28-arcs-and-beats.md`) — a sequence of legs, each an arc or a beat
  — not a new content type outside that tree.
- **FR-002**: A journey MUST resolve each leg through one of the two mechanisms
  `docs/design/18-campaign.md` already defines: **played** (a beat, run through the core roll) or
  **summarised** (elapsed time and expected-value events). No third resolution path is
  introduced.
- **FR-003**: The engine MUST support attaching, per journey, an optional pace (how much
  distance or time one leg covers), an optional ordered set of roles (who is doing what
  while travelling — e.g. navigating, foraging, standing watch), and an optional hazard
  table (entries that can trigger per leg).
- **FR-004**: Any hazard that triggers during a journey MUST resolve through the core
  percentile roll (`docs/design/03-rules.md`), using an existing skill and difficulty — a journey
  introduces no bespoke resolution mechanic.
- **FR-004a**: Each journey MUST carry a hazard rating; each leg rolls `d100` once against
  `rating × 10` to decide whether a hazard triggers, mirroring the Threat activation roll
  (`docs/design/18-campaign.md`) rather than introducing a second per-leg-chance formula.
- **FR-004b**: Each leg MUST declare its own resolution mode (`played` or `summarised`) using
  the existing `mode:` field beats already carry (`docs/design/28-arcs-and-beats.md`); the engine
  does not choose a leg's mode at runtime.
- **FR-005**: Supply and encumbrance consequences arising from a journey MUST use the
  existing material-economy abstraction (`docs/design/04-the-character.md` /
  standing-material-economy work) rather than a journey-specific inventory or logistics
  ledger — consistent with the engine's existing preference for abstracted supply over
  granular tracking.
- **FR-006**: The subsystem MUST be fully optional per setting: a setting that configures no
  journeys behaves exactly as the engine does today (narrated travel via
  `docs/design/18-campaign.md`), and every journey-specific configuration field MUST have a
  documented default that lets a setting configure only what it cares about.
- **FR-007**: A journey MUST be able to end before its declared distance is covered
  (abandoned, rerouted, interrupted), applying elapsed time and consequences for the
  distance actually travelled.
- **FR-008**: The elapsed-time and expected-value machinery a journey uses for its
  summarised legs MUST be the same mechanism `docs/design/18-campaign.md` already defines
  (`wyrd advance-time`), not a duplicate implementation.
- **FR-009**: The design document(s) introducing journeys MUST use setting-agnostic,
  descriptive English for every new label (per `CLAUDE.md`) — no term that only makes sense
  to someone who has read a specific source system.
- **FR-010**: The known engine gap recorded in `settings.yaml` (the `note:` referencing the
  missing journey subsystem) MUST be closed or restated to accurately reflect the delivered
  subsystem once this feature lands.

### Key Entities

- **Journey**: A travel-centred arc — a named route between two or more places, covering a
  distance or duration, decomposed into legs. Carries an optional pace, an optional ordered
  set of travel roles, and an optional hazard table.
- **Leg**: One step of a journey — either a played beat (run through the core roll) or a
  summarised span (advanced via elapsed time and expected-value events), per the existing
  played/summarised split.
- **Hazard entry**: One row of a journey's optional hazard table — a triggering condition
  and a resolution that routes through the core roll and an existing skill/difficulty.
- **Travel role**: An optional per-character assignment (e.g. navigating, foraging,
  standing watch) that a setting may attach meaning or mechanical effect to; the engine
  need only carry the assignment, not enforce what it does.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A journey between two places can be run end to end using only the rules as
  written in `design/`, with no undefined mechanic referenced along the way.
- **SC-002**: A setting that does not configure journeys shows zero behavioural difference
  from the engine's current narrated-travel handling — verified by re-reading
  `docs/design/18-campaign.md`'s existing elapsed-time section and confirming nothing there
  changed to accommodate the new subsystem.
- **SC-003**: Every hazard resolution inside a journey traces to the same core-roll mechanic
  used elsewhere in the engine — zero journey-specific resolution tables that bypass it.
- **SC-004**: The `settings.yaml` known-gap note about the missing journey subsystem is
  updated to reflect the shipped design, with no stale note remaining.

## Assumptions

- Journeys are engine (design-document) work in this repository, not setting content — no
  actual route, place names, or hazard tables for a specific setting are authored here; a
  setting overlay supplies those.
- "Roles" (navigator, forager, lookout etc.) are an optional structural slot the engine
  defines the shape of; assigning meaning or bonuses to a specific role is left to a
  setting's `rename:`/configuration layer, consistent with "engine labels are defaults;
  settings rename them."
- The anti-logistics preference already established for the material economy (Standing/gear
  work, ADR 0033) — abstracted supply over itemised inventory — extends to journeys: a
  journey may reference supply consumption but does not introduce per-item logistics
  tracking.
- A journey is authored the same way any other arc is: it may start as a stub and be
  converted lazily (`docs/design/28-arcs-and-beats.md`); this feature defines the shape, not a
  populated example.
- "Configurable and disablable per setting" (the issue's acceptance criterion) is satisfied
  by every journey field being optional with a documented default — no separate
  enable/disable flag is required if the subsystem is inert when unconfigured.
