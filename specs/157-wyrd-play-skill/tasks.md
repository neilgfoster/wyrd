# Tasks: The /wyrd-play skill

**Input**: Design documents from `specs/157-wyrd-play-skill/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/wyrd-play-skill.md, quickstart.md

**Tests**: Not requested for this feature -- the spec's own verification path is a manual
quickstart walkthrough against a real bootstrapped chronicle (research.md's "no automated test
harness" decision), matching how the four sibling skills were themselves verified.

**Organization**: This feature's deliverable is a single `SKILL.md` file, so tasks are organized
by the section of that file each user story's requirements land in, rather than by
model/service/endpoint layers. All tasks touch the same repository
(`wyrd-chronicle-template`, cloned/available alongside this `wyrd` checkout) except the final
verification and design-doc-sync tasks, which touch `wyrd`.

## Path Conventions

- Deliverable file: `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`
- Reference files (read-only, for convention-matching): `wyrd-chronicle-template/.claude/skills/{wyrd-character,wyrd-downtime,wyrd-end-session,wyrd-bootstrap}/SKILL.md`

---

## Phase 1: Setup

- [ ] T001 Create `wyrd-chronicle-template/.claude/skills/wyrd-play/` directory and confirm the
      four sibling skill directories' shape (`SKILL.md` only, no other files) to match.

## Phase 2: Foundational

- [ ] T002 Write `SKILL.md`'s YAML frontmatter (`name`, `description`, `user-invocable`,
      `disable-model-invocation`) and its "What this skill does" section in
      `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`, stating the code/prose split
      this skill honours (docs/design/02-architecture.md) and citing FR-007/FR-009's
      never-recompute rule, matching the sibling skills' own opening-section conventions.
- [ ] T003 Write the "Locating and calling the engine CLI" section in the same file, reusing
      the four sibling skills' identical `WYRD_PKG_DIR`/`PYTHONPATH` snippet verbatim
      (research.md's "locate the engine CLI" decision).

## Phase 3: User Story 1 - Resume and orient at the start of a session (Priority: P1)

**Goal**: Loading the Always-loaded tier, resuming a `pending` marker if present, and orienting
the player in prose with no option menu and no exposed engine scaffolding.

**Independent Test**: quickstart.md steps 1-3.

- [ ] T004 [US1] Write the "Step 0 -- guard: is this chronicle bootstrapped?" section in
      `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`: check `chronicle.yaml`
      exists, and if not, state so plainly and stop without calling any verb (FR-002),
      matching `wyrd-bootstrap`'s own Step 0 guard convention.
- [ ] T005 [US1] Write the "Step 1 -- load the Always-loaded tier" section: call
      `session-context --chronicle-dir .` exactly once, and state that its returned
      `player_character`, `companions`, `threads`, `recap`, and `contract` are the *only*
      source for the orientation narration (FR-003, contracts/wyrd-play-skill.md).
- [ ] T006 [US1] Write the "Step 2 -- resume a pending marker" section: if `chronicle.yaml`'s
      `pending` field is non-null, resume exactly `pending.awaiting` before offering any new
      beat, rather than starting fresh (FR-004, data-model.md's `pending` row).
- [ ] T007 [US1] Write the "Step 3 -- orient the player" section: narrate in prose what
      changed and where the character is, explicitly listing the engine-scaffolding items that
      must never appear (thread ids, beat labels, difficulty numbers, Tension/Bond values,
      per docs/design/01-principles.md) and stating no option menu is ever presented (FR-005,
      FR-006).

**Checkpoint**: quickstart.md steps 1-3 pass in isolation (cold-start guard, orientation,
pending resumption) before Phase 4 begins.

## Phase 4: User Story 2 - Run a beat with code-backed resolution (Priority: P1)

**Goal**: Resolving the player's declared action through the correct existing engine verb for
every mechanical step, narrating only from each verb's own returned result.

**Independent Test**: quickstart.md steps 4-5.

- [ ] T008 [US2] Write the "Step 4 -- resolve a skill test" section: call `propose`
      (`mechanic=ordinary-test` or `combat-attack`) or `opposed-test` as appropriate (per
      research.md's verb-mapping table), narrate strictly from the returned result, and
      `commit` or `discard` depending on whether the outcome is accepted into the fiction
      (FR-007, FR-009, contracts/wyrd-play-skill.md's propose/commit/discard row).
- [ ] T009 [US2] Write the "Step 5 -- declaration bonuses" section: for a specific,
      in-character detail that plausibly earns a bonus, call `declaration-bonus --category <c>`
      and use its returned value verbatim, never deriving one from length or style (FR-008).
- [ ] T010 [US2] Write the "Step 6 -- track changes, elapsed time, and threat checks outside a
      propose cascade" section: call `track`, `advance-time`, or `threat-check` as the beat's
      fiction calls for, per research.md's verb table, never computing any of their arithmetic
      in prose (FR-007).
- [ ] T011 [US2] Write the "Step 7 -- when no roll is warranted" section: state explicitly that
      an action with no real uncertainty and no opposition is narrated in prose with no
      `propose`/`opposed-test` call invented for it (edge case from spec.md).

**Checkpoint**: quickstart.md steps 4-5 pass; Phase 3's orientation flow still passes
unmodified (US1 and US2 are additive, not overlapping, sections of the same file).

## Phase 5: User Story 3 - Leave valid, saved state at every stopping point (Priority: P2)

**Goal**: Closing a beat cleanly with a Rally and a save, or writing an accurate `pending`
marker if the player must stop mid-beat -- persisting before narrating in both cases.

**Independent Test**: quickstart.md steps 6-7.

- [ ] T012 [US3] Write the "Step 8 -- close the beat cleanly" section: call `rally` (fixed
      Strain/Stamina recovery, discard of any leftover open proposal, optional advance award),
      then `save`, and state explicitly that the closing narration is shown only after `save`
      succeeds (FR-010, docs/design/01-principles.md principle 2), matching
      `wyrd-end-session`'s own Step 2/Step 3 ordering convention.
- [ ] T013 [US3] Write the "Step 9 -- stopping mid-beat" section: if the player must stop
      before the current action resolves, write a `pending` marker naming the beat and the
      unresolved action, `save` it, and state plainly that no outcome is fabricated to force a
      clean stopping point instead (FR-011), matching `wyrd-end-session`'s own `pending:`
      convention verbatim.
- [ ] T014 [US3] Write the "Step 10 -- confirm valid state" section: call
      `validate --chronicle-dir .` at the end of every invocation and state that a non-clean
      result must be reported to the player rather than silently accepted (FR-012, SC-003).

**Checkpoint**: quickstart.md steps 6-7 pass; all three user stories' sections coexist in one
coherent `SKILL.md` without contradicting each other's step numbering.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T015 [P] Write the closing "Never" section in
      `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`, listing (at minimum):
      recomputing a roll/degree/mutation the CLI already returned; presenting an option menu;
      exposing a thread id/beat id/difficulty number/Tension/Bond value in narration; committing
      a proposal before its outcome is known; narrating before `save` succeeds; performing
      character creation, downtime, or end-session compaction (FR-014) -- matching the sibling
      skills' own closing-"Never"-section convention.
- [ ] T016 Read the finished `SKILL.md` end-to-end and confirm quickstart.md's step 8
      (setting-agnostic prose check): no setting- or system-specific name appears anywhere in
      the skill's own prose or examples (FR-013, SC-005).
- [ ] T017 Run the full quickstart.md walkthrough (all 8 steps) against a real bootstrapped
      chronicle in `wyrd-setting-darkfuture` or `wyrd-setting-titan`, recording the result of
      each step; note #411 (career skill-cap shape) as already-tracked if hit, without
      re-diagnosing it (per the issue's own known-issue guidance).
- [ ] T018 [P] In this `wyrd` repository, confirm no `docs/design/` document needs updating --
      `16-session.md` and `02-architecture.md` already specify this skill's behaviour and are
      unchanged by this feature (per plan.md's Constitution Check); if T017's walkthrough
      surfaces a genuine design-document/reality mismatch, update the design document per
      CLAUDE.md's "update the design document when the change lands" rule.

## Dependencies & Execution Order

- **Phase 1 (Setup)** blocks Phase 2.
- **Phase 2 (Foundational)** blocks all user story phases -- every step below Step 0 depends on
  the CLI-location convention (T003) already being in the file.
- **User Story 1 (Phase 3)** has no dependency on US2/US3 and is independently testable
  (quickstart steps 1-3) once T001-T007 are done.
- **User Story 2 (Phase 4)** depends on US1's orientation being in place (a beat is declared
  only after orientation), but does not depend on US3.
- **User Story 3 (Phase 5)** depends on US2 existing (there is nothing to close or leave
  `pending` on until a beat has been attempted), but its own steps (T012-T014) do not depend on
  which specific mechanic US2 resolved.
- **Polish (Phase 6)** runs only after all three user story phases are complete -- T017 in
  particular exercises the whole file end-to-end.

```
Setup (T001) → Foundational (T002-T003) → US1 (T004-T007) → US2 (T008-T011) → US3 (T012-T014) → Polish (T015-T018)
```

Within Phase 6, T015/T018 are marked [P] (independent files/concerns); T016 and T017 are
sequential (T016 reads the file T015 just finished; T017 exercises the whole finished file).

## Implementation Strategy

**MVP scope**: Phases 1-4 (Setup, Foundational, US1, US2) already deliver a `/wyrd-play` that
orients the player and runs a mechanically-correct beat -- the two P1 stories. Phase 5 (US3,
P2) adds the persistence/pending-marker guarantees that make repeated invocation and clean
handoff to `/wyrd-end-session` safe, and should land in the same PR given how small this
feature is (one file), but is called out separately here because it is a distinct acceptance
criterion or reviewer could otherwise reasonably question when a Rally's write ordering was
actually specified.

**Incremental delivery**: because all three user stories are sections of one file, they are
delivered together in practice (T001-T014 before opening a PR) rather than as separate
merges -- the "independently testable" property named per story exists so quickstart.md can
verify each concern in isolation, not so each ships alone.
