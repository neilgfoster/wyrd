"""Tests for engine/wyrd/threat.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import threat  # noqa: E402

DROWNED_COUNT = {
    "id": "the-drowned-count",
    "type": "character",
    "threat": {
        "imminence": 4,
        "effects": {"1": "grows stronger", "3-6": "spreads to an adjacent place", "7": "calamity"},
    },
}

FADED_ORG = {
    "id": "the-broken-guild",
    "type": "organisation",
    "threat": {"imminence": 0, "effects": {}},
}

ORDINARY_NPC = {"id": "ordinary-npc", "type": "character"}

QUIET_PLACE = {
    "id": "quiet-hollow",
    "type": "place",
    "threat": {"imminence": 2, "effects": {"1-2": "an occasional body"}},
}


class ActiveThreatsTests(unittest.TestCase):
    def test_mixed_entity_types_all_returned(self) -> None:
        active = threat.active_threats([DROWNED_COUNT, QUIET_PLACE])
        self.assertEqual([e["id"] for e in active], ["the-drowned-count", "quiet-hollow"])

    def test_zero_imminence_excluded(self) -> None:
        active = threat.active_threats([DROWNED_COUNT, FADED_ORG])
        self.assertEqual([e["id"] for e in active], ["the-drowned-count"])

    def test_no_threat_block_excluded(self) -> None:
        active = threat.active_threats([DROWNED_COUNT, ORDINARY_NPC])
        self.assertEqual([e["id"] for e in active], ["the-drowned-count"])

    def test_empty_input(self) -> None:
        self.assertEqual(threat.active_threats([]), [])


class CheckActivationTests(unittest.TestCase):
    def test_activates_at_boundary(self) -> None:
        self.assertTrue(threat.check_activation(imminence=4, wyrd_roll=40))

    def test_does_not_activate_past_boundary(self) -> None:
        self.assertFalse(threat.check_activation(imminence=4, wyrd_roll=41))

    def test_zero_imminence_never_activates(self) -> None:
        self.assertFalse(threat.check_activation(imminence=0, wyrd_roll=1))


class ResolveEffectsTests(unittest.TestCase):
    def test_single_value_key_match(self) -> None:
        result = threat.resolve_effects({"1": "grows stronger"}, table_roll=1)
        self.assertEqual(result, {"matched": "grows stronger"})

    def test_range_key_match(self) -> None:
        result = threat.resolve_effects({"3-6": "spreads"}, table_roll=5)
        self.assertEqual(result, {"matched": "spreads"})

    def test_unmatched_roll_is_no_op(self) -> None:
        result = threat.resolve_effects({"1-2": "a rumour"}, table_roll=9)
        self.assertEqual(result, {"matched": None})

    def test_empty_table_is_no_op(self) -> None:
        result = threat.resolve_effects({}, table_roll=1)
        self.assertEqual(result, {"matched": None})


class PromoteTests(unittest.TestCase):
    def test_attaches_block_and_preserves_other_fields(self) -> None:
        companion = {"id": "left-for-dead", "type": "character", "role": "companion"}
        new_threat = {"imminence": 3, "effects": {}}
        promoted = threat.promote(companion, new_threat, objective="hunts the player")

        self.assertEqual(promoted["threat"], new_threat)
        self.assertEqual(promoted["objective"], "hunts the player")
        self.assertEqual(promoted["role"], "companion")
        self.assertEqual(promoted["id"], "left-for-dead")
        # original untouched
        self.assertNotIn("threat", companion)

    def test_rejects_already_promoted_entity(self) -> None:
        with self.assertRaises(ValueError):
            threat.promote(DROWNED_COUNT, {"imminence": 1}, objective="anything")

    def test_rejects_zero_imminence(self) -> None:
        with self.assertRaises(ValueError):
            threat.promote(ORDINARY_NPC, {"imminence": 0}, objective="anything")


class FadeTests(unittest.TestCase):
    def test_faded_threat_excluded_but_block_retained(self) -> None:
        entity = {"id": "spent-conspiracy", "type": "organisation", "threat": {"imminence": 3}}
        entity["threat"]["imminence"] = 0

        self.assertEqual(threat.active_threats([entity]), [])
        self.assertIn("threat", entity)


class ValidateConnectionsTests(unittest.TestCase):
    def _threat(self, connection) -> dict:
        return {"id": "some-threat", "threat": {"connection": connection}}

    def test_non_empty_connection_passes(self) -> None:
        self.assertEqual(threat.validate_connections([self._threat("he drowned your brother")]), [])

    def test_absent_connection_reported(self) -> None:
        entity = {"id": "no-connection-field", "threat": {}}
        problems = threat.validate_connections([entity])
        self.assertEqual(len(problems), 1)
        self.assertIn("no-connection-field", problems[0])

    def test_none_connection_reported(self) -> None:
        problems = threat.validate_connections([self._threat(None)])
        self.assertEqual(len(problems), 1)

    def test_empty_string_connection_reported(self) -> None:
        problems = threat.validate_connections([self._threat("")])
        self.assertEqual(len(problems), 1)

    def test_whitespace_only_connection_reported(self) -> None:
        problems = threat.validate_connections([self._threat("   ")])
        self.assertEqual(len(problems), 1)

    def test_mixed_list_order_preserved(self) -> None:
        good = {"id": "good-threat", "threat": {"connection": "a real reason"}}
        bad_first = {"id": "bad-first", "threat": {"connection": ""}}
        bad_second = {"id": "bad-second", "threat": {"connection": None}}
        problems = threat.validate_connections([bad_first, good, bad_second])
        self.assertEqual(len(problems), 2)
        self.assertIn("bad-first", problems[0])
        self.assertIn("bad-second", problems[1])

    def test_empty_input_list(self) -> None:
        self.assertEqual(threat.validate_connections([]), [])

    def test_threat_missing_its_own_id(self) -> None:
        entity = {"threat": {"connection": ""}}
        problems = threat.validate_connections([entity])
        self.assertEqual(len(problems), 1)

    def test_threat_block_none_reported_not_raised(self) -> None:
        entity = {"id": "no-threat-block", "threat": None}
        problems = threat.validate_connections([entity])
        self.assertEqual(len(problems), 1)
        self.assertIn("no-threat-block", problems[0])

    def test_entity_with_no_threat_key_at_all_reported_not_raised(self) -> None:
        entity = {"id": "not-even-a-threat"}
        problems = threat.validate_connections([entity])
        self.assertEqual(len(problems), 1)
        self.assertIn("not-even-a-threat", problems[0])

    def test_never_raises(self) -> None:
        # exercised across every case above -- none construct a try/except, all call directly
        threat.validate_connections([{}, {"threat": {}}, {"threat": {"connection": None}}])


if __name__ == "__main__":
    unittest.main()
