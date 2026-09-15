# Phase 0 Research: Per-type entity status vocabulary

No `NEEDS CLARIFICATION` markers were left in the Technical Context — this is a scoped bug fix in
an already-understood module, not a new capability with open technology choices. The research
that matters here is confirming the actual vocabulary per entity type, since the issue explicitly
warns against assuming only companion/thread differ.

## Decision: which entity type/role combinations have their own status vocabulary

**Method**: read `docs/design/22-state.md` and `docs/design/25-entities.md` in full (not
grepped in isolation) and record every place either document states a `status:` field's legal
values.

**Findings**:

| Type / role | Vocabulary | Source |
|---|---|---|
| Default (every type unless overridden below) | `stub \| drafted \| complete` | `25-entities.md` common schema |
| `character`, `role: companion` | `with-party \| away \| dead \| lost \| departed` | `22-state.md` § Companions |
| `thread` | `open \| resolved \| cold \| never-answered` | `22-state.md` § Threads |
| `character`, any other/no `role` (player, nemesis, bystander, ally, authority, quarry) | default | no override documented; `22-state.md`'s player-character frontmatter example omits `status` entirely, implying it follows the common-schema default like every other entity |
| `place`, `organisation`, `arc`, `beat`, `creature`, `item`, `tracker`, `lore` | default | no override documented anywhere in either file |

**Decision**: two overrides exist today — `character`+`role: companion`, and `thread` — and every
other type/role combination uses the default. This matches the issue's own framing (companion and
thread as the reported cases) and is now confirmed rather than assumed, per the issue's explicit
instruction to check every type.

**Alternatives considered**:

- *Open up `STATUSES` to accept the union of all three vocabularies for every type.* Rejected —
  it would let a `place` accept `status: with-party`, which is meaningless and defeats the point
  of a closed vocabulary; FR-003/User Story 3 explicitly require the default to still reject
  values outside it.
- *Give every one of the ten types its own vocabulary table, even where it's identical to the
  default.* Rejected as unnecessary indirection — a lookup with a documented fallback expresses
  "no override here" more directly than ten identical tuples would, and is the smaller diff.
- *Key the companion override on `type: character` alone (ignore `role`).* Rejected — `22-state.md`
  is explicit that `with-party`/etc. is the *companion's* vocabulary specifically
  (`role: companion` + `status: with-party` in its own example); a `role: player` or
  `role: nemesis` character is a `character` entity too and must keep the default per User Story 3.

## Decision: how the lookup is keyed

**Decision**: a dict keyed by `type`, with `character`'s entry itself branching on `role` (default
vocabulary unless `role == "companion"`). Every other type maps directly to a single vocabulary
tuple. Types with no entry fall back to the existing default `STATUSES` tuple — this is what keeps
`place`/`organisation`/etc. behaving exactly as before with zero new table entries for them.

**Rationale**: mirrors the existing `_TYPE_ENUM_FIELDS` pattern already in `entity.py` (a dict
keyed by `type`, `.get(entity_type, {})` falling back to nothing) — using the same shape keeps
this fix idiomatic to the file rather than inventing a second convention for the same kind of
lookup.

**Alternatives considered**:

- *A single flat `dict[str, tuple]` keyed by `type` only, with `"character"` mapping to the
  companion vocabulary and a separate `is_companion()` check gating which table applies before
  the lookup.* Workable, but pushes the role-branching logic into `validate()` itself rather than
  keeping status-vocabulary knowledge in one place; keeping the branch inside the lookup function
  is more contained and easier to test in isolation.
