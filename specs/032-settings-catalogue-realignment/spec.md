# Feature Specification: Realign the settings catalogue with reality

**Feature Branch**: `032-settings-catalogue-realignment`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Realign the settings catalogue and repo naming with reality" (issue #35)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trust the catalogue at a glance (Priority: P1)

The maintainer opens `settings.yaml` to find a setting's repository, and the `repo:` value
actually points at a repository that exists, under the naming convention the rest of the repo
(and `CLAUDE.md`) actually uses.

**Why this priority**: Every other use of the catalogue depends on this being true. A catalogue
whose `repo:` values are wrong is worse than no catalogue — it reads as authoritative and is not
(CLAUDE.md's fault class 4).

**Independent Test**: For every entry in `settings.yaml`, `repo:` names a repository that
actually exists under the account, and `CLAUDE.md`'s repository table names the same naming
convention.

**Acceptance Scenarios**:

1. **Given** the fourteen `wyrd-setting-*` repositories that exist today, **When** `settings.yaml`
   is read, **Then** every one of them has an entry whose `repo:` value matches its real name.
2. **Given** `CLAUDE.md`'s repository table, **When** it is read alongside `settings.yaml`,
   **Then** both describe the same naming convention (`wyrd-setting-<name>`).
3. **Given** a `repo:` value in `settings.yaml` for a repository that has since been renamed or
   removed, **When** the drift check (User Story 3) runs, **Then** it is reported rather than
   silently trusted.

---

### User Story 2 - Know how far along a setting actually is (Priority: P2)

The maintainer reads a setting's `status:` and it distinguishes a setting nobody has touched from
one with library material loaded, from one that has been indexed, from one that is playable —
rather than every entry reading `stub` regardless of real progress.

**Why this priority**: Second priority because it depends on User Story 1's repo identity being
correct first — there is no point tracking a setting's progress under the wrong repository name.
Real value: right now every entry says `stub` while several have library material already loaded,
so the field carries no information.

**Independent Test**: For a setting with library content but no index, `status:` reads
`library-loaded`, not `stub`; for one with neither, it reads `stub`.

**Acceptance Scenarios**:

1. **Given** a setting repository whose `library/` holds real content beyond the template's
   `.gitkeep` placeholder, **When** the catalogue is read, **Then** its `status:` is
   `library-loaded` or later, not `stub`.
2. **Given** a setting repository whose `index/` holds a real index (not merely `.gitkeep`),
   **When** the catalogue is read, **Then** its `status:` is `indexed` or later.
3. **Given** none of the fourteen settings has a populated `index/` as of this feature (confirmed
   by live inspection during this feature's implementation), **When** the catalogue is written,
   **Then** every entry reads `library-loaded`, not `indexed` or `playable` — the field must
   reflect what is actually true today, not an aspiration.

---

### User Story 3 - Catch drift before it goes stale again (Priority: P3)

The maintainer runs one command and finds out whether the catalogue and the live fleet still
agree, the same way `tools/backlog.py check` already does for the board.

**Why this priority**: Lowest of the three because it is a safeguard against *future* drift,
while User Stories 1-2 fix the *current* drift. Without it, this fix decays the same way the
original catalogue did — CLAUDE.md notes it has already gone stale twice.

**Independent Test**: Run the check against the current, corrected catalogue and get a clean
pass; temporarily edit one `repo:` value to a nonexistent name and get a reported failure.

**Acceptance Scenarios**:

1. **Given** the corrected `settings.yaml` and the live fleet, **When** the drift check runs,
   **Then** it exits zero and reports no drift.
2. **Given** a `wyrd-setting-*` repository that exists but has no entry in `settings.yaml`,
   **When** the drift check runs, **Then** it is reported as missing from the catalogue.
3. **Given** a `settings.yaml` entry whose `repo:` does not match any live repository, **When**
   the drift check runs, **Then** it is reported rather than silently accepted.

### Edge Cases

- What happens when a live repository is renamed after the catalogue is written? The drift check
  must report the catalogue's now-dangling `repo:` value rather than silently treating it as gone.
- What happens when two settings share a world (the `wh40k-` and `maelstrom-` prefixes)? The
  catalogue records the grouping as data (an optional field on each entry); building any new
  mechanic that *acts* on that grouping is explicitly out of scope here and belongs to the
  related-settings feature (#36) — CLAUDE.md's "do not build both" instruction in the issue.
- What happens to a setting repository that is intentionally not yet started (a future candidate,
  no repository yet)? It is not listed as a `settings:` entry — the catalogue lists what exists,
  a separate "candidates" note (already present in the file) lists what does not.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `settings.yaml` MUST list every `wyrd-setting-*` repository that currently exists,
  each with a `repo:` value matching its real name.
- **FR-002**: `CLAUDE.md`'s repository table MUST describe the `wyrd-setting-<name>` convention,
  not the superseded `wyrd-<setting>` form.
- **FR-003**: `status:` MUST take one of four values — `stub` (no library content),
  `library-loaded` (library content present, not yet indexed), `indexed` (an index exists), or
  `playable` (indexed and confirmed usable at the table) — reflecting each setting's actual,
  currently-observed state.
- **FR-004**: Each entry MAY carry an optional `group:` field naming a shared world (e.g.
  `wh40k`, `maelstrom`) for settings that are distinct entries within one; entries with no shared
  world omit it.
- **FR-005**: A drift-check script MUST report, for the live fleet against `settings.yaml`: any
  live `wyrd-setting-*` repository missing from the catalogue, and any catalogue `repo:` value
  matching no live repository. It MUST be read-only and MUST exit non-zero on any drift found.
- **FR-006**: The catalogue MUST contain nothing unpublishable — no library contents, no document
  titles or extracted text from any private repository's source material.

### Key Entities

- **Settings catalogue entry**: one setting — id, title, repo name, visibility, status, and an
  optional shared-world group.
- **Drift report**: the live-vs-catalogue comparison the check script produces — repos missing
  from the catalogue, and catalogue entries naming a repo that does not exist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the fourteen live `wyrd-setting-*` repositories has a corresponding,
  correctly-named entry in `settings.yaml`.
- **SC-002**: Reading `CLAUDE.md`'s repository table and `settings.yaml` side by side shows the
  same naming convention.
- **SC-003**: The drift-check script exits zero against the corrected catalogue and non-zero
  when a `repo:` value or a missing entry is deliberately introduced.
- **SC-004**: No entry in the corrected catalogue reads `status: stub` for a setting whose
  `library/` holds real content.

## Assumptions

- "Real library content" is judged by whether a repository's `library/` tree holds anything
  beyond the template skeleton's `.gitkeep` placeholder — confirmed by live inspection during
  this feature's implementation to be true for all fourteen settings, and none has real `index/`
  content yet, so every corrected entry reads `library-loaded`.
- The shared-world `group:` field is data only; it introduces no new engine mechanism and no new
  catalogue-consuming code path — satisfying the issue's "do not build both" instruction without
  blocking the related-settings feature (#36) from building the actual grouping behavior later.
- The drift check follows `tools/backlog.py`'s existing precedent: stdlib-only, `gh`-CLI-driven,
  read-only, run on demand rather than in CI (this repository has no CI workflow yet, per
  `docs/design/27-tooling.md`).
- `wyrd-research`, `wyrd-chronicle-template`, and `wyrd-chronicle-<name>` repositories are out of
  scope for this catalogue — it lists settings only, matching its existing purpose.
