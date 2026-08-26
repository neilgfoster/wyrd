# Feature Specification: Move the design documents under doc/ and settle numbering

**Feature Branch**: `033-doc-move-and-numbering`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Move the design documents under doc/ and settle the numbering convention" (issue #38)

## Clarifications

### Session 2026-08-26

- Q: Should closed features' `specs/*/*.md` files have their `design/` references rewritten
  too, or left as historical record? → A: Initially "left alone" (a spec documents what was
  true when written; git holds the history). Revisited once implementation hit a pre-existing
  rule this decision conflicted with: `tools/check_docs.py` already enforces that `specs/` is
  exempt from *reachability* but never from *link rot* (a real, prior test,
  `test_dead_link_inside_specs_is_still_caught`). Leaving `specs/*/*.md`'s `design/` paths
  unrepaired would make every one of them report as a dead link forever. Final answer: repair
  only the literal path token in each `specs/*/*.md` reference (old file → new location),
  exactly the same posture as the ADR-link decision below — never touching a spec's prose,
  reasoning, or any non-path content.
- Q: Target layout? → A: Nested, with ADRs promoted to a sibling: `doc/design/*.md` and
  `doc/adr/*.md` (not `doc/design/adr/`).
- Q: Flatten the `03a`/`03a-2` inserts, or formalize the hierarchy they encode? → A: Flatten
  fully to a single reading-order sequence (`01`-`30`); the annex relationship becomes ordering
  only, not filename structure.
- Q: May a path inside an accepted ADR be repaired for this move? → A: Yes — an ADR's reasoning
  is immutable; a relative link inside it that breaks because a file moved is repaired like any
  other link in the repo. Recorded as a new ADR so it is never re-asked.
- Q: (Discovered during specification, not anticipated by the issue) `README.md`'s "Read in this
  order" table is itself stale — missing `03a-5-oracle-answers.md`, `03a-6-oracle-prompts.md`,
  and `04a-out-of-character-mode.md` (present on disk, reachable via other links, absent from the
  curated table). → A: Confirmed with the operator; the flattened order slots them in by their
  filename's implied position (`03a-5`/`03a-6` between `03a-4` and `03a-7`; `04a` between `04`
  and `05`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read the design in one place, in the right order (Priority: P1)

Someone opens the repository and reads the design documents in the order the engine is meant to
be understood, without the filename scheme itself carrying stale artifacts of past insertions.

**Why this priority**: This is the actual deliverable — everything else (link rewriting, the
check script) exists to make this safe and to keep it true.

**Independent Test**: `doc/design/` contains thirty sequentially-numbered documents; reading them
in filename order matches the intended understanding order (the corrected version of `README.md`'s
own table).

**Acceptance Scenarios**:

1. **Given** the current `design/` tree, **When** the move completes, **Then** every document
   exists under `doc/design/` (or `doc/adr/` for decision records) with a flat two-digit number,
   `03a-1-criticals.md` through `03a-7-systems-of-power.md` no longer carrying letter-then-number
   notation.
2. **Given** the corrected order, **When** `README.md`'s reading-order table is read, **Then** it
   lists all thirty documents, including the three previously missing from it.
3. **Given** `doc/adr/*.md`, **When** the move completes, **Then** every ADR exists under
   `doc/adr/` with its original number unchanged (ADR numbers are historical identifiers, not
   reading-order positions, and are never renumbered).

---

### User Story 2 - Nothing that pointed at the old location breaks (Priority: P1)

Every live reference — `README.md`, `CLAUDE.md`, every script under `tools/`, and every open
GitHub issue that cites a `design/` path — resolves to the document's new location.

**Why this priority**: Equal priority to User Story 1: a move that breaks navigation is not a
completed move, it is a regression wearing the first story's success.

**Independent Test**: `tools/check_docs.py` (updated for the new root) reports zero dead links;
grepping every open issue's cited path against the new tree finds a match.

**Acceptance Scenarios**:

1. **Given** every relative link inside the moved tree, **When** the move completes, **Then**
   every one resolves (`git mv` preserves the tree's internal relative structure for `doc/design/`
   internally, and cross-references to `../adr/...` are repaired for the new sibling layout).
2. **Given** `README.md` and `CLAUDE.md`'s references to `design/...` paths, **When** the move
   completes, **Then** both are rewritten to their `doc/design/...` or `doc/adr/...` equivalents.
3. **Given** the eighteen `design/`-referencing lines across `tools/`, **When** the move
   completes, **Then** every one is rewritten and every affected script still runs correctly.
4. **Given** the currently-open GitHub issues citing a `design/` path (with or without a line
   number), **When** the move completes, **Then** each such issue's body is updated to the new
   path; a citation with a line number is flagged rather than silently guessed if the line moved.
5. **Given** `specs/*/*.md`'s existing `design/` path references, **When** the move completes,
   **Then** each path token is repaired to its new location — but no other content in any
   `specs/*/*.md` file is touched, so the record of what each feature specified is otherwise
   unchanged.

---

### User Story 3 - Drift cannot creep back in unnoticed (Priority: P2)

Once moved, a broken relative link inside `doc/` or an ADR missing from the index fails a script,
the same way a stale board or a stale settings catalogue now does.

**Why this priority**: Second priority because it protects the outcome of User Stories 1-2 going
forward rather than delivering the move itself — but the issue is explicit that this is "the
durable win," since the equivalent gap (a stale ADR index) already went unnoticed once.

**Independent Test**: Run the check against the corrected tree for a clean pass; delete one link
target or remove one ADR from the index and get a reported failure.

**Acceptance Scenarios**:

1. **Given** the corrected `doc/` tree, **When** the check runs, **Then** it reports no dead
   relative links and no ADR missing from the index.
2. **Given** a deliberately broken relative link inside `doc/`, **When** the check runs, **Then**
   it is reported.
3. **Given** an ADR file present on disk but absent from the index, **When** the check runs,
   **Then** it is reported — this is `tools/check_docs.py`'s existing behavior, retargeted at the
   new root, not new behavior.

### Edge Cases

- What happens to a `design/`-path citation inside a *closed* issue? Left alone entirely, unlike
  `specs/*/*.md` (User Story 2, Scenario 5) — a closed issue is not read by `tools/check_docs.py`
  at all, so there is no link-rot check forcing a repair the way there is for `specs/`.
- What happens to an open issue's citation that includes a line number
  (`doc/design/26-authoring-a-setting.md:157`)? The path is rewritten; the line number cannot survive
  a document rename with content otherwise unchanged in position, so it is flagged in the issue
  update as "line reference may have shifted" rather than silently kept or silently dropped.
- What happens to a relative link that already lives inside an ADR and breaks because its target
  moved? Repaired, per the Clarifications' ADR-link decision — recorded as its own new ADR so the
  policy is written down, not re-litigated per broken link.
- What happens to `doc/README.md` itself, which currently describes both `design/*.md` and
  `doc/adr/*.md` as a pair? It moves to `doc/README.md` — the natural hub once the two
  subtrees (`doc/design/`, `doc/adr/`) are siblings, not a design-only document — and
  `tools/check_docs.py`'s `ADR_INDEX` constant is retargeted there.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every document currently under `design/*.md` MUST exist under `doc/design/` after
  the move, renumbered to a flat, gap-free sequence reflecting the corrected reading order.
- **FR-002**: Every document currently under `doc/adr/*.md` MUST exist under `doc/adr/` after
  the move, keeping its original ADR number unchanged.
- **FR-003**: `doc/README.md` MUST move to `doc/README.md`, retaining its role as the hub
  describing the `doc/design/` vs `doc/adr/` distinction and indexing every ADR.
- **FR-004**: All 199 relative links internal to the moved tree MUST resolve after the move,
  including any `design/*.md` ↔ `doc/adr/*.md` cross-reference now crossing a sibling boundary
  (`doc/design/` ↔ `doc/adr/`) rather than a parent-child one.
- **FR-005**: `README.md` and `CLAUDE.md`'s references to the moved paths MUST be rewritten to
  the new locations.
- **FR-006**: Every `design/`-referencing line in `tools/*.py` MUST be rewritten to the new
  location, and every affected script MUST still pass its own tests afterward.
- **FR-007**: Every currently-open GitHub issue that cites a `design/` path MUST have that
  citation rewritten to the new path; one that also cites a line number MUST be flagged as
  possibly stale on the line rather than silently corrected.
- **FR-008**: Every `design/`-path token inside a `specs/*/*.md` file MUST be repaired to its new
  location (`tools/check_docs.py`'s existing dead-link check applies to `specs/` and must keep
  passing); no other content in any `specs/*/*.md` file — prose, reasoning, structure — MUST be
  touched.
- **FR-009**: No relative-link rewrite MUST be performed by unverified bulk find-and-replace; each
  rewrite MUST be produced by parsing the link and substituting a known old→new path mapping, and
  the result MUST be grepped for word-level corruption afterward (`CLAUDE.md`'s three recorded
  corruptions from exactly this kind of mistake).
- **FR-010**: All `git mv` operations MUST be used for the moves so file history remains
  followable by `git log --follow`.
- **FR-011**: A link-check script MUST fail when a relative link inside `doc/` is dead, or when
  an ADR file exists on disk with no entry in `doc/README.md`'s index — retargeting
  `tools/check_docs.py`'s existing checks at the new root rather than writing new ones.
- **FR-012**: The ADR-link-repair decision (Clarifications) MUST be recorded as a new ADR.

### Key Entities

- **Design document**: one file under `doc/design/`, identified by its flat sequence number.
- **Decision record (ADR)**: one file under `doc/adr/`, identified by its historical number,
  independent of reading-order position.
- **Reference**: a citation of a `design/...` path in `README.md`, `CLAUDE.md`, `tools/`, or an
  open issue body — the set this feature updates. A citation in `specs/` or a closed issue is
  explicitly out of scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `doc/design/` holds thirty flatly-numbered documents and `doc/adr/` holds every
  ADR under its original number; nothing remains under the old `design/` path.
- **SC-002**: `tools/check_docs.py`, retargeted at `doc/`, reports zero dead links and a complete
  ADR index in one run.
- **SC-003**: Every currently-open issue citing a `design/` path resolves to the correct new file
  after the update.
- **SC-004**: A `git log --follow doc/design/<any file>` on any moved document reaches its
  pre-move history.
- **SC-005**: A grep for common substitution-corruption patterns (mangled words) across every
  file this feature touches finds none.

## Assumptions

- The 133 `specs/*/*.{md,py}` files referencing `design/` paths get a path-only repair (see
  Clarifications) — rewriting a spec's prose or reasoning for a later reorganization would be
  scope creep, but leaving the path dead would violate `tools/check_docs.py`'s existing,
  pre-dating-this-feature rule that `specs/` is checked for link rot.
- "Currently open" issues are evaluated once, at implementation time; an issue opened after this
  feature merges is expected to already cite the new path.
- The three files missing from `README.md`'s existing reading-order table
  (`03a-5-oracle-answers.md`, `03a-6-oracle-prompts.md`, `04a-out-of-character-mode.md`) are
  slotted into the flattened sequence by their filename's implied position, confirmed with the
  operator during specification.
- `doc/README.md`'s move to `doc/README.md` is itself a `git mv`, preserving its history.
