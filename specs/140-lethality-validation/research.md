# Research: Chronicle intent's lethality is validated against the mortality vocabulary

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision recorded:

- **Decision**: declare a local `_LETHALITY_LEVELS` constant in `state.py` rather than
  importing `creation.MORTALITY_FATE`/`resolution.MORTALITY_LEVELS`.
  **Rationale**: `state.py` is imported by `character.py`, which `creation.py` imports — so
  `state.py` importing `creation.py` (or `resolution.py`, which also imports `state.py`
  directly) would create an import cycle. `resolution.py` itself already declares an
  independent `MORTALITY_LEVELS = frozenset({"low", "standard", "high"})` rather than importing
  it from `creation.py` (its own comment: "`MORTALITY_FATE` does -- this module never
  interprets it beyond 'is it low'"), so a third independent declaration in `state.py` matches
  an already-accepted pattern in this codebase rather than introducing a new one.
  **Alternatives considered**: restructuring imports so a shared constant module holds the
  vocabulary once — rejected as disproportionate for a three-string frozenset when the existing
  precedent (two independent declarations already coexisting) shows this codebase tolerates the
  duplication for this specific, small, stable vocabulary.
