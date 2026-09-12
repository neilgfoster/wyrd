# Phase 1 Data Model: Related settings — shared worlds and kindred tone

## Entity: Relation (new `settings.yaml` top-level list, `relations:`)

A pairwise, typed, directionless kinship declaration between two catalogue entries.

| Field | Type | Required | Notes |
|---|---|---|---|
| `a` | setting id (string) | yes | Must match an existing `settings:` entry's `id`. |
| `b` | setting id (string) | yes | Must match an existing `settings:` entry's `id`. Must differ from `a`. |
| `kind` | enum: `same-world` \| `kindred-tone` | yes | Closed vocabulary — no other value. |

**Validation rules** (enforced by `tools/check_settings_catalogue.py`):

- `a` and `b` must each name a setting present in `settings:` (FR-004 / SC-003: unknown-id case).
- `a` must not equal `b` (FR-004 / Edge Cases: self-kinship case).
- The unordered pair `{a, b}` must not appear more than once across `relations:`, regardless of
  which field holds which id — `{a: X, b: Y}` and `{a: Y, b: X}` are the same entry
  (FR-004: symmetry-without-duplication).
- The unordered pair `{a, b}` must not appear under both `kind` values (FR-002 / User Story 2,
  Scenario 2: a pair cannot be both same-world and kindred-tone).
- If a setting named by `a` or `b` is removed from `settings:` (deleted or renamed), any relation
  still naming it fails validation (Edge Cases: deleted/renamed setting).

**Existing field retired**: the `group:` field on a `settings:` entry is removed; a setting's
same-world memberships are read by scanning `relations:` for `kind: same-world` entries naming its
id, rather than from a separate per-entry field (research.md, "relation storage shape").

## Entity: Borrowed-entity provenance stamp (documented in `docs/design/24-authoring-a-setting.md`,
attached to whatever entity schema a setting defines — not a `settings.yaml` field)

| Field | Type | Required | Notes |
|---|---|---|---|
| `from_setting` | setting id (string) | yes | The setting the entity originated in. |
| `from_entity` | entity id (string) | yes | The entity's id within `from_setting`. |
| `relation` | enum: `same-world` \| `kindred-tone` | yes | Must match a `relations:` entry between the borrowing setting and `from_setting` at the time of borrowing. |
| `on` | date | yes | When the borrow happened — mirrors `converted: {on}`'s existing convention. |

Recorded on the entity as `borrowed: {from_setting: ..., from_entity: ..., relation: ..., on: ...}`,
parallel to and distinguishable from the existing `converted: {rules, on}` stamp (research.md,
"provenance stamp shape for a borrowed entity"). An entity carries at most one of `converted:` or
`borrowed:` — never both — since FR-007 makes borrowing-with-no-declared-relation fall back to
ordinary conversion rather than producing a hybrid stamp.

**Chain provenance** (Edge Cases: borrowed-then-borrowed-again): a `borrowed:` stamp names only the
*immediate* origin. If `from_entity` in `from_setting` is itself stamped `converted:` or `borrowed:`,
that stamp is preserved on the origin entity and is reachable by following the chain one hop at a
time — this feature does not flatten a multi-hop chain into a single record, since doing so would
lose exactly the information Edge Cases requires kept.

## State / lifecycle

Neither entity has a lifecycle beyond existing (a relation is asserted or removed; a provenance
stamp is written once, at borrow time, and never rewritten — consistent with `docs/design/29-evolution.md`'s
forward-only rule: if a later relation change means a past borrow "shouldn't" have happened, the
stamp is history and stays as recorded).
