# Feature Specification: Full design consistency check

**Feature Branch**: `040-design-consistency-check`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Full design consistency check (closes #92, closes Stage 13 / #52). Stage 13 scoped three remaining items once #59 (dangling-mechanic check) and #14 (paper playtest) were done: (1) a cross-reading pass over document pairs describing one mechanic, looking for the two-coherent-descriptions fault; (2) every probability/statistical claim in docs/design/ backed by a passing computation, not prose alone; (3) a script confirming no setting/system vocabulary reached docs/design/ or README.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader trusts that two documents describing one mechanic agree (Priority: P1)

Someone reading `docs/design/03-rules.md`'s combat section and `docs/design/12-the-adversary.md`'s
adversary block wants confidence the two describe the same mechanic consistently — the same
crowd-clearing threshold, the same critical formula, the same Aftermath scope — without having to
cross-check every number themselves.

**Why this priority**: This is the fault class CLAUDE.md names as hardest to see ("two documents
describing one thing differently... found only by reading them against each other") and the one
Stage 13 exists to close out before the design programme can call itself complete.

**Independent Test**: Read the identified high-risk document pairs against each other and confirm
each shared claim (a threshold, a formula, a scope rule) reads identically in both places.

**Acceptance Scenarios**:

1. **Given** `docs/design/03-rules.md`'s crowd rule ("ahead by 20 or more") and
   `docs/design/12-the-adversary.md`'s reference to the same threshold, **When** read against each
   other, **Then** both state the same figure.
2. **Given** `docs/design/07-transformations.md`'s threshold statement and ADR 0029's decision,
   **When** read against each other, **Then** both state thresholds at every multiple of 3.
3. **Given** any divergence found during the pass, **When** it is found, **Then** it is corrected
   in the design documents (or, if it reflects a real unresolved question, explicitly flagged
   rather than silently left) before this feature is considered complete.

### User Story 2 - Every derived probability claim in the design corpus is computed, not asserted (Priority: P1)

A reader of any percentage or rate published in `docs/design/` wants to know it was computed at
the values a real character actually has, per CLAUDE.md's own recorded fault ("Probability claims
were wrong twice, and both were only caught by computing them"), rather than picked to sound right.

**Why this priority**: This is the second explicit item Stage 13 scoped, and the exact class of
error CLAUDE.md records as having recurred.

**Independent Test**: `python3 tools/check_probability_coverage.py` exits 0, confirming every
identified derived claim in `docs/design/` has a passing backing computation.

**Acceptance Scenarios**:

1. **Given** every design document containing a percentage, **When** classified as either a
   defined input constant (e.g. the untrained 10%, diegesis's descriptive bands) or a derived
   claim (a rate that follows from combining rules), **Then** every derived claim has a named
   backing script that computes and asserts it.
2. **Given** `python3 tools/check_probability_coverage.py`, **When** run, **Then** it re-runs every
   backing script and exits non-zero if any of them fails.

### User Story 3 - No setting or system name has leaked into the setting-agnostic engine documents (Priority: P1)

A reader of `docs/design/` or `README.md` wants assurance the engine never names a specific
setting or source system, per CLAUDE.md's own rule, checkable rather than trusted to review alone.

**Why this priority**: The third item Stage 13 scoped, and the one most likely to regress silently
— a rewrite pass, a worked example, or a hastily-added row can reintroduce a name without anyone
noticing it slipped past review.

**Independent Test**: `python3 tools/check_no_setting_vocabulary.py` exits 0.

**Acceptance Scenarios**:

1. **Given** `settings.yaml`'s current catalogue of setting ids and titles, **When**
   `docs/design/*.md` and `README.md` are scanned for any of those terms, **Then** none are found.
2. **Given** a setting name that did leak in (found during this feature's own first run:
   `docs/design/26-corpus-index.md` named "Maelstrom" as a worked example), **When** found,
   **Then** it is rewritten to generic language before this feature is complete.

### Edge Cases

- What about a percentage that is a defined constant, not a derived claim (e.g. the 25%
  skill-open value, the 70% career cap)? Out of scope for the coverage script — those are inputs
  the ruleset states, not outputs that could be computed wrong, and treating them as claims
  needing a backing script would be checking that a definition equals itself.
- What about `docs/design/20-journeys.md`'s "40% per leg" hazard-roll figure? It is exact by the
  document's own stated formula (`rating x 10` on `d100`) — not a claim combining multiple
  distributions the way an attrition figure does — so it needs no separate computation script.
- What if a future design change adds a new derived probability claim? `check_probability_coverage.py`'s
  own COVERAGE table is a closed, hand-maintained list (like `check_dangling_mechanics.py`'s own
  approach) — a new claim needs a new entry and a new backing script, the same discipline every
  prior probability feature in this repo already followed.
- What if a future setting is added to `settings.yaml` with a name that happens to be a common
  English word? `check_no_setting_vocabulary.py` excludes a short, hand-maintained
  too-generic list from its denylist for exactly this reason, tolerating the rare miss over a
  flood of false positives — the same posture `check_dangling_mechanics.py` already established.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A cross-reading pass MUST be performed over document pairs identified as describing
  one mechanic from two angles, checking for divergent restatements of the same fact.
- **FR-002**: Any divergence found by the cross-reading pass MUST be corrected before this feature
  is complete.
- **FR-003**: A script MUST exist that re-runs every backing computation for a derived probability
  claim published in `docs/design/` and exits non-zero if any fails.
- **FR-004**: A script MUST exist that exits non-zero if a setting or system name from
  `settings.yaml`'s catalogue appears in `docs/design/*.md` or `README.md`.
- **FR-005**: Any setting/system vocabulary found by the new script MUST be rewritten to generic
  language before this feature is complete.
- **FR-006**: `python3 tools/check_docs.py` and `python3 tools/backlog.py check` MUST still pass
  after this feature's changes.

### Key Entities

*(none — this feature adds two verification scripts and corrects prose; no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `python3 tools/check_probability_coverage.py` exits 0.
- **SC-002**: `python3 tools/check_no_setting_vocabulary.py` exits 0.
- **SC-003**: `python3 tools/check_docs.py` exits 0.
- **SC-004**: `python3 tools/backlog.py check` exits 0.
- **SC-005**: `python3 -m pytest -q` passes with no regression.
- **SC-006**: The cross-reading pass documented in `research.md` covers at minimum the two pairs
  the originating issue named (`03-rules.md`/`12-the-adversary.md` on combat;
  `07-transformations.md`/ADR 0029 on thresholds) plus the Stamina-recovery and crowd-rule pairs,
  with its findings recorded regardless of outcome (including "no divergence found").

## Assumptions

- This feature closes both #92 and, by being the last open child, Stage 13 (#52) — but **not**
  the parent epic #1, which the operator explicitly wants left open for a further review round
  after this PR merges. This feature's own scope ends at #92's acceptance criteria; closing #1 is
  an operator decision, out of scope here.
- The cross-reading pass is manual, judgment-driven work (reading prose against prose), recorded
  in `research.md` as a finding log — not a script, since "do two sentences describing the same
  fact agree" is not mechanically checkable the way a percentage or a link target is.
- No ADR is warranted: this feature adds verification tooling and corrects two found drifts
  (a stale/leaked setting name, in this case), it does not decide a new position on any mechanic
  with a real rejected alternative.
