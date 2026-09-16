# Tasks: Haiku corpus fact-finder subagent for create-setting

**Input**: Design documents from `specs/169-haiku-corpus-fact-finder/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (all present)

**Tests**: Not requested in the feature specification — `wyrd-setting-template` has no CI/test
suite; verification is the manual quickstart.md walkthrough (Phase 6 below).

**Organization**: Tasks are grouped by user story from spec.md. All implementation happens in the
sibling repository `wyrd-setting-template` (not this repo, `wyrd`), per plan.md's Project
Structure and the established precedent for this feature family.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)

## Path Conventions

All file paths below are relative to a checkout of `wyrd-setting-template`
(sibling to this `wyrd` checkout unless otherwise located).

---

## Phase 1: Setup

- [ ] T001 Confirm a `wyrd-setting-template` checkout is available and create/checkout a working
      branch there for this change (mirroring this repo's `169-haiku-corpus-fact-finder` branch
      name is fine but not required, since that repo has no Spec Kit substrate).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Nothing here blocks either user story — this feature has no shared infrastructure
beyond the two files touched. This phase is intentionally empty; proceed directly to Phase 3.

---

## Phase 3: User Story 1 - Delegate a single fact-grounding lookup to Haiku (Priority: P1) 🎯 MVP

**Goal**: A real `.claude/agents/` Haiku subagent definition exists, scoped to mechanical corpus
fact-finding/verification, per data-model.md's "Haiku corpus fact-finder subagent definition"
entity.

**Independent Test**: Read the subagent definition file on its own (quickstart.md Step 1) and
confirm it declares `model: haiku`, a `tools` list of `Read, Grep, Glob` only, and a body that
describes retrieval-and-reporting only, with no content-writing instruction.

### Implementation for User Story 1

- [ ] T002 [US1] Write `.claude/agents/corpus-fact-finder.md` in `wyrd-setting-template`, with
      frontmatter `name: corpus-fact-finder`, a one-sentence `description` naming the closed
      retrieval task and when to invoke it, `tools: Read, Grep, Glob`, and `model: haiku`, per
      data-model.md's frontmatter table.
- [ ] T003 [US1] Write the subagent's body (system-prompt instructions) stating: its one job
      (given a claim and a corpus location, find and report the exact supporting/contradicting
      quote and source location, or report not-found); the three possible outcomes and their
      required output shape (quote text, exact file path, line number or nearest identifiable
      location); what it must never do (invent, paraphrase, or approximate a quote; write setting
      content; judge whether a claim is acceptable to keep); and how to distinguish "no corpus
      text available to search" from "searched and found nothing," per data-model.md's Interface
      section.

**Checkpoint**: User Story 1 is independently testable now — quickstart.md Step 1 and (if
feasible) Step 3's dry run can both run against this file alone, before touching
`create-setting`.

---

## Phase 4: User Story 2 - create-setting's own tier is declared and the ceiling is capped (Priority: P2)

**Goal**: `create-setting`'s `SKILL.md` frontmatter declares `model: sonnet`.

**Independent Test**: Read `create-setting/SKILL.md`'s frontmatter alone (no dependency on User
Story 1 or 3) and confirm `model: sonnet` is present.

### Implementation for User Story 2

- [ ] T004 [P] [US2] Add `model: sonnet` to
      `.claude/skills/create-setting/SKILL.md`'s existing frontmatter block in
      `wyrd-setting-template`, alongside the existing `name`/`description`/`argument-hint`/
      `user-invocable`/`disable-model-invocation` fields, changing nothing else in the
      frontmatter.

**Checkpoint**: User Stories 1 and 2 both independently verifiable now.

---

## Phase 5: User Story 3 - Phase 3/4's mechanical lookups are rewritten to delegate, prose stays put (Priority: P1)

**Goal**: `create-setting`'s Phase 3 and Phase 4 name the `corpus-fact-finder` subagent for every
claim-grounding/verification step, while every prose-writing/register-synthesis step stays
attributed to the invoking skill, with the reasoning for that boundary written into the file.

**Independent Test**: Re-read the full updated Phase 3/4 flow (quickstart.md Step 2) and confirm
every sentence classifies cleanly as either a delegated lookup or a judgement step, per spec.md
Acceptance Scenarios 1-4 for this story.

**Depends on**: T002/T003 (User Story 1) — Phase 3/4's rewritten text names the subagent by name,
so the subagent file should exist first, though the prose changes themselves touch a different
file and could be drafted in parallel if desired.

### Implementation for User Story 3

- [ ] T005 [US3] Rewrite Phase 3's claim-grounding instructions in
      `.claude/skills/create-setting/SKILL.md` (the "For every specific claim... ground it in
      this setting's actual corpus/ text" paragraph and its surrounding numbered steps) to
      describe invoking the `corpus-fact-finder` subagent with the specific claim and the
      relevant corpus location, and using its returned outcome (support/contradict/not-found) to
      decide what to write and how to label it — per research.md's "where Phase 3/4 delegate
      versus where they don't" decision.
- [ ] T006 [US3] Leave and, where useful, sharpen Phase 3's prose-writing/register-synthesis
      instructions (voice.md's register, career/gear/bestiary/entity content composition, hedging
      on thin or ambiguous sources) as explicitly invoking-skill work — do not move any of this
      text into the subagent-delegation rewrite from T005.
- [ ] T007 [US3] Rewrite Phase 4's grep-verification spot-check paragraph in the same file to
      describe invoking `corpus-fact-finder` with the claimed quote/fact and its stated source
      location, instead of running `grep -rn` inline, reusing the same three-outcome contract as
      T005.
- [ ] T008 [US3] Add a short, explicit statement to `create-setting/SKILL.md` (near the top,
      alongside the existing governing rule, or at the start of Phase 3) documenting why the
      mechanical-fact-finding/judgement boundary sits where it does — citing
      `docs/design/27-tooling.md` section 5's tiering table — so a future reader does not have to
      reconstruct the reasoning (FR-008).
- [ ] T009 [US3] Re-read Phase 1, Phase 0, and Phase 2 of `create-setting/SKILL.md` to confirm
      they were not touched by T005-T008, and that the existing governing rule and Phase 1's
      web-research/original-invention labelling language are unchanged verbatim (FR-009).

**Checkpoint**: All three user stories independently functional; the split documented in
spec.md's User Story 3 and FR-008 is satisfied.

---

## Phase 6: Polish & Verification

**Purpose**: Confirm the whole feature holds together, per quickstart.md.

- [ ] T010 Run quickstart.md Step 1 (read the subagent definition alone) and Step 2 (read the
      full Phase 3/4 flow) and confirm both expected outcomes (SC-001, SC-002).
- [ ] T011 If a `wyrd-setting-*` repository with extracted `corpus/` text is available (e.g.
      darkfuture or titan), run quickstart.md Step 3's manual dry run: one known-supported claim,
      one known-unsupported claim, confirming SC-003.
- [ ] T012 Run quickstart.md Step 4: diff the rewritten `SKILL.md` against its previous version
      and confirm nothing beyond T004-T008's scope changed.
- [ ] T013 [P] Update `wyrd` (this repo)'s own PR body/spec trail to reference the corresponding
      `wyrd-setting-template` PR once opened, per this feature's split-repository precedent.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Empty — nothing blocks the user stories.
- **User Story 1 (Phase 3)**: Can start immediately after Setup.
- **User Story 2 (Phase 4)**: Can start immediately after Setup, fully independent of User Story 1
  (different file, no shared text).
- **User Story 3 (Phase 5)**: Best done after User Story 1 exists (T002/T003), since its rewritten
  text names the subagent by name — but does not depend on User Story 2's frontmatter change.
- **Polish (Phase 6)**: Depends on all three user stories being complete.

### Parallel Opportunities

- T004 (US2) can run in parallel with T002/T003 (US1) — different files.
- T013 can run in parallel with T010-T012 — different concern (this repo's own PR trail vs. the
  setting-template repo's content).

---

## Implementation Strategy

### MVP First

1. Complete Phase 1: Setup.
2. Complete Phase 3: User Story 1 (the subagent definition) — this alone proves FR-001/FR-002/
   FR-003 and is independently reviewable.
3. Complete Phase 4: User Story 2 (the frontmatter cap) — trivial, independent, can land alongside
   or after User Story 1.
4. Complete Phase 5: User Story 3 (the Phase 3/4 rewrite) — the actual behaviour change the issue
   asks for, and the piece that makes User Story 1's subagent load-bearing rather than unused.
5. Complete Phase 6: Polish & Verification.

### Incremental Delivery

Given the small size of this feature (two files, one new, one edited, in one repository), all
three user stories are delivered together in a single PR against `wyrd-setting-template` rather
than staged across multiple PRs — but the task breakdown above still lets each story be reviewed
and verified independently within that one PR's diff.

---

## Notes

- No test tasks: `wyrd-setting-template` has no CI/test suite (per plan.md's Technical Context);
  verification is the manual quickstart.md walkthrough in Phase 6.
- This repo's (`wyrd`) own deliverable is exactly this `specs/169-haiku-corpus-fact-finder/`
  documentation trail — no source-code tasks apply here, per plan.md's Structure Decision.
- Avoid: moving any prose-writing/register-synthesis instruction into the subagent's body (T003)
  or into the delegation rewrite (T005) — that would violate FR-007/the issue's explicit
  constraint.
