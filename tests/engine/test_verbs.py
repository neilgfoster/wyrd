"""Tests for engine/wyrd/verbs.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import state, verbs  # noqa: E402


class RollVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def test_roll_returns_expected_shape(self):
        result = verbs.roll(sides=100, seed=1, state_path=self.path)
        self.assertEqual(result["verb"], "roll")
        self.assertEqual(result["sides"], 100)
        self.assertEqual(result["seed"], 1)
        self.assertTrue(result["state_written"])
        self.assertGreaterEqual(result["result"], 1)
        self.assertLessEqual(result["result"], 100)

    def test_roll_persists_last_roll_to_state(self):
        result = verbs.roll(sides=100, seed=1, state_path=self.path)
        loaded = state.load(self.path)
        self.assertEqual(loaded["last_roll"]["result"], result["result"])
        self.assertEqual(loaded["last_roll"]["sides"], 100)
        self.assertEqual(loaded["last_roll"]["seed"], 1)

    def test_roll_is_deterministic_given_same_seed_and_state_persists_each_time(self):
        first = verbs.roll(sides=100, seed=42, state_path=self.path)
        second = verbs.roll(sides=100, seed=42, state_path=self.path)
        self.assertEqual(first["result"], second["result"])

    def test_invalid_sides_raises_value_error(self):
        with self.assertRaises(ValueError):
            verbs.roll(sides=0, state_path=self.path)


if __name__ == "__main__":
    unittest.main()
