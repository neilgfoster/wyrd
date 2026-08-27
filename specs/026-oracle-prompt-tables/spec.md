# Feature Specification: Oracle prompt tables

**Feature Branch**: `026-oracle-prompt-tables`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Oracle prompt tables" (issue #21)

## Clarifications

### Session 2026-08-26

- Q: Should oracle prompt tables be documented as a variant of the existing 'oracles' family row
  in `docs/design/04-tables.md`'s index, or get their own separate index row? → A: Variant of oracles
  — one `Oracles` index row covers both `docs/design/14-oracle-answers.md` and the new
  `docs/design/15-oracle-prompts.md`, the same way criticals already holds several variant tables
  under one row. The index stays at five families.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate content instead of inventing it (Priority: P1)

Mid-scene, the GM needs to invent something the fiction hasn't specified yet — what an NPC
actually wants, why a place is empty, what a thread turns on — and left to its own devices an LLM
GM reaches for the same handful of dramatic shapes every time, then escalates them across
sessions. The GM instead rolls a prompt table for the right family and reads the row, the same way
it would roll an oracle answer for a yes/no question.

**Why this priority**: This is the entire point of the family. Without it, "prompt oracles" stays
an unwritten companion to #20, and the GM keeps inventing motives and complications the same
handful of ways.

**Independent Test**: Given a prompt family and a roll, reading the row produces a genre-neutral
generative seed with no remaining judgment call about what it says — only about how the GM
narrates it into the scene.

**Acceptance Scenarios**:

1. **Given** a scene where an NPC's real objective hasn't been established, **When** the GM rolls
   the NPC-objective prompt table, **Then** the roll resolves to exactly one row, and the row's
   content is concrete enough to constrain what the GM narrates next.
2. **Given** the same generated content is needed again later (the same NPC's motive comes back
   into play), **When** the GM checks state first, **Then** the previously recorded result is
   reused and no new roll happens.

---

### User Story 2 - Keep a generated row usable in any setting (Priority: P2)

A setting running a grim register and a setting running a comic one both use the same engine
tables. A row that reads as a threat in one and as a joke in the other — or that only makes sense
against one tone — leaks that setting's register into the engine.

**Why this priority**: This is what makes the family genre-neutral rather than merely
setting-agnostic in name. A row that fails this test is the exact staleness `CLAUDE.md` warns
tables hide.

**Independent Test**: Every row in every prompt table can be read once as if the setting were grim
and once as if it were comic, and reads sensibly both times; a row that only works in one is
removed, and that check is recorded rather than merely asserted.

---

### User Story 3 - Extend the tables without replacing them (Priority: P3)

A setting wants prompts of its own far more often than it wants its own criticals — its own list
of NPC motives specific to its factions, its own reasons a place would be empty. The setting
author needs to add rows on top of the engine's set, not only swap the whole table out.

**Why this priority**: Without an extension path, every setting with its own flavour of prompt
either forks the whole table (losing the engine's baseline) or has nowhere to put its additions at
all.

**Independent Test**: A setting can declare additional rows for a prompt table, in a form the
override mechanism from `docs/design/04-tables.md` and `docs/design/24-authoring-a-setting.md` accepts,
without needing to restate or discard the engine's own rows.

---

### Edge Cases

- What happens when no prompt family fits what the GM needs to invent? The document states the
  prompt families are the minimum that constrain invention where it actually runs loose, not an
  exhaustive catalogue — anything outside that set stays an ordinary GM decision, the same as an
  oracle-unbound question.
- What happens when a generated NPC objective conflicts with a companion's already-established
  objective or Tension (`docs/design/16-session.md`)? The document states that a roll never overrides
  already-established fiction; it only fills a gap that hasn't been decided yet.
- What happens when the GM has a prompt table available but doesn't roll it? As with answer
  oracles, the document states this obligation plainly and names which situations trigger it,
  consistent with `docs/design/01-principles.md`.
- What happens when a setting's extension row and an engine row would generate the same content by
  coincidence? Not an error — rows are independent draws, not a deduplicated set, unlike the
  answer oracle's `repeatable` declaration, which this family also uses.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The document MUST define the fixed set of prompt families the engine ships, each with
  a stated rationale, drawn from where GM invention actually runs loose (NPC objective, why a
  situation isn't as presented, what a thread turns on, what complicates a scene) rather than a
  broad table of atmosphere.
- **FR-002**: Each prompt family MUST define at least one table, addressed by a key, following the
  row schema and roll-declaration conventions of [`docs/design/04-tables.md`](../../docs/design/04-tables.md).
- **FR-003**: Every row in every table MUST be genre-neutral — the document MUST record, row by
  row, that each was checked once against a grim reading and once against a comic reading, and any
  row that failed either reading MUST NOT appear in the shipped table.
- **FR-004**: Every row MUST be concrete enough to constrain what the GM narrates next, not merely
  restate that "something happens" — the document states how this is judged.
- **FR-005**: The document MUST state which class of situation obliges the GM to roll a prompt
  table rather than invent, consistent with `docs/design/01-principles.md`, mirroring how
  `docs/design/14-oracle-answers.md` states the answer-oracle obligation.
- **FR-006**: The document MUST state how a family's generated content maps onto existing content
  structures — an NPC-objective row onto the companion/objective machinery in
  [`docs/design/16-session.md`](../../docs/design/16-session.md), a thread-turn row onto the thread/threat
  structures in [`docs/design/19-campaign.md`](../../docs/design/19-campaign.md) and
  [`docs/design/18-arcs-and-beats.md`](../../docs/design/18-arcs-and-beats.md) — so a roll's output is
  usable without further translation.
- **FR-007**: The document MUST specify the setting extension path: a setting adding its own rows
  to a prompt table's row set, distinct from wholesale replacement, consistent with the override
  mechanism in `docs/design/04-tables.md` and [`docs/design/24-authoring-a-setting.md`](../../docs/design/24-authoring-a-setting.md).
- **FR-008**: The document MUST state what a prompt roll records to state and where, consistent
  with the recording conventions in `docs/design/04-tables.md`, so a generated result can be reused
  rather than regenerated if the same gap is asked again.
- **FR-009**: `docs/design/04-tables.md`'s index row for oracles MUST be amended to also link
  `docs/design/15-oracle-prompts.md`, the same way the row already links
  `docs/design/14-oracle-answers.md` — prompts are a variant of the existing oracles family, not a
  sixth index row, per the Clarifications above.
- **FR-010**: `docs/design/02-architecture.md` and `docs/design/27-tooling.md` MUST be updated if the
  document's filename or the family's file layout differs from what those documents currently
  say.
- **FR-011**: No table row, example, or label in the document MAY name a specific setting, a
  source system, or bake in a tonal register — verified by grep, per `CLAUDE.md`.

### Key Entities

- **Prompt family**: a named category of GM invention the engine constrains with a table (e.g. an
  NPC's real objective) rather than leaving to unconstrained invention.
- **Prompt table**: a rollable table within a family, following `docs/design/04-tables.md`'s row
  schema, whose rows are genre-neutral generative seeds rather than fixed narrative content.
- **Generated content record**: the state entry a prompt roll writes, keyed so the same generative
  gap resolves to the same content if it recurs.
- **Setting extension**: rows a setting adds to an engine prompt table without replacing the
  engine's own rows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM (Claude, at play time) can fill any of the four scoped generative gaps — NPC
  objective, why a situation isn't as presented, what a thread turns on, what complicates a scene —
  by rolling a table and reading the row, with no invented content beyond narrating that row into
  the scene.
- **SC-002**: Every row in every shipped table has a recorded grim-reading/comic-reading check in
  the document, and no row fails either reading.
- **SC-003**: Grepping `design/` for setting or system vocabulary introduced by this change returns
  nothing.
- **SC-004**: A setting author reading only this document and `docs/design/24-authoring-a-setting.md`
  can correctly state how to add a table-specific row without replacing the engine's table.
- **SC-005**: A second GM reading only `docs/design/01-principles.md` and this document, with no other
  context, can state correctly whether a given example situation obliges a prompt roll.

## Assumptions

- The prompt families are a closed, small set chosen for where invention runs loose in the
  existing design (companion objectives in `docs/design/16-session.md`; thread/threat turns in
  `docs/design/19-campaign.md` and `docs/design/18-arcs-and-beats.md`), not an open-ended content library —
  actual setting-specific prompt content is explicitly out of scope (issue #21) and belongs in a
  `wyrd-<setting>` repo.
- The document lives at `docs/design/15-oracle-prompts.md` per the issue's stated goal, as a sibling
  to `docs/design/14-oracle-answers.md` under the same `oracles` family named in
  `docs/design/04-tables.md`'s index — resolved in Clarifications above as a variant of that one
  family, matching how criticals already hold several variant tables under one family entry.
- Prompt tables are `repeatable` (per `docs/design/04-tables.md`'s uniqueness declaration), matching
  the answer oracle rather than the unique-per-character transformation table, since rolling the
  same generative seed twice for two different NPCs or scenes is ordinary.
- Each prompt table declares its own die and modifier, per `docs/design/04-tables.md`'s "declared by
  the family" convention — reusing `1d100` (as the answer oracle does) is the default assumption
  unless a family's row count makes a smaller die a better fit, decided during planning.
- No verification script is assumed necessary the way `tools/check_oracle_answers.py` checks #20's
  probabilities, because this family's correctness criterion (genre-neutrality) is a qualitative
  reading check recorded in prose, not a computable probability; this may be revisited during
  planning if a computable property (e.g. row-range contiguity per `docs/design/04-tables.md`) turns
  out to need its own script, mirroring `tools/check_bestiary.py`-style structural checks used
  elsewhere.
