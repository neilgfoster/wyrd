# Data Model: Beat/arc entry and exit conditions, and thread-matched selection

## Entry block (optional, on an arc or beat)

| Field | Type | Notes |
|---|---|---|
| `requires_threads` | list of strings | Thread tags that must all be live. Empty/absent = always satisfiable. |
| `requires_state` | list | State conditions, shape-checked only (FR-001); evaluation against real chronicle state is out of scope (deferred to #300). |
| `hooks` | list of strings | Narrative hook strings, free text, carried through unvalidated beyond being a list of strings. |

## Exit block (optional, on an arc or beat)

| Field | Type | Notes |
|---|---|---|
| `emits_threads` | list of `{tag: str, if: str \| None}` | `if` is optional free text describing the outcome condition; not evaluated by this feature (FR-002, Edge Cases). |
| `changes` | list of strings | Free-text world changes, carried through unvalidated beyond being a list of strings. |
| `leads_to` | string \| wikilink \| None | A reference (resolved via `entity.resolve_wikilink`) to another arc/beat id; consulted only as the User Story 3 fallback. |

Both blocks are entirely optional (FR-003) — an entity with neither still validates, matching a
`status: stub` entity that has not yet declared entry/exit (the sibling lazy-conversion feature
under #299 owns the stub-sufficiency rules; this feature does not require entry/exit for a stub to
be valid).

## Selection inputs and output

| Name | Type | Notes |
|---|---|---|
| `live_threads` | `set[str]` (or any iterable coerced to a set) | Caller-supplied; not stored by this module (Assumptions). |
| `candidates` | list of frontmatter dicts | Each already validated (via `entity.validate`/`load`); this module reads `entry`/`exit` off each. |
| `current` | frontmatter dict or `None` | Only needed for the `leads_to` fallback (User Story 3) — the entity whose `exit.leads_to` is consulted when no thread match exists. |
| *(return)* | list of frontmatter dicts | The matching subset (thread match), or a one-element list from `leads_to` resolution, or `[]` if neither applies (FR-008). |

## Validation rules

- `entry.requires_threads`/`requires_state`/`hooks`, when present, must each be a list (else
  rejected with a field-naming error, matching `entity.validate`'s `{"valid": False, "error":
  ...}` shape).
- `exit.emits_threads`, when present, must be a list of mappings each carrying a `tag` (string);
  `if`, when present, must be a string.
- `exit.changes`, when present, must be a list of strings.
- `exit.leads_to`, when present, must be a string (wikilink-wrapped or bare id) — resolved, not
  dereferenced, by validation; dereferencing happens only at selection time.

## State / transitions

None — this module is stateless (no entity status transition is introduced or consumed here; that
lifecycle is the sibling lazy-conversion feature under #299).
