"""Tests for engine/wyrd/journey.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import journey  # noqa: E402

UNPACED = {
    "id": "the-short-hop",
    "type": "arc",
    "scale": "journey",
    "from": "the-drowned-town",
    "to": "the-shrine",
}

PACED = {
    "id": "the-road-to-the-shrine",
    "type": "arc",
    "scale": "journey",
    "pace": "one day's travel",
    "hazard_rating": 4,
    "hazards": {
        "1-2": {"name": "washed-out ford", "skill": "athletics", "difficulty": "challenging"},
        "3-5": {"name": "bandits on the ridge", "skill": "perception", "difficulty": "average"},
        "6": {"name": "a traveller with news", "skill": None, "difficulty": None},
    },
    "children": [
        {"id": "first-days-road", "mode": "played"},
        {"id": "the-washed-out-ford", "mode": "summarised", "span": 2},
        {"id": "approach-to-the-shrine", "mode": "played"},
    ],
}


class LegsForTest(unittest.TestCase):
    def test_an_unpaced_journey_runs_as_a_single_leg(self):
        # spec.md US1 scenario 1.
        legs = journey.legs_for(UNPACED)
        self.assertEqual(len(legs), 1)
        self.assertEqual(legs[0]["from"], "the-drowned-town")
        self.assertEqual(legs[0]["to"], "the-shrine")
        self.assertEqual(legs[0]["mode"], "played")

    def test_a_paced_journey_uses_its_declared_children_in_order(self):
        # spec.md US1 scenario 2.
        legs = journey.legs_for(PACED)
        self.assertEqual([leg["id"] for leg in legs], [c["id"] for c in PACED["children"]])


class ResolveLegTest(unittest.TestCase):
    def test_a_played_leg_resolves_as_an_ordinary_beat(self):
        # spec.md US1 scenario 3.
        result = journey.resolve_leg({"id": "a", "mode": "played"})
        self.assertEqual(result["kind"], "beat")

    def test_a_summarised_leg_resolves_as_an_elapsed_time_advance(self):
        # spec.md US1 scenario 4.
        result = journey.resolve_leg({"id": "b", "mode": "summarised", "span": 2})
        self.assertEqual(result["kind"], "elapsed-time")
        self.assertEqual(result["span"], 2)

    def test_an_unrecognised_mode_is_a_data_error_not_a_third_mode(self):
        with self.assertRaises(ValueError):
            journey.resolve_leg({"id": "c", "mode": "narrated"})

    def test_a_leg_crossing_an_active_threats_reach_surfaces_its_ambient_cost(self):
        # spec.md US3 scenario 2.
        threats = {"the-hollow-king": {"ambient": ["a chill that never quite lifts"]}}
        leg = {"id": "d", "mode": "played", "crosses_threat": "the-hollow-king"}
        result = journey.resolve_leg(leg, threats=threats)
        self.assertEqual(result["ambient"], ["a chill that never quite lifts"])

    def test_a_leg_with_no_threat_crossing_carries_no_ambient_cost(self):
        # spec.md US3 scenario 3.
        result = journey.resolve_leg({"id": "e", "mode": "played"}, threats={})
        self.assertNotIn("ambient", result)


class RollHazardTest(unittest.TestCase):
    def test_hazard_activates_at_exactly_the_rating_times_ten_threshold(self):
        # spec.md US2 scenario 1.
        self.assertTrue(journey.roll_hazard(PACED, 40, table_roll=1)["activated"])

    def test_hazard_does_not_activate_above_the_threshold(self):
        self.assertFalse(journey.roll_hazard(PACED, 41)["activated"])

    def test_zero_hazard_rating_never_activates(self):
        # spec.md US2 scenario 2.
        no_hazard = {**PACED, "hazard_rating": 0}
        self.assertFalse(journey.roll_hazard(no_hazard, 1)["activated"])

    def test_default_hazard_rating_is_zero_and_never_activates(self):
        self.assertFalse(journey.roll_hazard(UNPACED, 1)["activated"])

    def test_a_matched_entry_with_a_skill_resolves_through_the_core_roll_request(self):
        # spec.md US2 scenario 3.
        result = journey.roll_hazard(PACED, 40, table_roll=2)
        self.assertEqual(result["matched"]["name"], "washed-out ford")
        self.assertEqual(result["kind"], "test")
        self.assertEqual(result["request"]["skill"], "athletics")
        self.assertEqual(result["request"]["difficulty"], "challenging")

    def test_a_matched_entry_on_the_boundary_of_a_second_range(self):
        result = journey.roll_hazard(PACED, 40, table_roll=3)
        self.assertEqual(result["matched"]["name"], "bandits on the ridge")

    def test_a_matched_entry_with_no_skill_is_narration_only(self):
        # spec.md US2 scenario 4.
        result = journey.roll_hazard(PACED, 40, table_roll=6)
        self.assertEqual(result["kind"], "narration")
        self.assertNotIn("request", result)

    def test_a_roll_matching_no_entry_is_a_no_op(self):
        gap = {**PACED, "hazards": {"1-2": PACED["hazards"]["1-2"]}}
        result = journey.roll_hazard(gap, 40, table_roll=5)
        self.assertTrue(result["activated"])
        self.assertIsNone(result["matched"])

    def test_an_activated_hazard_against_an_empty_table_is_a_no_op(self):
        # spec.md US2 scenario 5.
        empty = {**PACED, "hazards": {}}
        result = journey.roll_hazard(empty, 40, table_roll=1)
        self.assertTrue(result["activated"])
        self.assertIsNone(result["matched"])


class CloseJourneyTest(unittest.TestCase):
    def test_early_ending_reports_consequences_for_exactly_the_legs_reached(self):
        # spec.md US3 scenario 1.
        three_leg = {
            **PACED,
            "children": [
                {"id": "leg-1", "mode": "played"},
                {"id": "leg-2", "mode": "played"},
                {"id": "leg-3", "mode": "played"},
            ],
        }
        reached = [journey.resolve_leg(leg) for leg in three_leg["children"][:2]]
        result = journey.close_journey(three_leg, reached)
        self.assertEqual([r["leg"]["id"] for r in result["reached"]], ["leg-1", "leg-2"])
        self.assertEqual([leg["id"] for leg in result["not_reached"]], ["leg-3"])


if __name__ == "__main__":
    unittest.main()
