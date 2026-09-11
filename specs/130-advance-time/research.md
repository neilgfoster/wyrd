# Research: Elapsed time and the advance-time command

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Two decisions worth recording:

- **Decision**: the expected-value formula is `round(weeks * imminence / 10)`, `weeks = elapsed //
  7`, using Python's banker's-rounding `round()`.
  **Rationale**: docs/design/19-campaign.md's own worked example -- "A threat at imminence 4
  activates roughly once per three weeks, so a five-week jump produces about two activations" --
  matches `5 * 4 / 10 = 2.0` exactly, confirming the formula's shape (weeks times the per-week
  percentage, `imminence * 10%`). `round()` is the plain reading of "roughly"/"about" in the
  design text; no other rounding convention is used anywhere else in this codebase for a similar
  expected-value computation.
  **Alternatives considered**: floor or ceiling instead of round-to-nearest — rejected; both
  would systematically bias the long-run activation rate low or high relative to the stated
  per-week percentage, where round-to-nearest does not.

- **Decision**: `advance_time` takes a seed and calls `rules.roll_d100(seed=seed)` once per
  activation (varying an offset per call so repeated activations for the same Threat, or across
  Threats, don't all draw the identical roll), rather than requiring the caller to supply a list
  of pre-rolled values the way `threat.check_activation`/`resolve_effects` take caller-supplied
  dice.
  **Rationale**: this issue's own acceptance criterion is explicit -- "deterministic given a
  fixed seed" -- which is exactly `verbs.roll`'s existing convention (an optional `seed` argument
  routed to `rules.roll_d100`) for a top-level operation that may need to generate an a priori
  unknown number of rolls (the activation count itself is computed, not caller-supplied).
  `threat.py`'s per-check convention still applies at the single-Threat, single-week level; this
  module is the one level up that owns generating the rolls a multi-week span implies.
  **Alternatives considered**: requiring the caller to pre-generate and pass in exactly
  `activation_count` rolls per Threat — rejected, since the caller cannot know
  `activation_count` in advance without first calling this module's own formula, creating an
  awkward two-step protocol for no benefit over an internal seeded roll.

- **Decision**: a 365-day year, `day` wraps at 365 into `year`, `month` untouched.
  **Rationale**: reuses #335's already-established decision (`thread.py`'s decay stepping)
  rather than introducing a second calendar-length convention in the same engine.
  **Alternatives considered**: none — this is a straight reuse of an existing decision, not a new
  question.
