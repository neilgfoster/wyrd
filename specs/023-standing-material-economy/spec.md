# Feature Specification: Standing and the material economy

**Feature Branch**: `023-standing-material-economy`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Define Standing and the material economy (#55) — Standing is
referenced in Upkeep and defined nowhere; the material economy (gear, wealth, encumbrance, the
casual/martial distinction) is sketched only as a setting file promise. Define both, or remove
what can't be defined, without turning play into inventory logistics."

## Clarifications

### Session 2026-08-26

- Q: Does Standing get a fixed numeric scale (like a percentile skill or a small 0–N track), or
  does it stay an open, uncapped count the way coin would? → A: A small open-ended count, not a
  percentile or a fixed 0–N band — consistent with how Taint/Trauma/Strain/Resolve are specified
  as accruing tracks rather than bounded scores in `03-rules.md`, and because Upkeep only ever
  moves it by 1 at a time. Planning MUST NOT invent a percentile Standing.
- Q: Is wealth ("coin") a numeric score the character tracks, or a narrative abstraction resolved
  case-by-case like inventory already is? → A: A numeric-but-small abstraction — coin is a plain
  count a player can state a total for (it is spent "equal to Standing" in Upkeep, which requires
  comparing two numbers), but it is not a ledger of transactions; the design does not ask the
  player to itemize purchases. This keeps FR-005/FR-006 from drifting into logistics.
- Q: Does the encumbrance rule need a concrete mechanical test (a roll, a threshold), or is it
  purely a GM judgment call? → A: GM judgment call, framed as a question the GM asks of the
  fiction ("would it make sense for them to have this"), the same shape `10-diegesis.md` already
  uses for "what is missing" — no roll, no threshold number. This bounds FR-006's scope for
  planning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upkeep resolves to a defined term (Priority: P1)

A player finishes a scenario away from home and enters Downtime. The Upkeep step reads "lose 1
Standing, or spend coin equal to Standing." The player, or the GM narrating on the engine's
behalf, needs to know what Standing *is* — what it represents, what raises and lowers it, and
what losing a point of it means at the table — without looking outside the engine's own design
documents.

**Why this priority**: This is the fault the issue exists to correct. Every other change is
downstream of deciding whether Standing survives.

**Independent Test**: Read `doc/design/16-session.md`'s Upkeep step cold, with no other document
open. Every term it uses resolves within the design docs.

**Acceptance Scenarios**:

1. **Given** a character has a Standing score, **When** Upkeep is paid away from home, **Then**
   the character either loses 1 Standing or spends coin equal to their current Standing, and both
   outcomes are defined in terms the design already establishes.
2. **Given** a character's Standing has changed (risen or fallen), **When** the GM narrates a
   social scene, **Then** the design states what about the scene Standing is meant to change —
   it is diegetic status, not a hidden number (`10-diegesis.md`).

---

### User Story 2 - A setting author can write a gear entry (Priority: P1)

A setting author opens `13-authoring-a-setting.md`, follows the promise of `gear.yaml`, and needs
to know exactly what fields a weapon or armour entry declares, so that combat's existing
mechanical dependencies (weapon damage dice, armour rank, the casual/martial distinction) have
something concrete to read.

**Why this priority**: `03-rules.md` already depends on gear mechanically today; this closes a
dependency the ruleset has been running on trust.

**Independent Test**: Author a small gear list (a few weapons, a few armour pieces) against the
schema alone, with no example to copy, and have it validate.

**Acceptance Scenarios**:

1. **Given** the gear schema, **When** a setting author writes a weapon entry, **Then** it
   declares at minimum: damage dice, damage type (one of the closed four), whether it is casual or
   martial, price, and availability/legality.
2. **Given** the gear schema, **When** a setting author writes an armour entry, **Then** it
   declares at minimum: armour rank (none/light/modest/heavy, matching `03-rules.md` §2), price,
   and availability/legality.
3. **Given** a gear entry with an invalid armour rank, an invalid damage type, or a missing
   required field, **When** it is validated, **Then** validation reports the specific problem
   (mirroring how the adversary block is validated today).

---

### User Story 3 - A player carries and pays for things without logistics (Priority: P2)

A player accumulates gear and coin over a chronicle. The design has already ruled out an
encumbrance table and an item list unless asked (`10-diegesis.md`). The player still needs to
know, when it matters narratively, whether they can carry something, and what having money — or
not having it — changes about a scene, without either party doing inventory bookkeeping.

**Why this priority**: This is what keeps the first two stories from reintroducing the logistics
the diegesis document already rejected. It depends on Standing and gear existing first.

**Independent Test**: Walk through a scene where a character needs to decide whether they can
plausibly be carrying something, and a scene where wealth is spent, using only the rule this
feature defines — no table lookup, no running total the player is asked to maintain.

**Acceptance Scenarios**:

1. **Given** a character's stated gear and the scene's fiction, **When** the question "can they
   plausibly be carrying this" comes up, **Then** the engine gives the GM a rule to answer it that
   does not require a numeric encumbrance total.
2. **Given** a character has coin and/or Standing, **When** they want to buy, bribe, or requisition
   something, **Then** the design states what determines whether they can, in terms that don't
   require a tracked currency ledger unless the setting supplies one.

---

### User Story 4 - The casual/martial distinction has mechanical teeth (Priority: P3)

A player is carrying a martial weapon in a civilised setting. The design currently states this is
socially costly but not what, mechanically, that costs them.

**Why this priority**: Named in the issue's scope as needing confirmation; smallest and most
self-contained of the four threads, and the one most likely to already be adequately covered by
existing social/Standing mechanics once those are defined.

**Independent Test**: Given a character openly carrying a martial weapon in a setting that
forbids it, the design states a concrete consequence path (a test, a Standing effect, an
encounter trigger) rather than only a sentence of flavour text.

**Acceptance Scenarios**:

1. **Given** a character carries a martial weapon somewhere it's illegal, **When** that becomes
   visible in a scene, **Then** the design names what happens next in mechanical terms (not only
   "this has social consequences").

### Edge Cases

- What resolves Upkeep when a character has *no* Standing left to lose and no coin to spend?
- What does a Standing score start at for a new character, and does it cap the way careers now do
  (career caps, #12, already landed — see `03-rules.md` §6)?
- Does Standing move at times other than Upkeep — e.g., as a consequence of a scene, the way
  Taint or Trauma do?
- A setting with no formal currency at all (barter, favours) — does the wealth abstraction still
  work, or does it require `gear.yaml` prices to mean something?
- A character who owns gear far beyond what any scene could plausibly need them to justify
  carrying — does the "realistic, not logistic" rule still resolve cleanly, or does it need a
  named boundary (e.g., a home/stash distinction)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST define Standing — what it represents, its starting value, what
  raises and lowers it, and how it is rendered to the player (diegetically, per
  `10-diegesis.md`) — or MUST remove every reference to it and rewrite Upkeep in terms
  that are otherwise defined.
- **FR-002**: If Standing is kept, the design MUST state what losing Upkeep's "1 Standing" costs
  the character in play — not merely that the number changes.
- **FR-003**: The design MUST specify a gear entry schema covering weapons (damage dice, damage
  type from the closed four, casual/martial, price, availability/legality) and armour (rank,
  price, availability/legality), consistent with the fields `03-rules.md` §2 and
  `03d-the-adversary.md` already assume.
- **FR-004**: The design MUST provide (or point to) a validator for a gear file against that
  schema, consistent with how the adversary block is validated today
  (`doc/design/06-the-adversary.md`).
- **FR-005**: The design MUST state how wealth works — a small numeric count of coin the player
  can state a total for, without itemized transaction tracking — and MUST reconcile it explicitly
  with Standing (are they the same resource, do they interconvert, are they independent).
- **FR-006**: The design MUST specify encumbrance as a GM judgment call against the fiction (the
  same shape `doc/design/23-diegesis.md` already uses for what a character is missing), not as a roll
  or a numeric threshold, and that specification MUST NOT require the player or GM to maintain a
  numeric running total or consult an item-weight table.
- **FR-007**: The design MUST state a concrete mechanical consequence (not only social framing)
  for carrying a martial weapon somewhere it's restricted, or MUST show that an existing mechanic
  (e.g. a Standing effect, an encounter rule) already covers it and cite where.
- **FR-008**: Every mechanic this feature touches MUST use a setting-agnostic engine label, per
  `CLAUDE.md` — no source-system term, and any setting-specific flavour goes in a setting's
  `rename:` block, not into `design/`.
- **FR-009**: Wherever this feature's rules depend on a number (e.g. a starting Standing value, a
  price band, a threshold for "too much to plausibly carry"), that number MUST be computed or
  justified against the existing numeric conventions in the ruleset (e.g. `03-rules.md`'s damage
  and armour figures), not asserted by feel.

### Key Entities

- **Standing**: a character's score for social position/reputation, spent or lost as part of
  Upkeep, rendered diegetically rather than as a raw number.
- **Gear entry**: a weapon or armour item as declared in a setting's `gear.yaml` — carries
  damage/armour stats, a legality/casual-martial marker, and a price.
- **Wealth**: however the design resolves "what a character can pay with" — may be Standing
  itself, a separate coin abstraction, or both, reconciled by this feature.
- **Encumbrance rule**: the (non-numeric) rule for whether a character can plausibly be carrying
  something, given their gear and the scene's fiction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every use of "Standing" across `design/` resolves to a defined term — zero
  remaining undefined mechanic references, checked by `python3 tools/check_docs.py` and by grep.
- **SC-002**: A setting author can write a complete, valid `gear.yaml` weapon and armour entry
  using only the schema this feature defines, without consulting an existing setting for an
  example.
- **SC-003**: The Upkeep step in `doc/design/16-session.md` requires no document outside `design/` to
  fully resolve.
- **SC-004**: The GM can answer "can this character plausibly be carrying that" and "what does
  this cost them" in a live scene without pausing to look up a number, consistent with
  `doc/design/23-diegesis.md`.

## Assumptions

- Standing is worth keeping rather than removing — the issue's own framing ("define... or
  remove") leaves both open, but Standing already does real narrative work in Upkeep and is the
  natural anchor for the casual/martial social consequence (User Story 4), so this spec assumes
  definition over deletion. If clarification finds otherwise, Upkeep is rewritten instead.
- Wealth is modelled as an abstraction reconciled with Standing rather than as a tracked numeric
  currency by default — a setting that wants a harder currency simulation can still declare prices
  in `gear.yaml` and layer a ledger via its own rules overlay, per
  `13-authoring-a-setting.md`'s `rules/` mechanism.
- This feature does not design a full trade/economy simulation (markets, supply, haggling
  mechanics) — only what a character owns, what it's worth, and what having or lacking it costs
  them at the table, per the issue's stated goal.
- The gear schema and validator follow the same shape as the adversary block's schema/validator
  (`doc/design/06-the-adversary.md`, `03d-the-adversary.md` §validation) rather than inventing a new
  validation convention.
