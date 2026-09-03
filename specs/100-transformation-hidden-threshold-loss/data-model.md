# Data Model: Transformation count reaching the hidden threshold

## Character (existing entity, `engine/wyrd/character.py`, docs/design/22-state.md)

Two fields already exist on the character frontmatter and are already listed in
`PLAYER_CHARACTER_FIELDS`; this feature is the first to write to either.

### `transformations`

- **Type**: list, initialized `[]` (`engine/wyrd/creation.py`)
- **Written by**: `_stage_transformation_chain`, once per Transformation staged — an `append`
  mutation, the same mutation shape `_stage_affliction_roll` already uses for `afflictions`
- **Entry shape**: the row number (1-6) taken, mirroring `afflictions`' entries (its row's key).
  No further shape is fixed by the design documents beyond "a durable entry."
- **Read by**: the new threshold comparison, as `len(after_transformations)` against
  `hidden_threshold`

### `hidden_threshold`

- **Type**: `int | None`, secret (docs/design/13-diegesis.md "never shown")
- **Unchanged by this feature**: still set once, on the character's first Transformation, by the
  existing code path. This feature only reads it, never writes it.

### `status` (companion) / chronicle-ending signal (player character)

- **Type**: string enum for a companion — `with-party | away | dead | lost | departed`
  (docs/design/22-state.md)
- **Written by**: the new loss transition, a `set` mutation to `status: lost`, staged once the
  `transformations` count reaches `hidden_threshold` — for both `role: player` and
  `role: companion` characters, per docs/design/22-state.md's invariants line
  ("`transformations` count exceeding `hidden_threshold` sets `status: lost`").
- **Downstream effect**: removes the character from the `with-party` query
  (docs/design/22-state.md "Companions" — the party is a query, not a manifest) and, for a player
  character, is the signal docs/design/19-campaign.md's succession machinery already reads to end
  a chronicle. This feature stages the `status: lost` mutation only; it does not implement or
  duplicate succession itself (out of scope, per the issue).

### `fate`

- **Unchanged.** No mutation to `fate` is staged by the loss transition
  (docs/design/07-transformations.md: "Fate is a valve against dying, and this is a different kind
  of loss entirely").

## State transition

```
Transformation staged
  -> transformations.append(row)
  -> len(transformations) compared to hidden_threshold
       < threshold: cascade continues as before (re-roll loop may continue if Taint still ≥
         crossed threshold)
       == threshold (reaches it): status set to "lost" on the same step; the re-roll loop stops
         for this character even if Taint would otherwise call for another Transformation roll
```

No new entity is introduced. No schema migration is needed — every field this feature writes is
already declared.
