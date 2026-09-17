# Tasks: Session friction capture

**Input**: Design documents from `/specs/171-session-friction-capture/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Not requested. This is a documentation-only feature (no code); validation is
`tools/check_docs.py` plus the manual worked-example check in quickstart.md, both covered by
Phase 4 below rather than a generated test suite.

## Phase 1: Setup

- [x] T001 Confirm `docs/design/16-session.md` is the correct edit target and note its current
      structure (Rally / session loop sections) so the new material lands adjacent to related
      per-beat bookkeeping — no file changes yet.

## Phase 2: Foundational

*No blocking prerequisites beyond Phase 1 — a single-document edit has nothing else to share
across user stories.*

## Phase 3: User Story 1 - GM records friction mid-beat without leaving the fiction (Priority: P1) 🎯 MVP

**Goal**: `docs/design/16-session.md` documents where the friction log lives, its entry format,
and that recording it never pauses player-visible narration.

**Independent Test**: A reader of the edited document alone can state the file path, the entry
format, and confirm nothing in the wording requires pausing the scene.

- [x] T002 [US1] Add a "Session friction capture" subsection to `docs/design/16-session.md`,
      placed near "The Rally" (both are per-beat, GM-side bookkeeping), stating the friction log's
      location as `log/friction.md` inside the chronicle repo's existing `log/` directory (FR-001).
- [x] T003 [US1] In the same subsection, specify the entry format: three required fields (mechanic
      or table implicated; what happened; what the GM did about it), plain Markdown, append-only,
      with one complete worked example (FR-002, FR-003).
- [x] T004 [US1] State explicitly, in the same subsection, that capture happens entirely on the
      GM's/engine's side of the fourth wall, costs no player-visible pause, and requires no
      confirmation step (FR-005, FR-007, FR-008).

## Phase 4: User Story 2 - Harvest can read entries without seeing the chronicle's story (Priority: P1)

**Goal**: The documented entry format and triage line ensure every entry is self-contained,
mechanical, and setting-agnostic, so a later harvest pass (#95) never needs narrative context.

**Independent Test**: Given a written entry following the documented format, a reader with zero
chronicle context can state which engine mechanic it concerns, with no setting name or narrative
detail present.

- [x] T005 [US2] In `docs/design/16-session.md`, state the triage line's three qualifying
      conditions (unpredicted reading of a documented mechanic; a correctly-applied mechanic
      producing a result that felt wrong; an undocumented case forcing improvisation) and that
      ordinary narrative color never qualifies on its own (FR-004).
- [x] T006 [US2] Add one worked example each of a qualifying friction note and a non-qualifying
      color note, phrased generically (values and outcome only, no chronicle-specific names or
      plot), directly answering issue #94's second acceptance criterion (FR-006).
- [x] T007 [P] [US2] Grep the new subsection for setting vocabulary or borrowed terms and confirm
      none appears, per `CLAUDE.md` "the engine is setting-agnostic" (FR-009).

## Phase 5: User Story 3 - Convention holds in solo, GM-plays-the-party play (Priority: P2)

**Goal**: Confirm and, if needed, adjust the wording so nothing in the convention assumes a
second real participant is present to notice friction.

**Independent Test**: Re-read the full new subsection and confirm every sentence describing who
notices/records friction names the GM (the engine, narrating) alone, never "a player" or "another
person at the table."

- [x] T008 [P] [US3] Review the subsection drafted in Phase 3/4 for any implicit assumption of a
      second real participant; rephrase any such sentence to name the GM/engine alone (FR-005).

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T009 Run `python3 tools/check_docs.py` and confirm it reports no new issues introduced by
      this edit (reachability, dead links, ADR index, link policy).
- [x] T010 Walk `specs/171-session-friction-capture/quickstart.md` end to end against the final
      wording of `docs/design/16-session.md` and confirm every validation step passes.
- [x] T011 Re-check `docs/design/16-session.md`'s new subsection against `CLAUDE.md`'s "Design
      documents are... rewritten in place" rule — no changelog language, no "previously..." notes.

## Dependencies & Execution Order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (Foundational) is empty for this feature.
- Phase 3 (US1) depends on Phase 1 only, and can begin immediately — it is the MVP slice.
- Phase 4 (US2) depends on Phase 3 landing the same subsection (both edit the same block of
  prose), so in practice T002-T006 are drafted together rather than as two separable diffs,
  even though the spec treats them as independently testable statements within the one document.
- Phase 5 (US3) is a review pass over the combined output of Phases 3-4.
- Phase 6 (Polish) depends on Phases 3-5 being complete.

## Parallel Execution Examples

- T007 (grep for setting vocabulary) and T008 (solo-play review) touch no other tasks' files
  mid-edit and can run in parallel once Phases 3-4's prose is drafted, since both are read-only
  review passes over the same finished text rather than edits themselves.

## Implementation Strategy

**MVP first**: Phase 3 (US1) alone already delivers a usable convention — a GM could start
recording friction entries in `log/friction.md` from that subsection alone. Phases 4-5 make the
entries usable by the future harvest step (#95) and confirm the solo-play case, both required by
this issue's own acceptance criteria before the feature is complete, but US1 is the standalone
MVP slice if this had to ship in stages.
