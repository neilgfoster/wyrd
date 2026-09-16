# Feature Specification: Scenarios Index Build and Bootstrap Wiring

**Feature Branch**: `166-scenarios-index-build`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Build the scenarios.json index and wire scenario selection into
/wyrd-bootstrap (issue #418)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trigger scenarios.json's lazy, cached extraction (Priority: P1)

A setting repo's own tooling holds a document (an adventure) it wants a thematic scenario record
for, plus a model's already-produced structured extraction of that document. It calls one engine
function to fold that record into the setting's `scenarios.json`, cached by content hash and
schema version, without the engine ever calling a model itself.

**Why this priority**: without this, `engine/wyrd/corpus_pipeline.py`'s existing
`build_scenario_index`/`documents_needing_scenario_generation` primitives (#356, already built
and tested against synthetic fixtures) have no CLI entry point any setting repo can actually call
— the lazy-build policy `docs/design/26-corpus-index.md` describes has never been triggered for a
real setting.

**Independent Test**: run the new tool's `plan` verb against a setting directory with a
`corpus_build_cache.json` and no scenario cache; confirm every candidate document is reported
`missing`. Supply a JSON file of already-produced records for a subset and run `commit`; confirm
`index/scenarios.json` gains exactly those records and `index/scenario_build_cache.json` records
their content hash and schema version. Re-run `commit` with the same inputs; confirm no record is
regenerated (the injected generator is never invoked for an already-fresh document) and the
output is byte-identical.

**Acceptance Scenarios**:

1. **Given** a setting directory with a built `corpus_build_cache.json` and no
   `scenario_build_cache.json`, **When** `plan` runs, **Then** every document matching the
   caller's own path filter is reported `missing`.
2. **Given** a JSON file mapping document id to an already-produced scenario record for two of
   those documents, **When** `commit` runs, **Then** `index/scenarios.json` contains exactly
   those two records and `index/scenario_build_cache.json` caches them by content hash and
   schema version.
3. **Given** an unchanged corpus and cache from Scenario 2, **When** `commit` runs again with the
   same records file, **Then** neither record is regenerated (the tool never re-derives what the
   cache already reports fresh) and the written files are unchanged.
4. **Given** a document whose corpus text hash has changed since it was last cached, **When**
   `plan` runs, **Then** that document is reported `stale`, not `fresh`.
5. **Given** a records file missing an entry for a document `plan` reported `missing` or `stale`,
   **When** `commit` runs, **Then** it fails naming the specific document id, and writes nothing
   for any document (partial output is never persisted for a run that can't complete every
   requested document).

### User Story 2 - /wyrd-bootstrap selects from a setting's real scenario index (Priority: P1)

A player runs `/wyrd-bootstrap` in a chronicle cloned from a setting that has a built
`scenarios.json` with more than one candidate. Step 3 (the opening situation) selects among those
real candidates, matched against the player's stated intent, instead of always opening on
whichever single arc entity happens to exist in the setting's `entities/`.

**Why this priority**: this is the issue's own stated Definition of Done — "a real
`/wyrd-bootstrap` run against Titan offers (or selects among) more than one real candidate opening
scenario."

**Independent Test**: walk `/wyrd-bootstrap`'s Step 3 against a setting fixture carrying a
multi-record `scenarios.json`; confirm the selected candidate is one whose declared theme/tone
plausibly matches the stated `about`/`avoid` intent, and that the skill's own text records which
candidates were passed over. Walk the same step against a setting fixture with no
`index/scenarios.json` at all; confirm it falls back to reading `entities/` exactly as it does
today, and does not error.

**Acceptance Scenarios**:

1. **Given** a setting with `index/scenarios.json` present, **When** Step 3 runs, **Then** it
   reads that file, filters to records eligible for the current setting, and picks (or offers) a
   candidate matching the player's stated intent -- never mechanically the first record.
2. **Given** a setting with no `index/scenarios.json` file, **When** Step 3 runs, **Then** it
   falls back to today's behaviour (reading an existing `entities/` arc) rather than raising an
   error or blocking bootstrap.
3. **Given** a setting whose `scenarios.json` exists but is empty (`[]`), **When** Step 3 runs,
   **Then** it also falls back to today's `entities/`-reading behaviour, the same as the
   no-file case.

### Edge Cases

- A `plan`/`commit` path filter that matches zero documents: `plan` reports an empty list rather
  than erroring; `commit` with an empty records file writes an empty (or unchanged) index.
- A records file entry whose deterministic fields fail `corpus_scenario.validate_scenario_record`
  (an unrecognised `scale`/`season`): `commit` fails naming the offending document and field,
  before writing anything, matching User Story 1's Acceptance Scenario 5's all-or-nothing rule.
- Two documents from different settings sharing a content hash: each is cached independently,
  scoped by `(setting, id)`, matching `corpus_pipeline`'s own existing per-setting scoping.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine repo MUST provide a CLI entry point (a `tools/` script, following
  `tools/setting_build.py`'s existing convention) that a setting repo's own tooling can invoke to
  fold an already-produced scenario record into that setting's `scenarios.json`.
- **FR-002**: That entry point MUST NOT call a model itself -- the structured scenario record for
  each document is supplied by the caller, exactly as `generation_pipeline.assemble_pacing`/
  `write_prose` take an already-produced model response as an ordinary argument.
- **FR-003**: The entry point MUST reuse `corpus_pipeline.build_scenario_index`/
  `documents_needing_scenario_generation`/`scenario_cache_status` unchanged for its
  lazy/cached decision -- it introduces no second staleness rule.
- **FR-004**: Freshness MUST be judged by the same `(content_hash, schema_version)` pair
  `corpus_pipeline.scenario_cache_status` already defines; a document already fresh MUST NOT be
  regenerated even when a caller supplies a record for it.
- **FR-005**: The entry point MUST validate each newly-accepted record against
  `corpus_scenario.validate_scenario_record` before writing it, and MUST write nothing for any
  document in the run if any one record fails validation or is missing.
- **FR-006**: `wyrd-chronicle-template`'s `/wyrd-bootstrap` skill (Step 3) MUST call
  `scenario_selection.select_scenario` against a setting's `index/scenarios.json` (when present
  and non-empty) plus the player's bootstrap-interview intent, in preference to reading an
  `entities/` arc directly.
- **FR-007**: `/wyrd-bootstrap` Step 3 MUST fall back to today's `entities/`-reading behaviour,
  unchanged, when a setting has no `index/scenarios.json` file or an empty one -- never an error.
- **FR-008**: The scenarios index MUST be built for real against at least a handful of
  `wyrd-setting-titan`'s `library/03 - adventures/` gamebooks, each record grounded in that
  adventure's own extracted `corpus/` text (never fabricated).

### Key Entities

- **Scenario record**: the schema `docs/design/26-corpus-index.md` §5 already defines
  (`id`, `source`, `adaptation`, `settings`, deterministic selection fields, model-generated
  thematic fields, graph fields). This feature does not change the schema.
- **Scenario build cache**: `index/scenario_build_cache.json` in a setting repo, keyed by
  `(setting, document id)`, holding `content_hash`, `schema_version`, and the cached `record` --
  the on-disk form of `corpus_pipeline.build_scenario_index`'s in-memory `cache` argument.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running the new tool's `commit` verb twice in a row against an unchanged corpus and
  an unchanged records file produces byte-identical `index/scenarios.json` and
  `index/scenario_build_cache.json`, and invokes the injected generator zero times on the second
  run.
- **SC-002**: A `/wyrd-bootstrap` walkthrough against a setting fixture with three or more
  `scenarios.json` candidates selects a candidate other than "the first one in the file" for at
  least one distinct stated intent, demonstrating real selection rather than a fixed pick.
- **SC-003**: A `/wyrd-bootstrap` walkthrough against a setting fixture with no `scenarios.json`
  completes Step 3 exactly as it does today, with no behavioural change and no error.
- **SC-004**: At least five of Titan's real `03 - adventures/` gamebooks have a `scenarios.json`
  record grounded in their own corpus text, committed in `wyrd-setting-titan`.
