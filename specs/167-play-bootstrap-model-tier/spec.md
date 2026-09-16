# Feature Specification: Tier /wyrd-play and /wyrd-bootstrap at Sonnet, with effort decided per skill

**Feature Branch**: `167-play-bootstrap-model-tier`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Tier /wyrd-play and /wyrd-bootstrap at Sonnet, with effort decided
per skill (wyrd#430, part of epic wyrd#429). Cap model choice at Sonnet as a hard ceiling
everywhere (never Opus), but do not force effort to low by default for skills whose actual job is
narration/judgement -- decide effort per skill against what it actually does, against
docs/design/27-tooling.md section 5's narration-stays-capable stance."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An operator runs `/wyrd-play` and gets the capable model, deliberately (Priority: P1)

A player invokes `/wyrd-play` to run a beat of a chronicle. Today the skill carries no `model:`
or `effort:` frontmatter at all, so it silently inherits whatever the harness defaults to --
which could drift to a smaller or lower-effort model without anyone having decided that on
purpose. After this change, the skill's own frontmatter states plainly which model tier and
effort level it runs at, and that choice is traceable to a written reason grounded in what the
skill actually does (almost entirely narration and GM judgement -- exactly the class
`docs/design/27-tooling.md` section 5 says must not be economised).

**Why this priority**: `/wyrd-play` is the most-invoked skill in actual play -- every beat of
every session runs through it. An undecided or accidentally-cheapened model tier here is the
single biggest risk to the engine's actual value (the quality of the fiction), so pinning it
deliberately is the higher-priority half of this feature.

**Independent Test**: Read `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md` in full.
Confirm its frontmatter declares `model: sonnet` and an `effort:` value, and that a written
justification for that effort value (naming which of the skill's steps are mechanical and which
are judgement-requiring) appears in the file, without needing to run the skill itself.

**Acceptance Scenarios**:

1. **Given** `/wyrd-play`'s SKILL.md previously had no `model:`/`effort:` frontmatter, **When**
   this feature lands, **Then** its frontmatter declares `model: sonnet` and a specific
   `effort:` value, never `opus`.
2. **Given** the skill's steps mix a handful of mechanical actions (loading session context,
   formatting a roll result verbatim) with steps that are almost entirely narration and GM
   judgement (orienting the player, resolving what a result means, closing a beat), **When** the
   effort level is chosen, **Then** the written justification names both categories explicitly
   and explains why the chosen single effort value is right for the skill as a whole, rather than
   silently defaulting to the cheapest option.

### User Story 2 - An operator runs `/wyrd-bootstrap` and gets the capable model, deliberately (Priority: P2)

A player invokes `/wyrd-bootstrap` once, immediately after `./bootstrap`, to complete character
creation and seed the chronicle's opening situation and first Threat. Today this skill also
carries no `model:`/`effort:` frontmatter. After this change, it declares `model: sonnet` and an
effort level chosen by weighing its more mechanical steps (walking the character-creation
allocation, calling `create-character`, writing files) against its one real judgement step (Step
3's opening-scenario selection, matching a setting's indexed candidates or an `entities/` arc
against the player's stated intent).

**Why this priority**: `/wyrd-bootstrap` runs exactly once per chronicle rather than once per
beat, so an under-provisioned model tier here is lower-frequency risk than `/wyrd-play`'s -- but
Step 3's scenario-matching judgement is real and consequential (it sets the entire opening
situation a chronicle plays out from), so it still needs a deliberate, written decision rather
than an assumed default.

**Independent Test**: Read `wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md` in
full. Confirm its frontmatter declares `model: sonnet` and an `effort:` value, and that a written
justification names Step 3's scenario/arc-matching judgement against the skill's more mechanical
steps, without needing to run the skill itself.

**Acceptance Scenarios**:

1. **Given** `/wyrd-bootstrap`'s SKILL.md previously had no `model:`/`effort:` frontmatter,
   **When** this feature lands, **Then** its frontmatter declares `model: sonnet` and a specific
   `effort:` value, never `opus`.
2. **Given** the skill's Step 3 (opening-scenario selection) is its one real judgement step,
   distinct from its otherwise mechanical character-creation and file-writing steps, **When** the
   effort level is chosen, **Then** the written justification names that distinction explicitly.

### Edge Cases

- What happens if a later change to either skill removes its one judgement-requiring step (e.g.
  Step 3's scenario matching becomes fully mechanical)? The written justification in this feature
  is tied to the skill's *current* mix of steps; a future change that shifts that mix is expected
  to revisit the justification rather than leave a stale reason standing next to a changed skill.
- What happens if the frontmatter schema Claude Code reads does not support a value this feature
  wants to set? Out of scope here -- both `model:` and `effort:` are already-supported SKILL.md
  frontmatter fields (confirmed in wyrd#430's own orientation), so this is not expected to arise.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/wyrd-play`'s SKILL.md MUST declare `model: sonnet` in its frontmatter.
- **FR-002**: `/wyrd-bootstrap`'s SKILL.md MUST declare `model: sonnet` in its frontmatter.
- **FR-003**: Neither skill MUST ever declare `model: opus` -- Sonnet is a hard ceiling, not a
  default that a later edit could raise.
- **FR-004**: `/wyrd-play`'s SKILL.md MUST declare an explicit `effort:` value, chosen
  deliberately rather than left unset or silently defaulted to the lowest available value.
- **FR-005**: `/wyrd-bootstrap`'s SKILL.md MUST declare an explicit `effort:` value, chosen
  deliberately rather than left unset or silently defaulted to the lowest available value.
- **FR-006**: Each skill's chosen `effort:` value MUST be accompanied by a written justification,
  in the skill file itself, that reasons against `docs/design/27-tooling.md` section 5's
  narration-stays-capable stance (the GM session itself -- narration, character voice and motive,
  judgement about what a result means -- is "the one place not to economise").
- **FR-007**: Each written justification MUST explicitly distinguish which parts of that skill's
  own steps are mechanical (have a computable right answer, already delegated to an engine CLI
  verb) versus judgement-requiring (narration, or a matching/selection call graded against the
  player's stated intent), even though the frontmatter itself can only express one `effort:`
  setting for the whole skill.
- **FR-008**: This feature MUST NOT change either skill's own operational steps, CLI-verb
  contracts, or Never-list -- it adds frontmatter and a justification note only.

### Key Entities

- **SKILL.md frontmatter**: the YAML front matter block at the top of a Claude Code skill file;
  already supports `model:` and `effort:` keys read by the harness to select which model runs the
  skill and at what reasoning-effort tier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both `/wyrd-play` and `/wyrd-bootstrap` declare `model: sonnet` in their SKILL.md
  frontmatter, verifiable by reading the two files directly.
- **SC-002**: Both skills declare an `effort:` value together with a written justification
  referencing `docs/design/27-tooling.md` section 5, verifiable by reading the two files
  directly -- no run of either skill is needed to confirm this.
- **SC-003**: Neither skill's frontmatter declares `model: opus`, verifiable by grep.
- **SC-004**: Each justification names at least one mechanical step and one judgement-requiring
  step from that skill's own body, verifiable by reading the justification text against the
  skill's own numbered steps.

## Assumptions

- `model:` and `effort:` are supported SKILL.md frontmatter keys in the Claude Code harness this
  engine targets (stated in wyrd#430's own orientation; not re-verified by this spec).
- The capability itself (the two skill files' frontmatter and justification prose) lands in
  `wyrd-chronicle-template`, the repo that actually owns those skill files -- this spec, plan and
  tasks trail lives in `wyrd` (this repo) only because that is where the Spec Kit substrate is
  installed, matching the precedent set by wyrd#403/#404/#405/#418.
- `wyrd-chronicle-template` has no CI or automated tests; verification of this feature is by
  re-reading both updated skill files in full, not by an automated check.
- This feature does not change model or effort tiering for any other skill in
  `wyrd-chronicle-template` -- those remain epic wyrd#429's own separate, later work.
