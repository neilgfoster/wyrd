# Tasks: Career graph — skill counts and succession

**Input**: Design documents from `/specs/035-career-graph/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: not requested — documentation-only feature (spec FR-009). Validation is
`tools/check_docs.py` plus the manual worked-example proof in `quickstart.md`.

**Organization**: tasks are grouped by user story from spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: which user story this task belongs to (US1, US2, US3)

## Phase 1: Setup

- [x] T001 Confirm branch `035-career-graph` is checked out and `specs/035-career-graph/` design
      docs (plan.md, research.md, data-model.md, quickstart.md) are present and committed-ready

## Phase 2: Foundational

None — this feature edits existing prose sections in two already-existing design documents;
there is no shared scaffolding to stand up before the user stories.

## Phase 3: User Story 1 — A setting author declares a career graph (P1)

**Goal**: `26-authoring-a-setting.md` states exactly what a career declares (identifier, skill
list, entry-point flag, prerequisite) so an author can write any career unambiguously.

**Independent Test**: per quickstart.md's worked example, an author can write both an entry
career and a dependent non-entry career and state their full shape with no invented fields.

- [x] T002 [US1] Rewrite the `careers.yaml` description in
      `docs/design/24-authoring-a-setting.md` to state the career-graph structure: identifier,
      `skills` (setting-defined length per career, not fixed — research.md), `entry` flag, and
      `prerequisites` (required, length >= 1, when `entry` is false, absent when `entry` is true;
      OR semantics -- completing any one qualifies),
      per `data-model.md`
- [x] T003 [US1] Add the validity rules to the same section: at least one entry career required
      (already stated in `05-character-creation.md`, cross-referenced here), at least one
      prerequisite per non-entry career (OR semantics -- a multi-entry list is the zigzag case),
      the prerequisite graph must be acyclic, and every prerequisite must name an existing
      career — all as setting-authoring validation expectations (research.md's cardinality and
      cycle-policy decisions)

**Checkpoint**: `26-authoring-a-setting.md` alone is enough to write a legal `careers.yaml` entry
of either kind.

## Phase 4: User Story 2 — A player reads what "completing" a career means (P2)

**Goal**: `05-character-creation.md` states the completion definition and ties the existing
Stamina bonus and the new eligibility rule to it.

**Independent Test**: given a character's advance history inside a career, completion resolves
to yes/no per the worked example in quickstart.md steps 2–4.

- [x] T004 [US2] In `docs/design/11-character-creation.md`, add the completion definition next
      to the existing "+1 maximum Stamina" bonus text: a career is complete for a character when
      every skill it grants has been opened and raised to the career's cap (data-model.md's
      derived-state section)
- [x] T005 [US2] In the same document, state the eligibility rule for a non-entry career: a
      character may choose it once any one of its declared prerequisites (per T002) is complete
      for that character, per the completion definition in T004

**Checkpoint**: both the Stamina bonus and career eligibility now cite one shared, checkable
completion definition — no separate or conflicting notion of "completing a career" remains
anywhere in the corpus.

## Phase 5: User Story 3 — The dead cross-reference resolves (P3)

**Goal**: the link in `05-character-creation.md` that currently points at `27-entities.md` for
"the setting's career graph" resolves to real content.

**Independent Test**: following the link lands on the career-graph definition written in T002/T003.

- [x] T006 [US3] In `docs/design/11-character-creation.md`, change the "the setting's career
      graph" cross-reference from `27-entities.md` to point at the `careers.yaml` section of
      `26-authoring-a-setting.md` (the section rewritten in T002)

**Checkpoint**: no dead cross-reference remains for the career graph.

## Phase 6: Polish & cross-cutting

- [x] T007 [P] Run `python3 tools/check_docs.py` and confirm it passes with no dead links or
      reachability failures introduced by T002–T006 (SC-003)
- [x] T008 Walk through `quickstart.md`'s worked example end-to-end against the edited prose and
      confirm every step in it resolves to exactly one answer with no invented rule (SC-001,
      SC-002)
- [x] T009 Diff `26-authoring-a-setting.md`'s career-graph field list (T002) against
      `data-model.md`'s `Career` table field-for-field to confirm they match exactly (SC-004)

## Phase 7: Revision — zigzag/generalist support (post-PR feedback)

**Goal**: widen `prerequisite` (singular, exactly-one) to `prerequisites` (plural, OR semantics)
so a career can converge from more than one ladder — the mechanism a specialist/generalist
distinction needs (research.md's revised cardinality decision).

- [x] T010 Update `research.md`'s prerequisite-cardinality and cycle-policy decisions,
      `data-model.md`'s `Career` table and validity rules, `spec.md`'s FR-005/edge cases/Story 1
      acceptance scenarios, `quickstart.md`'s worked example, and this file's US1 task text — all
      from singular `prerequisite`/exactly-one to plural `prerequisites`/OR-semantics
- [x] T011 Rewrite the `careers.yaml` example and prose in `docs/design/24-authoring-a-setting.md`
      to use `prerequisites` (a list, OR semantics) with a convergence example (two entry
      careers both feeding one non-entry career)
- [x] T012 Re-run `python3 tools/check_docs.py` and re-walk `quickstart.md`'s (updated) worked
      example to confirm SC-001–SC-004 still hold under the widened cardinality

## Dependencies

- T001 (Setup) has no dependencies.
- **US1** (T002, T003) depends only on T001. T003 depends on T002 (same section, sequential
  edit).
- **US2** (T004, T005) depends on T002 (needs the `prerequisites` field named in prose to write
  the eligibility rule against) but not on T003. T005 depends on T004.
- **US3** (T006) depends on T002 (the destination section must exist before the link can point
  at it).
- **Polish** (T007–T009) depends on T002–T006 all being complete.

## Parallel execution examples

- T002 and T004 touch different files (`26-authoring-a-setting.md` vs.
  `05-character-creation.md`) but T004's eligibility half (T005) needs T002's `prerequisites`
  field to exist first — so within a single pass, do T002 before starting T004/T005, but T003
  and the *drafting* of T004's completion-definition text (which does not need T002) can proceed
  together.
- T007 and T009 are independent checks over the finished prose and can run in parallel with each
  other once T002–T006 land; T008 is a manual read-through and can run alongside them.

## Implementation strategy

**MVP = User Story 1 alone (T001–T003)**: a setting author can write a legal career graph. US2
and US3 are both small, low-risk follow-ons over the same two files and are included in this
same pass rather than deferred, since the whole feature is a single coordinated documentation
edit — splitting it across separate PRs would leave the cross-reference dangling (US3) or the
Stamina-bonus text stale (US2) in the interim.
