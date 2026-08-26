# Phase 0 research: Two-layer companions and a positive party track

No open `NEEDS CLARIFICATION` markers were left by `/speckit-clarify` (the spec's Assumptions
section resolved the two judgment calls with reasonable defaults). This phase records the design
research behind those defaults, so the decisions in `plan.md` are traceable to the existing text
rather than invented fresh.

## Decision: the mechanical layer is the fields the design already reads for resolution

**Decision**: The companion mechanical layer is exactly `career`, `bond`, `taint`, `strain`, and
`wounds` — no new field, no new competence rating.

**Rationale**: `design/03-rules.md` already states, twice, that a companion's mechanical
substance is deliberately thin: "the engine holds no capability score for a companion" (danger
scaling) and "Companions have no Fate of their own; their mechanical layer is deliberately thin"
(Fate section). Every value a resolution actually touches for a companion is already one of these
five: `career` bounds the skill % a test uses (career cap, `03-rules.md` §"Careers"); `bond`
modifies Tension gain and whether the companion follows into danger or tells the truth
(`04-session.md`); `taint` and `strain` are read on the same terms as the player character
(`03-rules.md` §4); `wounds` records lasting-wound entries on the same Aftermath table, same rows
(`03-rules.md` §3, "Companions recover on the same rule ... there is no companion rate"). Naming
the layer as exactly this set turns an implicit pattern into an explicit, closed one.

**Alternatives considered**:
- *A companion skill percentage of their own.* Rejected outright — contradicts the existing
  "no capability score" rule directly; would also require a character-sheet-equivalent per
  companion, which is the exact cost the issue names as unaffordable across years of play.
  This is not a real alternative worth an ADR (FR-003 already forbids it structurally); it's
  in-scope confirmation, not a rejected design.
- *Naming Stamina as part of the mechanical layer.* Considered and rejected: the design never
  gives companions a Stamina track separate from a wound state — wounds already carry
  `stamina_max: -N` as one of their possible effects (`03-rules.md`), so a companion's Stamina is
  fully expressed through `wounds`, not a sixth tracked field.

## Decision: Bond becomes the positive party track; no standalone track is added

**Decision**: Reconcile the positive-track gap by giving **Bond** an explicit positive mechanical
effect, rather than adding a new 0-N track that mirrors Party Tension in reverse.

**Rationale**: The issue itself names Bond as the leading candidate ("Bonds, which already exist
and may already be the positive track under another name"). Bond already: (a) modifies Tension
gain — the negative track — so it is already load-bearing on the "how is the party doing"
question from one side; (b) is described as "the closest thing Wyrd has to a relationship score"
(`04-session.md`); (c) moves slowly, which is the right cadence for a track meant to reward
sustained investment rather than a single beat's choice, matching User Story 2's framing of
"consistently invested... over several sessions." A second track answering the same underlying
question — is this party working — would be the two-documents-describing-one-thing-differently
fault CLAUDE.md names as recurring fault #3, and it is exactly the kind of thing worth an ADR:
a real, workable alternative (the mirror track) was considered and rejected, and a future
contributor revisiting `04-session.md`'s asymmetric-looking Tension track would plausibly propose
it again.

**Alternatives considered**:
- *A standalone 0-6 "Cohesion" track, rising on the same axis Tension falls.* Rejected — this is
  the duplicate-mechanic risk the spec's User Story 2 warns about. Two tracks moving in answer to
  the same fictional inputs (shared meals, spent beats on companions' problems, kept promises)
  would need constant reconciliation logic (does Cohesion rise exactly when Tension falls? by how
  much? do they interact?) that Bond's existing single value already avoids by being one number.
- *Leaving the asymmetry as deliberate and writing only an ADR, no mechanical change.* Considered,
  but rejected because Bond's existing text already gestures at being the answer without
  finishing the thought — its effects are described narratively ("modifies... whether they follow
  into danger, and whether they tell you the truth") but not spelled out as a concrete positive
  effect a GM can point to, which is what SC-004 in the spec requires ("traceable to a specific,
  defined effect"). The gap is real; the fix is finishing Bond's definition, not declining to.

## Decision: succession starts a fresh mechanical layer; the narrative layer is written fresh

**Decision**: Confirm, without change, `03-rules.md`'s "a successor inherits none of the
competence and all of the position" — under the completed model this reads as: the successor's
mechanical layer (career, bond, taint, strain, wounds) starts at its own baseline, and their
narrative layer (objective, flaw, secret, arc) is written fresh for the new person, same as any
new companion.

**Rationale**: This was already true before the split; the split makes explicit which fields are
"the competence" (mechanical) and confirms none of them survive a succession. No text changes to
this specific sentence are needed beyond what the two-layer split itself supplies as context — a
one-line cross-reference from `03-rules.md` to the new terminology in `04-session.md` is enough
to keep the two documents from drifting (recurring fault #3).

**Alternatives considered**: None — this was a confirmation task (spec User Story 3, lowest
priority), not a design decision with a real alternative.
