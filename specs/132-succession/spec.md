# Feature Specification: Succession: successor selection and inheritance

**Feature Branch**: `132-succession`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Succession: successor selection and inheritance" (issue #340)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Successor candidates are ranked by entanglement, not affection (Priority: P1)

When a character's chronicle ends for them, the GM needs two or three successor candidates to
propose — ranked by how strongly the predecessor's own history entangles them, in the priority
order docs/design/19-campaign.md lays out: someone wronged, someone investigating, a bystander
whose life changed, a rival, whoever found what was left behind, and — least interesting — a
companion.

**Why this priority**: this ordering is the entire point the design document makes ("the
successor need not have liked the predecessor... an investigator who took the case... is a
better second act than any heir") — without it, nothing distinguishes this from picking any
convenient character.

**Independent Test**: given a list of candidate characters each carrying a declared
`entanglement` category, confirm they are ranked in exactly the design's stated priority order,
regardless of the order they were supplied in.

**Acceptance Scenarios**:

1. **Given** candidates carrying `wronged`, `rival`, and `companion` entanglements supplied in
   arbitrary order, **When** candidates are ranked, **Then** the returned order is `wronged`,
   `rival`, `companion` — the design's stated priority order.
2. **Given** two candidates with the same entanglement category, **When** candidates are
   ranked, **Then** their relative order is preserved (stable sort) — no arbitrary re-ordering
   within a tied category.
3. **Given** more than three ranked candidates, **When** the GM's proposal set is drawn,
   **Then** at most three are returned — "the GM proposes two or three candidates"
   (docs/design/19-campaign.md).

---

### User Story 2 - Inheritance follows the stated table exactly (Priority: P1)

Succession passes threads, enemies, active Threats, and what the world believes — never skills,
careers, Stamina, Fate, Taint, transformations, afflictions, or an assumption of goodwill.
Reputation is the sharpest inheritance and is carried across unlabelled (a fresh label starts,
but the old one's fact persists in the world). Holdings are never automatically passed on.

**Why this priority**: getting this table wrong in either direction breaks the design's central
claim — that succession makes a chronicle "about the situation that outlives everyone who
touches it", not a fresh character with borrowed stats.

**Independent Test**: given a predecessor's full state, confirm the successor's inherited state
contains exactly the inherited fields (unchanged) and none of the excluded ones, with holdings
absent unless explicitly passed through.

**Acceptance Scenarios**:

1. **Given** a predecessor with `threads`, `enemies`, `active_threats`, `world_belief`, `coin`,
   `skills`, `stamina`, `fate`, `taint`, `holdings`, **When** inheritance is computed, **Then**
   the result carries `threads`, `enemies`, `active_threats`, `world_belief` unchanged, and
   contains no `skills`, `stamina`, `fate`, `taint`, or `holdings` key at all.
2. **Given** a predecessor with a `reputation` field, **When** inheritance is computed,
   **Then** the successor's own reputation starts fresh (`None`/absent) while the predecessor's
   original `reputation` fact is preserved separately in the returned result (not silently
   dropped) — "the successor may spend years being mistaken for what their predecessor was."
3. **Given** an explicit decision that one particular holding reaches the successor, **When**
   inheritance is computed with that holding passed in, **Then** it is carried, marked
   encumbered — never carried by default from the predecessor's full holdings list.

---

### User Story 3 - The predecessor's post-succession state is recorded (Priority: P2)

Once succession happens, the predecessor doesn't simply vanish: lost means GM-controlled from
here on; died means a fact in the entity store with a rumour in the world that need not match
it; retired means findable, and may not want to be found.

**Why this priority**: without a recorded state, nothing distinguishes "this predecessor could
still appear in play" from "this predecessor is entirely gone" — three very different narrative
possibilities the design explicitly keeps open.

**Independent Test**: given each of the three predecessor outcomes, confirm the recorded state
carries the correct queryable marker and, for `died`, both a fact and a (possibly different)
rumour field.

**Acceptance Scenarios**:

1. **Given** outcome `lost`, **When** the predecessor's state is recorded, **Then** it is marked
   `status: "gm-controlled"`.
2. **Given** outcome `died`, **When** the predecessor's state is recorded with a fact and a
   rumour, **Then** both are present and independently queryable, and they are permitted to
   differ.
3. **Given** outcome `retired`, **When** the predecessor's state is recorded, **Then** it is
   marked `status: "findable"`.

### Edge Cases

- Fewer than three candidates are supplied (even zero) — ranking and proposal drawing both
  degrade gracefully, returning whatever exists (or an empty list), never erroring or padding
  with a fabricated candidate.
- A candidate with an entanglement category outside the design's six is rejected at ranking time
  — the vocabulary is closed, matching this codebase's established closed-vocabulary convention
  (ADR 0026's adversary traits).
- A predecessor with no `reputation` field at all inherits nothing reputation-shaped, and the
  successor's own reputation is simply absent — never a fabricated default.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST rank a list of candidate characters, each declaring an
  `entanglement` category, in the fixed priority order: `wronged`, `investigating`, `bystander`,
  `rival`, `found_evidence`, `companion` — a closed, six-member vocabulary.
- **FR-002**: Ranking MUST be stable within a tied entanglement category, and MUST reject a
  candidate whose `entanglement` is outside the six-member vocabulary.
- **FR-003**: The engine MUST provide a way to draw a proposal set of at most three ranked
  candidates.
- **FR-004**: The engine MUST provide a way to compute a successor's inherited state from a
  predecessor's, carrying `threads`, `enemies`, `active_threats`, and `world_belief` unchanged,
  and excluding `skills`, `careers`, `advances`, `stamina`, `fate`, `taint`, `transformations`,
  `afflictions`, and `holdings` entirely (never present, not merely emptied).
- **FR-005**: The predecessor's `reputation`, if present, MUST be preserved in the result
  separately from the successor's own (fresh/absent) reputation — never copied onto the
  successor directly.
- **FR-006**: A holding MUST reach the successor only when explicitly passed in for that
  purpose, and MUST be marked encumbered when it does — never inherited by default from the
  predecessor's full holdings list.
- **FR-007**: The engine MUST provide a way to record a predecessor's post-succession state for
  each of the three outcomes (`lost`, `died`, `retired`), each with its own queryable marker;
  `died` MUST carry an independently-settable fact and rumour, permitted to differ.

### Key Entities

- **Candidate**: a plain character dict carrying an `entanglement` field naming one of the six
  categories. This feature does not decide *how* a character came to carry that label — that is
  GM judgment during play, matching the separation `journey.py`/`threat.py` already keep between
  mechanical resolution and GM narration.
- **Inherited state**: `{threads, enemies, active_threats, world_belief,
  predecessor_reputation}` plus any explicitly-passed encumbered holding.
- **Predecessor record**: `{status: "gm-controlled" | "findable" | "died", fact?, rumour?}` —
  `fact`/`rumour` present only for `died`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Candidate ranking output order matches the design's stated priority exactly for
  every tested combination, and is stable on ties — verified by exact-input tests.
- **SC-002**: The inherited-state result never contains any excluded key, and always contains
  every included key that was present on the predecessor — verified by exact-input tests, not
  eyeballed.
- **SC-003**: A holding is present in the inherited result if and only if it was explicitly
  passed in, and is always marked encumbered when it is.
- **SC-004**: Each of the three predecessor outcomes produces its own distinct, correctly-shaped
  recorded state.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no I/O —
  matching every sibling module in this epic. Selecting *which* candidates exist in a chronicle
  and *what* entanglement each one carries (an entity-store-wide scan, and the GM judgment that
  assigns the label) is out of scope — this feature takes an already-labelled candidate list, the
  same boundary `threat.py`/`scenario_selection.py` keep for their own inputs.
- "At the table: succession is offered, never imposed... the player chooses or declines"
  (docs/design/19-campaign.md) is a play-time interaction this feature does not implement — it
  provides the ranked proposal set and the inheritance computation; presenting them to the
  player and recording their choice is session-orchestration, out of scope here (the same
  boundary #338's advance-time keeps toward its own callers).
- "Whoever found what you left behind" (the design's fifth-priority category) is represented as
  the `found_evidence` entanglement value — the design's own prose uses a longer phrase with no
  fixed identifier; `found_evidence` is chosen as the closest direct, unambiguous slug, matching
  every other engine-neutral vocabulary term already in this codebase (snake_case, no
  abbreviation).
- Reads `active_threats` as the shape `threat.active_threats` (#334) already produces, and
  `threads` as the shape `thread.py` (#335) already produces — no new shape is introduced for
  either; this feature only decides which of a predecessor's already-shaped fields carry across.
