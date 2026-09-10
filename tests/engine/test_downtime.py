"""Tests for engine/wyrd/downtime.py: the Downtime phase's five steps and Mend.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import downtime  # noqa: E402


def _wound(effect, *, recurring=False, closed=None, wound_id="w1"):
    return {
        "id": wound_id,
        "effect": dict(effect),
        "bears_on": "athletics" if "skill" in effect else None,
        "recurring": recurring,
        "closed": closed,
    }


class DowntimeLoopTests(unittest.TestCase):
    # User Story 1 - the five-step sequence

    def test_full_sequence_is_legal(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        state = downtime.advance_downtime(state, "upkeep")
        state = downtime.advance_downtime(state, "advances")
        state = downtime.advance_downtime(state, "undertaking", undertaking="mend")
        state = downtime.advance_downtime(state, "rest")
        self.assertEqual(state["step"], "rest")
        self.assertEqual(state["undertaking"], "mend")

    def test_skipping_a_step_is_rejected(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        with self.assertRaises(ValueError):
            downtime.advance_downtime(state, "advances")

    def test_destination_is_only_the_first_step(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        with self.assertRaises(ValueError):
            downtime.advance_downtime(state, "destination")

    def test_second_undertaking_in_same_period_is_rejected(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        state = downtime.advance_downtime(state, "upkeep")
        state = downtime.advance_downtime(state, "advances")
        state = downtime.advance_downtime(state, "undertaking", undertaking="mend")
        with self.assertRaises(ValueError):
            downtime.advance_downtime(state, "undertaking", undertaking="recover")

    def test_undertaking_must_be_a_known_undertaking(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        state = downtime.advance_downtime(state, "upkeep")
        state = downtime.advance_downtime(state, "advances")
        with self.assertRaises(ValueError):
            downtime.advance_downtime(state, "undertaking", undertaking="not-a-thing")

    def test_input_state_is_not_mutated(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        before = dict(state)
        downtime.advance_downtime(state, "upkeep")
        self.assertEqual(state, before)


class UpkeepTests(unittest.TestCase):
    def test_at_home_costs_nothing(self):
        self.assertEqual(
            downtime.apply_upkeep("home", standing=3, coin=10),
            {"standing": 3, "coin": 10, "trade": "none"},
        )

    def test_away_standing_trade(self):
        self.assertEqual(
            downtime.apply_upkeep("away", standing=3, coin=10, trade="standing"),
            {"standing": 2, "coin": 10, "trade": "standing"},
        )

    def test_away_coin_trade(self):
        self.assertEqual(
            downtime.apply_upkeep("away", standing=3, coin=10, trade="coin"),
            {"standing": 3, "coin": 7, "trade": "coin"},
        )

    def test_away_with_no_trade_is_rejected(self):
        result = downtime.apply_upkeep("away", standing=3, coin=10)
        self.assertEqual(result["trade"], None)
        self.assertEqual(result["standing"], 3)
        self.assertEqual(result["coin"], 10)

    def test_away_coin_trade_insufficient_funds_is_rejected(self):
        result = downtime.apply_upkeep("away", standing=5, coin=2, trade="coin")
        self.assertIsNone(result["trade"])
        self.assertEqual(result["coin"], 2)


class RestTests(unittest.TestCase):
    def test_rest_returns_maximum_unconditionally(self):
        self.assertEqual(downtime.apply_rest(stamina_max=8), 8)


class CloseDowntimeTests(unittest.TestCase):
    def test_close_exposes_calendar_advance(self):
        state = downtime.new_downtime_state()
        self.assertEqual(downtime.close_downtime(state), {"calendar_advanced": True})


class MendTests(unittest.TestCase):
    # User Story 2 - Mend steps one grade, never touches a recurring wound

    def test_mend_skill_first_rung(self):
        wounds = [_wound({"skill": -10})]
        result = downtime.apply_mend("w1", wounds)
        self.assertTrue(result["success"])
        self.assertFalse(result["closed"])
        self.assertEqual(result["wounds"][0]["effect"], {"skill": -5})
        self.assertIsNone(result["wounds"][0]["closed"])

    def test_mend_skill_second_rung_closes(self):
        wounds = [_wound({"skill": -5})]
        result = downtime.apply_mend("w1", wounds)
        self.assertTrue(result["success"])
        self.assertTrue(result["closed"])
        mended = result["wounds"][0]
        self.assertEqual(mended["effect"], {})
        self.assertIsNotNone(mended["closed"])
        self.assertEqual(mended["id"], "w1")
        self.assertEqual(mended["bears_on"], "athletics")

    def test_mend_stamina_max_closes_directly(self):
        wounds = [_wound({"stamina_max": -1})]
        result = downtime.apply_mend("w1", wounds)
        self.assertTrue(result["success"])
        self.assertTrue(result["closed"])

    def test_mend_dread_closes_directly(self):
        wounds = [_wound({"dread": 1})]
        result = downtime.apply_mend("w1", wounds)
        self.assertTrue(result["success"])
        self.assertTrue(result["closed"])

    def test_mend_leaves_other_fields_untouched(self):
        wounds = [_wound({"skill": -10}, wound_id="the-knee-that-never-set")]
        result = downtime.apply_mend("the-knee-that-never-set", wounds)
        mended = result["wounds"][0]
        self.assertEqual(mended["id"], "the-knee-that-never-set")
        self.assertEqual(mended["recurring"], False)

    def test_mend_rejects_recurring_wound(self):
        wounds = [_wound({"skill": -10}, recurring=True)]
        result = downtime.apply_mend("w1", wounds)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "recurring")
        self.assertEqual(result["wounds"], wounds)

    def test_mend_repeated_attempts_never_close_a_recurring_wound(self):
        wounds = [_wound({"skill": -10}, recurring=True)]
        for _ in range(5):
            result = downtime.apply_mend("w1", wounds)
            self.assertFalse(result["success"])
            wounds = result["wounds"]
        self.assertIsNone(wounds[0]["closed"])

    def test_mend_rejects_unknown_wound_id(self):
        result = downtime.apply_mend("no-such-wound", [_wound({"skill": -10})])
        self.assertEqual(result["reason"], "unknown_wound")

    def test_mend_rejects_already_closed_wound(self):
        wounds = [_wound({}, closed=True)]
        result = downtime.apply_mend("w1", wounds)
        self.assertEqual(result["reason"], "already_closed")

    def test_mend_does_not_mutate_input_list(self):
        wounds = [_wound({"skill": -10})]
        original = [dict(wounds[0])]
        downtime.apply_mend("w1", wounds)
        self.assertEqual(wounds, original)

    def test_mend_consumes_the_downtime_undertaking_slot(self):
        state = downtime.new_downtime_state()
        state = downtime.advance_downtime(state, "destination")
        state = downtime.advance_downtime(state, "upkeep")
        state = downtime.advance_downtime(state, "advances")
        state = downtime.advance_downtime(state, "undertaking", undertaking="mend")
        self.assertTrue(state["undertaking_chosen"])
        with self.assertRaises(ValueError):
            downtime.advance_downtime(state, "undertaking", undertaking="pursue")


if __name__ == "__main__":
    unittest.main()
