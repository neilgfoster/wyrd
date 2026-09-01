"""Tests for engine/wyrd/character.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, state  # noqa: E402

FULL_CHARACTER = {
    "id": "aria-nightingale",
    "type": "character",
    "role": "player",
    "loyalty": "the-old-guard",
    "career": "wanderer",
    "career_history": ["soldier"],
    "skills": {"stealth": 45, "swordplay": 30},
    "stamina": {"current": 8, "max": 10},
    "fate": {"current": 1, "max": 3},
    "fortune": {"current": 2},
    "resolve": {"current": 1},
    "taint": 2,
    "trauma": 0,
    "strain": 1,
    "pending_omen": None,
    "hidden_threshold": None,
    "fault_line": None,
    "transformations": [],
    "afflictions": [],
    "dread": 0,
    "reputation": {"score": 3, "label": "known"},
    "drives": ["find the truth"],
    "misfortune": None,
    "wounds": [
        {
            "id": "the-knee-that-never-set",
            "from": {"table": "aftermath", "beat": 412},
            "effect": {"skill": -10},
            "bears_on": "swordplay",
            "recurring": False,
            "closed": None,
            "description": "the knee never set right",
        }
    ],
    "holdings": [],
    "allegiances": [],
    "marks": [],
    "advances_unspent": 2,
}


class EntityRoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "aria.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_full_character_round_trips_every_field(self):
        character.save(FULL_CHARACTER, "Some prose about Aria.\n", self.path)
        loaded_frontmatter, loaded_body = character.load(self.path)
        self.assertEqual(loaded_frontmatter, FULL_CHARACTER)
        self.assertEqual(loaded_body, "Some prose about Aria.\n")

    def test_body_is_preserved_unchanged(self):
        body = "Line one.\n\n---\n\nLine after a horizontal rule.\n"
        character.save({"id": "x"}, body, self.path)
        _, loaded_body = character.load(self.path)
        self.assertEqual(loaded_body, body)


class ValidateWoundTest(unittest.TestCase):
    def test_valid_skill_effect_with_bears_on(self):
        character.validate_wound({"id": "w1", "effect": {"skill": -10}, "bears_on": "stealth"})

    def test_valid_stamina_max_effect_without_bears_on(self):
        character.validate_wound({"id": "w1", "effect": {"stamina_max": -1}})

    def test_valid_dread_effect_without_bears_on(self):
        character.validate_wound({"id": "w1", "effect": {"dread": 1}})

    def test_unrecognized_effect_key_raises(self):
        with self.assertRaises(state.StateError) as ctx:
            character.validate_wound({"id": "w1", "effect": {"damage": 5}})
        self.assertIn("w1", str(ctx.exception))

    def test_skill_effect_without_bears_on_raises(self):
        with self.assertRaises(state.StateError):
            character.validate_wound({"id": "w1", "effect": {"skill": -10}})

    def test_recurring_with_closed_raises(self):
        with self.assertRaises(state.StateError):
            character.validate_wound(
                {"id": "w1", "effect": {"dread": 1}, "recurring": True, "closed": 10}
            )

    def test_recurring_without_closed_is_valid(self):
        character.validate_wound(
            {"id": "w1", "effect": {"dread": 1}, "recurring": True, "closed": None}
        )

    def test_no_wounds_field_is_valid(self):
        character.validate_character({"id": "x"})


class CharacterLoadValidatesWoundsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "bad.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_invalid_wound_rejected_on_load(self):
        bad = {"id": "x", "wounds": [{"id": "w1", "effect": {"damage": 5}}]}
        # Bypass character.save's own validation to write a deliberately-bad file, the way a
        # hand-edited or corrupted file might arrive.
        state.save_entity(bad, "", self.path)
        with self.assertRaises(state.StateError):
            character.load(self.path)

    def test_invalid_wound_rejected_on_save(self):
        bad = {"id": "x", "wounds": [{"id": "w1", "effect": {"skill": -10}}]}
        with self.assertRaises(state.StateError):
            character.save(bad, "", self.path)
        self.assertFalse(self.path.exists())


class ActiveWoundEffectsTest(unittest.TestCase):
    def test_excludes_closed_includes_open_and_recurring(self):
        wounds = [
            {"id": "open", "effect": {"dread": 1}, "closed": None},
            {"id": "closed", "effect": {"skill": -5}, "bears_on": "stealth", "closed": 10},
            {"id": "recurring", "effect": {"stamina_max": -1}, "recurring": True, "closed": None},
        ]
        active = character.active_wound_effects(wounds)
        ids = {entry["wound_id"] for entry in active}
        self.assertEqual(ids, {"open", "recurring"})

    def test_closed_wound_remains_in_original_list(self):
        wounds = [{"id": "closed", "effect": {"dread": 1}, "closed": 10}]
        character.active_wound_effects(wounds)
        self.assertEqual(len(wounds), 1)
        self.assertEqual(wounds[0]["id"], "closed")


if __name__ == "__main__":
    unittest.main()
