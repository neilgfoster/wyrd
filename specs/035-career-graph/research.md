# Phase 0 Research: Career graph — skill counts and succession

## Where the career graph structure lives

**Decision**: `26-authoring-a-setting.md`, in its existing `careers.yaml` description — not
`27-entities.md`.

**Rationale**: `26-authoring-a-setting.md` already classifies `careers.yaml` as a **lookup
table** — "queried by key, never linked to individually," alongside gear, names, the calendar
and the bestiary — and states explicitly: "a career is a row; the guild that grants it is an
entity." `27-entities.md` closes its type list at ten ("Nothing else. A new type is an engine
change, never a setting one") and none of the ten fit a career: it is not a `character`, has no
containment or connection relation to declare, and is never linked to individually the way an
entity is. Moving the graph structure into `27-entities.md` would mean either inventing an
eleventh type against that document's own closing rule, or documenting a non-entity concept in
the entity-model document — both worse than fixing the cross-reference to point at the document
that already owns lookup-table shapes.

**Alternatives considered**:
- *Add `career` as an eleventh entity type.* Rejected — `27-entities.md` is explicit that a new
  type is a bigger engine change than this issue calls for, and a career has none of the
  properties (individual linkage, containment/connection) that make the other ten entities.
- *Document it in both places.* Rejected per `CLAUDE.md` fault class 3 — two documents
  describing one thing differently is the recurring fault this repo keeps getting corrected
  for; one home, one cross-reference.

## Skill count: fixed or setting-defined per career

**Decision**: setting-defined per career (variable), not a fixed count across all careers.

**Rationale**: `05-character-creation.md` already treats career skill lists as varying in
practice — "at least two skills must be opened" out of 8 advances is a floor, not an assertion
that every career grants the same number of skills, and nothing in the corpus ties skill-list
length to a fixed number. A soldier's career and a scholar's career are not obliged to be the
same shape, and forcing them to be would be inventing a constraint the issue never asked for and
the existing text never implied. This also matches the issue's own observation: "current text
implies the latter but never states it."

**Alternatives considered**:
- *Fix every career to the same skill count* (e.g. always exactly 4). Rejected — no existing
  text motivates a specific number, and it would need re-litigating with the same "check the
  maths" rigor as Stamina's 6 ([`05-character-creation.md`](../../docs/design/05-character-creation.md)
  §"Why Stamina is 6") for a constraint nobody asked for.

## Prerequisite cardinality

**Decision**: a non-entry career declares exactly one prerequisite career.

**Rationale**: every existing mention of succession in the corpus is singular — "a character
cannot start as a 'master' without first completing 'apprentice'" (issue #118's own framing),
and `05-character-creation.md` never gestures at a career needing more than one predecessor.
A single-prerequisite graph is a strict tree/DAG of chains and merges cleanly with the
cycle-forbidding rule below. Multi-prerequisite (AND/OR) support is speculative generality this
feature was not asked to build; it can be added later as a forward-only rule change
([`22-evolution.md`](../../docs/design/22-evolution.md)) if a setting ever needs it, without
disturbing any career graph authored under this rule.

**Alternatives considered**:
- *Allow a list of prerequisites, ANY of which satisfies eligibility.* Rejected for now —
  no source material or existing text calls for branching convergence, and it complicates the
  eligibility check (FR-004) for no requested benefit.
- *Allow a list of prerequisites, ALL of which are required.* Rejected for the same reason, and
  additionally: requiring multiple completed careers before touching a third pushes character
  creation/advancement pacing further than anything in `05-character-creation.md` establishes.

## Cycle policy

**Decision**: the career graph must be acyclic. A career naming itself as a prerequisite,
directly or transitively, is a setting-authoring error.

**Rationale**: with a single prerequisite per career (above), a cycle would mean a career is
permanently unreachable — its prerequisite's prerequisite chain never terminates at an entry
career, so no character could ever complete it and become eligible. That is a broken graph, not
a valid design choice, so it belongs in the class of setting-authoring errors the setting's own
validation is expected to catch (consistent with `26-authoring-a-setting.md`'s general framing
of `careers.yaml` as setting-owned, validated content) — not a case the engine's rules need to
define behavior for.

**Alternatives considered**:
- *Permit cycles and treat them as an intentional dead loop* (a career nobody can ever reach).
  Rejected — indistinguishable from an authoring mistake, and defining "expected" behavior for
  an unreachable career serves no design purpose.

## Completion definition

**Decision**: a career is **complete** when every skill it grants has been opened and raised to
that career's cap.

**Rationale**: this is the only definition expressible purely in terms of mechanics
`05-character-creation.md` §3 already establishes — advances open a career-granted skill at 25%
or raise an open one by +5% "to the career's cap," and nothing may exceed that cap. Completion
as "every granted skill capped" is the natural terminal state of that process, requires no new
mechanic, and gives a binary, computable answer for any character's advance history (Story 2,
FR-003). It is also the state that plausibly earns "the only durable toughening" — a career only
grants its Stamina bonus once a character has genuinely finished learning everything it had to
teach, not partway through.

**Alternatives considered**:
- *Completion after a fixed number of advances spent in the career, regardless of which skills.*
  Rejected — decouples completion from the career's own content (a character could "complete" a
  6-skill career without ever opening half its skills), which weakens both the Stamina-bonus
  rationale and the eligibility gate for successor careers.
- *GM judgment call ("when the story says so").* Rejected under "deterministic over inference"
  ([`20-tooling.md`](../../docs/design/20-tooling.md)) — this is exactly the kind of claim that can
  be checked mechanically and should be.
