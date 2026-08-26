# Feature Specification: The Aftermath table

**Feature Branch**: `002-aftermath-table`

**Created**: 2026-08-22

**Status**: Draft

**Input**: GitHub issue #16 — "The Aftermath table". Define the Aftermath table family in its own
design document, conforming to the conventions established by #15 (`doc/design/07-tables.md`), so that
a combatant who drops in combat can be resolved without a judgement call the rules do not cover.
Out of scope: Stamina recovery and whether lasting wounds ever heal (R1.2 of epic #1).

## Context

`doc/design/03-rules.md` defers all combat death to a table that does not exist:

> **Death is deferred.** Nothing resolves during the fight; a combatant who drops is *out of
> action*. Afterwards, roll on the **Aftermath** table. Most results are a lasting mark rather than
> death — a permanent wound, a new enemy, capture, a disfigurement that frightens people, a wound
> that recurs before every future fight.

Five outcome shapes are promised in that sentence and none exists. This is the load-bearing table in
the engine: deferred resolution is the whole reason a single-character chronicle survives lethal
combat, and every other document that mentions mortality — the tone contract's `mortality` knob
(`doc/design/01-principles.md`), the bootstrap question "how lethal?" (`doc/design/29-chronicle-bootstrap.md`),
the setting-authoring conversion surface (`doc/design/26-authoring-a-setting.md`) — points at a table
whose rows nobody has written.

It is also a hard gate. R1.2 of epic #1 (Stamina recovery, and whether lasting wounds ever heal)
cannot be specified until this lands, because "lasting wound" currently has no definition to give a
fate to. `doc/design/19-state.md` already carries a `wounds: []` field on the player character with no
schema behind it.

Sibling dependency #15 has merged, so the conventions this family must satisfy — the row schema, the
contiguous-ranges-with-an-open-top rule, the uniqueness declaration, the override contract — are
fixed and are not re-litigated here.

## Clarifications

### Session 2026-08-22

- Q: Issue #16 names `design/03a-1-aftermath.md`, but the index #15 merged assigns `03a-1-` to
  criticals and `03a-2-` to aftermath. Which wins? → A: The index. The document is
  `doc/design/09-aftermath.md`; the issue's path is stale and the issue is corrected rather than the
  index renumbered.
- Q: Does a character who spends Fate to avoid a death result still take an Aftermath result? → A:
  Yes. Fate closes the death rows only; the result is re-read on the worst non-death row, so the
  character survives and is demonstrably not better off. Fate never suppresses the roll.
- Q: Do companions roll on this table? → A: Yes — the same table, the same modifier, the same rows.
  The only difference is that companions have no Fate of their own, so a death row stands unless the
  player is present and spends Fate for them.
- Q: What does the family roll and what modifies it? → A: `d100 + (5 × points below zero)`.
  Percentile matches the rest of the engine and lets a setting tune finely; the modifier reuses the
  number the ruleset already computes for the critical.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolving a player character who dropped (Priority: P1)

A fight ends. The player character took a critical that put them below 0 Stamina and has been *out
of action* since. The GM now resolves what that cost, by rolling the family's die, applying its
modifier, reading one row, and applying that row's effect to state — with no point at which the
rules run out and the GM has to invent an answer.

**Why this priority**: This is the sentence `doc/design/03-rules.md` already makes and cannot currently
honour. Without it the ruleset has a hole at its most consequential moment.

**Independent Test**: Take a character who dropped to −3 Stamina, roll the declared die, and follow
the document alone to a single row, a single applied effect, and a single recorded outcome. No step
should require a judgement the document does not cover.

**Acceptance Scenarios**:

1. **Given** a combatant who dropped below 0 Stamina during a fight, **When** the fight ends,
   **Then** the Aftermath table is rolled once for that combatant, and not before the fight ends.
2. **Given** any legal total the family's die and modifier can produce, **When** the row is looked
   up, **Then** exactly one row contains that total — including totals far above the table's
   nominal top, which the open-topped last row absorbs.
3. **Given** a rolled row, **When** its effect is applied, **Then** every mechanic the effect names
   already exists in the engine, or is defined by this feature.
4. **Given** a resolved Aftermath roll, **When** the outcome is recorded, **Then** the record
   carries the table's key alongside the engine version, per `doc/design/07-tables.md`.

---

### User Story 2 - A lasting wound that later mechanics can read (Priority: P1)

A character walks away from a fight permanently marked. That mark has to be a thing state can hold,
that a later session can render diegetically, and that R1.2 can eventually give a recovery rule to.

**Why this priority**: `doc/design/19-state.md` already declares `wounds: []` with nothing defining an
entry. This is the gate on R1.2, and a wound that exists only in prose cannot be given a fate.

**Independent Test**: Apply a lasting-wound result and write the resulting entry into a character's
`wounds` list; confirm every field a later recovery rule would need to key on is present, and that
nothing in the entry is a description masquerading as an effect.

**Acceptance Scenarios**:

1. **Given** a row whose effect is a lasting wound, **When** it is applied, **Then** a structured
   wound record is added to the character's `wounds` list.
2. **Given** a wound record, **When** it is rendered for the player, **Then** it is rendered
   diegetically per `doc/design/23-diegesis.md` — never as a raw score.
3. **Given** a wound record, **When** a future rule needs to ask whether it has healed, **Then** the
   record carries enough structure for that question to be asked, even though this feature does not
   answer it.

---

### User Story 3 - A wound that recurs before every future fight (Priority: P2)

One promised outcome is not a one-off result at all: it is an ongoing effect that surfaces again
every time the character fights, for the rest of the chronicle.

**Why this priority**: It is one of the five shapes `doc/design/03-rules.md` promises, and it is the one
most likely to be written as flavour and quietly never applied.

**Independent Test**: Give a character a recurring wound, then start three separate fights and
confirm the same stated mechanical effect fires at the start of each, with no per-fight GM judgement
required.

**Acceptance Scenarios**:

1. **Given** a character carrying a recurring wound, **When** a fight begins, **Then** the wound's
   stated mechanical effect is applied at a stated moment, deterministically.
2. **Given** a character carrying a recurring wound, **When** no fight is occurring, **Then** the
   wound imposes nothing.

---

### User Story 4 - Fate spent against a death result (Priority: P1)

The player character rolls a death result and the player spends a Fate point. Two mechanics both
claim this moment: Fate says the character *survives and is not better off*, and Aftermath says what
dropping cost. The boundary between them has to be stated, because a reader can currently construct
two contradictory readings from the two documents and neither looks wrong.

**Why this priority**: An unstated interaction between the death valve and the death table is the
exact fault class `CLAUDE.md` names as hardest to see — two documents describing one thing
differently, both internally coherent.

**Independent Test**: Roll a death result for a character with Fate remaining, spend it, and follow
both documents to a single unambiguous outcome.

**Acceptance Scenarios**:

1. **Given** a death result and a spent Fate point, **When** the outcome resolves, **Then** the
   character survives and is demonstrably *not better off* — consistent with
   `doc/design/03-rules.md` section 3.
2. **Given** a death result and a spent Fate point, **When** the outcome resolves, **Then** the
   result is re-read on the worst non-death row and that row's effect is applied — the roll is not
   suppressed, and the character does not walk away unmarked.
3. **Given** a character with no Fate, or a player who declines to spend it, **When** a death result
   comes up, **Then** the death stands — per the GM contract in `doc/design/01-principles.md`.

---

### User Story 5 - A companion who dropped (Priority: P2)

A companion goes down. Companions have no Fate of their own and are the engine's declared reliable
source of loss. Whether they take the same table, a harsher reading of it, or a different resolution
entirely is a real decision with real consequences for how a chronicle loses people.

**Why this priority**: `doc/design/03-rules.md` and `doc/design/01-principles.md` both make load-bearing
claims about companion mortality; leaving this unstated leaves both under-determined.

**Independent Test**: Resolve a dropped companion using the document alone and confirm no step
requires reading the player-character rules and guessing whether they transfer.

**Acceptance Scenarios**:

1. **Given** a companion who dropped, **When** the fight ends, **Then** the Aftermath table is
   rolled for them on the same terms as for the player character — same rows, same modifier — and
   the document says so explicitly rather than leaving it to inference.
2. **Given** a companion facing a death result and a player present and able to act, **When** the
   player spends Fate for them, **Then** the companion survives and is not better off, per
   `doc/design/03-rules.md`'s existing rule for spending Fate for someone else.
3. **Given** a companion who dies, **When** state is updated, **Then** their `status` moves to a
   value `doc/design/19-state.md` already declares.

### Edge Cases

- **A total far above the table's top.** The modifier is derived from how far below zero the
  combatant dropped, which is unbounded — a hard enough blow runs off any table with a highest row.
  The open-topped last row must absorb it.
- **The lowest possible total.** Ranges must begin at the family's genuine lowest total, not at 1 by
  habit. That lowest total is a computed number, not an assumed one.
- **The same result twice.** The family must declare itself repeatable or unique-per-character, and
  if unique, declare what happens when a character has taken every result.
- **A character who drops more than once in one fight.** Whether that is possible, and if so whether
  it produces one Aftermath roll or several, must not be left to inference.
- **Multiple combatants down at the end of one fight.** Resolution order must not change any
  individual outcome.
- **A "new enemy" result.** The enemy has to become something the world can act with, not a note —
  `doc/design/27-entities.md` already fixes what a `character` with `role: nemesis` carries, including an
  `objective` block that advances while the player is elsewhere.
- **A "capture" result.** Capture removes a character from the party without killing them; what
  state records that, and what open loop the chronicle carries as a result, must be stated.
- **A "disfigurement that frightens people" result.** The engine already has **Dread** for exactly
  this; a new parallel mechanic would be a second description of one thing.
- **`mortality: low` or similar settings.** `doc/design/01-principles.md` says the tone contract governs
  "how the Aftermath table is applied". That claim must either be honoured by this feature or
  corrected, not left dangling.

## Requirements *(mandatory)*

### Functional Requirements

**The table itself**

- **FR-001**: The engine MUST define the Aftermath family in `doc/design/09-aftermath.md`, one table
  to the file, named for the family's key, at the path the tables index already reserves for it.
- **FR-002**: The document MUST declare the family's roll as **`d100 + (5 × points below zero)`**,
  explicitly, per `doc/design/07-tables.md`'s rule that the roll belongs to the family and not to the
  engine.
- **FR-003**: The modifier MUST be derived from the points below zero the ruleset already computes
  for the critical, so a worse blow reads further down the table. A combatant who dropped by 1 and
  one who dropped by 12 MUST NOT face the same distribution.
- **FR-004**: Ranges MUST be contiguous, non-overlapping, begin at the family's lowest possible
  total — which is **6**, since points below zero is at least 1 and `d100` is at least 1 — and end
  in a row open at the top.
- **FR-005**: Every row MUST carry the three fields the row schema requires — range, effect,
  description — with effect stated in a form applicable without reading the prose.
- **FR-006**: The family MUST declare itself repeatable or unique-per-character, and if unique MUST
  declare its exhaustion outcome.
- **FR-007**: The document MUST declare any extra field the family's rows carry, or state that it
  declares none. A field no rule reads MUST NOT be introduced.

**Coverage of what the ruleset already promises**

- **FR-008**: The table MUST carry at least one row for each of the five outcome shapes
  `doc/design/03-rules.md` names: a permanent wound, a new enemy, capture, a disfigurement that
  frightens people, and a wound that recurs before every future fight.
- **FR-009**: The table MUST carry death at its extreme, in its highest rows, consistent with the
  ruleset's existing statement that high results are lethal.
- **FR-010**: The table MUST be weighted so that a lasting mark is the common outcome and death is
  the uncommon one — the ruleset already claims "most results are a lasting mark rather than death",
  and that claim MUST be true of the rows as written.

**The lasting-wound record**

- **FR-011**: The engine MUST define the structure of an entry in the character's existing `wounds`
  list, sufficient for a later rule to identify a wound, apply its effect, and ask whether it has
  healed.
- **FR-012**: A wound's mechanical effect MUST be separable from its description, so a setting can
  rewrite the words without changing what the wound does.
- **FR-013**: The wound record MUST NOT presuppose any particular recovery rule, since whether
  wounds heal is R1.2's decision.

**The recurring wound**

- **FR-014**: The recurring-wound result MUST state a mechanical effect, the moment it fires, and
  its duration, such that it can be applied without GM judgement at every future fight.
- **FR-015**: The recurring wound MUST reuse an existing engine mechanic where one fits, rather than
  introducing a parallel one.

**Interactions**

- **FR-016**: Spending Fate MUST close the table's death rows to that character rather than
  suppressing the roll. The result MUST be re-read on the worst non-death row the table holds, so
  the character survives and carries a lasting mark — Fate's existing guarantee that they are *not
  better off*, made mechanical. Fate MUST NOT be spendable to improve a non-death result.
- **FR-017**: Companions MUST roll on the same table, with the same modifier and the same rows. The
  only difference MUST be that companions have no Fate of their own, so a death row stands unless
  the player is present, able to act, and spends Fate for them per `doc/design/03-rules.md` section 3.
  No companion-specific rows, modifier or table may be introduced.
- **FR-018**: A "new enemy" result MUST create an entity conforming to `doc/design/27-entities.md`, not
  a free-text note.
- **FR-019**: A "disfigurement" result MUST feed the engine's existing Dread track rather than
  introducing a second social-consequence mechanic.
- **FR-020**: The document MUST state what the tone contract's `mortality` value changes about how
  this table is applied, honouring the claim `doc/design/01-principles.md` already makes.

**Consistency with the rest of `design/`**

- **FR-021**: `doc/design/03-rules.md` MUST link to the new document and MUST NOT continue to describe
  the table as though it were undefined.
- **FR-022**: The tables index in `doc/design/07-tables.md` MUST have its Aftermath row completed — its
  roll and uniqueness stated, and its "not yet written" placeholder replaced with a link.
- **FR-023**: Any other design document whose description of Aftermath this feature changes MUST be
  updated in place, describing the present, with no changelog or "previously we…" note.

**Repository constraints**

- **FR-024**: No setting name, system name, or term borrowed from a source system may appear in any
  added or changed file, verified by grep rather than asserted.
- **FR-025**: No row may bake in a tonal register — grim, heroic or comic. Descriptions state what
  happened, and the setting supplies the register.
- **FR-026**: Every probability or frequency claim made about the table MUST be computed by a script
  and checked against the rows as written, not asserted.
- **FR-027**: A decision recorded here that rejected a workable alternative someone would plausibly
  propose again MUST earn an ADR in `doc/adr/`.
- **FR-028**: `specs/002-aftermath-table/` MUST be committed.

### Key Entities

- **Aftermath table**: the family's single table. Carries a key, a declared die, a declared modifier
  source, a uniqueness declaration, and an ordered list of rows.
- **Aftermath row**: range, effect, description — plus any extra field the family declares.
- **Wound record**: an entry in a character's existing `wounds` list. Identifies the wound, carries
  its mechanical effect separately from its description, and is legible to a later recovery rule.
- **Recurring wound**: a wound record whose effect fires at the start of every future fight rather
  than once.
- **New enemy**: a `character` entity per `doc/design/27-entities.md`, with a role, a disposition and an
  objective that advances while the player is elsewhere.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given only the new document and a dropped combatant can reach a single
  applied outcome with zero judgement calls the document does not cover — for every one of: the
  lowest possible total, a mid-table total, a death-row total, and a total far above the table's
  nominal top.
- **SC-002**: All five outcome shapes named in `doc/design/03-rules.md` are covered by at least one row
  each, and a grep of that sentence against the table finds no promise without a row.
- **SC-003**: A script confirms the ranges are contiguous, non-overlapping, start at the computed
  lowest possible total, and end open at the top — no total is unanswered and none is answered
  twice.
- **SC-004**: A script computes the outcome distribution and confirms the ruleset's existing claim
  that most results are a lasting mark rather than death holds for the rows as written, across the
  realistic range of modifiers a character actually experiences — not only at the midpoint.
- **SC-005**: The Fate interaction and the companion question each resolve to exactly one reading
  when the new document and `doc/design/03-rules.md` are read against each other.
- **SC-006**: A grep over all added and changed files returns no setting name and no system name.
- **SC-007**: `doc/design/07-tables.md`'s index has no remaining "not yet written" placeholder in the
  Aftermath row, and every cell in that row matches what the new document actually declares.
- **SC-008**: R1.2 can be specified against the wound record as defined, without needing a further
  decision from this feature.

## Assumptions

- **The document is `doc/design/09-aftermath.md`, not `design/03a-1-aftermath.md`.** Issue #16 names
  the latter, but it was written before #15 merged; the index that #15 established assigns `03a-1-`
  to criticals and `03a-2-` to aftermath. Per `CLAUDE.md`, where a spec and a design document
  disagree the design document is the engine's description, so the index wins and the issue's path
  is treated as stale. Confirmed by the operator (see Clarifications); issue #16's acceptance
  criteria should be corrected to match rather than the index renumbered.
- **This feature is design-only.** There is no `engine/` directory in the repository yet, so
  `engine/tables/aftermath.yaml` is not created here even though `doc/design/07-tables.md` states where
  engine tables will live. The design document is the deliverable; the data file follows when the
  engine does. Verification scripts written for SC-003 and SC-004 are checks against the document,
  not engine code.
- **The conventions from #15 are settled and are not re-opened.** This feature declares within them.
  If a convention genuinely cannot accommodate the Aftermath family, that is a finding to raise
  against #15's document, not a local exception.
- **Recovery is out of scope.** This feature defines what a lasting wound *is*; R1.2 decides whether
  it ever heals. Wording that presupposes an answer either way is a defect.
- **Criticals remain a separate family.** The critical table (rolled during the fight, per damage
  type) and the Aftermath table (rolled after it) are distinct; this feature defines only the
  latter, but must state their relationship clearly enough that the sibling issue writing criticals
  does not contradict it.
- **Existing mechanics are reused rather than duplicated.** Dread for social consequence, Trauma for
  mental cost, the `wounds` list for physical marks, `character`/`thread` entities for enemies and
  open loops, companion `status` values for loss. A new parallel mechanic requires justification.
