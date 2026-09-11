# Research: Chronicle.yaml schema, load/save and versioning

No `[NEEDS CLARIFICATION]` markers remain in the spec; this phase records the concrete design
choices made in filling the Technical Context.

## Decision: extend `state.py` in place, not a new module

**Rationale**: `engine/wyrd/state.py`'s own docstring already commits to this ("Later features
extend the schema; this module's read/write contract does not change to accommodate that"). Its
`save`/`load`/`dump_yaml`/`parse_yaml` are already fully generic over an arbitrary mapping — they
need no change at all. What's missing is chronicle-specific *shape*: a default chronicle state,
and validation of that shape's own rules (required fields, migration immutability, enum-checked
`class`, non-negative counters).

**Alternatives considered**: a new `chronicle.py` module. Rejected — it would duplicate the
atomic-write/restricted-YAML machinery `state.py` already provides and tests, for no benefit; the
existing module's docstring explicitly anticipates this extension happening in place.

## Decision: validation lives in a dedicated `validate_chronicle()` function, not inline in `save`

**Rationale**: `save()` is generic (used for any state shape, including the pre-chronicle minimal
scaffold and, potentially, other future shapes). Chronicle-specific rules (FR-004 migration
immutability, FR-005 enum, FR-008 required fields, FR-010 non-negative) belong in a function the
chronicle-state call site invokes before saving, mirroring how `engine/wyrd/entity.py` already
separates `validate()` from the generic save/load in `state.py`.

**Alternatives considered**: validating inside `save()` itself via an optional schema parameter.
Rejected — `save()` already serves entity files and the old minimal-scaffold shape with no
validation; adding a schema-aware branch there would blur what the function is generic over.

## Decision: migration immutability is enforced by comparison against the previously-loaded log, not a checksum/lock

**Rationale**: The engine's own commit that calls `append_migration()` already holds the
previously-loaded state in memory (it just read it via `load()` to decide there's something new
to migrate). Comparing the new list's first N entries against the old list's N entries at
`validate_chronicle()` time is a direct, cheap, dependency-free check — consistent with "verify a
background job is actually running" / "check the maths" style direct verification this repo's own
CLAUDE.md asks for, rather than trusting a convention.

**Alternatives considered**: hashing each entry and storing the hash. Rejected — adds a field
purely for internal bookkeeping that has no place in docs/design/22-state.md's documented schema,
and a plain list-prefix comparison already gives the same guarantee with no extra state.

## Decision: `pending` is round-tripped as an entirely opaque `dict | None`

**Rationale**: The spec (FR-006) and issue (#325) both explicitly defer `pending`'s semantics to
a later feature (#328). `state.py`'s generic `dump_yaml`/`parse_yaml` already round-trip an
arbitrary nested mapping without this feature adding anything chronicle-specific to it.

**Alternatives considered**: a typed `Pending` shape now. Rejected — over-scopes this feature past
its own dependency boundary (#328 owns that shape) and risks disagreeing with what #328 decides.

## Decision: pre-existing minimal-scaffold files upgrade on load rather than failing

**Rationale**: `specs/075-engine-scaffolding`'s existing `default_state()` shape
(`schema_version` + `last_roll`) predates this feature and may already exist on disk in some
chronicle. `load_chronicle()` treats a state missing the newer fields as needing defaults filled
in (FR-009), the same policy `docs/design/22-state.md` already states for entities with no
`schema_version` ("treated as version 1 and flagged, not rejected") — applied here to the parallel
case of an old chronicle.yaml missing new-but-optional chronicle-level fields. A state missing a
field this feature's own schema treats as *required* (not merely new-and-optional) still fails
per FR-008 — the two are distinguished by which fields are optional vs. required, documented in
data-model.md.

**Alternatives considered**: a hard version-gate that rejects anything not already carrying every
new field. Rejected — would make the pre-existing scaffold file itself (which every chronicle
created before this feature already has) unreadable, which is exactly the silent-breakage
docs/design/22-state.md's own entity-versioning policy exists to avoid.
