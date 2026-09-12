# Feature Specification: Setting build pipeline — scheduled execution and web augmentation policy

**Feature Branch**: `149-setting-pipeline-scheduling`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Setting build pipeline: scheduled execution and web augmentation" (issue #102)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deciding whether the pipeline runs unattended (Priority: P1)

A setting author has Pass 0 (#100) and the generalised corpus extraction/indexing pipeline (#101)
both working against their own `library/`. Today, running either pass means opening a session.
The author wants to know: can this run on a schedule with nobody watching, and if so, how — or is
there a concrete reason it should stay a manual, attended step?

**Why this priority**: nothing else in this feature has a subject until this question has an
explicit, recorded answer. Issue #102's own acceptance criteria require "a scheduled run is
specified... or an explicit decision against one, with the reason recorded" — a decision against
scheduling, reasoned, satisfies this story exactly as well as a design for one.

**Independent Test**: given the design document this feature produces, confirm it states
unambiguously whether scheduled execution is recommended, and if so, names the runner
mechanism and the repository boundary the run stays inside; if not, confirm it names the specific
reason and what would need to change for the answer to flip.

**Acceptance Scenarios**:

1. **Given** a setting repository with Pass 0 and the corpus pipeline already callable, **When**
   a setting author reads this feature's design output, **Then** they can tell, without asking
   anyone, whether to wire up scheduled execution and, if so, where the workflow file belongs.
2. **Given** the constraint that copyrighted source material must never leave the private setting
   repo it lives in, **When** the scheduled-execution design is evaluated, **Then** it explains
   how a scheduled run keeps every read of `library/` and every write of derived indexes inside
   that same repository boundary.
3. **Given** the design recommends scheduled execution, **When** the design is inspected, **Then**
   it identifies which pipeline steps are safe to run unattended (deterministic, no external
   network call) and which are not (the scenario index's model call, per
   docs/design/26-corpus-index.md), and what change of behaviour, if any, unattended execution
   requires of the latter.

---

### User Story 2 - Knowing when a derived fact may draw on a public source (Priority: P1)

A setting author's library is privately sourced, but some worldbuilding gaps (a gap the Pass 0 gap
report surfaces, per #100) could plausibly be filled from material that is legitimately public —
a public-domain reference, an author's own freely published errata, common folklore. The author
needs an explicit, stated rule for when that is acceptable, and a way to tell, later, which facts
in the setting came from the private library and which came from a public source.

**Why this priority**: issue #102 names this as a co-equal deliverable ("has an explicit rule for
when public sources may supplement a private library... every derived fact records where it came
from"), and it is the one this feature's own scope note resolves against CLAUDE.md's "no tooling
that fetches source material" constraint — the policy and its provenance schema are this repo's to
define; performing an actual fetch is not.

**Independent Test**: given the provenance schema this feature defines, confirm a derived fact
can be tagged with a source origin (library vs. public) and a specific reference, and that the
policy document states, in checkable terms, when a public source is and is not an acceptable
input.

**Acceptance Scenarios**:

1. **Given** the public-augmentation policy, **When** a setting author considers supplementing a
   gap with a public source, **Then** the policy tells them, without further judgment calls,
   whether that class of source is in-bounds.
2. **Given** a derived fact produced by either path, **When** its record is inspected, **Then** it
   names which origin (library or public) it came from and, for a public origin, the specific
   source reference — never a bare "public" tag with no traceable reference.
3. **Given** this repository's own constraint that no tooling here may fetch source material,
   **When** the policy and schema are read, **Then** neither describes or ships a live web-fetch
   call from this repository — any actual fetch is explicitly scoped to a setting repo's own
   tooling, consistent with #101's own precedent for the same boundary.

### Edge Cases

- A setting author runs the scheduled workflow with `library/` completely empty (no material
  triaged in yet): the design states what happens — a no-op run that reports nothing new to
  process, not an error, matching Pass 0's own empty-library behaviour (#100).
- A derived fact is later found to have been produced before this provenance schema existed (a
  setting repo built before #102 landed): the design states this is out of scope for
  backfilling — provenance is recorded going forward, per the engine's forward-only evolution rule
  (docs/design/29-evolution.md), not retrofitted onto history.
- A public source itself changes or disappears after a derived fact cites it: the design records
  the reference as it was captured (specific enough to be checked against an archived or dated
  copy) rather than assuming the reference will remain live indefinitely.
- The scenario index's model call (the one non-deterministic pipeline step, per
  docs/design/26-corpus-index.md) is scheduled to run unattended: the design states explicitly
  whether that call is included in scheduled runs or held back for an attended pass, and why.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: This feature MUST produce a design document stating whether scheduled, unattended
  execution of the setting build pipeline (Pass 0 plus the corpus extraction/indexing pipeline) is
  recommended, with the reason recorded either way.
- **FR-002**: Where scheduled execution is recommended, the design MUST specify it as a workflow
  that runs inside the setting repository itself (never a shared or engine-repo runner), so that
  copyrighted source material never crosses a repository boundary.
- **FR-003**: The design MUST distinguish pipeline steps that are safe to run unattended
  (deterministic, no external call) from any step that is not (a model call), and state how
  scheduled execution treats the latter.
- **FR-004**: This feature MUST define a public-augmentation policy stating, in checkable terms,
  when a public source may supplement a private setting library's coverage of an engine gap
  (per #100's gap report) and when it may not.
- **FR-005**: This feature MUST define a provenance schema every derived fact can carry, recording
  its origin (library-sourced or public-sourced) and, for a public origin, a specific, checkable
  source reference.
- **FR-006**: Neither this feature's design nor any code it adds to this repository MAY perform,
  or ship a script that performs, a live fetch of source material from the public internet —
  consistent with CLAUDE.md's "no tooling that fetches source material" constraint and with #101's
  own precedent for the same boundary (specs/148-generalise-corpus-extraction/spec.md's Scope
  note). Any such fetch is explicitly scoped to a setting repository's own tooling, outside this
  repository.
- **FR-007**: The provenance schema MUST be a pure data shape (fields and their meaning) that a
  setting repository's own tooling can attach to a derived fact — this repository defines the
  shape, not an implementation that populates it end-to-end against a live source.
- **FR-008**: The design MUST state explicitly that a scheduled run's failure mode (a step errors,
  or the workflow itself does not fire) is surfaced observably (e.g. the runner's own failure
  reporting) rather than failing silently, since nobody is watching a scheduled run in real time.

### Key Entities *(include if feature involves data)*

- **Scheduled run design**: the recommendation (or reasoned decision against) unattended execution
  of the pipeline, which steps it covers, and the repository boundary it stays inside.
- **Public-augmentation policy**: the stated rule for when a public source may supplement a
  private library's coverage of an engine gap.
- **Provenance record**: the schema attached to a derived fact — origin (`library` or `public`),
  and for `public`, a specific source reference — that lets any derived fact be traced back to
  where it came from.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author can read this feature's design output and correctly answer, without
  asking anyone, "does my pipeline run on a schedule, and if so where does the workflow file go?"
- **SC-002**: A setting author can read the public-augmentation policy and correctly classify at
  least three concrete example sources (a private rulebook page, a public-domain reference work, a
  fan wiki of uncertain licence) as in-bounds or not, using the policy's stated rule alone.
- **SC-003**: Every derived fact produced under the provenance schema can be traced to a specific
  origin and, when public, a specific checkable reference — zero derived facts carry an
  unattributed "public" tag.
- **SC-004**: This repository's own lint and repository-boundary checks (`ruff check .`,
  `ruff format --check .`, CLAUDE.md's "nothing unpublishable enters this repository" rule) stay
  green after this feature lands — no fetch capability, fixture of copyrighted material, or
  setting-specific reference is added to this repository.

## Assumptions

- Scope is this repository (the engine/meta repo) only. Per CLAUDE.md's repository table, actual
  scheduled-execution wiring (the GitHub Action workflow file itself) and any live web-fetch
  script are a `wyrd-setting-<name>` repository's own concern — this feature specifies the design
  and policy, not a working implementation deployed against a real setting repo.
- "Scheduled execution" is read as GitHub Actions' own `schedule` (cron) trigger, the natural fit
  for a setting repository already using GitHub for its private repo — issue #102 names GitHub
  Actions explicitly as the option to evaluate.
- The scenario index's thematic-generation step is the pipeline's only non-deterministic,
  model-calling step (per docs/design/26-corpus-index.md); every other step (documents, nouns,
  terms, tables, and Pass 0's own catalogue/gap-survey/idempotence machinery) is deterministic and
  a reasonable candidate for unattended execution.
- "Public source" means material with a clear, checkable licence or provenance that does not
  require anyone's private library to already exist — a public-domain text, an author's own
  freely published material, common/attested folklore — not merely "found on the open internet."
  The policy states this distinction rather than leaving "public" undefined.
- No new runtime dependency is introduced in this repository; the design and schema are documents
  and, if any code is added, it stays within this repo's existing "standard library only" rule
  (docs/design/27-tooling.md) exactly as corpus_pipeline.py and setting_pass0.py already do.
