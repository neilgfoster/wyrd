"""Tests for engine/wyrd/career.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import career  # noqa: E402

CAREER = {"skills": {"stealth": 55, "swordplay": 45, "lore": 45}, "entry_point": True}


def _open(skill):
    return {"action": "open", "skill": skill}


def _raise(skill):
    return {"action": "raise", "skill": skill}


class WorkedSpreadsTest(unittest.TestCase):
    def test_open_two_everything_into_one(self):
        # open stealth, open swordplay, raise stealth x6 -> 55%/25%
        actions = [_open("stealth"), _open("swordplay")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 55)
        self.assertEqual(result["skills"]["swordplay"], 25)

    def test_open_two_split_evenly(self):
        # open both, raise each x3 -> 40%/40%
        actions = (
            [_open("stealth"), _open("swordplay")]
            + [_raise("stealth")] * 3
            + [_raise("swordplay")] * 3
        )
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 40)
        self.assertEqual(result["skills"]["swordplay"], 40)

    def test_open_three(self):
        # open 3, raise stealth x2, swordplay x2, lore x1 -> 35/35/30
        actions = (
            [_open("stealth"), _open("swordplay"), _open("lore")]
            + [_raise("stealth")] * 2
            + [_raise("swordplay")] * 2
            + [_raise("lore")] * 1
        )
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 35)
        self.assertEqual(result["skills"]["swordplay"], 35)
        self.assertEqual(result["skills"]["lore"], 30)

    def test_open_four(self):
        four_career = {"skills": {"a": 45, "b": 45, "c": 45, "d": 45}, "entry_point": True}
        actions = [_open("a"), _open("b"), _open("c"), _open("d")] + [_raise(s) for s in "abcd"]
        result = career.validate_allocation(actions, four_career)
        self.assertTrue(result["valid"], result.get("error"))
        for skill in "abcd":
            self.assertEqual(result["skills"][skill], 30)


class RejectionTest(unittest.TestCase):
    def test_wrong_total_rejected(self):
        actions = [_open("stealth"), _open("swordplay")] + [_raise("stealth")] * 5  # 7 total
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("7", result["error"])

    def test_fewer_than_two_opened_rejected(self):
        actions = [_open("stealth")] + [_raise("stealth")] * 7
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])

    def test_exceeding_cap_rejected(self):
        # swordplay cap 45; opening + 4 raises = 45 (at cap); one more raise exceeds it
        actions = [_open("stealth"), _open("swordplay")] + [_raise("swordplay")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("swordplay", result["error"])

    def test_skill_outside_union_rejected(self):
        actions = [_open("stealth"), _open("alchemy")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("alchemy", result["error"])

    def test_opening_already_open_skill_rejected(self):
        actions = [_open("stealth"), _open("stealth")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])

    def test_raising_unopened_skill_rejected(self):
        actions = [_open("stealth"), _open("swordplay")] + [_raise("lore")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("lore", result["error"])

    def test_empty_allocation_rejected(self):
        result = career.validate_allocation([], CAREER)
        self.assertFalse(result["valid"])


class AncestryTest(unittest.TestCase):
    def test_ancestry_skill_accepted_without_extra_budget(self):
        ancestry = {"skills": {"herbalism": 40}}
        actions = (
            [_open("stealth"), _open("herbalism")]
            + [_raise("stealth")] * 4
            + [_raise("herbalism")] * 2
        )
        result = career.validate_allocation(actions, CAREER, ancestry)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["herbalism"], 35)
        self.assertEqual(len(actions), 8)

    def test_higher_of_conflicting_caps_applies(self):
        ancestry = {"skills": {"swordplay": 60}}  # higher than career's 45
        # open + 8 raises would be 25+40=65 -- clamp at career+ancestry test: use 7 raises = 60
        actions = [_open("stealth"), _open("swordplay")] + [_raise("swordplay")] * 6
        result = career.validate_allocation(actions, CAREER, ancestry)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["swordplay"], 55)


if __name__ == "__main__":
    unittest.main()
