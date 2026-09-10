# Phase 0 Research: Beat/arc entry and exit conditions, and thread-matched selection

No `NEEDS CLARIFICATION` markers remain in the Technical Context — the driving issue (#321) and
its design references (`docs/design/18-arcs-and-beats.md`, `docs/design/26-corpus-index.md`)
already settle language, dependencies, storage, and testing convention, all of which match the
existing `engine/wyrd/*` pattern. The two open questions worth a short decision record are below.

## Decision: where entry/exit validation lives

**Decision**: A new module, `engine/wyrd/arc_selection.py`, not an extension of `entity.py`.

**Rationale**: `entity.py`'s docstring scopes it to "common-schema and per-type validation,
containment resolution... and chronicle overlay resolution" — the entity *file format* itself.
Entry/exit conditions and selection are a play-time concern layered on top of that format (the
design doc treats §"Selection" as distinct from the entity shape in `25-entities.md`), matching
how `session.py` was kept separate from `entity.py` for the same reason (#309's plan.md: "session
loop logic... not the entity file format itself"). Reusing `entity.validate()` for the base
common-schema check and adding entry/exit as an additional, optional validation pass keeps that
boundary intact.

**Alternatives considered**: Extending `entity.validate()`'s `_TYPE_ENUM_FIELDS`/type-specific
checks directly — rejected because entry/exit are shape-checked (nested dict/list structure), not
a small enum, and because `entity.py` would then own both file-format concerns and selection
concerns, contradicting its own stated scope.

## Decision: selection as a pure function over caller-supplied threads

**Decision**: `select(live_threads, candidates, *, current=None)` takes a `set[str]` of live
threads and a list of candidate frontmatter dicts (already loaded via `entity.load`/`load_set`),
returning the matching subset; `leads_to` fallback resolution takes the `current` beat/arc's own
`exit.leads_to` value plus the same candidate pool.

**Rationale**: Matches the existing engine module contract (`adversary.py`, `session.py`): no
hidden state, no I/O, setting/caller data passed in as plain arguments. The chronicle/campaign
state layer that will actually track live threads (#300/#301) does not exist yet, so this feature
must not invent a storage shape for it — spec.md's Assumptions section already states this
explicitly.

**Alternatives considered**: Having selection read `parent`/thread state directly off entity
frontmatter (treating "live threads" as another entity field) — rejected because live threads are
chronicle-scoped runtime state, not a property of any single arc/beat entity, and conflating the
two would make selection depend on a storage layer this feature is explicitly not building.
