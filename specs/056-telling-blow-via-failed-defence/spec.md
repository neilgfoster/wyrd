# Feature Specification: Clarify how telling blow is computed via a failed defence roll

**Feature Branch**: `156-telling-blow-failed-defence`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Clarify how telling blow is computed when a blow lands via a failed defence roll (closes #155, found during the playtest epic #134/#148). 03-rules.md sec2 says degrees are read exactly as sec1, but sec1's own convention means a failed defence roll -- the roll that lands the blow -- has no degrees at all under a literal reading, so a telling blow via defence failure appears to be impossible. check_conversion.py's own probability modelling for ADR 0028's damage-multiplier figures already assumes the symmetric case. Decide the rule and state a GM-followable per-roll procedure, checking whether ADR 0028's figures need re-deriving."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM can compute a telling blow from one specific failed defence roll, by hand (Priority: P1)

A GM running a fight needs to know, from a single natural roll the player just made, whether the
blow that lands via a failed defence is a telling blow — not an aggregate probability, one
specific number.

**Why this priority**: This is the whole gap #155 raised — the rule existed only as an implicit
assumption inside a probability script, unusable at the table.

**Independent Test**: Read `03-rules.md` §2's degrees bullets; confirm a GM given one failed
defence roll and the defender's effective% can compute a definite degrees value and telling-blow
result without consulting any script.

**Acceptance Scenarios**:

1. **Given** a defence roll `r` that fails against `eff_def`, **When** the GM applies the stated
   virtual-roll procedure, **Then** a definite degrees value results, checkable against the
   telling-blow threshold exactly as an attack roll would be.
2. **Given** the same procedure, **When** compared against `check_conversion.py`'s own aggregate
   modelling for the opponent's telling-blow rate, **Then** the two agree exactly, confirming the
   stated procedure is the one the existing modelling already assumed, not a new invention.

### User Story 2 - ADR 0028's published damage-multiplier figures are confirmed, not silently invalidated (Priority: P2)

Someone reading ADR 0028's figures wants confidence they still hold once this ambiguity is
resolved, rather than discovering later they were computed under an assumption the rules text
never actually stated.

**Why this priority**: A resolution that required re-deriving ADR 0028's figures would be a
materially bigger change than a documentation clarification; confirming they already hold is the
better outcome and needs to be shown, not asserted.

**Independent Test**: Read ADR 0044's Consequences section; confirm it states plainly whether
ADR 0028 needed re-deriving.

**Acceptance Scenarios**:

1. **Given** the resolved per-roll procedure, **When** compared computationally against ADR
   0028's own modelling, **Then** the two match exactly, so ADR 0028's figures stand unchanged.

### Edge Cases

- Does this change ADR 0028's own numbers? No — confirmed identical by computation
  (`check_defence_telling.py`), not re-derived.
- Does this playtest re-run §7's combat exchange? No — §7's own worked example is left as a
  historical record of the ambiguity as found, with a note pointing to the resolution, rather than
  rewritten to a different outcome.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` §2 MUST state explicitly whether a telling blow can trigger via a
  failed defence roll.
- **FR-002**: If yes, `03-rules.md` §2 MUST state a GM-followable per-roll procedure for computing
  degrees from one specific failed defence roll, not only an aggregate probability model.
- **FR-003**: The stated procedure MUST be verified computationally against
  `check_conversion.py`'s own existing aggregate modelling, not merely asserted to match.
- **FR-004**: The decision MUST record whether ADR 0028's damage-multiplier figures need
  re-deriving, with that check actually performed rather than assumed.
- **FR-005**: A real, workable rejected alternative exists (attack-only telling blow) with a
  genuine balance consequence, so this decision is recorded as an ADR.

### Key Entities

*(none — this feature is a rules clarification, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `03-rules.md` §2 states the per-roll procedure for a telling blow via a failed
  defence roll.
- **SC-002**: A new ADR records the decision, including the rejected attack-only alternative.
- **SC-003**: `specs/056-telling-blow-via-failed-defence/check_defence_telling.py` proves the
  stated procedure reproduces `check_conversion.py`'s own aggregate telling-rate exactly, across a
  spread of effective% values.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
  `python3 -m pytest -q` pass.

## Assumptions

- The symmetric (virtual-roll) reading is adopted, since it is what `check_conversion.py`'s own
  modelling for ADR 0028 already assumed — confirmed by exact computational match, not chosen
  arbitrarily.
- Documentation-only: no engine code changes; the verification script is a design artefact under
  `specs/`, matching this repo's established precedent.
