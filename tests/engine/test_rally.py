"""Tests for engine/wyrd/rally.py: fixed Strain/Stamina recovery, the optional advance-award
hook, and the persist/commit step.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import advancement, rally  # noqa: E402


class RallyTests(unittest.TestCase):
    # User Story 1 - fixed recovery at a Rally

    def test_apply_recovery_reduces_strain_and_raises_stamina(self):
        self.assertEqual(
            rally.apply_recovery(strain=3, stamina=4, stamina_max=6),
            {"strain": 2, "stamina": 5},
        )

    def test_apply_recovery_floors_strain_at_zero(self):
        self.assertEqual(rally.apply_recovery(strain=0, stamina=4, stamina_max=6)["strain"], 0)

    def test_apply_recovery_caps_stamina_at_maximum(self):
        self.assertEqual(rally.apply_recovery(strain=1, stamina=6, stamina_max=6)["stamina"], 6)

    # User Story 2 - the advance award is optional

    def test_apply_rally_with_no_trigger_leaves_award_none(self):
        record = advancement.new_record()
        result = rally.apply_rally(strain=3, stamina=4, stamina_max=6, advancement_record=record)
        self.assertIsNone(result["award"])
        self.assertEqual(result["strain"], 2)
        self.assertEqual(result["stamina"], 5)

    def test_apply_rally_with_valid_trigger_matches_award_advance_directly(self):
        result = rally.apply_rally(
            strain=3,
            stamina=4,
            stamina_max=6,
            advancement_record=advancement.new_record(),
            trigger="endured",
        )
        expected = advancement.award_advance("endured", advancement.new_record())
        self.assertEqual(result["award"], expected)

    def test_apply_rally_refused_award_still_applies_recovery(self):
        already_awarded = advancement.award_advance("endured", advancement.new_record())["record"]
        result = rally.apply_rally(
            strain=3,
            stamina=4,
            stamina_max=6,
            advancement_record=already_awarded,
            trigger="endured",
        )
        self.assertFalse(result["award"]["awarded"])
        self.assertEqual(result["award"]["refusal"], "already_awarded")
        self.assertEqual(result["strain"], 2)
        self.assertEqual(result["stamina"], 5)

    # User Story 3 - state is written and committed only at a Rally

    def test_apply_rally_calls_commit_exactly_once(self):
        calls = []
        rally.apply_rally(
            strain=3,
            stamina=4,
            stamina_max=6,
            advancement_record=advancement.new_record(),
            trigger="learned",
            commit=lambda: calls.append("committed"),
        )
        self.assertEqual(calls, ["committed"])

    def test_apply_rally_calls_commit_even_with_no_award(self):
        calls = []
        rally.apply_rally(
            strain=3,
            stamina=4,
            stamina_max=6,
            advancement_record=advancement.new_record(),
            commit=lambda: calls.append("committed"),
        )
        self.assertEqual(calls, ["committed"])

    def test_apply_rally_with_no_commit_does_not_raise(self):
        rally.apply_rally(
            strain=3, stamina=4, stamina_max=6, advancement_record=advancement.new_record()
        )


if __name__ == "__main__":
    unittest.main()
