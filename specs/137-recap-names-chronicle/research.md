# Research: Recap names its chronicle and setting

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One decision worth recording:

- **Decision**: the new section reads `chronicle.get("name")` and
  `chronicle.get("setting", {}).get("repo")`, each independently falling back to
  `_RECAP_PLACEHOLDER` — not a single combined "chronicle identity" field.
  **Rationale**: `state.default_chronicle_state`'s existing shape already separates `name`
  (the chronicle's own id) from `setting.repo` (the setting it runs under) — reading them
  independently, with independent fallbacks, matches every other section's existing convention
  (`where`/`changes`/`body_mind` each fall back independently) rather than introducing a new
  combined-or-nothing rule.
  **Alternatives considered**: requiring both present or neither shown — rejected; a chronicle
  missing one field (e.g. an in-progress migration) shouldn't suppress the other's already-known
  value.
