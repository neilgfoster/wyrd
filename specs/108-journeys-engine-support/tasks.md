# Tasks: Journeys: engine support

**Input**: plan.md, spec.md in this directory.

- [X] T001 Create `engine/wyrd/journey.py` with `legs_for(journey)`: single synthetic leg when
      `pace` absent, `journey["children"]` in order when present (FR-001, SC-001).
- [X] T002 Add `resolve_leg(leg)` to `journey.py`: `mode: played` → `{"kind": "beat", ...}`,
      `mode: summarised` → `{"kind": "elapsed-time", ...}`, any other/missing value raises
      `ValueError` (FR-002).
- [X] T003 Add `roll_hazard(journey, wyrd_roll, table_roll)` to `journey.py`: activation at
      `wyrd_roll <= hazard_rating * 10` (no roll semantics implied when `hazard_rating == 0`),
      range-key match against `hazards` (parsing `"N"`/`"N-M"` keys), no-op result on no match
      (including empty table), narration-only result for a matched entry with `skill: null`, and
      a `resolution.propose`-ready request dict for a matched entry with a skill (FR-003, FR-004,
      FR-005).
- [X] T004 Add `close_journey(journey, legs_reached)` to `journey.py`: partitions
      already-produced leg/hazard results into reached-with-consequences vs. `not_reached`,
      computing nothing new itself (FR-006).
- [X] T005 Extend `resolve_leg` to surface a Threat's `ambient` list when the leg record carries
      `crosses_threat`, alongside the leg's own outcome; absent the key, no `ambient` entry is
      added (FR-007).
- [X] T006 [P] `tests/test_journey.py`: cover spec.md's acceptance scenarios — unpaced single-leg
      vs. paced multi-leg derivation (US1); `played`/`summarised` dispatch and the invalid-mode
      error (US1); hazard activation at the exact `hazard_rating * 10` boundary and at
      `hazard_rating: 0` (US2); sub-table match on both range and single-value keys, a gap
      producing a no-op, an empty table producing a no-op, and a skill-less matched entry
      returning narration (US2); early-ending reporting consequences for exactly the legs
      reached and `not_reached` for the remainder (US3); a leg with `crosses_threat` surfacing
      the Threat's `ambient` list, and one without carrying none (US3).
- [X] T007 `ruff check . && ruff format --check .` clean; `PYTHONPATH=engine pytest -q` green.
