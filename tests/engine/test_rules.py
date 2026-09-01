"""Tests for engine/wyrd/rules.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import rules  # noqa: E402


class RollD100Test(unittest.TestCase):
    def test_same_seed_is_deterministic_across_100_calls(self):
        first = rules.roll_d100(seed=1)
        for _ in range(100):
            self.assertEqual(rules.roll_d100(seed=1), first)

    def test_no_seed_is_not_always_identical(self):
        results = {rules.roll_d100() for _ in range(50)}
        self.assertGreater(len(results), 1, "50 unseeded rolls all came back identical")

    def test_result_in_range_for_d100(self):
        for seed in range(200):
            result = rules.roll_d100(seed=seed)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 100)

    def test_result_in_range_for_other_sides(self):
        for seed in range(50):
            result = rules.roll_d100(sides=6, seed=seed)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 6)

    def test_zero_sides_rejected(self):
        with self.assertRaises(ValueError):
            rules.roll_d100(sides=0)

    def test_negative_sides_rejected(self):
        with self.assertRaises(ValueError):
            rules.roll_d100(sides=-5)

    def test_seed_does_not_leak_between_calls(self):
        # A seeded call must not perturb an immediately following unseeded call's source of
        # randomness -- i.e. the module-level `random` global must be untouched.
        rules.roll_d100(seed=1)
        results = {rules.roll_d100() for _ in range(50)}
        self.assertGreater(len(results), 1)


if __name__ == "__main__":
    unittest.main()
