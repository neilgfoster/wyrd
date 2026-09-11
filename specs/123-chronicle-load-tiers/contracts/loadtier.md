# Contract: `engine/wyrd/loadtier.py`

This is a library module (no CLI verb in this feature) exposing the following public functions.

## `always_tier(entities: dict[str, dict]) -> dict`

Returns `{"player_character": dict | None, "companions": dict[str, dict], "threads": dict[str,
dict]}` — see data-model.md. Pure function of `entities`; makes no I/O call itself.

- Raises nothing on an empty `entities` mapping — returns `{"player_character": None,
  "companions": {}, "threads": {}}`.
- More than one entity with `role: player` is a caller/data error, not this function's to
  arbitrate silently: raises `ValueError` naming both ids.

## `lookup(entity_id: str, entities: dict[str, dict]) -> dict | None`

On-demand fetch by id. Returns the entity's frontmatter dict, or `None` if `entity_id` is absent.

## `search(term: str, entities: dict[str, dict], bodies: dict[str, str] | None = None) -> list[str]`

On-demand search. Returns the ids (in `entities`' own iteration order) of every entity whose
frontmatter values (stringified) or whose body (if `bodies` supplies one for that id) contain
`term`, case-insensitively. Empty `term` returns an empty list rather than matching everything.

## `generate_recap(entities: dict[str, dict], chronicle: dict, *, where: str | None = None, changes: list[str] | None = None, body_mind: str | None = None) -> str`

Returns the recap.md text (see data-model.md for section derivation). Deterministic given the
same inputs — no randomness, no clock read beyond what `chronicle` already carries.

## Wiring into `engine/wyrd/session.py`

`run_close(steps)` already accepts a list of zero-argument callables (existing contract, no
signature change). This feature's caller wires a closure over `generate_recap` plus
`state.write_text_atomic` into that list — `session.py` itself gains no new public function.
