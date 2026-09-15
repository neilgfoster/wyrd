# Phase 1 Data Model: Per-type entity status vocabulary

No persisted schema changes — no entity file needs a new field or a rewritten value. This
documents the one derived concept the fix introduces in code.

## Entity status vocabulary (derived, not stored)

The closed set of legal `status` values for a given entity, selected by `type` and — for
`character` — also by `role`. Not a stored field itself; computed by a lookup function from
fields the entity already carries (`type`, `role`).

| Selector | Vocabulary | Values |
|---|---|---|
| default (any `type` not listed below) | authoring lifecycle | `stub`, `drafted`, `complete` |
| `type: character`, `role: companion` | companion life-cycle | `with-party`, `away`, `dead`, `lost`, `departed` |
| `type: thread` | thread life-cycle | `open`, `resolved`, `cold`, `never-answered` |

**Relationships**: keyed off two existing entity fields (`type`, required on every entity;
`role`, optional, only meaningful on `type: character`). No new relationship to any other entity.

**Validation rule** (`FR-001`–`FR-003`): an entity's `status` value must be a member of the
vocabulary selected for its `type`/`role`; membership in a *different* type's vocabulary does not
count — a companion with `status: complete` is invalid, even though `complete` is a legal value
for the default vocabulary, because the companion override replaces the default for companions
rather than extending it.

**State transitions**: out of scope for this fix. `legal_transition()` continues to model only
the linear `stub → drafted → complete` authoring progression; the companion and thread
vocabularies have no documented ordering (`22-state.md` never describes one status as "further
along" than another for either), so no transition table is added for them.
