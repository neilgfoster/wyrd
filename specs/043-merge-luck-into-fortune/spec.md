# Feature Specification: Merge Luck into Fortune

**Feature Branch**: `043-merge-luck-into-fortune`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Merge Luck into Fortune (drop the separate arc-scoped Luck mechanic) (closes #137). Operator decision after reviewing the two live alternatives: merge Luck into Fortune. Fortune (daily, reroll/defend/act sooner) covers its ground."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader no longer meets a naming collision between Fate's renames and Luck's own name (Priority: P1)

Someone reading `03-rules.md`'s engine-labels table sees "Fate" → "Fate · Luck · Destiny" as
rename examples, then later in the same document meets "Luck" again as the formal name of a
completely different mechanic. That collision is gone.

**Why this priority**: This is the hard problem #137 raised — not just unclear differentiation,
but an actual internal contradiction between two uses of the same word in one document.

**Independent Test**: Grep `docs/design/` for "Luck" and confirm no hits remain.

**Acceptance Scenarios**:

1. **Given** `docs/design/03-rules.md`'s engine-labels table, **When** read for Fate's rename
   examples, **Then** none of them is "Luck."
2. **Given** the whole `docs/design/` corpus, **When** grepped for "Luck", **Then** no reference
   to a standalone Luck mechanic remains.

### User Story 2 - A player's resource economy is simpler, with nothing they could previously do made impossible (Priority: P1)

A player who used to test Luck to dodge a misfortune or break a tie can still do that — by
spending a Fortune point instead. Nothing they could do before is gone; one fewer number to track.

**Why this priority**: The operator's own framing of the merge decision — Fortune "covers its
ground" — means this is a consolidation, not a removal of capability.

**Independent Test**: Read Fortune's spend list in `03-rules.md` and confirm "dodge a misfortune"
and "break a tie" both appear.

**Acceptance Scenarios**:

1. **Given** `docs/design/03-rules.md`'s Fate-and-Fortune section, **When** read, **Then**
   Fortune's spend list includes reroll, defend again, act sooner, dodge a misfortune, and break
   a tie.
2. **Given** character creation, **When** a new character is created, **Then** they receive
   Fortune (equal to Fate, renewed daily) and no separate Luck value.

### User Story 3 - Every document that mentioned Luck as a resource is corrected, not just the primary rules document (Priority: P2)

Someone reading any of `10-the-character.md`, `11-character-creation.md`, `12-the-adversary.md`,
`13-diegesis.md`, `19-campaign.md`, or `30-playtest-transcript.md` finds no reference to Luck as
a distinct resource, consistent with `03-rules.md`.

**Why this priority**: A merge that fixes the primary document but leaves six others describing
the old three-resource model is exactly the "two documents describing one thing differently"
fault #92's cross-reading pass exists to catch — this feature must not reintroduce it.

**Independent Test**: `python3 tools/check_dangling_mechanics.py` shows no new reference to
"Luck", and a manual grep of `docs/design/` confirms zero hits.

**Acceptance Scenarios**:

1. **Given** each of the six documents listed above, **When** read, **Then** none mentions Luck
   as a resource distinct from Fortune.
2. **Given** `docs/design/11-character-creation.md`'s numbered creation steps, **When** the Luck
   step is removed, **Then** every subsequent step number and every cross-reference to a step
   number elsewhere in that document is renumbered consistently.

### Edge Cases

- What happens to ADR 0039 (Luck resets at the top-level arc boundary), an accepted record?
  Never edited — moved to `docs/adr/superseded/`, keeping its number permanently, with only its
  `Status:` line changed to point at the new ADR, per the consolidation rule ADR 0012
  established. Its reasoning (why an arc-scoped reset made sense for Luck) remains an accurate
  historical record of a decision this feature supersedes, not something rewritten.
- What happens to ADR 0014's "Stamina 6, Luck 40" line — also accepted, also never edited? Left
  exactly as written; it accurately recorded the design at the time it was written. The new ADR
  notes the supersession without touching ADR 0014's text.
- What happens to `specs/008-character-creation/check_creation.py`'s Luck-computation section?
  Left unmodified — a committed spec is historical record too (CLAUDE.md), and this section
  documents the reasoning behind a decision this feature supersedes, not a currently-live claim
  the repo's tooling would assert against a doc that no longer states it.
- Does the ADR sequence get renumbered to close the gap left by 0039 moving to the archive? No —
  ADR 0012 explicitly authorised a one-time renumber only *during* the design programme's Stage
  13, and explicitly forbids renumbering outside it ("afterwards the normal rule resumes,
  unchanged"). Stage 13 (#52) is now closed, so the normal rule applies: the live sequence simply
  has a gap where 0039 used to be, and the new record takes the next free number (0041).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Luck MUST NOT exist as a mechanic distinct from Fortune anywhere in `docs/design/`.
- **FR-002**: Fortune's spend list MUST cover what Luck previously covered (dodge a misfortune,
  break a tie), without introducing a new resource, pool, or refresh cadence.
- **FR-003**: The Fate rename table's collision with "Luck" MUST be resolved.
- **FR-004**: `docs/design/11-character-creation.md`'s creation procedure MUST drop the Luck step
  and renumber every subsequent step and cross-reference consistently.
- **FR-005**: A new ADR MUST supersede ADR 0039 in full, following ADR 0012's consolidation rule
  (move to `docs/adr/superseded/`, status-only edit, both indexes updated) — never editing an
  accepted record's reasoning.
- **FR-006**: `docs/adr/0014-character-creation-is-chosen-not-rolled.md` MUST NOT be edited; the
  new ADR records the partial supersession of its Luck-related content in its own text instead.
- **FR-007**: `specs/008-character-creation/check_creation.py` MUST NOT be edited — its Luck
  section is historical record of superseded reasoning, not a live claim.

### Key Entities

*(none — this feature removes a resource, it adds no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `grep -rn "Luck" docs/design/` returns zero matches.
- **SC-002**: `python3 tools/check_docs.py` passes (link/index integrity, including the new and
  moved ADRs).
- **SC-003**: `python3 tools/check_dangling_mechanics.py` shows no new dangling reference.
- **SC-004**: `python3 tools/check_probability_coverage.py` passes (the Stamina/8-advance backing
  script this feature doesn't touch keeps working).
- **SC-005**: `python3 -m pytest -q` passes with no regression.
- **SC-006**: Every step-number cross-reference within `docs/design/11-character-creation.md` and
  `docs/design/30-playtest-transcript.md` is internally consistent after renumbering.

## Assumptions

- This is a capability change per CLAUDE.md's own test (a real alternative — "keep both, sharpen
  the split" — was rejected in favour of merging), so it goes through the Spec Kit cycle and earns
  an ADR, unlike a pure documentation-drift fix.
- No code or schema changes: Luck was prose/design-doc-only, with no engine implementation yet
  (epic #133/#90 haven't started), so this feature's entire scope is `docs/design/` and
  `docs/adr/`.
- `wyrd-setting-template`, `wyrd-chronicle-hemmelfurt`, and other cross-repo artifacts are out of
  scope — this repo's own convention (CLAUDE.md) is that settings/chronicles live in separate
  repositories this repo doesn't own or write to.
