# Tasks: Out-of-character mode at play time

**Input**: Design documents from `specs/031-ooc-mode/`
**Prerequisites**: plan.md (required)

**Tests**: this feature is prose-only (see plan.md's "What the check script has to settle") —
there is no schema and no validator to write. Verification is the repo-wide reachability/dangling
guards plus a read-through against the spec's acceptance scenarios; no separate test suite
applies.

## Phase 1: Setup

- [X] T001 Confirm branch `031-ooc-mode` is checked out and
      `specs/031-ooc-mode/{spec.md,plan.md}` exist (already done by prior pipeline steps; no
      file changes).

## Phase 2: Foundational

- [X] T002 Write `docs/adr/0037-out-of-character-mode-is-a-prefix-trigger.md` recording the
      load-bearing fork: a one-character prefix trigger (`?`) vs. a slash command (`/ooc`),
      decided in favour of the prefix, with the rejected alternative and its reasoning (mirrors
      plan.md's "The load-bearing decision" section and the existing ADR format, e.g.
      `docs/adr/0036-one-configurable-power-mechanism.md`).

**Checkpoint**: ADR 0037 exists and is internally consistent with plan.md before the design
document depends on it.

## Phase 3: User Story 1 - Ask an out-of-character question mid-scene (Priority: P1)

**Goal**: A player can trigger OOC mode with `?`, get raw mechanical state on request, and
resume play with the fiction untouched.

**Independent Test**: read the design document's trigger/suspension/logging rules against the
spec's Acceptance Scenarios 1.1-1.2 and confirm both are satisfied by the written rule, with no
gap between "the response gives the number" and "nothing about the exchange enters the
chronicle."

- [X] T003 [US1] Create `docs/design/17-out-of-character-mode.md`: state the `?` trigger (FR-001,
      one character, prepended to the message), the suspension of the diegetic contract for
      that one response (FR-002, raw numbers on request — cross-referencing
      `docs/design/13-diegesis.md`'s existing "on request" line), and the chronicle-exclusion rule
      (FR-003) with the exact wording "nothing said out-of-character becomes established
      fiction" carried over from the issue's Definition of Done.
- [X] T004 [US1] Add the per-message scope rule to `docs/design/17-out-of-character-mode.md`
      (FR-006): OOC handling applies to the triggered message and the GM's one response; the
      next untriggered message returns to in-character handling automatically — no
      session-wide toggle.
- [X] T005 [US1] Add the separate-logging rule to `docs/design/17-out-of-character-mode.md`
      (FR-007, FR-008): OOC exchanges are excluded from the session's in-character narrative
      output and from the chronicle's fictional record, but are logged somewhere the player and
      GM can refer back to, distinct from that record; note the concrete storage location is an
      implementation decision deferred to whichever system later realises session logging (per
      plan.md's Technical Context).
- [X] T006 [US1] Add a worked example to `docs/design/17-out-of-character-mode.md` walking through
      the spec's own scenario: player sends `?what's my stamina`, GM responds with the exact
      number and the OOC marker (forward reference to T009), player's next message resumes the
      scene with no reference to the exchange.

**Checkpoint**: User Story 1 is independently complete — the trigger, suspension and
chronicle-exclusion rules are fully specified and internally consistent.

## Phase 4: User Story 2 - Ask whether the character would know something (Priority: P2)

**Goal**: In OOC mode, the GM can answer "would my character know this?" honestly, distinguishing
the character's in-fiction knowledge from the player's own knowledge of the narration.

**Independent Test**: read the answer-shape section against the spec's Acceptance Scenarios
2.1-2.2 and confirm both the "no, and here is what they'd believe instead" case and the "yes, at
their competence" case are covered, with the latter cross-referencing `docs/design/13-diegesis.md`'s
existing knowledge-source rule rather than restating it.

- [X] T007 [US2] Add the "would my character know this?" section to
      `docs/design/17-out-of-character-mode.md` (FR-004): the answer distinguishes the character's
      in-fiction knowledge from the player's own knowledge of the narration; where the character
      would not know something, the response says so and states what the character would
      believe or assume instead where answerable; where the character would know it, the answer
      is given at the character's scaled competence per `docs/design/13-diegesis.md`'s "the character
      as a knowledge source" section (cross-referenced, not restated).
    - [X] T007a [US2] In the same section, add the "never shown" boundary case: where the
      honest answer would reveal engine-hidden state or another character's information the
      player's own character has no path to (e.g. a hidden threshold, another character's
      motive), the response says plainly the answer isn't available, per
      `docs/design/13-diegesis.md`'s "never shown" visibility class — it does not fabricate an
      in-fiction justification.

**Checkpoint**: User Story 2 is independently complete — the knowledge-question answer shape is
fully specified and consistent with the existing diegetic knowledge-source rule.

## Phase 5: User Story 3 - See which mode is active at a glance (Priority: P3)

**Goal**: Every OOC response carries an unmistakable textual marker, and no in-character response
does.

**Independent Test**: read the marker section against the spec's Acceptance Scenarios 3.1-3.2 and
`docs/design/01-principles.md`'s "no engine scaffolding in narration" rule, confirming the marker is
distinguishable without being narrative-breaking scaffolding *within* in-character prose (it only
ever appears on an OOC response, never inside one).

- [X] T008 [US3] Investigate whether Claude Code exposes a hook or mechanism to change UI chrome
      (e.g. input box colour) from within a conversation turn, per the issue's "visible mode
      indication" acceptance criterion. Record the finding directly in
      `docs/design/17-out-of-character-mode.md` — if no such hook exists, say so plainly, matching
      the issue's own instruction to "say so plainly and fall back to an unmistakable textual
      marker."
- [X] T009 [US3] Add the textual-marker rule to `docs/design/17-out-of-character-mode.md` (FR-005):
      every GM response to an OOC-triggered message opens with an unmistakable textual marker
      (e.g. a leading `[OOC]` line); no in-character response ever carries it. Note this is
      mechanism, not voice — the exact wording is available to a setting's `rename:` block like
      any other engine label, per `CLAUDE.md`'s engine-labels rule.
- [X] T010 [US3] Add the edge-case handling to `docs/design/17-out-of-character-mode.md` covering the
      spec's Edge Cases: a bare `?` with no question prompts for what the player wants to know
      (still OOC-marked, never falling through to in-character play); an untriggered
      in-character knowledge question ("what do I know about this place?") is unaffected by this
      feature and continues to be answered in character per `docs/design/13-diegesis.md`; OOC mode is
      explicitly not a rewind/undo mechanism for established fiction (out of scope, per the
      issue).

**Checkpoint**: User Story 3 is independently complete — the mode is unambiguous to the player at
all times, and the feature's boundaries (what it does not do) are explicit.

## Phase 6: Polish & cross-cutting concerns

- [X] T011 [P] Add a one-line cross-reference in `docs/design/01-principles.md` at the point that
      currently implies everything typed is in-character speech and action, pointing to
      `docs/design/17-out-of-character-mode.md`.
- [X] T012 [P] Add a one-line cross-reference in `docs/design/13-diegesis.md` at "Mechanical detail is
      always available on request", pointing to `docs/design/17-out-of-character-mode.md` as where
      the request mechanism is specified.
- [X] T013 [P] Add a one-line cross-reference in `docs/design/16-session.md` noting OOC mode as the
      escape hatch that does not itself become part of a beat, pointing to
      `docs/design/17-out-of-character-mode.md`.
- [X] T014 [P] Add a link to `docs/design/17-out-of-character-mode.md` from `docs/README.md`'s
      index so `tools/check_docs.py`'s reachability check passes.
- [X] T015 [P] Run `python3 tools/check_docs.py` and confirm the new document is reachable and
      the ADR index picks up ADR 0037.
- [X] T016 [P] Run `python3 tools/check_dangling_mechanics.py` and confirm no dangling reference
      is introduced by the new document.
- [X] T017 [P] Run `python3 tools/backlog.py check` and confirm no drift.
- [X] T018 Run `ruff check . && ruff format --check . && python3 -m pytest -q` and confirm the
      repo-wide suite is green.
- [X] T019 Re-read `docs/design/17-out-of-character-mode.md` end to end for the recurring fault
      classes in `CLAUDE.md`'s checklist (setting vocabulary, tone baked into a mechanic, a
      stale claim against `01-principles.md`/`10-diegesis.md`) before raising the PR.

## Dependencies & execution order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (T002, the ADR) blocks every later phase — the trigger choice and its rejected
  alternative are decided there, not re-derived in the design document.
- Phase 3 (US1) depends only on Phase 2. It is the MVP: the trigger, suspension and
  chronicle-exclusion rules alone already satisfy the issue's core Definition of Done ("a player
  can ask for their exact Stamina, get a number, and resume play with the fiction untouched").
- Phase 4 (US2) depends on Phase 3 (T007 extends the same document T003-T006 created).
- Phase 5 (US3) depends on Phase 3 (the marker rule applies to the response format T006's worked
  example already shows) but not on Phase 4 — it can run in parallel with Phase 4 once Phase 3 is
  complete, since both extend the same document in independent sections.
- Phase 6 (Polish) depends on all prior phases.

## Parallel execution examples

- Phase 4 (US2) and Phase 5 (US3) can proceed in parallel once Phase 3 is complete, provided
  edits to `docs/design/17-out-of-character-mode.md` are sequenced to avoid conflicting writes to the
  same file.
- Within Phase 6: T011, T012, T013, T014 (cross-references, different files) and T015, T016, T017
  (independent read-only checks) can all run in parallel with each other; T018 and T019 should
  run after them.

## Implementation strategy

**MVP first**: Phase 1 + Phase 2 + Phase 3 (User Story 1) delivers the issue's core Definition of
Done — trigger, suspension, chronicle exclusion — before the knowledge-question answer shape
(Phase 4) and the visible-marker specification (Phase 5) are written up. Both later phases extend
the same document additively; neither requires revisiting Phase 3's text.
