"""Tests for engine/wyrd/corpus_scenario.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import adversary  # noqa: E402
from wyrd import corpus_scenario as cs  # noqa: E402


def _record(**overrides) -> dict:
    base = {
        "id": "the-drowning-well",
        "settings": ["my-setting"],
        "scale": "village",
        "region": "any",
        "danger": 3,
        "written_for": 4,
        "length": 2,
        "season": "any",
        "needs_access": ["temple"],
        "needs_capability": ["literacy"],
        "helped_by": ["medicine"],
        "adaptation": "reskin",
    }
    base.update(overrides)
    return base


class ValidateScenarioRecordTests(unittest.TestCase):
    def test_all_nine_scale_values(self) -> None:
        for scale in (
            "village",
            "town",
            "city",
            "wilderness",
            "underground",
            "waterway",
            "road",
            "ship",
            "fortress",
        ):
            with self.subTest(scale=scale):
                cs.validate_scenario_record(_record(scale=scale))

    def test_all_four_season_values(self) -> None:
        for season in ("any", "winter", "harvest", "festival"):
            with self.subTest(season=season):
                cs.validate_scenario_record(_record(season=season))

    def test_rejects_unknown_scale(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            cs.validate_scenario_record(_record(scale="continent"))
        self.assertIn("scale", str(ctx.exception))

    def test_rejects_unknown_season(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            cs.validate_scenario_record(_record(season="summer"))
        self.assertIn("season", str(ctx.exception))


class ScaleDangerTests(unittest.TestCase):
    def test_matches_adversary_danger_effective_exactly(self) -> None:
        record = _record(danger=3, written_for=4)
        result = cs.scale_danger(record, party=6)
        self.assertEqual(result, adversary.danger_effective(3, 6, 4))

    def test_party_of_one_still_produces_a_value(self) -> None:
        record = _record(danger=3, written_for=4)
        result = cs.scale_danger(record, party=1)
        self.assertEqual(result, adversary.danger_effective(3, 1, 4))


class CheckRequirementsTests(unittest.TestCase):
    def test_unmet_reported_not_excluded(self) -> None:
        record = _record(needs_access=["temple"], needs_capability=["literacy"])
        result = cs.check_requirements(record, available_access=[], available_capability=[])
        self.assertEqual(result["access"]["unmet"], ["temple"])
        self.assertEqual(result["capability"]["unmet"], ["literacy"])

    def test_met_reported(self) -> None:
        record = _record(needs_access=["temple"], needs_capability=["literacy"])
        result = cs.check_requirements(
            record, available_access=["temple"], available_capability=["literacy"]
        )
        self.assertEqual(result["access"]["met"], ["temple"])
        self.assertEqual(result["capability"]["met"], ["literacy"])

    def test_empty_requirements_trivially_met(self) -> None:
        record = _record(needs_access=[], needs_capability=[])
        result = cs.check_requirements(record, available_access=[], available_capability=[])
        self.assertEqual(result["access"], {"met": [], "unmet": []})
        self.assertEqual(result["capability"], {"met": [], "unmet": []})


class CheckHelpedByTests(unittest.TestCase):
    def test_reports_met_and_unmet_regardless(self) -> None:
        record = _record(helped_by=["medicine", "literacy"])
        result = cs.check_helped_by(record, available=["medicine"])
        self.assertEqual(result["met"], ["medicine"])
        self.assertEqual(result["unmet"], ["literacy"])
        # never raises, never filters -- record is not touched at all by this call


class IsEligibleForSettingTests(unittest.TestCase):
    def test_eligible(self) -> None:
        record = _record(settings=["my-setting"])
        self.assertTrue(cs.is_eligible_for_setting(record, "my-setting"))

    def test_ineligible(self) -> None:
        record = _record(settings=["my-setting"])
        self.assertFalse(cs.is_eligible_for_setting(record, "some-other-setting"))


if __name__ == "__main__":
    unittest.main()
