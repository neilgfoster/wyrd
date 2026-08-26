# Feature Specification: Career graph — skill counts and succession

**Feature Branch**: `035-career-graph`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Define the career graph: what a career actually declares (skill list, whether it has a fixed or variable skill count), and how succession between careers works (entry vs. non-entry, and the eligibility rule for the latter)." (issue #118)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author declares a career graph (Priority: P1)

A setting author writing `careers.yaml` needs to know exactly what fields a career declares —
its skill list, whether that list has a fixed length, and (for a non-entry career) what makes a
character eligible to take it.

**Why this priority**: without this, `careers.yaml` cannot be written or validated at all —
every other part of the character system depends on the career graph existing.

**Independent Test**: given the decided structure, an author can write a `careers.yaml` entry
for a non-entry career and state unambiguously what a character must have done to be allowed to
choose it.

**Acceptance Scenarios**:

1. **Given** the career-graph structure is defined in the design docs, **When** a setting author
   writes an entry career, **Then** they can state its skill list and entry-point flag with no
   remaining ambiguity.
2. **Given** the same structure, **When** a setting author writes a non-entry career, **Then**
   they can state its prerequisite career(s) and the eligibility rule resolves to a clear
   yes/no for any given character.
3. **Given** a setting author wants a career reachable from more than one ladder (e.g. a career
   captain's post reachable from either a guard's or a soldier's career), **When** they declare
   more than one prerequisite on it, **Then** a character who has completed *any one* of them is
   eligible — no character need complete every listed prerequisite.

### User Story 2 - A player reads what "completing" their career means (Priority: P2)

A player advancing their character needs to know when their career counts as *completed* — the
event that grants the existing "+1 maximum Stamina" bonus ([`05-character-creation.md`](../../docs/design/05-character-creation.md)) and, for a non-entry
career elsewhere in the graph, satisfies that career as one of its qualifying prerequisites.

**Why this priority**: the completion bonus already exists in the text as an effect with no
defined cause; this is the second load-bearing consumer of the same definition, after the entry
requirement in Story 1.

**Independent Test**: given a character's advance history inside a career, it can be determined
without ambiguity whether that career is complete.

**Acceptance Scenarios**:

1. **Given** a character has spent advances inside a career up to its cap on every skill it
   grants, **When** completion is checked, **Then** the career is complete.
2. **Given** a character has opened only some of a career's skills, or has not raised them all
   to the career's cap, **When** completion is checked, **Then** the career is not complete.

### User Story 3 - The dead cross-reference resolves (Priority: P3)

`05-character-creation.md` currently points at `27-entities.md` for "the setting's career
graph," and `27-entities.md` says nothing about careers. Once the graph is defined somewhere
real, that link must point at real content.

**Why this priority**: lower than Stories 1–2 because it is a documentation-consistency fix
that falls out of resolving them, not an independent design question.

**Independent Test**: following the link from `05-character-creation.md` lands on a section
that actually defines the career graph.

**Acceptance Scenarios**:

1. **Given** the career graph is documented in its chosen home, **When** a reader follows the
   cross-reference from `05-character-creation.md`, **Then** they land on that definition.

### Edge Cases

- A setting declares a non-entry career whose prerequisite career is itself never marked as an
  entry point (an unreachable career) — the graph does not need to forbid this, but the rule
  must not silently treat such a career as reachable.
- A career may name more than one prerequisite — a **zigzag** path, where several different
  ladders converge on the same next rung and completing any one of them qualifies. This is what
  lets a **specialist** (one ladder, climbed straight up) and a **generalist** (a spread of
  completed careers across different ladders) both exist as different choices over the same
  graph shape, rather than needing separate mechanics for each.
- Two careers could name each other as mutual prerequisites, or a career could be its own
  prerequisite through a longer cycle — the decision must state whether cycles are permitted or
  are a validation error. With multiple prerequisites per career, a cycle exists only when
  **every** one of a career's prerequisite entries eventually requires the career itself — a
  career listed as a prerequisite by more than one other career is convergence, not a cycle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST state what a career declares: an identifier, an entry-point flag
  (or absence of one), a skill list, and — for a non-entry career — its prerequisite career(s).
- **FR-002**: The design MUST decide, and state, whether every career grants the same number of
  skills or whether the count is setting-defined per career.
- **FR-003**: The design MUST define what it means for a character to have **completed** a
  career, in terms of the advance mechanics already defined in
  [`05-character-creation.md`](../../docs/design/05-character-creation.md) §3, and MUST cross-reference the
  existing "+1 maximum Stamina" completion bonus to this definition.
- **FR-004**: The design MUST define the eligibility rule for a non-entry career: what a
  character must have done (in terms of career completion, per FR-003) to be allowed to choose
  it, resolvable to a clear yes/no for any character and any non-entry career.
- **FR-005**: A non-entry career MUST be able to declare one or more prerequisite careers, and
  satisfying **any one** of them (not all) MUST grant eligibility — this is what makes a zigzag
  career path (convergence from several ladders onto one career) possible, alongside the plain
  single-prerequisite ladder case.
- **FR-006**: The design MUST state whether the career graph may contain cycles (a career
  reachable, directly or transitively, as its own prerequisite), and if not, that this is a
  setting-authoring error the setting's own validation is expected to catch.
- **FR-007**: `docs/design/05-character-creation.md`'s cross-reference to "the setting's career
  graph" MUST be updated to point at wherever the graph structure is actually defined.
- **FR-008**: `docs/design/26-authoring-a-setting.md`'s description of `careers.yaml`'s expected
  shape MUST be consistent with the decided career-graph structure (entry-point flag, skill
  list, prerequisite field(s)).
- **FR-009**: This is a documentation-only design decision (per the source issue); no
  `careers.yaml` schema validator or other code is in scope.

### Key Entities

- **Career**: a row in a setting's career lookup table (`careers.yaml`), not a Wyrd entity
  ([`27-entities.md`](../../docs/design/27-entities.md)). Declares an identifier, a skill list, an
  entry-point flag, and — if non-entry — its prerequisite career(s).
- **Career completion**: an event, defined in terms of a character's advance history inside a
  career, that grants the "+1 maximum Stamina" bonus and satisfies a successor career's
  prerequisite.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author can write any career — entry or non-entry — into `careers.yaml`
  and state its full declared shape without needing to guess or invent a field.
- **SC-002**: For any character and any non-entry career in a setting's graph, eligibility
  resolves to a single yes/no with no case left undecided.
- **SC-003**: The cross-reference in `05-character-creation.md` resolves to content that
  actually defines the career graph — zero dead links remain (`tools/check_docs.py` passes).
- **SC-004**: `careers.yaml`'s documented shape in `26-authoring-a-setting.md` matches the
  decided structure exactly — no field named in one document and missing from the other.

## Assumptions

- Careers remain a **lookup-table row**, not a Wyrd entity type — consistent with
  `26-authoring-a-setting.md`'s existing classification of `careers.yaml` alongside gear,
  names, and the bestiary. This spec does not propose adding `career` to the ten entity types
  in `27-entities.md`.
- The career-graph structure may end up documented primarily in `26-authoring-a-setting.md`
  (where `careers.yaml`'s shape already lives) rather than `27-entities.md`, if that turns out
  to be the more consistent home; `27-entities.md` is amended only if the graph is in fact
  entity-relevant (e.g. as an instance of the existing containment/connection relations). The
  planning phase decides which; both are in scope for FR-007/FR-008 either way.
- "Completing" a career, per FR-003, is defined using only mechanics `05-character-creation.md`
  §3 already establishes (advances, the career's skill cap) — this feature does not introduce a
  new advancement mechanic.
- A character who has completed no career yet cannot take any non-entry career — only entry
  careers are available at character creation, consistent with the existing "any the setting
  marks as an entry point" creation-step text.
