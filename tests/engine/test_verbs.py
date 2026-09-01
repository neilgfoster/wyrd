"""Tests for engine/wyrd/verbs.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import os
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


class OpposedTestVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name)
        self._cwd = pathlib.Path.cwd()
        os.chdir(self.path)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_returns_expected_shape(self):
        result = verbs.opposed_test(skill=70, opponent=30, seed=1)
        self.assertEqual(result["verb"], "opposed-test")
        self.assertEqual(result["skill"], 70)
        self.assertEqual(result["opponent"], 30)
        self.assertEqual(result["effective_pct"], 90)
        self.assertIn("roll", result)
        self.assertIn("success", result)
        self.assertIn("degrees", result)
        self.assertIn("wyrd", result)

    def test_performs_no_state_write(self):
        verbs.opposed_test(skill=70, opponent=30, seed=1)
        self.assertFalse((self.path / "chronicle_state.yaml").exists())

    def test_deterministic_given_same_seed(self):
        first = verbs.opposed_test(skill=70, opponent=30, seed=42)
        second = verbs.opposed_test(skill=70, opponent=30, seed=42)
        self.assertEqual(first, second)

    def test_passes_declaration_and_helper_through(self):
        result = verbs.opposed_test(
            skill=50, opponent=50, declaration="specific", helper_skill=45, seed=1
        )
        self.assertEqual(result["effective_pct"], 64)


class DeclarationBonusVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.declaration_bonus("specific")
        self.assertEqual(result["verb"], "declaration-bonus")
        self.assertEqual(result["category"], "specific")
        self.assertEqual(result["bonus"], 10)
        self.assertFalse(result["no_roll"])

    def test_removes_risk_shape(self):
        result = verbs.declaration_bonus("removes_risk")
        self.assertIsNone(result["bonus"])
        self.assertTrue(result["no_roll"])


class AssistanceBonusVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.assistance_bonus(45)
        self.assertEqual(result["verb"], "assistance-bonus")
        self.assertEqual(result["helper_skill"], 45)
        self.assertTrue(result["can_attempt"])
        self.assertEqual(result["bonus"], 4)


class GroupTestVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.group_test(
            member_skills=[70, 45, 30], mode="most_capable", opponent=50, seed=1
        )
        self.assertEqual(result["verb"], "group-test")
        self.assertEqual(result["selected_skill"], 70)
        self.assertEqual(result["mode"], "most_capable")
        self.assertEqual(result["member_skills"], [70, 45, 30])


class ResolveExtendedIntervalVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.resolve_extended_interval(
            skill=45, opponent=50, progress=2, target=4, seed=1
        )
        self.assertEqual(result["verb"], "extended-task-interval")
        self.assertEqual(result["target"], 4)
        self.assertIn("gained", result)
        self.assertIn("done", result)


class CharacterVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "aria.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_then_load_round_trip(self):
        verbs.character_save(path=self.path, frontmatter={"id": "aria"}, body="Prose.\n")
        loaded = verbs.character_load(path=self.path)
        self.assertEqual(loaded["verb"], "character-load")
        self.assertEqual(loaded["frontmatter"], {"id": "aria"})
        self.assertEqual(loaded["body"], "Prose.\n")


class SkillScaleVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.skill_scale()
        self.assertEqual(result["verb"], "skill-scale")
        self.assertEqual(result["open_value"], 25)
        self.assertEqual(result["advance_step"], 5)
        self.assertEqual(result["untrained"], 10)


if __name__ == "__main__":
    unittest.main()
