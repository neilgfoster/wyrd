"""Tests for engine/wyrd/holding.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import holding  # noqa: E402


class FlagPersonalStakesTests(unittest.TestCase):
    def test_held_entity_flagged_true(self) -> None:
        threats = [{"id": "the-drowned-mill", "threat": {"imminence": 4}}]
        result = holding.flag_personal_stakes(threats, ["the-drowned-mill"])
        self.assertTrue(result[0]["personal"])

    def test_unheld_entity_flagged_false(self) -> None:
        threats = [{"id": "quiet-hollow", "threat": {"imminence": 2}}]
        result = holding.flag_personal_stakes(threats, ["the-drowned-mill"])
        self.assertFalse(result[0]["personal"])

    def test_empty_threats_list(self) -> None:
        self.assertEqual(holding.flag_personal_stakes([], ["the-drowned-mill"]), [])

    def test_empty_holdings_list(self) -> None:
        threats = [{"id": "the-drowned-mill", "threat": {"imminence": 4}}]
        result = holding.flag_personal_stakes(threats, [])
        self.assertFalse(result[0]["personal"])

    def test_entity_with_no_id_flagged_false(self) -> None:
        threats = [{"threat": {"imminence": 4}}]
        result = holding.flag_personal_stakes(threats, ["the-drowned-mill"])
        self.assertFalse(result[0]["personal"])

    def test_order_and_length_preserved_and_other_fields_unchanged(self) -> None:
        threats = [
            {"id": "the-drowned-mill", "type": "place", "threat": {"imminence": 4}},
            {"id": "quiet-hollow", "type": "place", "threat": {"imminence": 2}},
        ]
        result = holding.flag_personal_stakes(threats, ["the-drowned-mill"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "the-drowned-mill")
        self.assertEqual(result[1]["id"], "quiet-hollow")
        self.assertEqual(result[0]["type"], "place")
        self.assertTrue(result[0]["personal"])
        self.assertFalse(result[1]["personal"])


if __name__ == "__main__":
    unittest.main()
