# Research: Threads: open-loop tracking, heat and decay

No `[NEEDS CLARIFICATION]` markers remain in spec.md. One quantitative default needed pinning
down (already recorded in spec.md's Assumptions, restated here for the record):

- **Decision**: one game-year = 365 game-days for `decay`'s whole-year stepping.
  **Rationale**: docs/design/19-campaign.md states the qualitative rule ("a thread untouched for
  a year of game time drops in heat") without naming an exact day count; 365 is the plain
  calendar year already implied by `chronicle.yaml`'s `calendar: {year, month, day}` shape
  (`state.py`), keeping this feature consistent with the rest of the engine's elapsed-time
  handling rather than inventing a second calendar convention.
  **Alternatives considered**: a settings-configurable year length — rejected as unnecessary
  ceremony; nothing else in the engine parameterises calendar length, and the design document
  itself treats "a year" as a fixed, ordinary unit.

- **Decision**: model `decay` as a pure function taking an elapsed-days integer, not an absolute
  "last touched" timestamp compared against a "current day".
  **Rationale**: matches `threat.py`'s and `journey.py`'s existing convention of taking
  caller-computed spans/rolls as arguments rather than doing date arithmetic internally — the
  caller (`advance-time`, #338) already owns the chronicle's calendar and computes elapsed spans
  for its own Threat-activation loop; this feature reuses that same shape rather than introducing
  a second way to express "how much time has passed".
  **Alternatives considered**: storing `last_touched` on the thread record and having `decay`
  read the chronicle's current date itself — rejected, since it would require this module to load
  `chronicle.yaml`, breaking the plain-dict-in/plain-dict-out convention every other runtime
  module in `engine/wyrd/` follows.
