# Phase 0 Research: The Rally: recovery, advance award and commit

No `NEEDS CLARIFICATION` markers remain in spec.md or plan.md's Technical Context -- every
technical choice below follows directly from existing, settled prior art in this repo, so no
open research questions were dispatched.

## Decision: Recovery amounts and clamping

**Decision**: A Rally reduces Strain by exactly 1, floored at 0, and raises Stamina by exactly 1,
capped at the character's current maximum. No roll, no GM discretion over the amount.

**Rationale**: `docs/design/03-rules.md` §2 and §5 state these figures directly ("recover 1
Strain", "At each Rally, recover 1 Stamina"), and ADR 0020 already derived and justified the rate
(reusing Strain's own cadence rather than inventing a second number). This feature applies that
settled rate; it does not re-derive it.

**Alternatives considered**: None -- the amounts are already fixed by an accepted ADR. Re-deriving
them here would duplicate ADR 0020's own reasoning rather than reusing its conclusion.

## Decision: The advance-award hook wires `advancement.award_advance`, not a new check

**Decision**: The optional award step in a Rally is a direct call to
`engine/wyrd/advancement.py`'s existing `award_advance(trigger, record)`, passed the session's
current advancement record. Its three refusal shapes (`unknown_trigger`, `already_awarded`,
`session_ceiling`) are surfaced to the caller unchanged.

**Rationale**: #277/PR #282 already implemented the full award/spend economy; CLAUDE.md's reuse
rule and the issue's own out-of-scope note ("The advancement-spending mechanics themselves...
this feature only wires the award hook at the Rally boundary") both point the same way. Adding a
second, Rally-specific award check would create exactly the "two documents/mechanisms describing
one thing differently" fault class CLAUDE.md names as this repo's most common review finding.

**Alternatives considered**: A Rally-specific award function with its own trigger vocabulary and
refusal messages. Rejected -- it would duplicate `award_advance`'s ceiling and already-awarded
checks, and any future change to the award economy would need to track two call sites instead of
one.

## Decision: Persist/commit as an injected callable, mirroring `session.run_close`

**Decision**: The Rally's persist/commit step accepts a caller-supplied zero-argument callable
(or `None`) and calls it exactly once, after recovery and any award are computed. This feature
does not implement what "write state" or "commit the chronicle" concretely do.

**Rationale**: #309's `wyrd.session.run_close` already established this exact shape for the same
reason: the chronicle/campaign state layer (#300) that would give persistence real content does
not exist yet. Reusing the pattern rather than inventing a second one keeps the two save points
`16-session.md` names (Rally and the mid-beat `pending:` marker) consistent in how they defer to
that future layer.

**Alternatives considered**: Stubbing a no-op persistence function inside this module and
replacing it once #300 lands. Rejected -- an injected callable makes "nothing is persisted until
a real implementation is wired in" the caller's own visible choice (an omitted/`None` steps
argument), rather than a silent no-op hidden inside this module that a future change would need
to notice and remove.

## Decision: Why the previously-rejected Resolve framing (ADR 0043, superseded) does not apply here

**Decision**: This feature's Strain/Stamina recovery is unconditional -- it does not cap Stamina's
recovery by Taint or introduce any Taint-relative headroom, unlike the rejected first draft of
Resolve's own Rally recovery.

**Rationale**: ADR 0043 was superseded because capping a *resource* by Taint (leaving no
headroom above the Spent-equivalent boundary) made that resource simultaneously "spendable" and
"immediately at its own floor" after every rest -- a self-contradiction specific to Resolve's
relationship with the Spent state. Stamina and Strain have no such Taint-relative boundary in
`docs/design/03-rules.md` §2/§5 -- Stamina's cap is its own `stamina_max` (raised only by career
completion, per #278/PR #283), and Strain's floor is a plain 0. Reading ADR 0043 confirms it is
about Resolve's cap formula specifically, not a general caution against Rally recovery -- so it
places no constraint on this feature's implementation.

**Alternatives considered**: None -- this is a documentation-verification step (issue #310 names
ADR 0043 explicitly as "check ... for why that particular framing was rejected"), not a design
choice with genuine alternatives.
