# Feature Specification: Tier the mechanical chronicle skills at Haiku

**Feature Branch**: `431-tier-haiku-skills`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Tier /wyrd-character, /wyrd-downtime and /wyrd-end-session at Haiku"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM session delegates pure CLI-verb dispatch to a cheaper model (Priority: P1)

A player invokes `/wyrd-character`, `/wyrd-downtime`, or `/wyrd-end-session` during a chronicle.
Each of these three skills is CLI-verb dispatch plus verbatim reporting of the verb's own return
value — none of them narrate in the GM-contract sense, resolve a test, or pick which option is
best on the player's behalf. Today all three inherit whatever model is running the parent GM
session (typically the capable model reserved for narration), spending that capacity on work
`docs/design/27-tooling.md` section 5 classifies as Haiku tier.

**Why this priority**: This is the entire scope of the feature — there is no smaller independently
valuable slice. Declaring the tier correctly is what lets the capable model's own job shrink to
exactly the narration/judgement work `27-tooling.md` section 5 says it should be doing.

**Independent Test**: Read each of the three skills' `SKILL.md` frontmatter and confirm
`model: haiku` is declared, and read the skill body to confirm the stated one-line justification
is present and uses the design's own tiering-table language.

**Acceptance Scenarios**:

1. **Given** `wyrd-chronicle-template/.claude/skills/wyrd-character/SKILL.md`, **When** its
   frontmatter is read, **Then** it declares `model: haiku` and the skill states, in its own
   prose, why Haiku tier fits (mechanical language work with a right answer, formatting a
   verb's return value into a sentence).
2. **Given** `wyrd-chronicle-template/.claude/skills/wyrd-downtime/SKILL.md`, **When** its
   frontmatter is read, **Then** it declares `model: haiku`, and its stated justification
   explicitly addresses the five uncoded Undertakings (Recover, Pursue, Cultivate, Learn, Ask)
   played "in prose" as bounded flavour text on a mechanically-inert choice, not GM judgement
   about what a roll means.
3. **Given** `wyrd-chronicle-template/.claude/skills/wyrd-end-session/SKILL.md`, **When** its
   frontmatter is read, **Then** it declares `model: haiku` and states why (a fixed `pending:`
   rule, verbatim reporting, a short factual commit message — no judgement step).

### Edge Cases

- What happens if a later change adds a judgement step to one of these three skills (e.g. the GM
  choosing which Undertaking outcome to narrate as consequential)? That change would need to
  reconsider this skill's tier at the same time — the tier is justified by the skill's current
  content, not asserted independently of it.
- What if Haiku cannot actually run the CLI-invocation/JSON-parsing steps reliably? Out of scope
  for this feature to verify by running a model (per the issue's own constraints, verification is
  by re-reading each skill against the tiering table, not by running anything); a future session
  finding Haiku's output thin on one of these skills is the named escape hatch, not a blocker
  here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `wyrd-character` skill's `SKILL.md` frontmatter MUST declare `model: haiku`.
- **FR-002**: The `wyrd-downtime` skill's `SKILL.md` frontmatter MUST declare `model: haiku`.
- **FR-003**: The `wyrd-end-session` skill's `SKILL.md` frontmatter MUST declare `model: haiku`.
- **FR-004**: Each of the three skills MUST state, in its frontmatter block or immediately
  following prose, a one-line reason why Haiku tier fits, using `docs/design/27-tooling.md`
  section 5's own tiering-table language ("mechanical language work with a right answer...
  formatting a roll into a sentence").
- **FR-005**: `wyrd-downtime`'s stated reason MUST explicitly address the five uncoded
  Undertakings played in prose, naming why that bounded flavour text does not push the skill
  above Haiku tier.
- **FR-006**: None of the three skills' frontmatter MUST declare a model above Sonnet (Haiku sits
  below the Sonnet ceiling epic #429 sets for every wyrd skill, so this is automatically satisfied
  — stated for the record per the issue's own acceptance criteria).
- **FR-007**: The change MUST NOT alter any of the three skills' actual behaviour (CLI verbs
  called, fields read/written, reporting rules) — this is a frontmatter/documentation change only.

### Key Entities

- **Skill frontmatter**: The YAML block at the top of a `SKILL.md` file; Claude Code reads
  `model:`/`effort:` from it to fix which model runs that skill, overriding the invoking
  session's model.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three targeted skills declare `model: haiku` (3 of 3), verifiable by reading
  each file's frontmatter.
- **SC-002**: Each of the three skills carries a stated Haiku-tier justification in the design's
  own language, verifiable by reading each file's frontmatter block or the prose immediately
  following it.
- **SC-003**: Zero non-frontmatter/non-justification lines change in any of the three
  `SKILL.md` files — the CLI-verb steps, reporting rules, and "Never" sections are byte-for-byte
  unchanged, verifiable by diffing against the pre-change files.

## Assumptions

- This Claude Code version's Haiku models do not require (or meaningfully use) an explicit
  `effort:` field the way Sonnet/Opus do, following kord's own `model: haiku` skills (e.g.
  `kord-install`, `kord-loop-log`, `kord-learnings-capture`), none of which pair `model: haiku`
  with `effort:`. `effort:` is added only if this session finds it meaningful for one of the
  three skills; otherwise it is omitted.
- This is a `wyrd-chronicle-template`-repo change, not an engine capability change in the `wyrd`
  repo sense: no Spec Kit gate applies in that repo (it has no speckit installed), but the
  Spec Kit cycle runs here in the `wyrd` repo per established precedent (#403/#404/#405/#418/#430)
  to record the reasoning as a spec/plan/tasks trail, with the actual frontmatter change landing
  as a separate PR in `wyrd-chronicle-template`.
- Verification is by re-reading each skill's full content against `27-tooling.md` section 5's
  tiering table, not by running any model — `wyrd-chronicle-template` has no CI/tests to run.
