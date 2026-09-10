# Phase 0 Research: Setting Overrides Mechanism

## Decision: the closed overridable set's initial membership

**Decision**: Seed `overrides.OVERRIDABLE` with Taint and Trauma (disable, rename) and the four
oracle-prompt table families plus `skills` (tables, extend) -- the mechanisms the design docs
already describe with a concrete setting-facing override path.

**Rationale**: docs/design/24-authoring-a-setting.md's own `overrides:` example uses exactly this
set (`disable: [taint, trauma]`, `rename: {taint: shadow}`, `tables: {critical-slashing: ...}`,
`extend: {skills: ..., oracle-prompt-npc-objective: ...}`), and
docs/design/15-oracle-prompts.md documents `tables:`/`extend:` against the oracle-prompt families
specifically, with the append-only, contiguous-range rule this feature's `extends` field mirrors.
Starting from mechanisms the design already names as overridable, rather than every mechanism the
engine happens to implement, keeps the closed set an accurate contract rather than a superset
that includes things no setting-facing path exists for yet.

**Alternatives considered**: including the four critical-damage tables (`CRITICAL_TABLES` in
`resolution.py`) and careers/gear/creatures from day one. Rejected for this feature: those tables
are still hardcoded Python literals with no per-name loader a setting's `tables:` override could
actually replace, and careers/gear/creatures have no engine-shipped baseline in this repo to
extend (settings declare their own outright) -- adding them to the closed set now would publish
overridability the engine cannot yet honour. `overrides.OVERRIDABLE` is designed to grow by
adding entries as each mechanism's own setting-facing path lands, so this is a sequencing choice,
not a permanent boundary.

## Decision: `extend` accumulates across layers rather than "last wins"

**Decision**: For the `extend` key, `resolve()` accumulates each layer's paths into a list per
mechanism, rather than each later layer's `extend:` block overwriting the previous one the way
`rename`/`tables` do.

**Rationale**: docs/design/15-oracle-prompts.md is explicit that extension rows are "appended
above the engine's own highest range -- contiguous with it, never overlapping -- leaving every
engine row live." Extension is additive by definition; a chronicle wanting its own extra oracle
rows on top of a setting's should not silently discard the setting's rows. "Last wins" describes
`rename`/`tables`, which really do replace a single value; `extend` is a different shape (a list
that grows) and the spec's own Assumptions section calls this out explicitly.

**Alternatives considered**: treating every key uniformly as "last wins," so a chronicle's
`extend:` for a mechanism replaces a setting's. Rejected: it would contradict the additive
semantics `15-oracle-prompts.md` documents and silently drop content, which is exactly the kind
of surprising behavior docs/design/27-tooling.md's "never a silent no-op" principle warns against
in the adjacent disable case.

## Decision: a real `track` verb, not synthetic test doubles, demonstrates disable/rename

**Decision**: Add `track` to `catalog.py`/`verbs.py`/`client.py` -- a small, stateless verb that
applies a delta to a trackable mechanism's value, tagged with `mechanisms: ["taint", "trauma"]` --
so the closed set's disable/rename behaviour has a genuine catalog entry to act on.

**Rationale**: docs/design/27-tooling.md section 4 states its own worked example in these terms:
"the verb is still `wyrd track <id> taint +1`." No verb tied to a specific mechanism existed in
the catalog before this feature, so disabling Taint had nothing concrete to remove from
`describe`, and the acceptance criteria (`docs/design/27-tooling.md`'s "its verbs are absent from
`describe`", "calling one anyway is a structured error") could not be demonstrated against real
code. `track` is deliberately minimal (no entity load/save, matching the existing stateless
verbs like `adjust-standing`) -- it exists to give the override mechanism a genuine consumer, not
to implement full Taint/Trauma entity tracking (which remains future work, unrelated to #316's
scope).

**Alternatives considered**: leaving `filter_tools` unexercised by any real catalog entry.
Rejected: an untested integration point is not evidence the mechanism works end-to-end, and the
spec's own acceptance scenarios require it.

## Decision: extend the engine's restricted YAML reader for flow-style collections

**Decision**: Add flow-style `[a, b]` and `{k: v}` parsing (flat, scalars only, no nesting) to
both `engine/wyrd/state.py`'s `_scalar` and `tools/check_bestiary.py`'s `_scalar`.

**Rationale**: every `overrides:` example in the design docs uses flow style
(`disable: [taint, trauma]`, `rename: {taint: shadow}`), and neither restricted reader parsed it
before this feature -- `_scalar` would have returned the bracketed text as a literal string.
`tools/check_setting.py`'s own comment already flagged `overrides:` as "recognised but
deliberately left unvalidated... that is #316's scope," which is exactly this gap. Extending both
readers narrowly (flat collections of scalars only) is sufficient for every override shape this
feature defines and keeps the change small and auditable.

**Alternatives considered**: requiring settings to write block-style YAML instead
(`disable:\n  - taint`). Rejected: it would silently diverge from every existing worked example in
the design docs, which is exactly the "two documents disagreeing" fault class `CLAUDE.md` calls
out -- and would surprise any setting author who copied the documented example verbatim.
