# Feature Specification: Fleet rollout of engine and template changes

**Feature Branch**: `032-fleet-rollout`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Fleet rollout: propagate engine and template changes across the wyrd repos" (issue #31)

## Clarifications

### Session 2026-08-26

- Q: How should the tooling discover which repos belong to the fleet? → A: List by name prefix — `gh repo list <owner>` filtered to names matching `wyrd-setting-*`, `wyrd-setting-template`, `wyrd-chronicle-template`.
- Q: How should a repo's synced template/engine version be represented? → A: A small metadata file in the target repo records the commit SHA of the source repo (`wyrd-setting-template`, `wyrd-chronicle-template`, or this engine repo) it last synced to.
- Q: When a repo is behind on more than one outstanding change, how should rollout PRs be structured? → A: One PR per repo, bundling every outstanding change since its recorded SHA.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See which repos are behind (Priority: P1)

The maintainer wants to know, at any moment and without opening each repository, which
`wyrd-*` repos are current with the engine/template and which have drifted, and specifically
what each one is missing.

**Why this priority**: Nothing else in this feature is checkable without a way to compare a
repo's actual state to what it should be. This is also independently useful on its own — it
turns silent drift into a visible, standing fact.

**Independent Test**: Run the status command against the fleet with no prior rollout tooling in
place; it correctly reports each repo's recorded version and lists what a repo is missing,
using only read access.

**Acceptance Scenarios**:

1. **Given** a `wyrd-setting-*` repo created from the current template, **When** the status
   command runs, **Then** that repo is reported as current.
2. **Given** a `wyrd-setting-*` repo created from an older template revision, **When** the
   status command runs, **Then** that repo is reported as behind, naming what changed since its
   recorded version.
3. **Given** a repo with no recorded version at all (pre-existing repos, before this feature),
   **When** the status command runs, **Then** that repo is reported as unversioned rather than
   silently skipped or crashing the run.
4. **Given** a private repo the maintainer's `gh` credentials can read, **When** the status
   command runs, **Then** it is included in the report on the same basis as a public repo.

---

### User Story 2 - Propose a change to every affected repo (Priority: P2)

The maintainer has changed the engine or the setting template and wants that change proposed,
as a pull request, to every downstream repo that needs it — without pushing directly to any of
them and without touching a repo's hand-authored content.

**Why this priority**: This is the actual rollout mechanism, but it depends on User Story 1
existing first (it needs to know which repos are affected). It is the second most valuable
piece because it turns a manual, repo-by-repo chore into one operation.

**Independent Test**: With the versioning from User Story 1 in place, run the rollout command
after an additive template change; it opens one PR per repo that is missing that change, and
opens no PR against a repo that already has it.

**Acceptance Scenarios**:

1. **Given** an additive change to the setting template (a new file or directory the template
   gains), **When** the rollout command runs, **Then** a PR proposing that addition is opened
   against every `wyrd-setting-*` repo that is missing it, and each such repo's hand-authored
   content is left untouched.
2. **Given** a structural change to the template (an existing path is renamed, moved, or
   removed), **When** the rollout command runs, **Then** the PR it opens performs the migration
   step rather than a raw file copy, distinguishing it from the additive case.
3. **Given** a repo that is already current, **When** the rollout command runs, **Then** no PR
   is opened against that repo.
4. **Given** a private repo, **When** the rollout command runs, **Then** the PR is opened
   against that private repo directly (never routed through a public intermediary), and no
   library or corpus content is read, copied, or otherwise moved by the tooling.
5. **Given** a repo where a prior rollout PR is still open and unmerged, **When** the rollout
   command runs again for the same change, **Then** it does not open a duplicate PR for that
   repo.

---

### User Story 3 - Recognize a deliberate divergence (Priority: P3)

The maintainer has deliberately let a specific repo diverge from the template (for example, a
one-off structural change that repo needed) and does not want the status report or the rollout
command to keep flagging or "fixing" that repo as if the divergence were a mistake.

**Why this priority**: Lower priority than the first two because it only matters once
divergence starts happening on purpose, which follows from the fleet actually being tracked.
Without this, the maintainer would face a choice between silencing real drift reports and being
repeatedly bothered about an intentional decision.

**Independent Test**: Mark one repo as deliberately diverged from a specific point, then run the
status and rollout commands; that repo is reported distinctly from ordinary drift and receives
no further rollout PRs for the divergence that was accepted.

**Acceptance Scenarios**:

1. **Given** a repo marked as deliberately diverged at a given change, **When** the status
   command runs, **Then** that repo is reported as "diverged (accepted)" rather than "behind".
2. **Given** the same repo, **When** the rollout command runs for the change that was
   deliberately not adopted, **Then** no PR is opened against that repo for that change.
3. **Given** that repo, **When** a *later, unrelated* change is rolled out, **Then** that later
   change is still proposed to the repo normally — accepting one divergence does not exempt the
   repo from everything after it.

### Edge Cases

- What happens when a repo's recorded version references a template/engine revision that no
  longer exists (e.g., force-pushed or rewritten history upstream)? The status command must
  report this as an unresolvable/unknown state rather than guessing a distance.
- How does the rollout command handle a repo that has been renamed or archived since it was last
  seen? It must be reported as unreachable rather than silently dropped from the fleet list.
- What happens when a rollout PR the tooling previously opened was closed without merging (the
  maintainer rejected it)? Re-running rollout for the same change must not reopen an
  identical PR; it should be reported as previously rejected.
- What happens when the engine and the template both change between two rollout runs? Both must
  be tracked and reported as distinct outstanding changes, not collapsed into one.
- What happens when a repo is missing the version marker file's *expected location* itself (a
  structural change that moved where the version is recorded)? This is itself a structural
  change and must be handled through the same migration path as any other structural change,
  not treated as "unversioned."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every `wyrd-*` repo MUST record, in a small committed metadata file, the commit SHA
  of the source repo (`wyrd-setting-template`, `wyrd-chronicle-template`, or this engine repo) it
  was last synced to.
- **FR-002**: The system MUST provide a single, read-only command that discovers the fleet by
  listing repos owned by the maintainer's GitHub account whose names match `wyrd-setting-*`,
  `wyrd-setting-template`, or `wyrd-chronicle-template`, and reports, for each, its recorded SHA
  and exactly what it is missing relative to the current template and engine.
- **FR-003**: The status report MUST distinguish at least three repo states: current, behind
  (with what it is missing named), and unversioned (no recorded revision at all).
- **FR-004**: The system MUST provide a rollout operation that opens exactly one pull request per
  affected repo, bundling every outstanding change since that repo's recorded SHA, rather than
  pushing to it directly or opening one PR per individual change.
- **FR-005**: The rollout operation MUST distinguish a structural change (the repo needs an
  active migration step) from an additive change (the repo gains something new), and MUST
  produce different PR content for each, per `design/09-evolution.md`'s structural/behavioural
  distinction.
- **FR-006**: The rollout operation MUST NOT read, copy, or otherwise move a setting repo's
  library or corpus content, and MUST function identically whether the target repo is public or
  private.
- **FR-007**: The rollout operation MUST NOT open a duplicate pull request for a change that
  already has an open, unmerged PR proposing it in the same repo.
- **FR-008**: The system MUST allow a repo to be marked as having deliberately diverged at a
  named point, and both the status report and the rollout operation MUST treat that repo's
  accepted divergence as such rather than as ordinary drift, while still tracking and proposing
  any later, unrelated change normally.
- **FR-009**: The system MUST report a repo it cannot read (renamed, archived, deleted,
  inaccessible credentials) as unreachable rather than omitting it from the report silently.
- **FR-010**: The system MUST be read-only unless explicitly invoked to open PRs — the status
  report MUST make no repository writes.

### Key Entities

- **Fleet repo record**: One `wyrd-*` repository's tracked state — which template revision and
  which engine revision it last synced to, and whether it carries an accepted-divergence marker.
- **Change**: A single engine or template revision, tagged as either structural or additive,
  that a repo can be behind on.
- **Rollout PR**: A pull request opened by the tooling against one repo, proposing exactly one
  outstanding change (or a batched set, per plan) via migration (structural) or addition
  (additive).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The maintainer can determine, in one command invocation and without opening any
  individual repository, which of the fleet's repos are current, which are behind, and what each
  behind repo is missing.
- **SC-002**: After an additive template change, a PR proposing it appears within one rollout run
  against every affected repo, and zero PRs are opened against repos that are already current.
- **SC-003**: No rollout run ever pushes a commit directly to a repo's default branch or modifies
  a repo's library/corpus content.
- **SC-004**: A repo marked as deliberately diverged is never re-flagged as "behind" for the
  specific change it diverged on, across repeated status-report runs.
- **SC-005**: Running the status command against the current sixteen `wyrd-setting-*` repos plus
  the two templates completes and reports on all of them, including any that are private.

## Assumptions

- The maintainer has `gh` credentials with read access to every `wyrd-*` repo (public and
  private) and write access sufficient to open pull requests against them.
- A structural change's migration step is expressed as a script or instructions the rollout PR
  carries, not as a fully automatic content transform for every possible structural change —
  some structural changes may need the repo owner's judgment before merging.
- This feature covers `wyrd-setting-*` repos, `wyrd-setting-template`, and `wyrd-chronicle-template`.
  Live chronicle repos (created from the chronicle template) are out of scope, per the issue's
  explicit exclusion of chronicle *state* migration (`design/09-evolution.md` already governs
  that).
- Engine changes propagate to setting/chronicle repos only insofar as those repos declare a
  dependency on an engine revision; the mechanism for a repo to declare that dependency is the
  same version-marker mechanism as the template (FR-001).
- Rollout runs are triggered manually by the maintainer (not on an unattended schedule) for this
  feature's initial scope; a scheduled/automatic trigger is a possible later enhancement, not a
  requirement here.
