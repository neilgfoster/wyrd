# Contract: `downtime` and `rally` CLI verbs

Both verbs follow the existing `wyrd <verb> [--flags]` shape (`--format json|text`, structured
`{"error": {...}}` on a caller-input failure) documented in docs/design/27-tooling.md.

## `downtime`

Thin wrapper selecting among `engine/wyrd/downtime.py`'s `apply_upkeep`, `apply_mend` and
`apply_rest`, by `--action`.

```
wyrd downtime --action upkeep --destination home|away --standing N --coin N [--trade standing|coin]
wyrd downtime --action mend --wound-id ID --wounds-json '<JSON list>'
wyrd downtime --action rest --stamina-max N
```

- `--action upkeep`: calls `downtime.apply_upkeep(destination, standing, coin, trade=trade)`.
  Returns `{"verb": "downtime", "action": "upkeep", "standing": ..., "coin": ..., "trade": ...}`,
  or with `"reason"` set and `"trade": None` on refusal (insufficient coin, or no trade given
  while away from home) — exactly `apply_upkeep`'s own result, unchanged.
- `--action mend`: calls `downtime.apply_mend(wound_id, wounds)`. Returns
  `{"verb": "downtime", "action": "mend", "success": ..., "wounds": ..., "closed": ...}` on
  success, or `{"verb": "downtime", "action": "mend", "success": False, "reason": ..., "wounds":
  ...}` on refusal (`unknown_wound`, `recurring`, `already_closed`).
- `--action rest`: calls `downtime.apply_rest(stamina_max)`. Returns
  `{"verb": "downtime", "action": "rest", "stamina": <stamina_max>}`.

A caller-input error (missing required flag for the chosen `--action`, invalid JSON in
`--wounds-json`) is reported as `{"error": {"verb": "downtime", "reason": ...}}`, never a bare
traceback, matching every other verb's error shape.

## `rally`

Thin wrapper over `engine/wyrd/rally.py`'s `apply_rally`, always called with `commit=None` (see
research.md — committing is the calling skill's own git step, not this verb's).

```
wyrd rally --strain N --stamina N --stamina-max N --advancement-record-json '<JSON>' \
    [--trigger TRIGGER] [--pending-json '<JSON>']
```

Calls `rally.apply_rally(strain, stamina, stamina_max, advancement_record, trigger=trigger,
pending=pending, commit=None)`. Returns
`{"verb": "rally", "strain": ..., "stamina": ..., "award": ..., "pending": ...}` — exactly
`apply_rally`'s own result, unchanged, with `"verb": "rally"` merged in (the same convention
`recap`/`save`/`spend-advance` already use).

A caller-input error (invalid JSON in `--advancement-record-json`/`--pending-json`) is reported
as `{"error": {"verb": "rally", "reason": ...}}`.
