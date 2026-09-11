# Research: Scenario selection by thread heat and hooks

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Two decisions worth recording:

- **Decision**: a scenario's match score against live threads is the *sum of heat* across every
  live thread whose own `hooks` list shares at least one entry with the scenario's `hooks`
  (counting each matching thread once, regardless of how many individual hooks it shares).
  **Rationale**: docs/design/19-campaign.md's own phrasing -- "finding one whose hooks match
  threads that are currently hot" -- ties selection to *heat*, not hook count; summing heat
  across matched threads is the direct reading of "the hottest match wins" without inventing a
  weighting scheme the design text doesn't specify.
  **Alternatives considered**: counting matched hooks instead of summed thread heat -- rejected;
  a scenario matching three cold threads would then beat one matching a single very hot thread,
  which inverts what "hot" is supposed to mean in this design.

- **Decision**: encounter scaling calls `adversary.scaled_count(written_count, danger, party,
  written_for)` per encounter, unchanged -- this feature supplies no new arguments beyond what
  that function already takes.
  **Rationale**: `adversary.scaled_count` already implements docs/design/03-rules.md section 7's
  full scaling formula (#98, epic #8) -- introducing a second scaling path here would duplicate
  logic this codebase has already gotten right once, and risks drifting from it (CLAUDE.md's own
  warning about two documents/mechanisms describing one thing differently).
  **Alternatives considered**: none seriously -- reusing the existing function is the only
  option consistent with FR-005's explicit "no new scaling formula" constraint.
