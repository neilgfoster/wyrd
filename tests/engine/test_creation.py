"""Tests for engine/wyrd/creation.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, creation  # noqa: E402

CAREER = {"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True}
VALID_ACTIONS = (
    [
        {"action": "open", "skill": "stealth"},
        {"action": "open", "skill": "swordplay"},
    ]
    + [{"action": "raise", "skill": "stealth"}] * 4
    + [{"action": "raise", "skill": "swordplay"}] * 2
)


def _base_kwargs(path):
    return dict(
        path=path,
        name="Aria Nightingale",
        career=CAREER,
        actions=VALID_ACTIONS,
        loyalty="the-old-guard",
        mortality="standard",
        fault_line="She trusts no one, because the guild sold her out once.",
    )


class MortalityToFateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def _create(self, mortality):
        path = pathlib.Path(self._tmp.name) / f"{mortality}.md"
        kwargs = _base_kwargs(path)
        kwargs["mortality"] = mortality
        return creation.create_character(**kwargs)

    def test_low(self):
        result = self._create("low")
        self.assertEqual(result["frontmatter"]["fate"], {"current": 2, "max": 2})
        self.assertEqual(result["frontmatter"]["fortune"], {"current": 2})

    def test_standard(self):
        result = self._create("standard")
        self.assertEqual(result["frontmatter"]["fate"], {"current": 3, "max": 3})
        self.assertEqual(result["frontmatter"]["fortune"], {"current": 3})

    def test_high(self):
        result = self._create("high")
        self.assertEqual(result["frontmatter"]["fate"], {"current": 4, "max": 4})
        self.assertEqual(result["frontmatter"]["fortune"], {"current": 4})


class FixedValuesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_stamina_and_zeroed_tracks_across_varied_inputs(self):
        variants = [
            {},
            {"name": "Someone Else", "loyalty": "a-different-loyalty"},
            {"mortality": "high"},
        ]
        for i, override in enumerate(variants):
            path = pathlib.Path(self._tmp.name) / f"c{i}.md"
            kwargs = _base_kwargs(path)
            kwargs.update(override)
            result = creation.create_character(**kwargs)
            fm = result["frontmatter"]
            self.assertEqual(fm["stamina"], {"current": 6, "max": 6})
            self.assertEqual(fm["taint"], 0)
            self.assertEqual(fm["trauma"], 0)
            self.assertEqual(fm["strain"], 0)
            self.assertEqual(fm["dread"], 0)
            self.assertEqual(fm["resolve"], {"current": 0})


class AllocationCompositionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_skills_match_validator_output(self):
        path = pathlib.Path(self._tmp.name) / "aria.md"
        result = creation.create_character(**_base_kwargs(path))
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["frontmatter"]["skills"], {"stealth": 45, "swordplay": 35})

    def test_invalid_allocation_rejected_and_writes_nothing(self):
        path = pathlib.Path(self._tmp.name) / "bad.md"
        kwargs = _base_kwargs(path)
        kwargs["actions"] = []  # wrong total
        result = creation.create_character(**kwargs)
        self.assertFalse(result["valid"])
        self.assertIn("error", result)
        self.assertFalse(path.exists())

    def test_cap_exceeded_rejected_and_writes_nothing(self):
        path = pathlib.Path(self._tmp.name) / "bad2.md"
        kwargs = _base_kwargs(path)
        kwargs["actions"] = [
            {"action": "open", "skill": "stealth"},
            {"action": "open", "skill": "swordplay"},
        ] + [{"action": "raise", "skill": "swordplay"}] * 6
        result = creation.create_character(**kwargs)
        self.assertFalse(result["valid"])
        self.assertFalse(path.exists())


class FictionPassThroughTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_fiction_fields_carried_through_unchanged(self):
        path = pathlib.Path(self._tmp.name) / "aria.md"
        kwargs = _base_kwargs(path)
        kwargs["drives"] = ["find the truth"]
        kwargs["misfortune"] = "hunted by the guild"
        result = creation.create_character(**kwargs)
        fm = result["frontmatter"]
        self.assertEqual(fm["name"], "Aria Nightingale")
        self.assertEqual(fm["loyalty"], "the-old-guard")
        self.assertEqual(fm["drives"], ["find the truth"])
        self.assertEqual(fm["misfortune"], "hunted by the guild")
        self.assertEqual(
            fm["fault_line"], "She trusts no one, because the guild sold her out once."
        )

    def test_empty_lists_and_defaults(self):
        path = pathlib.Path(self._tmp.name) / "aria.md"
        result = creation.create_character(**_base_kwargs(path))
        fm = result["frontmatter"]
        for field in (
            "career_history",
            "wounds",
            "holdings",
            "allegiances",
            "marks",
            "transformations",
            "afflictions",
        ):
            self.assertEqual(fm[field], [])
        self.assertEqual(fm["advances_unspent"], 0)
        self.assertIsNone(fm["hidden_threshold"])
        self.assertIsNone(fm["pending_omen"])
        self.assertEqual(fm["reputation"], {"score": 0, "label": None})
        self.assertEqual(fm["role"], "player")


class RoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_created_character_round_trips_via_character_module(self):
        path = pathlib.Path(self._tmp.name) / "aria.md"
        result = creation.create_character(**_base_kwargs(path))
        loaded_frontmatter, _ = character.load(path)
        self.assertEqual(loaded_frontmatter, result["frontmatter"])


if __name__ == "__main__":
    unittest.main()
