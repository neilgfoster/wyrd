# Research: Dread as a reaction/social test penalty

No NEEDS CLARIFICATION markers remained after specification — the source issue (#272) and the
existing design/code already settle every open question. This phase records the decisions taken
in reading the existing engine rather than resolving genuine unknowns.

## Decision: extend `ordinary-test`, don't add a new mechanic

**Rationale**: `docs/design/07-transformations.md`'s Dread rule targets "any reaction or social
test", and reaction/social tests already resolve through `resolution._resolve_ordinary_test` —
the same generic skill-test mechanic every non-combat, non-Exposure, non-Terror test uses. There
is no separate "reaction test" or "social test" mechanic in the engine to hang new behaviour off.

**Alternatives considered**: A dedicated `reaction-test`/`social-test` mechanic. Rejected — it
would duplicate `_resolve_ordinary_test` almost entirely for no behavioural gain, and the design
document itself treats "reaction or social test" as a description of *when* an ordinary test is
being made, not a distinct mechanic.

## Decision: a caller-supplied boolean, not an engine-computed judgment

**Rationale**: The design document is explicit that "made their peace" is the GM's fictional call.
The engine already has two precedents for taking an already-decided judgment as a request field
rather than computing it: Fault Line bias (`docs/design/07-transformations.md`, staged at
Transformation-cascade time) and Exposure's resist-skill choice (`skill` on an `exposure`
request). This feature follows the same shape: one new boolean field on the request, read once,
never stored.

**Alternatives considered**: Inferring "made peace" from some existing state (e.g. party
familiarity, a relationship field). Rejected by the issue's own scope note — no new UI/state for
tracking who has made peace is in scope, and the engine has no such field to read today.

## Decision: field lives on the request, applies inside `_resolve_ordinary_test` only

**Rationale**: `_stage_request` already resolves `target_state` for every non-combat mechanic and
passes it to the resolve function via `**_ignored` — `_resolve_ordinary_test` just needs to accept
and use it. Scoping the read to `_resolve_ordinary_test` alone satisfies FR-006 (the penalty must
not leak into Exposure, Terror, or combat) without an explicit mechanic-allowlist check: those
mechanics simply never read the new field.

**Alternatives considered**: Applying the penalty as a generic cross-mechanic modifier in
`_resolve_test` (the shared single-roll core). Rejected — `_resolve_test` is also used by Exposure
and Terror, and threading an opt-in flag through it to exclude those would be more surface area for
the same result.

## Decision: field name — `dread_witnessed`

**Rationale**: Reads as "this test's target was witnessed while carrying Dread, by someone who
hasn't made peace with it" — true means the penalty applies. Keeping the flag's default `False`
means every existing caller (and every existing test) is unaffected without passing anything new,
matching FR-004 and Success Criterion SC-002.

**Alternatives considered**: `dread_applies` (also considered, functionally identical name —
`dread_witnessed` reads slightly more clearly as *why* the penalty triggers, tying it to the
design document's own "when a transformed character is seen" framing).
