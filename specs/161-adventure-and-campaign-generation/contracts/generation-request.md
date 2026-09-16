# Contract: the generation request/result interface

This engine has no HTTP/RPC surface — its interfaces are the `TOOLS` catalog verbs described in
[`27-tooling.md`](../../../docs/design/27-tooling.md) §3. A future implementing feature would add
one verb to that catalog; this contract specifies its input/output shape and behaviour so that
implementation can be written and tested against this document without re-deriving the rules from
the spec prose each time.

## Verb shape (illustrative — naming is an implementation decision, not fixed here)

```
generate(request: GenerationRequest) -> GenerationResult | {"error": {...}}
accept(result: GenerationResult) -> {committed_entity_id, threads_consumed, threads_emitted, threat_updates}
```

Two calls, not one, because acceptance is a distinct, explicit step (data-model.md's
`GenerationResult` validation rule: nothing is written until accepted — FR-015). This mirrors the
existing `propose`/`commit` split `27-tooling.md`'s catalog already uses elsewhere
(`31-action-resolution.md`), rather than inventing a new interaction shape for this one capability.

## `generate` — request contract

Input: `GenerationRequest`, per `data-model.md`.

**Preconditions** (checked before any generation step runs, per FR-016's no-model tier):

1. Exactly one of the two mode-specific state blocks is present, matching `request.mode`
   (data-model.md validation rules). Violation → structured error, `generate` step never runs.
2. If `mode: setting-authoring`: `invention_permitted` is present and `true` (FR-005, FR-015).
   Violation → structured error naming the missing permission (User Story 2, Edge Cases).
3. If `mode: live-play`: at least one of `threads`/`threat_state` is non-empty (Edge Cases,
   first bullet). Violation → structured error, nothing generated.

**Processing** (per spec.md FR-016–FR-019, each step's model tier fixed by the step, not chosen at
call time — FR-020):

1. **No-model**: select which live threads/threats/existing entities ground this request
   (deterministic matching, `18-arcs-and-beats.md`'s existing thread-matching algorithm).
2. **No-model**: compute the candidate's `danger` band (ADR 0024), `scale_drift` bound (FR-010),
   and `written_for` scaling.
3. **Haiku tier**: assemble the candidate's structural entry/exit shape (which threads it
   consumes/emits) and, for `arc`-scale, its child-beat decomposition/pacing.
4. **Capable model tier**: write the candidate's prose body and any Q3-permitted invented names/
   details, labelled inline per the Clarifications convention.
5. **No-model**: run the FR-007–FR-011 anti-inflation checks against the assembled candidate,
   populating `GenerationResult.checks`. A `reject` outcome on any check means the result is
   returned with `checks` populated but MUST NOT be silently discarded — the caller sees why.

Output: `GenerationResult` (data-model.md), or a structured `{"error": {...}}` for a precondition
failure (never a bare traceback, per `27-tooling.md` §3's error-shape rule).

## `accept` — commit-back contract

Input: a `GenerationResult` with no `checks` entry at `outcome: reject`.

**Behaviour** (FR-012–FR-014):

1. Write the candidate as an ordinary `arc`/`beat` entity at `status: drafted`, via the same
   entity-write path (`state.py`, per `27-tooling.md` §3) authored content uses, with `sources`
   set to the generated-provenance shape (data-model.md).
2. Consume/emit threads and mutate threat `clues`/`imminence` through the same functions
   `campaign.py` already exposes for authored play (FR-013) — this contract requires the
   implementation call the *same* functions, not equivalent new ones, so this is checkable by
   reading the implementation's call sites rather than only its output.
3. Return the committed entity's id and the concrete thread/threat mutations that occurred, so the
   caller (a GM session, or the create-setting skill) can report them plainly rather than
   re-deriving what happened from a diff.

**Rejecting instead of accepting**: a `GenerationResult` is simply discarded — no call, no write
(FR-015). There is no `reject` verb; not calling `accept` is the reject path.

## Error shapes

Every rejection — precondition failure, anti-inflation `checks` rejection, or a caller declining
a result — is reported as structured data naming which rule/precondition failed, never a bare
exception or a silently empty result, per `27-tooling.md` §3 ("Errors are structured... and
actionable, never bare tracebacks").
