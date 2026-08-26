# Feature Specification: Oracle answer tables

**Feature Branch**: `025-oracle-answer-tables`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Oracle answer tables" (issue #20)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Settle a fact the fiction hasn't decided (Priority: P1)

Mid-scene, the GM needs an answer to a question nobody has established — "is the door locked?",
"did the guard notice?" — and inventing one on the spot risks a different fluent answer next
session. The GM instead rolls an oracle: states the question, judges how likely a yes is, rolls,
and reads the answer straight off the table.

**Why this priority**: This is the entire point of the family. Without it, the "oracle" filename
in the architecture stays an empty promise, and the GM keeps improvising unsettled facts twice.

**Independent Test**: Given a question and a likelihood band, rolling the table and reading the
row produces one of the defined outcomes with no judgment call left in it.

**Acceptance Scenarios**:

1. **Given** a question with no established answer, **When** the GM judges it roughly even odds
   and rolls the oracle, **Then** the roll resolves to exactly one row's outcome, with no
   remaining ambiguity about what happened.
2. **Given** the same question is asked again later in the chronicle, **When** the GM checks
   state first, **Then** the previously recorded answer is used and no new roll happens.

---

### User Story 2 - Weight a question that isn't a coin flip (Priority: P2)

Some questions are obviously more likely to be yes than no ("is the merchant still in business?")
or the reverse ("did the trap survive being triggered once already?"). The GM needs more than one
band of odds, or the oracle degenerates into a coin flip pretending to be a mechanic.

**Why this priority**: Without likelihood bands, the family can't carry the GM's judgment about
plausibility at all — every question would resolve at the same odds regardless of how loaded it
obviously is.

**Independent Test**: Rolling the same table under a different declared likelihood band changes
the probability of a "yes" outcome in the expected direction, and that probability can be computed
and checked, not just eyeballed.

---

### User Story 3 - Read the complication alongside the answer (Priority: P3)

An answer is sometimes accompanied by "and something else is true too" — the door's unlocked, but
it creaks. The GM needs to know whether that complication is a separate roll, a degree built into
the answer table itself, or the existing Wyrd die, so the mechanism isn't invented fresh each time
and doesn't quietly duplicate the Wyrd die's job.

**Why this priority**: Getting this wrong either bloats the table with a second die players never
asked for, or leaves complications unspecified and back to being improvised.

**Independent Test**: Given an oracle roll's total, the relationship to the Wyrd die (reused,
distinct, or absent) is stated as a fixed rule, not decided per-question.

---

### Edge Cases

- What happens when the GM is unsure which likelihood band applies? The document names the bands
  and gives enough examples that the choice is a judgment call bounded by clear anchors, not an
  open one.
- What happens when a question the oracle is bound to arises but the GM does not consult it? The
  document states plainly that this is not allowed — an oracle nobody is obliged to consult
  constrains nothing — and says which class of question triggers the obligation.
- What happens when the same question is asked in different words later? Recording is keyed to the
  question's substance as the GM records it, and the GM is responsible for recognising a repeat;
  the document does not require string-matching.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The document MUST define what an oracle is, in terms of the engine's determinism
  principle ([ADR 0005](../../doc/adr/0005-deterministic-over-inference.md)), distinguishing it
  from an ordinary GM narrative decision.
- **FR-002**: The document MUST state which class of in-fiction question is oracle-bound — the GM
  is obliged to roll rather than invent — and which the GM continues to simply decide.
- **FR-003**: `doc/design/01-principles.md` MUST agree with this obligation; if the existing GM
  contract does not already state it, this change amends that document rather than leaving the two
  in disagreement.
- **FR-004**: The document MUST define at least one answer table, addressed by the key
  `oracle-answer`, following the row schema and roll-declaration conventions of
  [`doc/design/07-tables.md`](../../doc/design/07-tables.md).
- **FR-005**: The table MUST support more than one likelihood band, so a GM's judgment that a
  question is more or less likely than even changes the odds of a "yes" outcome.
- **FR-006**: The table MUST express degrees of yes/no (e.g. a plain outcome and an extreme one)
  rather than a bare boolean, so a roll can carry more narrative weight than a coin flip.
- **FR-007**: Every outcome's probability, at every likelihood band, MUST be computed and shown in
  the document as a table of numbers, not asserted in prose.
- **FR-008**: The document MUST state explicitly whether an oracle roll also reads the Wyrd die
  (§1 of [`doc/design/03-rules.md`](../../doc/design/03-rules.md)), and if it adds any complication
  mechanism of its own, MUST say why that is not simply the Wyrd die.
- **FR-009**: The document MUST state what an oracle roll records to state and where, consistent
  with the versioning and recording conventions in `doc/design/07-tables.md` and
  [`doc/design/19-state.md`](../../doc/design/19-state.md), so the same question resolves the same way if
  asked again.
- **FR-010**: `doc/design/07-tables.md`'s index row for oracles MUST be updated to link the finished
  document and state its roll, in place of "not yet written".
- **FR-011**: `doc/design/02-architecture.md` and `doc/design/20-tooling.md` MUST be updated if the
  document's filename or the family's file layout differs from what those documents currently say.
- **FR-012**: No table row, example question, or label in the document MAY name a specific
  setting, a source system, or bake in a tonal register — verified by grep, per `CLAUDE.md`.

### Key Entities

- **Oracle**: a table family the GM rolls to answer a question the fiction has not yet settled,
  rather than inventing the answer, per [ADR 0005](../../doc/adr/0005-deterministic-over-inference.md).
- **Likelihood band**: a GM-declared judgment of how plausible a "yes" is before rolling, which
  shifts the table's odds without changing the roll or the table structure.
- **Oracle roll record**: the state entry an oracle roll writes, keyed so the same question
  resolves identically if asked again.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM (Claude, at play time) can resolve an unsettled yes/no question to a stable,
  recorded answer using only the document's table and no invented judgment about the outcome
  itself.
- **SC-002**: Every probability the document claims for the answer table is independently
  reproducible by computing it from the table's ranges — verified by a script, not read as
  asserted prose.
- **SC-003**: Grepping `design/` for setting or system vocabulary introduced by this change returns
  nothing.
- **SC-004**: A second GM reading only `doc/design/01-principles.md` and this document, with no other
  context, can state correctly whether a given example question obliges an oracle roll.

## Assumptions

- The answer table reuses the Wyrd die as its complication channel rather than inventing a second
  one, consistent with `doc/design/03-rules.md` §1's framing of the Wyrd die as the general "what else
  happened" channel; the document will state this explicitly per FR-008, and may reverse this
  assumption if reuse turns out to conflict with the table's own roll convention once the odds are
  computed.
- The table's die and modifier are declared by the family, per `doc/design/07-tables.md`'s convention
  that the roll is a per-family choice, not fixed by the engine.
- Likelihood bands are a fixed, small named set (not an arbitrary numeric slider) so the GM's
  choice at the table is bounded and auditable, matching how difficulty bands already work in
  `doc/design/03-rules.md` §1.
- The document lives at `doc/design/12-oracle-answers.md` per the issue's stated goal; the tables
  index's placeholder name `03a-5-oracles.md` is corrected to match once this document exists,
  since prompt oracles (#21) will need their own, separate file.
