"""Tests for engine/wyrd/economy.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import economy  # noqa: E402

CATALOG = [
    {"id": "shortsword", "name": "Shortsword", "price": 12},
    {"id": "dagger", "name": "Dagger", "price": 5},
]


class SpendCoinTest(unittest.TestCase):
    def test_an_affordable_purchase_falls_coin_by_exactly_the_price(self):
        # spec.md US1 scenario 1.
        result = economy.spend_coin("shortsword", 20, CATALOG)
        self.assertTrue(result["success"])
        self.assertEqual(result["coin"], 8)
        self.assertEqual(result["item"]["id"], "shortsword")

    def test_an_unaffordable_purchase_is_refused_and_leaves_coin_unchanged(self):
        # spec.md US1 scenario 2.
        result = economy.spend_coin("shortsword", 5, CATALOG)
        self.assertFalse(result["success"])
        self.assertEqual(result["coin"], 5)
        self.assertIn("insufficient coin", result["reason"])

    def test_an_unknown_gear_id_is_refused_naming_the_id(self):
        # spec.md US1 scenario 3.
        result = economy.spend_coin("nonexistent", 20, CATALOG)
        self.assertFalse(result["success"])
        self.assertIn("nonexistent", result["reason"])

    def test_a_purchase_priced_at_exactly_current_coin_succeeds_at_zero(self):
        # spec.md Edge Cases: exact-price purchase.
        result = economy.spend_coin("dagger", 5, CATALOG)
        self.assertTrue(result["success"])
        self.assertEqual(result["coin"], 0)


class MartialWeaponSightingTest(unittest.TestCase):
    def test_an_open_sighting_falls_standing_by_exactly_one(self):
        # spec.md US2 scenario 1.
        result = economy.martial_weapon_sighting(3, already_applied=False)
        self.assertEqual(result["standing"], 2)
        self.assertTrue(result["applied"])

    def test_an_already_charged_sighting_does_not_fall_standing_again(self):
        # spec.md US2 scenario 2/SC-002.
        result = economy.martial_weapon_sighting(2, already_applied=True)
        self.assertEqual(result["standing"], 2)
        self.assertFalse(result["applied"])


class AdjustStandingTest(unittest.TestCase):
    def test_a_negative_delta_lands_on_current_standing_exactly(self):
        # spec.md US3 scenario 1.
        result = economy.adjust_standing(4, -2)
        self.assertEqual(result["standing"], 2)

    def test_standing_has_no_floor(self):
        # spec.md US3 scenario 2: Standing is an open count, like Taint and Trauma.
        result = economy.adjust_standing(0, -1)
        self.assertEqual(result["standing"], -1)

    def test_a_zero_delta_is_a_no_op(self):
        # spec.md Edge Cases.
        result = economy.adjust_standing(4, 0)
        self.assertEqual(result["standing"], 4)


class AllegianceTest(unittest.TestCase):
    def test_gaining_an_allegiance_adds_it_once(self):
        # spec.md US1 scenario 1.
        result = economy.gain_allegiance("the-cell", [])
        self.assertTrue(result["success"])
        self.assertEqual(result["allegiances"], ["the-cell"])

    def test_gaining_an_allegiance_already_held_is_idempotent(self):
        # spec.md US1 scenario 2.
        result = economy.gain_allegiance("the-cell", ["the-cell"])
        self.assertTrue(result["success"])
        self.assertEqual(result["allegiances"], ["the-cell"])

    def test_losing_a_held_allegiance_removes_it(self):
        # spec.md US1 scenario 3.
        result = economy.lose_allegiance("the-cell", ["the-cell", "the-guild"])
        self.assertTrue(result["success"])
        self.assertEqual(result["allegiances"], ["the-guild"])

    def test_losing_an_unheld_allegiance_is_refused_and_leaves_the_list_unchanged(self):
        # spec.md US1 scenario 4.
        result = economy.lose_allegiance("the-cell", ["the-guild"])
        self.assertFalse(result["success"])
        self.assertEqual(result["allegiances"], ["the-guild"])
        self.assertIn("the-cell", result["reason"])


class HoldingTest(unittest.TestCase):
    def test_gaining_a_holding_adds_it_once(self):
        # spec.md US2 scenario 1.
        result = economy.gain_holding("the-mill", [])
        self.assertTrue(result["success"])
        self.assertEqual(result["holdings"], ["the-mill"])

    def test_gaining_a_holding_already_held_is_idempotent(self):
        # spec.md US2 scenario 2.
        result = economy.gain_holding("the-mill", ["the-mill"])
        self.assertTrue(result["success"])
        self.assertEqual(result["holdings"], ["the-mill"])

    def test_losing_a_held_holding_removes_it(self):
        # spec.md US2 scenario 3.
        result = economy.lose_holding("the-mill", ["the-mill", "the-boat"])
        self.assertTrue(result["success"])
        self.assertEqual(result["holdings"], ["the-boat"])

    def test_losing_an_unheld_holding_is_refused_and_leaves_the_list_unchanged(self):
        # spec.md US2 scenario 4.
        result = economy.lose_holding("the-mill", ["the-boat"])
        self.assertFalse(result["success"])
        self.assertEqual(result["holdings"], ["the-boat"])
        self.assertIn("the-mill", result["reason"])


class RollStandingTest(unittest.TestCase):
    def test_a_positive_standing_can_roll_favourable(self):
        # spec.md US3 scenario 1.
        result = economy.roll_standing(8, roll=1)
        self.assertEqual(result["outcome"], "favourable")
        self.assertNotIn("skill", result)

    def test_zero_standing_can_roll_not_recognised(self):
        # spec.md US3 scenario 2.
        result = economy.roll_standing(0, roll=50)
        self.assertEqual(result["outcome"], "neutral")

    def test_a_negative_standing_can_roll_unfavourable(self):
        # spec.md US3 scenario 3.
        result = economy.roll_standing(-8, roll=100)
        self.assertEqual(result["outcome"], "unfavourable")

    def test_the_outcome_never_carries_a_skill_or_difficulty_value(self):
        # spec.md US3 scenario 4/FR-006.
        result = economy.roll_standing(5, roll=42)
        self.assertEqual(set(result), {"outcome"})


if __name__ == "__main__":
    unittest.main()
