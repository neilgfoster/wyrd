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
  maths" rigor as Stamina's 6 ([`11-character-creation.md`](../../docs/design/11-character-creation.md)
  §"Why Stamina is 6") for a constraint nobody asked for.

## Prerequisite cardinality

**Decision**: a non-entry career declares one or more prerequisite careers; completing **any
one** of them satisfies eligibility (OR semantics).

**Rationale**: a single mandatory prerequisite only models a strict ladder — one lineage,
climbed one rung at a time. The design goal is to also support a **zigzag** path: a career
reachable from more than one lower career, so a character can converge on the same next rung
from different starting ladders (e.g. `guard-captain` reachable from either `guard` or
`soldier`). OR semantics is what "any one of several ladders can lead here" means mechanically,
and it degrades cleanly to the single-prerequisite case (a list of length one) — no separate
rule is needed for the common linear career, only a looser cardinality on the field.

A **specialist** and a **generalist** both fall out of this without any further mechanism: a
specialist keeps satisfying the same career's own listed prerequisites up one ladder; a
generalist completes a spread of different careers across different ladders (each satisfying
whatever OR-branches they open) rather than climbing one chain — a difference in *which* careers
a character chose to complete, not a difference the career graph's shape needs to encode
specially. No convergence career that *requires* several completed prerequisites at once (AND
semantics) is defined by this decision; nothing in the corpus or this feature's goal calls for
gating a career behind multiple simultaneous completions, only for widening how a single next
career can be reached.

**Alternatives considered**:
- *Exactly one prerequisite per career (no zigzag).* Rejected — cannot express a career reachable
  from more than one ladder, which is exactly the mechanic the zigzag/generalist goal needs.
- *AND semantics (a career requires every listed prerequisite completed).* Rejected — nothing in
  the corpus or the stated goal calls for a convergence career gated behind multiple simultaneous
  completions; the generalist/specialist distinction already falls out of OR semantics through
  which careers a character chooses to complete, without needing a career that mechanically
  demands more than one. AND can be added later as a forward-only change if a setting ever wants
  a true convergence career, without disturbing any graph authored under this rule (OR is a
  strict subset of what an AND-capable schema could express).
- *A per-career mode flag choosing AND or OR.* Rejected for now as more schema than the stated
  goal needs — OR alone already produces both the ladder and the zigzag/generalist cases the
  feature asked for.

## Cycle policy

**Decision**: the career graph must be acyclic. A career naming itself as a prerequisite,
directly or transitively, is a setting-authoring error.

**Rationale**: with OR semantics (above), a career now has one or more prerequisite edges, so
the graph is a DAG rather than a strict tree — but the same acyclicity requirement still applies
to every edge. A cycle among a career's *entire* prerequisite set (every one of its listed
prerequisites eventually requires the career itself) would mean it is permanently unreachable —
no branch of its OR terminates at an entry career, so no character could ever complete it and
become eligible. That is a broken graph, not a valid design choice, so it belongs in the class of
setting-authoring errors the setting's own validation is expected to catch (consistent with
`26-authoring-a-setting.md`'s general framing of `careers.yaml` as setting-owned, validated
content) — not a case the engine's rules need to define behavior for. (A career appearing on more
than one path — e.g. two different careers both naming it as a prerequisite — is not a cycle; the
graph is a DAG, not a tree, precisely because OR semantics allows convergence.)

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
  ([`27-tooling.md`](../../docs/design/27-tooling.md)) — this is exactly the kind of claim that can
  be checked mechanically and should be.
