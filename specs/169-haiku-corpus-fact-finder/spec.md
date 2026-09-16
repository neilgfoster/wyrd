# Feature Specification: Haiku corpus fact-finder subagent for create-setting

**Feature Branch**: `169-haiku-corpus-fact-finder`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Split create-setting onto a Haiku subagent for corpus extraction, Sonnet for voice/prose synthesis" (GitHub issue #432, wyrd repo)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delegate a single fact-grounding lookup to Haiku (Priority: P1)

While `create-setting` (running as the invoking, capable-tier skill) is writing a specific claim
into a setting file — a career's flavour line, a bestiary entry's grounding note, a named
faction's detail — it needs to know whether that claim is actually supported by the setting's
`corpus/` text, and if so, where. Instead of reading and searching corpus text itself, it hands
the claim and a corpus location to a narrowly-scoped Haiku subagent, which returns the exact
supporting or contradicting quote and its source location (or reports that no such quote
exists).

**Why this priority**: This is the mechanism the whole feature depends on — without it, nothing
else in the skill can change, since Phase 3/4's grounding lookups have nowhere else to go.

**Independent Test**: Can be fully tested by giving the subagent one specific claim and one
corpus file/directory known to contain (or not contain) supporting text, and confirming it
returns a verbatim quote with an exact file/line location when the claim is supported, and a
clear "not found" result when it is not — without writing or judging anything beyond that
lookup.

**Acceptance Scenarios**:

1. **Given** a claim that is verbatim present in a corpus text file, **When** the subagent is
   invoked with that claim and the corpus location, **Then** it returns the exact quote and its
   source file and line/location.
2. **Given** a claim with no supporting text anywhere in the given corpus location, **When** the
   subagent is invoked, **Then** it reports plainly that no supporting or contradicting passage
   was found, without inventing or approximating one.
3. **Given** a claim that is contradicted by corpus text (the corpus says the opposite), **When**
   the subagent is invoked, **Then** it returns the contradicting quote and its location, flagged
   as contradicting rather than supporting.

---

### User Story 2 - create-setting's own tier is declared and the ceiling is capped (Priority: P2)

An operator (or an agent) invoking `create-setting` sees that the skill itself is capped at the
Sonnet tier — the capable-model ceiling for this skill's actual work (voice/register synthesis,
career/bestiary content judgement) — consistent with every other Sonnet-tier skill in the wyrd
skill family, and consistent with `docs/design/27-tooling.md` section 5's tiering table.

**Why this priority**: Declaring the ceiling is what makes the delegation in User Story 1
meaningful — without it, nothing prevents the whole skill (including the mechanical fact-finding
it now delegates) from silently running on a more expensive tier than the work requires.

**Independent Test**: Can be tested independently by reading `create-setting`'s `SKILL.md`
frontmatter and confirming it declares the Sonnet tier, with no dependency on User Story 1's
subagent existing or being invoked.

**Acceptance Scenarios**:

1. **Given** `create-setting`'s `SKILL.md`, **When** its frontmatter is read, **Then** it
   declares `model: sonnet`.

---

### User Story 3 - Phase 3/4's mechanical lookups are rewritten to delegate, prose stays put (Priority: P1)

A future reader of `create-setting`'s `SKILL.md` can see, in Phase 3 and Phase 4, exactly which
steps are mechanical corpus fact-finding/verification (now delegated to the Haiku subagent) and
which are genuine judgement (voice/register synthesis, deciding what belongs, honest hedging on
thin sources) that stays on the invoking Sonnet-tier skill — with the reasoning for where that
boundary sits written down in the file itself, not left implicit.

**Why this priority**: This is the actual behaviour change the issue asks for; User Stories 1 and
2 build the pieces this story wires together and documents.

**Independent Test**: Can be tested by re-reading the full updated Phase 3/4 flow and confirming
every claim-grounding/quote-verification step names the subagent, while every
writing/register/judgement step remains attributed to the invoking skill, with no step doing
both.

**Acceptance Scenarios**:

1. **Given** the rewritten Phase 3, **When** a specific claim needs grounding (a name, quote,
   statistic, faction detail), **Then** the step describes invoking the Haiku subagent rather
   than reading/searching `corpus/` inline.
2. **Given** the rewritten Phase 3, **When** `voice.md`'s register is being written or a
   career/bestiary/entity's actual content is being composed, **Then** the step remains on the
   invoking Sonnet-tier skill, with no suggestion of delegating that judgement to Haiku.
3. **Given** the rewritten Phase 4, **When** a written claim is spot-checked with a grep-style
   verification against `corpus/`, **Then** that verification is described as a call to the
   subagent, consistent with Phase 3's grounding calls.
4. **Given** the rewritten `SKILL.md`, **When** a future reader looks for why the mechanical/
   judgement boundary sits where it does, **Then** they find that reasoning stated in the file
   itself.

### Edge Cases

- What happens when the corpus location given to the subagent doesn't exist or is empty (e.g. a
  setting with no `library/` material sourced yet)? The subagent reports that plainly as "no
  corpus text available to search," distinct from "searched and found nothing."
- How does the flow handle a claim that is only partially supported (the corpus supports part of
  a compound claim but not all of it)? The subagent reports exactly what it found and did not
  find, rather than rounding up to "supported" or down to "not found."
- What happens when Phase 1's web-research or original-invention permissions apply to a claim
  instead of corpus grounding? Those claims never go through the corpus fact-finder at all — the
  subagent's scope is corpus retrieval only, not web research or invention, and the skill's
  existing labelling rules for those two sources are unaffected by this change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST provide a `.claude/agents/` subagent definition, in the file
  format Claude Code actually expects for subagent definitions (frontmatter fields including at
  minimum `name`, `description`, `tools`, and `model`), declaring `model: haiku`.
- **FR-002**: The subagent's scope MUST be limited to: given a claim to ground and a corpus
  file/directory location, return the specific quote/passage/fact (with its exact source
  location) that supports or contradicts the claim, or report that none was found — a closed
  retrieval task with a checkable right answer.
- **FR-003**: The subagent definition MUST NOT include instructions or tooling for prose writing,
  register/voice synthesis, or any content-generation judgement — only retrieval and reporting.
- **FR-004**: `create-setting`'s `SKILL.md` frontmatter MUST declare `model: sonnet`.
- **FR-005**: `create-setting`'s Phase 3 MUST be rewritten so that every specific-claim-grounding
  lookup (a name, quote, statistic, faction detail sourced from `corpus/`) is described as a call
  to the new Haiku subagent, rather than as inline corpus reading/searching by the invoking
  skill.
- **FR-006**: `create-setting`'s Phase 4 grep-verification step MUST be rewritten, where it
  overlaps with corpus fact-finding, to delegate to the same Haiku subagent rather than
  performing the grep inline.
- **FR-007**: `create-setting`'s actual prose-writing and register/content-synthesis work (writing
  `voice.md`'s register, composing career/gear/bestiary/entity content, deciding what belongs, and
  hedging honestly on thin sources) MUST remain attributed to the invoking Sonnet-tier skill and
  MUST NOT be delegated to the Haiku subagent.
- **FR-008**: `create-setting`'s `SKILL.md` MUST document, in its own text, why the
  mechanical-fact-finding/judgement boundary sits where it does, so a future reader does not have
  to reconstruct the reasoning.
- **FR-009**: The skill's existing governing rule (never invent an unsupported specific claim) and
  its existing web-research/original-invention labelling rules from Phase 1 MUST remain intact and
  unaffected by the delegation — the subagent changes how a corpus lookup is performed, not what
  the skill is allowed to claim or how it labels sources.

### Key Entities

- **Haiku corpus fact-finder subagent**: A `.claude/agents/` definition in
  `wyrd-setting-template`, invoked with a claim and a corpus location, returning a
  supporting/contradicting quote and its exact source location, or a clear not-found result.
- **create-setting skill**: The existing Sonnet-tier `SKILL.md` in
  `wyrd-setting-template/.claude/skills/create-setting/`, whose Phase 3 and Phase 4 are updated to
  invoke the subagent for mechanical lookups while retaining all judgement-bearing work itself.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `create-setting`'s `SKILL.md` can identify, for every step in Phase 3
  and Phase 4, whether it is a delegated mechanical lookup or a judgement step that stays on the
  invoking skill, without needing to consult any file outside `create-setting`'s own directory.
- **SC-002**: The new subagent definition, read on its own, gives a Haiku-tier model everything it
  needs to perform one fact-finding lookup and nothing that invites it to write setting content.
- **SC-003**: A manual dry run of one corpus-fact-finding lookup against a real setting's
  `corpus/` text (e.g. darkfuture or titan) returns a correct verbatim quote and source location
  for a claim known to be supported, and a correct not-found result for a claim known to be
  unsupported.

## Assumptions

- This feature's actual implementation lands in `wyrd-setting-template` (a separate repository
  from this spec's home repository, `wyrd`), consistent with prior features in this same family
  (#403/#404/#405/#418/#430/#431) that specify from `wyrd` but implement in a setting/chronicle
  template repo.
- `wyrd-setting-template` has no CI or automated test suite; verification is by manual re-reading
  of the updated skill flow and, where feasible, a manual dry run of the subagent against a real
  corpus.
- The subagent definition's exact tool access (e.g. `Read`, `Grep`, `Glob`) is an implementation
  decision made during planning, constrained only by FR-002/FR-003 above (retrieval only, no
  content-writing tools needed).
- No existing `.claude/agents/` directory or convention exists yet in any wyrd repository — this
  is the first one, so its file format is validated against real Claude Code plugin examples
  during planning/implementation rather than assumed.
