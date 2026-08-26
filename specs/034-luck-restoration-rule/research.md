# Research: Luck restoration rule

## Decision: Luck resets to maximum at the start of each top-level arc

**Rationale**: `03-rules.md` §1 already says testing Luck "costs 1 Luck for the rest of the arc,
pass or fail." Scoping a cost to "the rest of the arc" is only a meaningful clause if something
happens at the arc's end that makes the scoping matter — otherwise the phrase would say "for the
rest of the character's life," which is what a never-restoring resource actually is. The natural
reading is that Luck comes back at the next arc, and this feature makes that reading explicit
rather than inferred.

`18-campaign.md` gives top-level arcs (the ones directly under a chronicle) a distinguishing job:
"each should end with something altered." Nested arcs recurse without that guarantee. Anchoring
restoration to the top-level boundary — not every recursive arc beneath it — keeps Luck's reset
tied to the one structural boundary the campaign design already treats as significant, rather than
inventing a second, competing notion of "arc end."

**Alternatives considered**:

- **Luck never restores (a one-way, whole-life resource)**: rejected. It is internally consistent
  and was named in the issue as the honest alternative, but it makes the existing "for the rest of
  the arc" phrasing dead weight — there would be no reason to scope the cost to an arc if the
  resource never comes back regardless. Adopting this would require rewriting `03-rules.md`'s
  existing sentence, not just adding a clause to it.
- **Resets at every recursive arc boundary (including nested arcs)**: rejected. `18-campaign.md`
  is explicit that only top-level arcs carry the "ends with something altered" property; treating
  every nested arc as a reset point would make Luck recover far more often than the resource's
  scarcity (40 at creation, spent 1 at a time) seems designed for, and would contradict the
  distinction `18-campaign.md` draws between arc levels.
- **Resets per session or per downtime, matching Stamina's per-Rally/per-downtime recovery
  pattern (ADR 0020/0021)**: rejected. Luck's own text already names
  "arc" as its scoping unit; borrowing Stamina's cadence would contradict `03-rules.md`'s existing
  wording rather than complete it, and there is no stated reason Luck and Stamina should recover on
  the same rhythm — they answer different fictional questions (Stamina is bodily condition in a
  fight; Luck is a finite favor from fortune across a whole story arc).

## Format precedent: how other resource-recovery rules are stated

`03-rules.md` and related design documents state recovery rules as a short, declarative clause
attached to the resource's existing description, not as a separate subsystem (e.g. Stamina's
Rally/downtime recovery, ADR 0020/0021). This feature follows the same shape: one sentence added
to the existing Luck paragraph, not a new section.

## Open questions

None remaining — the spec's Assumptions section already resolves the one real decision point, and
this research confirms it against both source documents.
