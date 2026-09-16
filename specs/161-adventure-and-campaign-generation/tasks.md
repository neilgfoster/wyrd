# Tasks: Adventure and campaign generation

**Input**: Design documents from `specs/161-adventure-and-campaign-generation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md (all present)

**Scope note**: This feature is specification-only, per issue #99's own Definition of Done
("Capability change: Spec Kit cycle, `specs/` committed") and plan.md's Summary. There is no
application code to write, so this task list contains no implementation tasks for a generation
mechanism — a future feature implements what this one specifies. Every task below verifies or
finalizes the *specification artefacts themselves* against this issue's three acceptance criteria,
which is what "implementation" means for a design-only deliverable.

**Tests**: Not applicable — no code exists to test. Quickstart.md's "Validating a future
implementation" section is itself the test plan a later, code-bearing feature will execute; this
feature's own validation is the artefact-consistency checking below.

## Phase 1: Setup

- [X] T001 Confirm the spec directory holds every artefact `plan.md`'s Project Structure section
      names (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/generation-request.md`,
      `quickstart.md`, `checklists/requirements.md`) in
      `specs/161-adventure-and-campaign-generation/` — no file listed as an output is missing.

## Phase 2: Foundational (blocking prerequisites)

- [X] T002 Cross-check `spec.md`'s three acceptance criteria (input contract per scale,
      anti-inflation as checkable rules, commit-back path with no fork) each against the specific
      FR-numbered requirements that satisfy them, recording the mapping in this task's own commit
      message rather than a new file — this is the gate every user-story task below assumes holds.
- [X] T003 Verify every cross-reference in `spec.md`, `plan.md`, `research.md`, and
      `data-model.md` resolves to a real file/section: `docs/design/18-arcs-and-beats.md`,
      `docs/design/19-campaign.md`, `docs/design/01-principles.md`, `docs/design/27-tooling.md`
      §5, `docs/design/25-entities.md`, `docs/design/03-rules.md` §7,
      `docs/adr/0003-recursive-containment.md`, `docs/adr/0024-a-party-is-worth-less-than-its-head-count.md`.
      A reference to a file/section that does not exist as written MUST be fixed before proceeding.

## Phase 3: User Story 1 - Generate the next beat during live play (P1)

**Goal**: The `live-play`/`beat`-scale slice of the request contract is complete and internally
consistent, and its acceptance scenarios are checkable against `data-model.md`/`contracts/`.

**Independent Test**: Read `spec.md`'s User Story 1 acceptance scenarios against
`data-model.md`'s `GenerationRequest` (`live-play` state block) and `contracts/generation-request.md`'s
`generate` preconditions; confirm every field the scenarios reference (`entry.requires_threads`,
`danger`, `cast`/`place`) is accounted for in the contract with no gap.

- [X] T004 [US1] Verify `data-model.md`'s `live-play` state block (`threads`, `threat_state`,
      `danger_rating`, `era`) supplies everything spec.md's User Story 1 acceptance scenarios
      reference, in `specs/161-adventure-and-campaign-generation/data-model.md`.
- [X] T005 [US1] Verify `contracts/generation-request.md`'s `generate` Processing steps 1–2 (no-model
      thread/threat selection and danger-band computation) are sufficient to produce the
      `entry.requires_threads` subset and `danger`-band guarantees FR-004/FR-009 state, in
      `specs/161-adventure-and-campaign-generation/contracts/generation-request.md`.

## Phase 4: User Story 2 - Generate a campaign spine with no chronicle yet (P2)

**Goal**: The `setting-authoring`/`campaign-spine`-scale slice is complete, consistent with
`create-setting`'s Phase 1 Q3 gate as it exists today, and its rejection path is unambiguous.

**Independent Test**: Read spec.md's User Story 2 acceptance scenarios against `data-model.md`'s
`setting-authoring` state block and FR-005/FR-015's rejection rule; confirm the "Q3 not granted →
refused, nothing written" path and the "Q3 granted → tone-contract-consistent, labelled output"
path are both fully specified with no open gap.

- [X] T006 [US2] Re-read `wyrd-setting-template`'s `create-setting` `SKILL.md` Phase 1 Q3 wording
      against `spec.md` FR-005 and `data-model.md`'s `invention_permitted` field; confirm the gate
      language matches (same permission model, not a second one), noting the check in this task's
      commit message.
- [X] T007 [US2] Verify `contracts/generation-request.md`'s `generate` precondition 2
      (`invention_permitted` check before any generation step) satisfies spec.md's Edge Case
      "Q3 not granted → refused before generation, nothing written" and Success Criterion SC-005,
      in `specs/161-adventure-and-campaign-generation/contracts/generation-request.md`.
- [X] T008 [US2] Verify `data-model.md`'s "Committed entity" body-prose provenance convention
      (`invented, per Phase 1 Q3`) is consistent with spec.md's Clarifications entry and FR-007(c),
      with no drift between the three, in
      `specs/161-adventure-and-campaign-generation/data-model.md`.

## Phase 5: User Story 3 - Generate an arc that nests beats and commits back as fact (P3)

**Goal**: The commit-back path is specified as strictly additive to the existing thread/threat
machinery, with no parallel state introduced anywhere in the three artefacts.

**Independent Test**: Read spec.md's User Story 3 acceptance scenarios against `data-model.md`'s
"Committed entity" relationships paragraph and `contracts/generation-request.md`'s `accept`
behaviour step 2 (same functions, not equivalent new ones); confirm there is exactly one additive
schema change (`sources.generated`) and zero new files/tables anywhere in the design.

- [X] T009 [US3] Verify `data-model.md`'s "Committed entity" table lists exactly one additive
      field (`sources`'s generated-provenance alternative) against the existing `arc`/`beat`
      schema in `docs/design/25-entities.md`/`docs/design/18-arcs-and-beats.md`, confirming
      Success Criterion SC-003's "exactly one new field, zero new files/tables" claim holds, in
      `specs/161-adventure-and-campaign-generation/data-model.md`.
- [X] T010 [US3] Verify `contracts/generation-request.md`'s `accept` step 2 explicitly requires
      calling the *same* `campaign.py`-class functions authored play uses (not equivalent new
      ones), matching spec.md FR-013's checkable requirement, in
      `specs/161-adventure-and-campaign-generation/contracts/generation-request.md`.

## Phase 6: Polish & cross-cutting concerns

- [X] T011 [P] Run `python3 tools/check_docs.py` from the repo root and confirm this feature (which
      adds no files under `docs/design/`) produces no new findings.
- [X] T012 [P] Run `python3 -m ruff check .` and `python3 -m ruff format --check .` from the repo
      root and confirm no findings attributable to this feature's own files (none of which are
      Python, so this is a no-op confirmation, recorded rather than assumed).
- [X] T013 Update the Spec Quality Checklist at
      `specs/161-adventure-and-campaign-generation/checklists/requirements.md` if any of T002–T010
      surfaced a fix to `spec.md`/`plan.md`/`data-model.md`, then re-confirm all items remain
      checked.

## Dependencies & execution order

- **Phase 1 (Setup)** has no dependencies — run first.
- **Phase 2 (Foundational)** depends on Phase 1, and blocks every user-story phase — the
  cross-reference and acceptance-criteria mapping it produces is what each story's tasks check
  against.
- **User Story phases (3, 4, 5)** each depend only on Phase 2, not on each other — they verify
  different slices of the same already-written artefacts, so they may run in any order or in
  parallel (they touch overlapping files for *reading*, but no task in one phase edits a file
  another phase's task is also editing at the same time — see note below).
- **Phase 6 (Polish)** depends on all of Phases 3–5 completing, since T013's checklist
  reconciliation needs to know whether any of them found something to fix.

## Parallel execution examples

Tasks marked `[P]` touch independent files/commands and may run together:

```
T011 (check_docs.py) and T012 (ruff) — independent tooling checks, no shared file.
```

Every user-story-phase task above (T004–T010) reads shared files (`spec.md`, `data-model.md`,
`contracts/generation-request.md`) rather than writing them, so they are safe to review in
parallel across a team; only mark them `[P]` for actual concurrent *editing* if a task turns out
to require a fix — reviewing is inherently parallel-safe, editing the same file from two tasks at
once is not, so no `[P]` marker is applied to T004–T010 themselves.

## Implementation strategy (MVP first)

Given this is a specification, "MVP" means: the smallest set of tasks that leaves the spec usable
by a future implementing feature even if nothing else in this list runs.

- **MVP = Phase 1 + Phase 2 + Phase 3 (US1 only)**: confirms the artefacts exist, are internally
  cross-referenced correctly, and that the highest-priority scenario (live-play beat generation,
  the case the issue was raised against) is fully specified end to end.
- Phases 4 and 5 (US2, US3) extend confidence to the setting-authoring mode and the commit-back
  path respectively, and Phase 6 is final polish — all are complete already as part of writing the
  artefacts in Phases 0/1 of `plan.md`; this task list's role is to verify that completeness
  explicitly rather than assume it.
