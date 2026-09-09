# Research: Chronicle overlay resolution

No `NEEDS CLARIFICATION` markers were left in the Technical Context — this feature is a small,
well-bounded extension of #305's existing entity module, and the two open questions worth
recording a decision for were resolved by reading design/25 and entity.py directly rather than by
external research.

## Decision: overlay files use the same file-level format as setting entities

**Decision**: An overlay file is read with `state.load_entity` exactly like a setting file — YAML
frontmatter + markdown body — and is *not* run through `entity.validate()` on its own (a partial
overlay legitimately omits required common-schema fields like `name` or `setting`).

**Rationale**: design/25's overlay example shows a file with only `id`, `overlay_of`, and the
changed fields — no `type`, no `name`. Requiring it to pass full entity validation before merging
would force every overlay to restate the entire setting entity, defeating the point of "carrying
only the delta." Validation instead applies once, to the merged effective entity (FR-009).

**Alternatives considered**: Validating the overlay file itself against a separate "partial
entity" schema was considered and rejected — it would be a second schema to keep in sync with the
main one, for a check that the merge-then-validate step (FR-009) already subsumes.

## Decision: merge is a shallow, field-level dict merge, not a deep/recursive merge

**Decision**: `overlay_fields | setting_fields` at the top level of the frontmatter dict — any key
present in the overlay (even if its value is a nested dict, like `threat` or `objective`)
replaces the setting entity's value for that key wholesale. There is no field-by-field merge
*inside* a nested structure.

**Rationale**: design/25's promotion example overlays a whole `threat: {imminence, connection}`
block as one unit, not a per-subfield patch. A `disposition` overlay is a plain scalar. Nothing in
the design document or the issue's acceptance criteria calls for deep-merging nested dicts, and
inventing that behavior would be exactly the kind of unspecified richness `CLAUDE.md`'s
deterministic-over-inference discipline warns against adding without a driving requirement.

**Alternatives considered**: A deep/recursive merge (so an overlay could patch one key of
`objective` without restating the rest) was considered. Rejected for this feature: it is not
required by any acceptance criterion, and a chronicle author who wants to change one field of
`objective` can simply restate the whole updated block — the overlay file is meant to be small,
hand-edited YAML, not a diff format. If a future issue needs field-level nested patching, that is
a new, separately-justified capability.

## Decision: body resolution mirrors frontmatter resolution (FR-007)

**Decision**: If the overlay file has a non-empty body, it replaces the setting entity's body
entirely; otherwise the setting body is used unchanged. No paragraph-level merge.

**Rationale**: Consistent with the frontmatter merge's "present overrides, absent falls through"
rule, applied to the one non-frontmatter piece of an entity file. Body content is prose describing
what the chronicle now knows was different from the setting record — an overlay's body is the
right shot at "here is the updated in-fiction description," and it should replace rather than
concatenate (concatenation would leave contradictory prose from before and after a promotion).

**Alternatives considered**: Concatenating setting body + overlay body was considered and
rejected for the reason above.

## Decision: dangling `overlay_of` is a load-time error, not a silent skip

**Decision**: If an overlay's `overlay_of` names an id absent from the loaded setting set, the
resolution function raises (or returns an explicit error result — see data-model.md) naming the
overlay file and its target, rather than silently ignoring the overlay or fabricating an entity.

**Rationale**: FR-008 in the spec; matches `entity.py`'s existing error-reporting style
(`state.StateError` naming the file) rather than inventing a new failure mode. Full referential-
integrity scanning across a whole chronicle remains `wyrd doctor`'s job (design/28, out of
scope) — this is only the point failure for the specific pair a resolution call is given.
