# Feature Specification: Two-layer companions and a positive party track

**Feature Branch**: `027-two-layer-companions`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Two-layer companions and a positive party track" (issue #57)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a whole party without a stack of character sheets (Priority: P1)

The GM is running a beat with three companions present. Each needs to act, take a hit, and be
told apart from the others — but the GM cannot afford to track a fourth and fifth full character
sheet alongside the player's, session after session, for years. The design must say exactly what
a companion carries mechanically, and that set must be small enough to hold in the GM's head for
a whole party at once.

**Why this priority**: This is the whole reason a "two-layer" split is being specified rather
than just adding more fields to the existing single layer. Without a small, closed mechanical
set, every future feature that touches companions re-litigates what a companion is made of.

**Independent Test**: Given a companion record as currently defined
([`16-session.md`](../../docs/design/16-session.md)) plus whatever this feature adds, the mechanical
fields alone (excluding narrative prose fields) can be listed and counted, and that count stays
small enough to run three or four companions at once without consulting a separate sheet per
companion.

**Acceptance Scenarios**:

1. **Given** a companion who has never been detailed beyond their entry in the party, **When**
   the GM needs them to attempt something, act in a fight, or take a wound, **Then** every value
   the resolution needs is already present on the thin mechanical layer — nothing has to be
   invented or looked up on a separate sheet.
2. **Given** four companions with the party at once, **When** the GM is asked to distinguish them
   in play, **Then** the narrative layer (objective, flaw, secret, arc) does that work and the
   mechanical layer stays uniform and small across all four.

---

### User Story 2 - A party that is working well has something to show for it (Priority: P2)

Party Tension only rises. A GM running a chronicle where the player has been generous, present,
and has spent beats on companions' problems has no mechanical way to register that the party is
doing well — the track has a break condition and nothing pulling the other way beyond Tension's
own decay. The design must either give a functioning party a positive expression, or record why
that asymmetry is deliberate.

**Why this priority**: Named directly in the issue as one of two recorded gaps, and it is the
one with a real risk of colliding with the existing Bond mechanic if solved carelessly — solving
it is lower risk to get wrong than the companion split, but the reconciliation step is the part
most likely to produce a duplicate mechanic.

**Independent Test**: Given a chronicle where the player has consistently invested in the party
(spent beats on companions' problems, kept them fed and paid, not overruled their agendas), the
design names a concrete, observable difference in play from a chronicle where the player has not
— either through Bond's existing effects being confirmed sufficient, or through a new track.

**Acceptance Scenarios**:

1. **Given** the reconciliation with Bond is complete, **When** a GM reads
   [`16-session.md`](../../docs/design/16-session.md) end to end, **Then** exactly one mechanism is
   named as the party's positive expression, with no second, overlapping one left implied.
2. **Given** a functioning party over several sessions, **When** the GM checks what that
   investment has bought, **Then** the answer is traceable to a specific, defined effect — not a
   general sense that "things are going well."

---

### User Story 3 - Advancement and succession still make sense (Priority: P3)

`03-rules.md` already states that companions advance rarely and simply, and that a successor
inherits the position and none of the competence. Once the two-layer split and any positive
track are defined, those two sentences need to still be true of the completed model — not
merely left standing because nobody re-read them.

**Why this priority**: Lowest-risk of the three because it is confirmation rather than new
design, but it is where a subtle drift is most likely to hide (recurring fault #3 in
[`CLAUDE.md`](../../CLAUDE.md) — two documents describing one thing differently).

**Independent Test**: Read `03-rules.md`'s companion-and-succession passage and `04-session.md`'s
companion record side by side; every field either document mentions maps onto the same set with
the same meaning in both.

**Acceptance Scenarios**:

1. **Given** the completed two-layer model, **When** a companion advances at a downtime, **Then**
   the advance lands on the mechanical layer only, exactly as the existing "one competence gained
   or limitation lost" rule already describes.
2. **Given** a companion's death or departure and a succession, **When** the successor takes the
   position, **Then** the new companion starts with a fresh mechanical layer at its baseline and
   the narrative layer is written fresh for them — nothing mechanical carries over.

### Edge Cases

- A companion who has been detailed heavily in play (long secret, several arc beats resolved) but
  whose mechanical layer has never advanced — the split must not tempt a GM into inflating the
  mechanical layer to match the narrative one.
- A party with zero companions — the positive track's absence must not read as a broken or
  incomplete state; a solo player-character chronicle is legal.
- A companion whose Bond is already at the ceiling (+3) — if the positive track derives from
  Bond, the design must say what a further well-run party buys once Bond has nowhere left to
  rise.
- A companion who is present but at `status` other than `with-party` (away, captured) when the
  positive track would otherwise apply — must not silently count toward it, matching the existing
  rule that only `with-party` companions count for anything (`03-rules.md`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST define a companion's mechanical layer as a closed, named set of
  fields, distinct from the narrative fields the companion record already carries
  (`objective`, `flaw`, `secret`, `arc`).
- **FR-002**: The mechanical layer MUST be small enough that a GM can run a full party (up to the
  largest party size the design elsewhere countenances) without a per-companion character sheet —
  concretely, no field on the mechanical layer requires a roll or lookup the GM does not already
  perform for the player character in the same beat.
- **FR-003**: The design MUST NOT grant companions a capability score, skill percentage, or
  equivalent numeric competence rating of their own, preserving the existing rule that "the
  engine holds no capability score for a companion" (`03-rules.md`, danger-scaling section).
- **FR-004**: The design MUST either (a) define a positive party track — its trigger conditions,
  its effect, and how it interacts with existing Party Tension — or (b) record an ADR stating
  why Party Tension is deliberately one-directional and no positive track is added.
- **FR-005**: If a positive track is added, the design MUST reconcile it explicitly against Bond
  — either folding the positive expression into Bond's existing effects, or stating precisely how
  the new track differs from what Bond already does, so the two are never two names for the same
  thing.
- **FR-006**: The design MUST confirm, or correct, the existing statements that companions
  "advance rarely and simply — one competence gained or limitation lost at a downtime" and that
  "a successor inherits none of the competence and all of the position" (`03-rules.md`), against
  the completed two-layer model.
- **FR-007**: Every mechanic the design names for this feature MUST be defined where it is
  introduced, not merely referenced (per `CLAUDE.md`'s Definition of Done for this issue).
- **FR-008**: The design MUST contain no setting or system name, in keeping with the engine's
  setting-agnostic constraint (`CLAUDE.md`).
- **FR-009**: Where a claim in this feature has a computable answer (e.g. a bound on how many
  companions the mechanical layer scales to, or a probability the positive track implies), it
  MUST be computed and checked by a script rather than asserted by eye (`CLAUDE.md`, "Check the
  maths").

### Key Entities *(include if feature involves data)*

- **Companion, narrative layer**: the existing rich fields — `objective`, `flaw`, `secret`,
  `arc`, plus `career` and `bond` as they already stand. Answers "who is this person."
- **Companion, mechanical layer**: the closed set this feature defines — carries only what
  resolution actually consumes (e.g. `career`'s skill cap for tests they attempt, `strain`,
  `taint`, wound state on the same terms as the player character). Answers "what can this person
  do and what state are they in," and nothing else.
- **Party Tension** *(existing)*: the 0-6 track in `04-session.md`; this feature's positive
  track, if added, is a new entity or an extension of Bond — not a duplicate of Tension read
  backwards.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM reading the companion record definition can name every mechanical field on it
  from memory after one read, without cross-referencing a second document.
- **SC-002**: The design document contains exactly one mechanism presented as "what a
  well-functioning party earns" — never two competing candidates left standing at once.
- **SC-003**: `tools/check_docs.py` and any new feature-specific check script both pass, with the
  new check asserting the same closed-field-count and reconciliation claims this spec states, not
  merely eyeballing them.
- **SC-004**: `03-rules.md`'s companion-and-succession passage and `04-session.md`'s companion
  record, read together, use every field name in the same sense in both places.

## Assumptions

- The "largest party size the design elsewhere countenances" in FR-002 is read from
  `03-rules.md`'s existing effective-size table, which lists up to 6 bodies — the mechanical
  layer is judged against running 5 companions alongside the player character.
- Bond is the most likely home for the positive expression, since the issue itself names Bond as
  a candidate that "may already be the positive track under another name" — this spec does not
  presuppose the answer, but the reconciliation requirement (FR-005) is written expecting Bond to
  be seriously considered before any new track is invented.
- This feature is design-only: it changes `docs/design/03-rules.md`, `docs/design/16-session.md`, and
  possibly adds an ADR, plus a check script under `tools/` or `specs/027-two-layer-companions/`.
  It does not touch any setting repository or add runtime code beyond a verification script, in
  keeping with the engine/setting separation in `CLAUDE.md`.
- "Mechanical layer" fields already partly exist today (`career`, `bond`, `taint`, `strain`) —
  this feature's job is to name the set as closed and complete, not necessarily to invent new
  fields from nothing.
