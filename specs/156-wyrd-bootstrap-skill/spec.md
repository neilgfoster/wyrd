# Feature Specification: Wyrd bootstrap skill

**Feature Branch**: `156-wyrd-bootstrap-skill`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Build a /wyrd-bootstrap Claude Code skill (SKILL.md), most likely in
wyrd-chronicle-template, that completes the interpretation half of the chronicle bootstrap
script's docstring: after the deterministic ./bootstrap script clones engine+setting and writes
the intent interview to chronicle.yaml.json, /wyrd-bootstrap runs once to: (1) complete character
creation by calling the engine's create-character CLI verb, (2) choose an opening situation
matching the interview's intent answers, (3) select at least one Threat with a personal
connection to the character, (4) seed overlay/ with that threat, (5) write the full
chronicle.yaml via the save CLI verb, and (6) make the first commit. Follows the established
conventions from wyrd-chronicle-template's existing /wyrd-character, /wyrd-downtime,
/wyrd-end-session skills. Out of scope: /wyrd-play itself. (GitHub issue neilgfoster/wyrd#403)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete a freshly-bootstrapped chronicle in one pass (Priority: P1)

A player has just run `./bootstrap` in a cloned chronicle repository, answering the setting
choice and the intent interview. The deterministic script has copied `engine/` and `setting/`
and recorded their answers, but the chronicle has no character, no opening scene, and no
`chronicle.yaml` yet. The player opens the repo in Claude Code and invokes `/wyrd-bootstrap`.

**Why this priority**: without this, a bootstrapped chronicle is not playable — `/wyrd-play`
(a separate, sibling feature) has nothing to load, per docs/design/23-chronicle-bootstrap.md.
This is the single path from "cloned template" to "playable chronicle."

**Independent Test**: run `./bootstrap` against a real setting (e.g. darkfuture), then invoke
`/wyrd-bootstrap`, and confirm the repository afterward has a complete `pc.yaml`, an opening
situation recorded, at least one seeded Threat with a stated personal connection in `overlay/`,
a valid `chronicle.yaml`, and a first git commit.

**Acceptance Scenarios**:

1. **Given** a chronicle repo where `./bootstrap` has run and `chronicle.yaml.json` exists but
   `chronicle.yaml` does not, **When** `/wyrd-bootstrap` is invoked, **Then** it walks the
   character-creation steps (career, advances, Loyalty, Drive, Misfortune, Fault Line), calls
   the engine's `create-character` verb, and writes `pc.yaml` from its returned frontmatter
   without recomputing any skill percentage, Fate value, or Stamina total itself.
2. **Given** a completed character with a chosen Misfortune, **When** the skill selects the
   opening Threat, **Then** it writes an `overlay/` entity carrying a `threat:` block whose
   `connection` names that Misfortune (or another concrete personal connection when the setting
   has no eligible Misfortune-linked entity), per docs/design/19-campaign.md's "threats are
   personal" rule.
3. **Given** the character, opening situation and Threat are all decided, **When** the skill
   assembles the full chronicle state, **Then** it calls the engine's `save` verb to write
   `chronicle.yaml`, reports any validation error verbatim without attempting to patch it
   itself, and only proceeds to commit once `save` succeeds.
4. **Given** a successful save, **When** the skill finishes, **Then** it commits `pc.yaml`,
   `chronicle.yaml`, and the new `overlay/` entity in one commit, and leaves
   `chronicle.yaml.json` removed (its contents now folded into `chronicle.yaml`).

### User Story 2 - Refuse to run twice (Priority: P2)

A player who has already completed `/wyrd-bootstrap` once invokes it again by mistake.

**Why this priority**: character creation and Threat seeding are one-time acts; running them
twice would silently overwrite a played character or double-seed the world with no record of
why, and issue #403 states the skill "runs once, right after the chronicle's own `./bootstrap`
script."

**Independent Test**: invoke `/wyrd-bootstrap` a second time against a chronicle where
`chronicle.yaml` already exists, and confirm it declines rather than recreating the character or
re-seeding a Threat.

**Acceptance Scenarios**:

1. **Given** a chronicle repo where `chronicle.yaml` already exists, **When** `/wyrd-bootstrap`
   is invoked, **Then** it reports that bootstrap interpretation has already run and stops
   without touching `pc.yaml`, `chronicle.yaml`, or `overlay/`.

### Edge Cases

- `chronicle.yaml.json` is missing entirely (the deterministic `./bootstrap` script was never
  run, or `chronicle.yaml` already exists from a prior `/wyrd-bootstrap` run): the skill reports
  this plainly and does not attempt to fabricate an intent interview from nothing.
- The setting's career/Loyalty/Drive/Misfortune data (`careers.yaml`, `loyalties.yaml`,
  `drives.yaml`, `misfortunes.yaml`) is missing a file `create-character` requires: the CLI's
  own error is surfaced verbatim, not papered over with an invented default.
- No entity in `setting/` is eligible to carry the seeded Threat's personal connection (no
  character/organisation/place plausibly tied to the chosen Misfortune): the skill still writes
  a Threat overlay, drawing the connection from the Misfortune's own text directly rather than
  refusing to seed a Threat at all — every active Threat must have a stated connection, but nothing
  requires that connection to already exist as a separate, named entity.
- `create-character` (or `save`) returns a refusal or validation error: the skill reports the
  exact error and does not commit, leaving the working tree exactly as `./bootstrap` left it
  (`chronicle.yaml.json` still present, no `pc.yaml`/`chronicle.yaml`/`overlay/` changes).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The skill MUST be invocable as a Claude Code skill (`/wyrd-bootstrap`) from within
  a chronicle repository where `./bootstrap` has already run.
- **FR-002**: The skill MUST refuse to run — reporting why, and changing nothing — when
  `chronicle.yaml` already exists (bootstrap interpretation has already completed) or when
  `chronicle.yaml.json` does not exist (the deterministic script has not run yet).
- **FR-003**: The skill MUST complete character creation by gathering the player's choices for
  each step docs/design/11-character-creation.md defines (career, the 8-advance spend, Loyalty,
  Drive, Misfortune, and the Fault Line sentence) and calling the engine's `create-character`
  CLI verb with them, writing `pc.yaml` from exactly the verb's returned frontmatter.
- **FR-004**: The skill MUST NOT recompute any mechanical value `create-character` is
  responsible for (a skill percentage, Fate, Stamina, or a refusal reason) — every such value in
  the finished `pc.yaml` MUST trace to the verb's own return value.
- **FR-005**: The skill MUST choose an opening situation that reflects the intent interview's
  recorded answers (`about`, `avoid`, `lethality`, `world_acts_offstage`) from
  `chronicle.yaml.json`, and MUST honour a stated `avoid` answer by not opening on content that
  answer excludes.
- **FR-006**: The skill MUST select at least one Threat carrying a personal connection to the
  player character, per docs/design/19-campaign.md's "threats are personal" rule, and MUST
  record that connection as concrete text (not a placeholder) in the Threat's `overlay/` entity.
- **FR-007**: The skill MUST write the seeded Threat as an `overlay/` entity (either an overlay
  of an existing `setting/` entity, promoting it, or a new chronicle-created entity under
  `entities/` when no existing entity fits), following docs/design/25-entities.md's overlay
  schema — never by editing anything under `setting/`.
- **FR-008**: The skill MUST assemble the full chronicle state (identity, pinned engine/setting
  versions, calendar, the recorded `intent`, and the seeded Threat's presence) and write it via
  the engine's `save` CLI verb, never by hand-writing `chronicle.yaml`'s YAML itself.
- **FR-009**: The skill MUST report a `save` (or `create-character`) failure exactly as the verb
  returned it, and MUST NOT commit anything when either call fails.
- **FR-010**: On success, the skill MUST make exactly one git commit covering `pc.yaml`,
  `chronicle.yaml`, and the new `overlay/` (and, if used, `entities/`) files, and MUST remove
  `chronicle.yaml.json` (its content having been folded into `chronicle.yaml`) as part of that
  same change.
- **FR-011**: The skill MUST locate the engine CLI the same way `/wyrd-character`,
  `/wyrd-downtime` and `/wyrd-end-session` already do (`find engine -maxdepth 4 -type d -name
  wyrd`), rather than assuming a fixed path.
- **FR-012**: The skill's own prose MUST NOT name a specific setting or game system beyond what
  is read from the setting chosen at bootstrap time, per docs/design's setting-agnosticism rule,
  and MUST NOT blur "Claude Code skill" with the engine's own game-mechanic vocabulary (ADR 0013).

### Key Entities

- **Bootstrap intent record** (`chronicle.yaml.json`): the deterministic `./bootstrap` script's
  output — chronicle name, chosen setting repo, pinned versions, and the intent interview's
  answers. Consumed and removed by this skill.
- **Player character** (`pc.yaml`): the character entity `create-character` produces —
  career, skills, Loyalty, Drive, Misfortune, Fault Line, Stamina, Fate.
- **Opening situation**: the arc/beat entity (or entities) the chronicle begins on, chosen to
  match the intent interview's answers.
- **Seeded Threat**: an entity (existing, overlaid, or newly created) carrying a `threat:` block
  with an `imminence` and a `connection` naming what ties it to the player character.
- **Chronicle state** (`chronicle.yaml`): the full state `save` validates and writes — identity,
  pinned versions, calendar, intent, and everything else docs/design/22-state.md's schema
  requires.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `/wyrd-bootstrap` once against a freshly-bootstrapped chronicle (against
  either of the two settings named in issue #403) produces, in a single pass with no manual file
  editing afterward, a complete character, a recorded opening situation, at least one seeded
  Threat with a stated personal connection, and a first commit.
- **SC-002**: A second `/wyrd-bootstrap` invocation against the same, now-completed chronicle
  changes nothing on disk and produces no second commit.
- **SC-003**: Every mechanical number appearing in the finished `pc.yaml` (skill percentages,
  Fate, Stamina) matches exactly what the `create-character` CLI verb returned for the same
  inputs — independently re-derivable by calling the verb again with the recorded choices.

## Assumptions

- `#402` (chronicle-level CLI verbs: `save`, `load`, `validate`, `recap`) is merged and available
  in `engine/wyrd/client.py` by the time this skill runs, per the issue's stated dependency.
- The skill file lives in `wyrd-chronicle-template` (most likely
  `.claude/skills/wyrd-bootstrap/SKILL.md`), matching where the three precedent skills
  (`/wyrd-character`, `/wyrd-downtime`, `/wyrd-end-session`) already live, since the chronicle
  repo — not the engine repo — is what needs to invoke it.
- The deterministic `./bootstrap` script's current behaviour (writing `chronicle.yaml.json` with
  `pending_seed: true` rather than a real `chronicle.yaml`) is accepted as this feature's input
  contract, not something this feature changes — except for its own printed next-step message,
  which currently tells the player to run `/wyrd-play` next; this feature corrects that message
  to name `/wyrd-bootstrap`; where the two disagree, docs/design/23-chronicle-bootstrap.md (this
  skill's own spec) governs.
- Opening-situation selection and Threat selection are judgment calls grounded in the setting's
  own content and the interview's answers, not arithmetic — there is no CLI verb to reimplement
  for either, so the skill performs them directly (writing entity/overlay files by hand, per
  docs/design/25-entities.md's plain frontmatter+prose format), the same way a human setting
  author would.
- `/wyrd-play` (loading and continuing an already-bootstrapped chronicle) is a separate, sibling
  feature and out of scope here.
