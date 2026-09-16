# Tasks: Tier /wyrd-play and /wyrd-bootstrap at Sonnet, with effort decided per skill

**Input**: Design documents from `/specs/167-play-bootstrap-model-tier/`
**Prerequisites**: plan.md, research.md, quickstart.md

**Tests**: Not requested — `wyrd-chronicle-template` has no CI or automated tests (spec.md
Assumptions); verification is the manual quickstart.md checklist, run as the final task of each
story.

**Repository note**: Every implementation task below edits files in **`wyrd-chronicle-template`**,
not this repo (`wyrd`) — this repo holds only the Spec Kit trail (spec/plan/tasks), per the
established precedent (wyrd#403/#404/#405/#418). Paths given are relative to
`wyrd-chronicle-template`'s own root.

## Phase 1: Setup

- [ ] T001 Locate the `wyrd-chronicle-template` checkout and confirm
      `.claude/skills/wyrd-play/SKILL.md` and `.claude/skills/wyrd-bootstrap/SKILL.md` both exist
      with bare frontmatter (no `model:`/`effort:` yet) — the precondition this feature edits
      against.

## Phase 2: Foundational

No foundational/blocking tasks — the two user stories below edit two independent files and share
no code path.

---

## Phase 3: User Story 1 - /wyrd-play declares a deliberate model/effort tier (Priority: P1)

**Goal**: `.claude/skills/wyrd-play/SKILL.md`'s frontmatter declares `model: sonnet` and
`effort: high`, with a written justification distinguishing its mechanical and judgement steps.

**Independent Test**: Read `.claude/skills/wyrd-play/SKILL.md` in full per quickstart.md step 1;
confirm the frontmatter and justification meet spec.md's FR-001, FR-003, FR-004, FR-006, FR-007.

- [ ] T002 [US1] In `.claude/skills/wyrd-play/SKILL.md`, add `model: sonnet` and `effort: high`
      to the YAML frontmatter block (between the existing `disable-model-invocation: false` line
      and the closing `---`).
- [ ] T003 [US1] Immediately below the frontmatter's closing `---` (before the `## What this
      skill does` heading), add a short justification note explaining the `effort: high` choice:
      name at least one mechanical step (e.g. Step 1's `session-context` load, Step 10's
      `validate` call) and at least one judgement-requiring step (e.g. Step 3's orientation
      narration, Step 4's interpretation of a `propose` result, Step 8's beat-closing narration),
      and reference `docs/design/27-tooling.md` section 5's stance that the GM's own narration
      and judgement is "the one place not to economise." Base the wording on research.md's
      `/wyrd-play` decision section.
- [ ] T004 [US1] Run quickstart.md's step 1 and step 3 (grep for `opus`) against the updated
      `.claude/skills/wyrd-play/SKILL.md`; confirm every check passes.
- [ ] T005 [US1] Run quickstart.md's step 4 (diff against the pre-feature version) to confirm no
      numbered step, CLI-verb invocation, or `## Never` entry changed — only frontmatter and the
      new justification note were added.

**Checkpoint**: `/wyrd-play` is independently complete and verifiable at this point.

---

## Phase 4: User Story 2 - /wyrd-bootstrap declares a deliberate model/effort tier (Priority: P2)

**Goal**: `.claude/skills/wyrd-bootstrap/SKILL.md`'s frontmatter declares `model: sonnet` and
`effort: high`, with a written justification distinguishing its mechanical and judgement steps
(centred on Step 3's scenario/arc match and Step 4's Threat connection).

**Independent Test**: Read `.claude/skills/wyrd-bootstrap/SKILL.md` in full per quickstart.md
step 2; confirm the frontmatter and justification meet spec.md's FR-002, FR-003, FR-005, FR-006,
FR-007.

- [ ] T006 [US2] In `.claude/skills/wyrd-bootstrap/SKILL.md`, add `model: sonnet` and
      `effort: high` to the YAML frontmatter block (between the existing
      `disable-model-invocation: false` line and the closing `---`).
- [ ] T007 [US2] Immediately below the frontmatter's closing `---` (before the `## What this
      skill does` heading), add a short justification note explaining the `effort: high` choice:
      name the skill's more mechanical steps (Step 2's `create-character` call, Step 5's `save`
      call, Step 6's commit) against its judgement-requiring steps (Step 3's opening-scenario/arc
      selection against the player's stated intent, Step 4's Threat personal-connection
      judgement), and reference `docs/design/27-tooling.md` section 5. Base the wording on
      research.md's `/wyrd-bootstrap` decision section, including why a smaller share of
      narration-heavy steps still earns `high` (Step 3/Step 4's foundational consequences for the
      whole chronicle, not their proportion of the file).
- [ ] T008 [US2] Run quickstart.md's step 2 and step 3 (grep for `opus`) against the updated
      `.claude/skills/wyrd-bootstrap/SKILL.md`; confirm every check passes.
- [ ] T009 [US2] Run quickstart.md's step 4 (diff against the pre-feature version) to confirm no
      numbered step, CLI-verb invocation, or `## Never` entry changed — only frontmatter and the
      new justification note were added.

**Checkpoint**: `/wyrd-bootstrap` is independently complete and verifiable at this point.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T010 Confirm neither updated file declares `model: opus` anywhere (spec.md FR-003),
      satisfying SC-003.
- [ ] T011 Confirm both justification notes each name at least one mechanical and one
      judgement-requiring step from that skill's own numbered steps (spec.md FR-007), satisfying
      SC-004.
- [ ] T012 Raise the PR in `wyrd-chronicle-template` carrying both skill-file edits, referencing
      wyrd#430 in its body (the tracking issue lives in `wyrd`, the change lands in
      `wyrd-chronicle-template` — no `Closes`/`Fixes` keyword, since GitHub cross-repo keywords
      only auto-close within the same repo; state the relationship in prose instead).

## Dependencies & Execution Order

- Setup (T001) has no dependencies.
- Foundational: none — skipped.
- User Story 1 (T002-T005) and User Story 2 (T006-T009) touch different files and have no
  dependency on each other; either can be done first, or both in parallel.
- Polish (T010-T012) depends on both user stories being complete (it verifies both files
  together and raises the one PR carrying both).

## Parallel Execution Example

```text
# US1 and US2 touch entirely different files — safe to run together:
T002 [US1] frontmatter edit — .claude/skills/wyrd-play/SKILL.md
T006 [US2] frontmatter edit — .claude/skills/wyrd-bootstrap/SKILL.md

# Then, also in parallel:
T003 [US1] justification note — .claude/skills/wyrd-play/SKILL.md
T007 [US2] justification note — .claude/skills/wyrd-bootstrap/SKILL.md
```

## Implementation Strategy

**MVP scope**: User Story 1 alone (`/wyrd-play`, T002-T005) is independently shippable and is the
higher-priority half of wyrd#430 (the more frequently-invoked skill). In practice, given both
stories are small, single-file, frontmatter-only edits with no shared code, this feature is
expected to complete both stories in one pass and raise one PR (T012) carrying both — the
per-story split above exists so each skill's correctness can be verified independently, not
because a partial delivery is actually planned.
