"""Tests for engine/wyrd/advance_time.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import advance_time  # noqa: E402


class AdvanceCalendarTests(unittest.TestCase):
    def test_plain_advance(self) -> None:
        calendar = {"year": 1, "month": None, "day": 100}
        result = advance_time.advance_calendar(calendar, 20)
        self.assertEqual(result, {"year": 1, "month": None, "day": 120})

    def test_year_boundary_wraps(self) -> None:
        calendar = {"year": 1, "month": None, "day": 350}
        result = advance_time.advance_calendar(calendar, 20)
        self.assertEqual(result["year"], 2)
        self.assertEqual(result["day"], 5)

    def test_zero_elapsed_is_no_op(self) -> None:
        calendar = {"year": 1, "month": None, "day": 100}
        result = advance_time.advance_calendar(calendar, 0)
        self.assertEqual(result, calendar)

    def test_month_untouched(self) -> None:
        calendar = {"year": 1, "month": "spring", "day": 10}
        result = advance_time.advance_calendar(calendar, 5)
        self.assertEqual(result["month"], "spring")


class ExpectedActivationCountTests(unittest.TestCase):
    def test_documented_worked_example(self) -> None:
        # imminence 4 over 5 weeks (35 days): round(5 * 4 / 10) = round(2.0) = 2
        self.assertEqual(advance_time.expected_activation_count(4, 35), 2)

    def test_rounds_to_zero(self) -> None:
        # imminence 2 over 1 week (7 days): round(1 * 2 / 10) = round(0.2) = 0
        self.assertEqual(advance_time.expected_activation_count(2, 7), 0)

    def test_zero_elapsed_days(self) -> None:
        self.assertEqual(advance_time.expected_activation_count(4, 0), 0)

    def test_three_weeks_imminence_four(self) -> None:
        # round(3 * 4 / 10) = round(1.2) = 1
        self.assertEqual(advance_time.expected_activation_count(4, 21), 1)


class AdvanceTimeTests(unittest.TestCase):
    def _threat(self, imminence: int) -> dict:
        return {
            "id": "the-drowned-count",
            "threat": {"imminence": imminence, "effects": {"1-100": "grows stronger"}},
        }

    def test_effects_count_matches_activation_count(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        result = advance_time.advance_time(calendar, [self._threat(4)], elapsed_days=35, seed=1)
        activation = result["activations"][0]
        self.assertEqual(activation["activation_count"], 2)
        self.assertEqual(len(activation["effects"]), 2)

    def test_zero_activations_yields_empty_effects(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        result = advance_time.advance_time(calendar, [self._threat(2)], elapsed_days=7, seed=1)
        activation = result["activations"][0]
        self.assertEqual(activation["activation_count"], 0)
        self.assertEqual(activation["effects"], [])

    def test_seed_reproducibility(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        threats = [self._threat(4)]
        first = advance_time.advance_time(calendar, threats, elapsed_days=35, seed=42)
        second = advance_time.advance_time(calendar, threats, elapsed_days=35, seed=42)
        self.assertEqual(first, second)

    def test_empty_threats_list(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        result = advance_time.advance_time(calendar, [], elapsed_days=35, seed=1)
        self.assertEqual(result["activations"], [])
        self.assertEqual(result["calendar"]["day"], 35)

    def test_multiple_threats_in_one_call(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        threats = [self._threat(4), {**self._threat(2), "id": "the-quiet-plague"}]
        result = advance_time.advance_time(calendar, threats, elapsed_days=35, seed=1)
        self.assertEqual(len(result["activations"]), 2)
        self.assertEqual(result["activations"][0]["id"], "the-drowned-count")
        self.assertEqual(result["activations"][1]["id"], "the-quiet-plague")

    def test_calendar_still_advances_with_no_seed(self) -> None:
        calendar = {"year": 1, "month": None, "day": 0}
        result = advance_time.advance_time(calendar, [self._threat(4)], elapsed_days=35)
        self.assertEqual(result["calendar"]["day"], 35)
        self.assertEqual(result["activations"][0]["activation_count"], 2)


if __name__ == "__main__":
    unittest.main()
