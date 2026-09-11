# Research: Scenario index schema and deterministic selection (scenarios.json)

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Two decisions worth recording:

- **Decision**: `scale_danger(scenario, party)` calls `adversary.danger_effective(scenario["danger"],
  party, scenario["written_for"])` directly, unchanged.
  **Rationale**: `adversary.danger_effective` already implements docs/design/03-rules.md section
  7's full formula (#98, epic #8); this feature's own job is only to route a scenario record's
  `danger`/`written_for` fields into it, matching #339's `scale_encounters`'s identical
  discipline toward `adversary.scaled_count`.
  **Alternatives considered**: none seriously — FR-004 explicitly forbids a second formula.

- **Decision**: `check_requirements`/`check_helped_by` return a report dict (`{"met": [...],
  "unmet": [...]}`), never a boolean pass/fail and never filter the scenario itself out of any
  collection.
  **Rationale**: docs/design/26-corpus-index.md is explicit that these fields are "inputs, not
  walls" — "obtaining it may itself become play" for `needs_access`, and `helped_by` is
  "flags only — easier with it, and more desperate and interesting without." A boolean
  pass/fail return shape would invite a caller to treat it as a filter by habit; a met/unmet
  report shape makes the informational nature structurally visible in the return value itself.
  **Alternatives considered**: a single boolean `all_met` — rejected, since it collapses exactly
  the distinction (which specific requirement is unmet, and by how much) a GM would want when
  deciding whether "obtaining the in" is itself worth playing out.
