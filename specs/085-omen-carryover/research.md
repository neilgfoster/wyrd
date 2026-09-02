# Phase 0 Research: Omen carryover

No `NEEDS CLARIFICATION` markers — `docs/design/31-action-resolution.md` and #235/#236/#237's
already-landed `resolution.py` answer every open question this feature needs.

## Decision: `_stage_requests` becomes the shared core of `propose_batch` and `reroll`

**Rationale**: Omen tracking must span every request in a call, in chronological order, whether
that call is a fresh `propose_batch` or a `reroll`'s own re-resolution of a downstream set that
(per this feature) can now span more than one top-level request. Factoring the per-actor token
loop into one function both entry points call is what keeps them from diverging — the same
reason #237 already factored `_stage_request` out of `propose`/`propose_batch`.

**Alternatives considered**: duplicating the token-tracking loop inside `reroll` (rejected —
exactly the kind of drift `CLAUDE.md`'s recurring-fault list names: "two documents describing one
thing differently," here two functions instead of documents).

## Decision: `reroll` collects every top-level request in the downstream set, not just the named one

**Rationale**: Before this feature, a rerolled step's downstream set only ever contained cascade-
produced steps (`inputs=None`) belonging to the *same* top-level request (#236/#237's own
scoping). Omen carryover breaks that assumption: a later request's own step can land in an
earlier request's downstream set purely via the Omen-consumption `depends_on` edge, with no
mutation-based cascade relationship at all. `reroll` must therefore re-run every top-level
request found in the downstream set, not only `step`'s own.

**Alternatives considered**: teaching `reroll` to special-case "was this dependency an Omen
edge?" (rejected — indistinguishable from any other `depends_on` edge by design, and treating it
specially would reintroduce the exact kind of Omen-specific logic inside `reroll` this feature's
own FR-007 says to avoid).

## Worked example: an Omen modifies the actor's own next roll (SC-001, User Story 1)

A character invented for this exercise (matching `docs/design/31-action-resolution.md`'s own
"alertness: 10, climbing: 45"), `pending_omen: None`, two unrelated ordinary tests batched
together, base seed `40` (freshly computed, not the document's own real dice — see the
Assumptions in spec.md):

```
step 0 (alertness, eff. 10): roll 59 -- fails. Units 9 -- Fair Omen.
step 1 (climbing, eff. 45 + 10 = 55): the pending Fair Omen applies, depends_on [0].
    Roll 49 -- succeeds, degrees 1. Units 9 -- also Fair Omen (replaces the spent token, same
    value here, but now attributed to step 1).
```

`propose_batch` stages both, step 1 depending on step 0 via the Omen it consumed, and one
`pending_omen` mutation (`set 10`, `produced_by_step: 1`) — the batch's final token, which
differs from the actor's original `None`.

## Worked example: the reroll unwinds correctly (SC-001, User Story 4)

Spending **Resolve** against step 0, reroll seed `1`:

```
step 0 reroll (eff. 30 = 10 + 20): roll 18 -- succeeds, degrees 2. Units 8 -- no Omen this time.
    resolve.current -1 staged (the resource's own cost).
step 1, downstream (pulled in via the now-discarded Omen edge), freshly re-resolved with NO
    pending modifier (step 0's reroll produced none): eff. 45 (unmodified). Roll 8 -- succeeds,
    degrees 4. depends_on: [] -- no Omen consumed this time.
```

Since the batch's final token (`None`) now equals what was originally persisted (`None`), no
`pending_omen` mutation is staged at all on the revised proposal — committing it changes nothing
about `pending_omen`, correctly. Step 1's *original* result (roll 49, `depends_on: [0]`) no
longer appears anywhere in the revised proposal.

## Worked example: a persisted incoming Omen (SC-002, User Story 2)

An actor with `pending_omen: 10` already on disk. `propose(actor, mechanic="ordinary-test",
skill="alertness", seed=1)`:

```
roll 18 against eff. 30 (10 + 10) -- succeeds. depends_on: [] (no step in this call produced the
    incoming Omen -- it came from persisted state).
```

`discard`ing this proposal leaves `pending_omen` on disk exactly `10`, untouched.

## Worked example: replace, not stack, across three requests (SC-003)

Three unrelated ordinary tests for the same actor, all skill `50`, `pending_omen: None`, base
seed `59`:

```
step 0 (eff. 50): roll 29 -- succeeds, degrees 2. Units 9 -- Fair Omen (token: +10, from step 0).
    Staged: pending_omen set 10 (produced_by_step 0) -- the token actually changed (None -> 10).
step 1 (eff. 50 + 10 = 60): consumes step 0's Fair Omen, depends_on [0].
    Roll 40 -- succeeds, degrees 2. Units 0 -- Ill Omen (token REPLACED: -10, now from step 1,
    not step 0 -- never +10 and -10 both in effect).
    Staged: pending_omen set -10 (produced_by_step 1) -- changed again (10 -> -10).
step 2 (eff. 50 - 10 = 40): consumes step 1's Ill Omen, depends_on [1] (not [0]).
    Roll 64 -- fails. Units 4 -- no Omen. Token, having just been consumed with nothing fresh
    produced, clears to None.
    Staged: pending_omen set None (produced_by_step 2) -- changed again (-10 -> None).
```

Three `pending_omen` mutations are staged, one per real transition (FR-005) -- not only the
batch's own net effect (`None -> None`, which by itself would look like nothing happened).
Committed in sequence they still land on exactly the actor's original value, `None` (FR-005's own
"costs nothing at commit time"); the difference only shows up if something later needs to
*replay* an intermediate value, which is exactly what the next worked example needs.

## Worked example: a reroll recovers a kept step's own genuinely-pending Omen (SC-004)

**This is the case an earlier draft of this feature got wrong, and adversarial review caught
before merge** — worth keeping as its own worked example rather than folding away, since it is
precisely the scenario that would silently regress if `_stage_requests`' mutation-staging were
ever "simplified" back to one net mutation per call.

Same setup as above (seed `59`; steps 0/1/2 exactly as computed there). Reroll **step 2 only**
(`resource="fortune"`, reroll seed `100`) — steps 0 and 1 are both *kept*, untouched:

```
step 0 (kept): unchanged -- Fair Omen, pending_omen set 10.
step 1 (kept): unchanged -- Ill Omen, depends_on [0], pending_omen set -10.
step 2 (rerolled, fresh seed 100): eff. 40 (50 - 10) -- the fresh step 2 still consumes step 1's
    genuinely-pending -10, and depends_on [1] -- the real, still-present kept step, not treated
    as if nothing were pending (which an implementation recovering the token only from the
    original call's own *net* mutation would have done, since that net mutation never existed:
    the original call's own final token equalled its own original value, `None`).
```

Without FR-005's per-transition staging, `reroll`'s scratch-state rebuild (replaying only kept
steps' own mutations) would see `pending_omen` still at `None` going into the redone step 2 --
silently dropping the Omen a fresh `propose_batch` over the same three requests would have kept.
With it, replaying step 0's and step 1's own `pending_omen` mutations in order correctly leaves
`pending_omen` at `-10` before step 2 is redone, and step 2's `depends_on` correctly points at
step 1 via `_stage_requests`' `initial_producing_step` parameter (a negative-sentinel encoding —
`-(id + 1)` — distinguishes "a real step_id from outside this call" from this call's own local
0-based numbering, so `_renumber_and_merge` never confuses the two id spaces).
