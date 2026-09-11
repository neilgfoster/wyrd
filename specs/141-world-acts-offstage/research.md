# Research: world_acts_offstage gates threat activation while the character is elsewhere

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision worth recording:

- **Decision**: two separate parameters (`world_acts_offstage`, `witnessed`), both required to
  be `False` together to suppress activation — not a single combined flag.
  **Rationale**: the design document names two genuinely independent facts: a chronicle-level
  setting choice (`world_acts_offstage`, from `intent`, fixed for the whole chronicle unless
  revised) and a per-call fact about this particular elapsed span (whether the player was
  actually present for it). Collapsing them into one parameter would force the caller to
  re-derive `world_acts_offstage`'s value at every call site instead of reading it once from
  the chronicle, or would force this feature to load `chronicle.yaml` itself (breaking the
  no-I/O convention every sibling module keeps).
  **Alternatives considered**: reading `chronicle["intent"]["world_acts_offstage"]` internally
  — rejected; this module takes no chronicle dict at all today (only `calendar`), and adding
  one just to read a single boolean would be a much larger signature change than two booleans.
