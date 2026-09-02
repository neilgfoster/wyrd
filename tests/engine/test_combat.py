"""Tests for engine/wyrd/combat.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, combat, resolution  # noqa: E402


class DetermineFirstActorTest(unittest.TestCase):
    """research.md's four combinations."""

    def test_explicit_starter_wins_outright(self):
        self.assertEqual(
            combat.determine_first_actor(
                "party", {"party": False, "opp": True}, player_side="party"
            ),
            "party",
        )

    def test_mutual_encounter_sole_armed_side(self):
        self.assertEqual(
            combat.determine_first_actor(None, {"party": True, "opp": False}, player_side="party"),
            "party",
        )
        self.assertEqual(
            combat.determine_first_actor(None, {"party": False, "opp": True}, player_side="party"),
            "opp",
        )

    def test_mutual_encounter_both_armed_defaults_to_player_side(self):
        self.assertEqual(
            combat.determine_first_actor(None, {"party": True, "opp": True}, player_side="party"),
            "party",
        )

    def test_mutual_encounter_neither_armed_defaults_to_player_side(self):
        self.assertEqual(
            combat.determine_first_actor(None, {"party": False, "opp": False}, player_side="party"),
            "party",
        )


class StartCombatTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def test_start_combat_computes_first_actor_and_persists_round_1(self):
        scene = combat.start_combat(
            sides={"party": {"armed": True}, "opp": {"armed": False}},
            started_by=None,
            player_side="party",
            state_path=self.path,
        )
        self.assertEqual(scene["first_actor"], "party")
        self.assertEqual(scene["round"], 1)

        # Persisted -- readable back without re-calling start_combat.
        self.assertTrue(combat.can_act("party", state_path=self.path))

    def test_unknown_started_by_raises(self):
        with self.assertRaises(ValueError):
            combat.start_combat(
                sides={"party": {"armed": True}},
                started_by="nobody",
                player_side="party",
                state_path=self.path,
            )

    def test_unknown_player_side_raises(self):
        with self.assertRaises(ValueError):
            combat.start_combat(
                sides={"party": {"armed": True}},
                started_by=None,
                player_side="nobody",
                state_path=self.path,
            )

    def test_flags_default_false_when_omitted(self):
        scene = combat.start_combat(
            sides={"party": {"armed": True}, "opp": {}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )
        self.assertEqual(
            scene["sides"]["opp"],
            {"armed": False, "surprised": False, "ambush": False},
        )


class SurpriseTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        combat.start_combat(
            sides={"party": {"armed": True}, "opp": {"armed": False, "surprised": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_surprised_side_cannot_act_in_round_1(self):
        self.assertFalse(combat.can_act("opp", state_path=self.path))

    def test_non_surprised_side_can_always_act(self):
        self.assertTrue(combat.can_act("party", state_path=self.path))

    def test_surprised_side_can_act_after_round_advances(self):
        combat.advance_round(state_path=self.path)
        self.assertTrue(combat.can_act("opp", state_path=self.path))

    def test_unknown_side_raises(self):
        with self.assertRaises(ValueError):
            combat.can_act("nobody", state_path=self.path)

    def test_no_scene_in_progress_raises(self):
        fresh_path = pathlib.Path(self._tmp.name) / "no-scene.yaml"
        with self.assertRaises(ValueError):
            combat.can_act("party", state_path=fresh_path)


class AmbushTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        combat.start_combat(
            sides={"party": {"armed": True, "ambush": True}, "opp": {"armed": False}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_ambushing_side_gets_plus_20_in_round_1(self):
        self.assertEqual(combat.attack_modifier("party", state_path=self.path), 20)

    def test_non_ambushing_side_gets_no_modifier(self):
        self.assertEqual(combat.attack_modifier("opp", state_path=self.path), 0)

    def test_modifier_drops_to_zero_after_round_1(self):
        combat.advance_round(state_path=self.path)
        self.assertEqual(combat.attack_modifier("party", state_path=self.path), 0)


class SurpriseDoesNotAffectResolutionTest(unittest.TestCase):
    """User Story 3 Scenario 2: a combat-attack against a surprised side's member resolves
    exactly as an unmodified attack would -- this feature adds no defensive penalty."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.attacker = pathlib.Path(self._tmp.name) / "attacker.md"
        self.target = pathlib.Path(self._tmp.name) / "target.md"
        character.save({"id": "attacker", "skills": {"swordplay": 60}}, "", self.attacker)
        character.save(
            {
                "id": "target",
                "skills": {"swordplay": 30},
                "stamina": {"current": 8, "max": 8},
                "wounds": [],
            },
            "",
            self.target,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_attack_against_a_surprised_targets_member_resolves_normally(self):
        with_scene = resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
        )
        without_scene = resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
        )
        self.assertEqual(with_scene["roll"], without_scene["roll"])


if __name__ == "__main__":
    unittest.main()
