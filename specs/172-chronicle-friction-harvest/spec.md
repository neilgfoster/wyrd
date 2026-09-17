# Feature Specification: Chronicle friction harvest

**Feature Branch**: `172-chronicle-friction-harvest`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Build the harvest step from chronicle friction to wyrd issues (issue #95): read captured friction notes (log/friction.md, per docs/design/16-session.md) from one or more chronicle repos, propose wyrd issues from genuine engine gaps among them, leave setting-local color alone."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Harvest one chronicle's friction log into proposed issues (Priority: P1)

An operator who has been playing a chronicle wants the accumulated `log/friction.md` entries
turned into a reviewable list of candidate `wyrd` issues, without having to re-read the whole
log by hand or file issues one at a time.

**Why this priority**: This is the entire point of the feature — without it, friction notes are
captured but never acted on, which is the exact gap issue #93's epic exists to close.

**Independent Test**: Run the harvest tool against a chronicle repo checkout whose
`log/friction.md` has at least one qualifying entry (per the triage line in
`docs/design/16-session.md`) and confirm it prints a proposed `wyrd` issue title/body for that
entry, without filing anything until the operator explicitly confirms.

**Acceptance Scenarios**:

1. **Given** a chronicle repo with a `log/friction.md` containing one entry describing a mechanic
   producing an unexpected result, **When** the harvest is run against that repo, **Then** it
   proposes exactly one candidate `wyrd` issue naming the mechanic and the finding, and does not
   file it without confirmation.
2. **Given** a chronicle repo with a `log/friction.md` containing an entry whose "what happened"
   text is really setting-local color rather than a mechanic finding, **When** the harvest is run,
   **Then** that entry produces no proposed issue.
3. **Given** a chronicle repo with no `log/friction.md` file at all, **When** the harvest is run
   against it, **Then** it reports nothing to harvest for that repo rather than erroring.

---

### User Story 2 - Harvest across multiple chronicle repos in one pass (Priority: P2)

An operator running several chronicles wants one invocation to sweep friction notes from all of
them, since the same engine gap can surface in more than one chronicle before anyone notices the
pattern.

**Why this priority**: Multiple chronicles are the normal case (per `wyrd`'s own repo table —
one `wyrd-chronicle-<name>` repo per chronicle); a harvest that only reads one repo at a time
would leave the sweep to be re-run manually per chronicle, re-introducing the "someone has to
remember" problem the feature exists to remove.

**Independent Test**: Point the harvest at two chronicle repo checkouts, one with a qualifying
entry and one without, and confirm the run's output attributes the proposed issue to the correct
source chronicle and reports the other as contributing nothing.

**Acceptance Scenarios**:

1. **Given** two chronicle repo checkouts passed to one harvest invocation, **When** it runs,
   **Then** each proposed issue names which chronicle repo it came from, and entries from
   different chronicles are not merged into one proposal even when they name the same mechanic.

---

### User Story 3 - Avoid re-proposing an already-known gap (Priority: P2)

An operator re-running the harvest after previous runs have already raised some of the same
engine gaps does not want the board flooded with duplicate issues for the same finding.

**Why this priority**: Without dedup, a repeatable, re-invocable harvest step (the shape
`kord-template-harvest` already establishes) degrades into a duplicate-issue generator on its
second run, which is worse than not automating the step at all.

**Independent Test**: Run the harvest twice against the same chronicle without filing the first
run's proposals as real issues, confirm behavior; then run it once for real (an issue gets filed
for a genuine gap), then run the harvest again against a friction log carrying an equivalent
entry, and confirm the second run reports a likely match to the existing issue instead of
proposing a fresh duplicate.

**Acceptance Scenarios**:

1. **Given** a `wyrd` issue already exists describing the same mechanic and finding as a
   friction-log entry, **When** the harvest is run, **Then** it reports the entry as a likely
   duplicate of that existing issue (naming it) instead of proposing a new one.

---

### Edge Cases

- What happens when a `log/friction.md` entry is missing one of the three required fields
  (mechanic / what happened / what the GM did)? The harvest skips it and reports it as
  malformed rather than guessing a missing field or silently dropping it without comment.
- How does the harvest handle a friction entry whose "what happened" or "what the GM did" text
  contains a proper noun, character name, or other narrative detail that looks like it crossed
  the boundary `docs/design/16-session.md` describes? It still proposes the issue (triage is
  about mechanic-vs-color, not about wording hygiene) but strips or flags anything that reads as
  narrative rather than mechanical before the proposal is shown, since nothing narrative may
  cross into `wyrd` (`CLAUDE.md`, "Nothing unpublishable may enter this repository").
- What happens when the same finding appears twice within one friction log (the GM re-hit the
  same gap in two sessions)? The harvest merges same-log repeats into one proposal rather than
  proposing the same issue twice from a single run.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The harvest MUST read one or more chronicle repos' `log/friction.md` files (the
  format `docs/design/16-session.md` settles: a bullet list, each entry with `mechanic`,
  `what happened`, and `what the GM did` fields).
- **FR-002**: The harvest MUST apply the triage line already stated in
  `docs/design/16-session.md` ("What qualifies") to each entry, treating an entry as a candidate
  only when it reports a mechanic/table producing an unpredicted reading, a correctly-applied
  mechanic producing a result that felt wrong, or a GM improvisation because nothing covered the
  situation.
- **FR-003**: The harvest MUST NOT silently file an issue. It proposes candidates for an operator
  to confirm, the same posture `kord-template-harvest` already takes for its own output epic.
- **FR-004**: The harvest MUST check each surviving candidate against `wyrd`'s existing open
  (and a bounded recently-closed set of) issues via the deterministic
  `github-issue-dedup-check` primitive before proposing a new issue; a match is reported as a
  likely duplicate of the existing issue rather than proposed as new (mirroring
  `kord-template-harvest`'s own dedup step, specs/057-harvest-dedup).
- **FR-005**: The harvest MUST NOT let narrative content cross into a proposed `wyrd` issue — a
  proposal contains the mechanic named and the mechanical finding only, never the chronicle's
  story text, character names, or setting vocabulary (`CLAUDE.md`, "Nothing unpublishable may
  enter this repository").
- **FR-006**: The harvest MUST run against a chronicle repo that has no `log/friction.md` file
  (a chronicle that has captured no friction yet) without erroring, reporting nothing to harvest
  for that repo.
- **FR-007**: The harvest MUST accept more than one chronicle repo in a single invocation and
  attribute each proposed issue to the specific chronicle repo it came from.
- **FR-008**: The harvest MUST skip (and report separately from valid proposals) a
  `log/friction.md` entry missing any of its three required fields, rather than guessing the
  missing content or dropping it without any record.
- **FR-009**: The harvest MUST be implemented in Python 3.11+, stdlib only, consistent with
  `tools/`'s existing scripts, except where cross-repo access requires shelling out to `gh` (to
  read another repo's `log/friction.md`) or to kord's `client.py` (for the dedup-check
  primitive) — the same allowance the issue's own Definition of Done states.
- **FR-010**: The harvest MUST be re-invocable without needing to remember which entries a prior
  run already proposed — running it again against a friction log that has grown since the last
  run proposes only what is new or was not previously actioned, using the dedup check (FR-004)
  as the mechanism, not a separate local "already seen" ledger that could drift from what is
  actually on the board.

### Key Entities

- **Friction entry**: one bullet from a chronicle's `log/friction.md` — `mechanic`,
  `what happened`, `what the GM did`.
- **Harvest proposal**: a candidate `wyrd` issue title/body, plus the source chronicle repo and
  the friction entry it was built from, awaiting operator confirmation before filing.
- **Dedup verdict**: the `github-issue-dedup-check` result for one proposal — either no match
  (propose as new) or a matched existing issue (report as a likely duplicate instead).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a chronicle with at least one qualifying friction entry, an operator can go
  from "friction was captured during play" to "a reviewable, correctly-scoped `wyrd` issue
  proposal exists for it" in one command, with no manual re-reading of the friction log required.
- **SC-002**: A friction entry that is ordinary narrative color (per the triage line) never
  produces a proposed issue — 0% false-positive rate on the two worked examples
  `docs/design/16-session.md` already gives (the qualifying opposed-test example and the
  non-qualifying coat-catching-on-a-nail example).
- **SC-003**: Re-running the harvest against a friction log whose already-actioned entries have
  matching filed issues produces no duplicate proposals for those entries — verified by running
  the harvest twice, filing the first run's genuine proposal for real between runs, and
  confirming the second run reports it as a likely duplicate rather than proposing it again.
- **SC-004**: No proposed issue body, across the test fixtures used to validate this feature,
  contains any narrative text (character names, scene description, setting vocabulary) that
  did not already appear in the friction entry's `mechanic` field.

## Assumptions

- A chronicle repo checkout is available locally (or accessible via `gh api` without a local
  clone) at the time the harvest is run; this feature does not itself add the machinery to
  discover *which* chronicle repos exist — the operator names them, the same way
  `kord-template-harvest` takes an explicit `--kord-repo` rather than guessing one.
- The harvest is triggered manually (a command an operator runs), not on an automatic schedule;
  scheduling, if ever wanted, is a separate concern layered on top later, consistent with the
  issue's own scope ("a repeatable harvest step", not "a cron job").
- `docs/design/16-session.md`'s friction-log format is stable as landed by issue #94 / PR #442;
  this feature reads that format as-is rather than re-deciding it.
- The existing `github-issue-dedup-check` and `github-issue-recurrence-comment` kord primitives
  (already used by `kord-template-harvest`) are reachable from this repo via `gh`/`client.py`
  calls, the same access pattern already used elsewhere in `tools/`.
- One friction entry maps to at most one proposed issue; entries that describe the same gap
  across two different chronicles are NOT auto-merged into one proposal in this feature — FR-004's
  dedup check is against `wyrd`'s existing issues, not across chronicles' friction logs at
  proposal time. Cross-chronicle correlation, if wanted, is future work.
