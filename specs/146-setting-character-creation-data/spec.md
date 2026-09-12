# Feature Specification: Setting-Level Character Creation Data

**Feature Branch**: `146-setting-character-creation-data`

**Created**: 2026-09-12

**Status**: Draft

**Input**: GitHub issue #37, "Setting-level character creation data"

## Summary

`docs/design/11-character-creation.md` §4 already names what a setting must supply for character
creation to run — entry careers, names, places, Drives, Misfortunes, and Loyalties — and
`docs/design/24-authoring-a-setting.md` already schemas and validates `careers.yaml` and
`gear.yaml`. But three of those six required inputs (Loyalties, Drives, Misfortunes) exist only as
prose promises: no file shape, no schema, and nothing rejects a setting that gets one wrong. A
fourth (`names.yaml`) is named in the setting's file tree but never given a shape. A fifth,
optional input — ancestries (species/lineage/culture, §3) — is documented in prose but has no file
of its own either. This leaves character creation's actual data contract split across five
documents' worth of prose and two schemas, with no single place — and no validator — that confirms
a setting can run the procedure at all.

**Repository boundary.** This repository (`wyrd`) is the engine: design documents, ADRs, and the
schemas/validators a setting's data must satisfy. The actual population of a setting's data — the
`wyrd-setting-template` skeleton, and any specific `wyrd-setting-<name>` repository's own
`careers.yaml`, `loyalties.yaml`, and so on — lives in those other repositories
([`CLAUDE.md`](../../CLAUDE.md)'s repository table) and is out of scope for a change made here.
This feature closes the engine-side half of issue #37: specifying and validating the contract.
Populating the template and a real setting are follow-up work tracked in their own repositories.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author gets one validator for the whole character-creation surface (Priority: P1)

A setting author has written `careers.yaml`, `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`,
and `names.yaml` (and optionally `ancestries.yaml`). They run one command and learn, before ever
trying to create a character, whether every file the procedure needs is present and correctly
shaped.

**Why this priority**: without this, a setting missing a Loyalty relation or a malformed Drive
list only surfaces as a confusing failure partway through character creation — exactly the
"filled in by the GM's judgement" failure mode §4 says must not happen.

**Independent Test**: run the validator against a setting directory with all six files correct,
and again with one file deliberately broken in each of the ways the schema forbids; the tool
accepts the first and names the specific problem in the second.

**Acceptance Scenarios**:

1. **Given** a setting directory with valid `careers.yaml`, `loyalties.yaml`, `drives.yaml`,
   `misfortunes.yaml`, and `names.yaml`, **When** the validator runs, **Then** it reports success.
2. **Given** a setting with no career marked `entry: true`, **When** the validator runs, **Then**
   it reports that specific failure (this rule already exists in `24-authoring-a-setting.md`, but
   had no validator).
3. **Given** a `loyalties.yaml` declaring a relation pair naming a Loyalty absent from the same
   file, **When** the validator runs, **Then** it reports the dangling reference.
4. **Given** a `loyalties.yaml` declaring a relation kind outside `strained`/`irreconcilable`,
   **When** the validator runs, **Then** it is rejected.
5. **Given** an optional `ancestries.yaml` present, **When** the validator runs, **Then** it is
   validated on the same terms as a career's skill list (§3: an ancestry only ever *widens* the
   skill pool, so it carries no advance or Stamina fields to reject).
6. **Given** no `ancestries.yaml` at all, **When** the validator runs, **Then** this is accepted —
   ancestry is optional, per §3.

---

### User Story 2 - The engine/setting contract table stops needing five separate reads (Priority: P2)

Someone building a new setting from scratch reads `24-authoring-a-setting.md` once and finds the
shape of every file character creation needs, not just the two (`careers.yaml`, `gear.yaml`)
documented before this change.

**Why this priority**: this is what makes the contract *discoverable*, which is the actual
complaint in issue #37 — "a setting cannot be played even with a complete engine" because it does
not know what to write.

**Independent Test**: starting only from `24-authoring-a-setting.md` and `11-character-creation.md`,
write a `loyalties.yaml`/`drives.yaml`/`misfortunes.yaml`/`names.yaml` that the validator accepts,
without reading any other design document or existing setting's files.

**Acceptance Scenarios**:

1. **Given** `24-authoring-a-setting.md`, **When** read alone, **Then** it states the required and
   optional fields of `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml`, and
   `ancestries.yaml`, in the same style already used for `careers.yaml`/`gear.yaml`.
2. **Given** `11-character-creation.md` §4's table, **When** read, **Then** each requirement links
   to the schema that satisfies it, rather than restating it in different words.

---

### Edge Cases

- A setting declaring a single Loyalty and no relations at all is legal (§4 already says so) — the
  validator must accept an empty relations list, not require at least one.
- A `loyalties.yaml` relation naming the same Loyalty on both sides of a pair is a self-reference
  and is rejected — a Loyalty cannot be strained or irreconcilable with itself.
- A `misfortunes.yaml`/`drives.yaml` entry is free text (what a character wants, what already
  works against them) — the schema constrains structure (an `id` and a `text`), never the content
  itself; the engine has no vocabulary to judge Drive or Misfortune content against
  ([ADR 0013](../../docs/adr/0013-the-engine-names-no-skill.md)'s reasoning applied the same way).
- `names.yaml` covering zero cultures is rejected — §4 requires "enough to name a person of this
  world," and an empty file cannot.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `docs/design/24-authoring-a-setting.md` MUST document the required and optional
  fields of `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml`, and the optional
  `ancestries.yaml`, in the same table/example style already used for `careers.yaml` and
  `gear.yaml`.
- **FR-002**: A new validator (`tools/check_character_creation_data.py`) MUST accept a setting
  directory and check every file character creation needs against its documented schema, the same
  shape as `check_bestiary.py`/`check_gear.py`/`check_setting.py` (missing required field,
  unrecognised field, closed-vocabulary violation, dangling reference), reporting every failure
  found rather than stopping at the first.
- **FR-003**: The validator MUST check `careers.yaml` against the rules `24-authoring-a-setting.md`
  already states but never validated: every entry has `id`/`entry`/`skills`; `entry: true` carries
  no `prerequisites` and `entry: false` carries at least one; at least one career is `entry: true`;
  every `prerequisites` entry names a career in the same file; the graph is acyclic.
- **FR-004**: The validator MUST check `loyalties.yaml`: at least one Loyalty declared; each
  relation pair names two distinct Loyalties present in the file; each relation's kind is
  `strained` or `irreconcilable` (the closed vocabulary [ADR 0015](../../docs/adr/0015-loyalty-has-three-relations-not-two.md)
  defines); no duplicate pair (in either order) declared twice.
- **FR-005**: The validator MUST check `drives.yaml` and `misfortunes.yaml`: at least one entry in
  each; every entry has a stable `id` and non-empty `text`; no duplicate `id` within a file.
- **FR-006**: The validator MUST check `names.yaml`: at least one culture declared; each culture
  has at least one non-empty list among `given`, `family`, and `place`.
- **FR-007**: The validator MUST, when `ancestries.yaml` is present, check it against the same
  `id`/`skills` shape as a career entry, minus `entry`/`prerequisites` (an ancestry is never an
  entry point and has no prerequisite chain — it only ever widens the skill pool, per §3 and
  [ADR 0040](../../docs/adr/0040-ancestry-widens-the-skill-pool-never-the-budget.md)). Its absence
  MUST NOT be an error.
- **FR-008**: `docs/design/11-character-creation.md` §4's table MUST link each requirement to the
  schema in `24-authoring-a-setting.md` that defines it, rather than restating the shape.
- **FR-009**: The validator's own documentation MUST state plainly that populating these files for
  any actual setting (including `wyrd-setting-template`) is out of scope for this repository —
  matching the pattern `check_setting.py`/`check_bestiary.py` already follow of validating a path
  the caller supplies, never a path this repository owns.

### Key Entities

- **Loyalty declaration** (`loyalties.yaml`): a list of Loyalty ids/names, plus a list of
  non-default relation pairs between them (`strained` or `irreconcilable`), per ADR 0015.
- **Drive / Misfortune declaration** (`drives.yaml` / `misfortunes.yaml`): a flat list of
  free-text options a player chooses from at creation steps 7–8.
- **Name declaration** (`names.yaml`): a list of cultures, each with given/family/place name
  pools.
- **Ancestry declaration** (`ancestries.yaml`, optional): a list of skill-granting entries a
  character's chosen ancestry can widen the creation skill pool with, per §3.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author who has read only `24-authoring-a-setting.md` and
  `11-character-creation.md` can write all six files (five required, one optional) without
  consulting any other document or an existing setting's source.
- **SC-002**: `tools/check_character_creation_data.py` rejects 100% of the schema violations
  listed in FR-003 through FR-007 when deliberately introduced, and accepts a correctly-shaped
  fixture with zero false positives.
- **SC-003**: The character-creation contract's required inputs (§4's table) are each backed by a
  documented schema and a runnable check — zero of the six remain "documented" without also being
  "validated."

## Assumptions

- Ancestry stays optional, per §3 as already written — this feature does not change whether a
  setting must declare one.
- The Loyalty relation vocabulary is exactly the two named in ADR 0015 (`strained`,
  `irreconcilable`); this feature does not revisit that decision, only schemas and validates data
  declared against it.
- `wyrd-setting-template`'s actual skeleton and any setting's actual population are out of scope
  here, per the repository table in `CLAUDE.md` — those are separate features to be raised in
  their own repositories once this contract exists to build against.
- Drive and Misfortune text is unconstrained prose (the engine holds no vocabulary to police
  content, consistent with ADR 0013's reasoning for skills); the schema validates structure only.
