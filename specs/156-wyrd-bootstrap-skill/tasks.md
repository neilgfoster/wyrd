# Tasks: Wyrd bootstrap skill

**Input**: Design documents from `/specs/156-wyrd-bootstrap-skill/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/wyrd-bootstrap-skill.md

**Tests**: not requested by the spec — `wyrd-chronicle-template` has no automated check
substrate; verification is the manual quickstart.md walkthrough (Polish phase, T012).

**Organization**: a single skill file delivers all of Requirements FR-001..FR-012, so this is
organized by the sequence the skill itself follows internally (matching User Story 1's ordering)
rather than by independent parallel stories — User Story 2 (the one-time guard) is one section
inside the same file, not a separately deployable slice.

**Repository note**: T001-T011 all touch files in **`wyrd-chronicle-template`**
(`/root/source/neilgfoster/wyrd-chronicle-template`), a sibling repository — not this one. This
repository (`wyrd`) carries only the spec trail itself.

## Phase 1: Setup

- [ ] T001 Confirm `wyrd-chronicle-template` has no uncommitted work in flight and create a
  feature branch there for this skill (mirroring this repo's own branch name is fine, but the
  two repos' PRs are independent).

## Phase 2: Foundational

**Purpose**: settle the two input-shape questions research.md flagged before writing any skill
prose that depends on their answer.

- [ ] T002 Reconcile `chronicle.yaml.json`'s `intent.lethality` vocabulary
  (`low`/`standard`/`grip` per `wyrd-chronicle-template/bootstrap`'s own `ask(...)` call) against
  `create-character --mortality`'s accepted vocabulary (`creation.MORTALITY_FATE`'s
  `low`/`standard`/`high`) by reading both directly; fix whichever one is wrong (most likely
  `bootstrap`'s `grim` choice, given `01-principles.md`/`23-chronicle-bootstrap.md` both use
  "grim" as a tone word, not a mortality level) rather than silently mapping around a mismatch in
  the new skill.
- [ ] T003 Confirm `engine/wyrd/client.py`'s `save`/`load`/`validate`/`create-character` verbs
  are present and callable in a real `engine/` copy (i.e. #402 is actually merged and reachable),
  per this feature's stated dependency.

**Checkpoint**: the skill's own CLI-call shapes are confirmed correct before Phase 3 writes prose
around them.

## Phase 3: User Story 1 - Complete a freshly-bootstrapped chronicle in one pass (Priority: P1) 🎯 MVP

**Goal**: `/wyrd-bootstrap`, invoked once after `./bootstrap`, produces a complete character, an
opening situation, a seeded personal Threat, a valid `chronicle.yaml`, and a first commit.

**Independent Test**: quickstart.md steps 1-2, against a real darkfuture- or titan-based
chronicle.

### Implementation for User Story 1

- [ ] T004 [US1] Write `wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md`
  frontmatter (`name`, `description`, `user-invocable: true`, `disable-model-invocation: false`)
  and its "What this skill does" section, stating plainly what it completes (the interpretation
  half `bootstrap`'s docstring defers) and citing docs/design/23-chronicle-bootstrap.md.
- [ ] T005 [US1] Write the "Locating and calling the engine CLI" section, reusing the exact
  `WYRD_PKG_DIR=$(find engine -maxdepth 4 -type d -name wyrd | head -1)` convention from
  `/wyrd-character`/`/wyrd-downtime`/`/wyrd-end-session`.
- [ ] T006 [US1] Write the character-creation step: read `chronicle.yaml.json`, walk the player
  through docs/design/11-character-creation.md's steps (career, the 8-advance spend, Loyalty,
  Drive, Misfortune, Fault Line), call `create-character` with the gathered inputs (per
  contracts/wyrd-bootstrap-skill.md and data-model.md's field table), and write `pc.yaml` from
  its returned frontmatter verbatim — no recomputed skill %, Fate, or Stamina (FR-003, FR-004).
- [ ] T007 [US1] Write the opening-situation step: read `intent.about`/`intent.avoid` from
  `chronicle.yaml.json`, and select or write an `arc`/`beat` entity that reflects `about` and
  avoids everything named in `avoid` (FR-005), per data-model.md's Opening situation section.
- [ ] T008 [US1] Write the Threat-seeding step: select at least one entity to carry a `threat:`
  block whose `connection` is concrete text tied to the character (typically the chosen
  Misfortune), and write it as an `overlay/` promotion or a new `entities/` file per
  docs/design/25-entities.md's schema (FR-006, FR-007, and the Edge Case for "no eligible existing
  entity").
- [ ] T009 [US1] Write the chronicle-state-assembly and save step: build the full state from
  `default_chronicle_state(...)`'s shape plus the recorded `intent`, call the `save` CLI verb, and
  report a returned `error` verbatim without committing on failure (FR-008, FR-009).
- [ ] T010 [US1] Write the first-commit step: on `save` success, delete `chronicle.yaml.json`, and
  make exactly one commit covering `pc.yaml`, `chronicle.yaml`, and the new overlay/entity
  file(s) (FR-010), with a commit message stating what was seeded — not a placeholder.

**Checkpoint**: User Story 1 is fully walkable end to end via quickstart.md steps 1-2.

## Phase 4: User Story 2 - Refuse to run twice (Priority: P2)

**Goal**: a second invocation against an already-completed chronicle changes nothing.

**Independent Test**: quickstart.md step 3.

### Implementation for User Story 2

- [ ] T011 [US2] Write the skill's leading guard clause: check for `chronicle.yaml`'s existence
  first (already-run case) and for `chronicle.yaml.json`'s absence (never-run case), reporting
  each plainly and stopping before touching any file, per FR-002 and the spec's Edge Cases.

**Checkpoint**: both user stories are covered by the same single `SKILL.md`.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T012 Run quickstart.md's full walkthrough (steps 1-3) against a real darkfuture- or
  titan-based chronicle, confirming SC-001/SC-002/SC-003 — this is the feature's actual
  acceptance test, standing in for an automated suite `wyrd-chronicle-template` doesn't have.
- [ ] T013 [P] Fix `wyrd-chronicle-template/bootstrap`'s stale final message and docstring
  parenthetical (currently pointing at `/wyrd-play`) to name `/wyrd-bootstrap` instead, per
  research.md's decision — a small, same-PR correction to the script this feature completes.
- [ ] T014 [P] Update `wyrd-chronicle-template/README.md` if its own bootstrap description still
  implies `/wyrd-play` is the very next step after `./bootstrap`, to mention `/wyrd-bootstrap` as
  the intervening one-time step.
- [ ] T015 Write this repository's own `docs/design/23-chronicle-bootstrap.md` update, if the
  implementation surfaces any behavior this design doc does not already describe accurately
  (CLAUDE.md: "Update the design document when the change lands, and do not leave the spec as the
  only record of current behaviour"). Expected to be a no-op, since the doc already describes
  this skill's sequence in full; confirm rather than assume.

## Dependencies & Execution Order

- **Setup (T001)**: no dependencies.
- **Foundational (T002-T003)**: depends on T001; BLOCKS all of Phase 3-4.
- **User Story 1 (T004-T010)**: depends on Foundational; T004-T005 first (shared skill
  scaffolding), then T006 → T007 → T008 → T009 → T010 in strict sequence, since each step's
  written section assumes the previous one's output (this mirrors the skill's own runtime order,
  not an implementation-file dependency).
- **User Story 2 (T011)**: depends on Foundational only; independent of T004-T010's content
  (it is a guard clause placed before them in the same file) but written after so it can
  reference the same file's structure.
- **Polish (T012-T015)**: T012 depends on all of T004-T011 being complete; T013-T014 are
  independent of each other and of T012; T015 depends on T012's outcome (only needed if the
  walkthrough reveals a doc gap).

## Parallel Opportunities

- T013 and T014 can run in parallel with each other (different files).
- T002 and T003 can run in parallel (independent checks, no shared file).

## Implementation Strategy

Single-file MVP: complete T001-T011 as one continuous `SKILL.md` draft, then T012's real-chronicle
walkthrough is the actual proof the feature works — there is no earlier "deploy" point, since a
half-written skill file is not usable at the table.
