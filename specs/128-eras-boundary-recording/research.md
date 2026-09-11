# Research: Eras: named periods and boundary recording

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One design choice worth recording:

- **Decision**: `eras`/`era_crossings` are added to `state.py`'s chronicle schema as new optional
  fields, not a separate file or a sub-structure inside the existing `era` scalar.
  **Rationale**: `docs/design/22-state.md`'s documented `chronicle.yaml` shape already reserves
  `era: null` as a bare pointer with no declared-in-advance list behind it yet — this feature is
  exactly the missing piece, the same way #328 gave `pending` (already round-tripped opaquely by
  #325) real semantics on top of an existing placeholder. `migrations` is the direct precedent for
  an append-only sub-list living on `chronicle.yaml` itself rather than a second file.
  **Alternatives considered**: a separate `eras.yaml` file — rejected; nothing else in the schema
  splits a chronicle-level concept across files, and `chronicle.yaml` is explicitly "the one file
  that is not an entity, because it describes the chronicle rather than anything in the world"
  (docs/design/22-state.md), which is exactly what era boundaries are.

- **Decision**: `cross_era` takes the full `eras` list and the current `era` id as separate
  arguments (not a combined chronicle dict), matching `chronicle.py`'s existing convention of
  operating on the specific sub-fields it owns rather than the whole chronicle state.
  **Rationale**: keeps `era.py` testable and reusable the same way `chronicle.py`'s
  `resume_state`/`discard_at_rally` take `pending` alone rather than the whole chronicle — a
  caller (session/Rally loop) already holds the loaded chronicle dict and can extract/reassemble
  the two fields around this module's pure functions.
  **Alternatives considered**: none seriously — this is the established pattern in this codebase
  for a sub-field-owning module (`chronicle.py`, `threat.py`, `thread.py`).
