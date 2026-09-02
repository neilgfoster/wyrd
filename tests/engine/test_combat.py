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


class EngagementTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        self.a = pathlib.Path(self._tmp.name) / "a.md"
        self.b = pathlib.Path(self._tmp.name) / "b.md"
        self.c = pathlib.Path(self._tmp.name) / "c.md"
        character.save({"id": "a", "skills": {"swordplay": 50}}, "", self.a)
        character.save(
            {
                "id": "b",
                "skills": {"swordplay": 50},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.b,
        )
        character.save(
            {
                "id": "c",
                "skills": {"swordplay": 50},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.c,
        )
        combat.start_combat(
            sides={"party": {"armed": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_close_creates_engagement_and_marks_acted(self):
        combat.close(self.a, self.b, state_path=self.path)
        self.assertEqual(combat.engaged_with(self.a, state_path=self.path), [str(self.b)])
        self.assertEqual(combat.engaged_with(self.b, state_path=self.path), [str(self.a)])
        self.assertTrue(combat.has_acted(self.a, state_path=self.path))

    def test_close_again_the_same_round_raises(self):
        combat.close(self.a, self.b, state_path=self.path)
        with self.assertRaises(ValueError):
            combat.close(self.a, self.c, state_path=self.path)

    def test_close_after_advance_round_succeeds(self):
        combat.close(self.a, self.b, state_path=self.path)
        combat.advance_round(state_path=self.path)
        combat.close(self.a, self.c, state_path=self.path)  # does not raise
        self.assertCountEqual(
            combat.engaged_with(self.a, state_path=self.path), [str(self.b), str(self.c)]
        )

    def test_break_off_one_opponent_stages_one_parting_blow(self):
        combat.close(self.a, self.b, state_path=self.path)
        result = combat.break_off(
            self.a,
            {str(self.b): {"skill": "swordplay", "weapon_dice": "1d8", "armour_dice": "1d3"}},
            seed=2,
            state_path=self.path,
        )
        attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
        self.assertEqual(len(attack_steps), 1)
        self.assertEqual(attack_steps[0]["roll"]["actor"], str(self.b))
        self.assertEqual(attack_steps[0]["roll"]["target"], str(self.a))
        self.assertEqual(combat.engaged_with(self.a, state_path=self.path), [])

    def test_break_off_two_opponents_stages_two_parting_blows(self):
        combat.close(self.a, self.b, state_path=self.path)
        combat.advance_round(state_path=self.path)
        combat.close(self.a, self.c, state_path=self.path)
        result = combat.break_off(
            self.a,
            {
                str(self.b): {"skill": "swordplay", "weapon_dice": "1d8", "armour_dice": "1d3"},
                str(self.c): {"skill": "swordplay", "weapon_dice": "1d8", "armour_dice": "1d3"},
            },
            seed=2,
            state_path=self.path,
        )
        attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
        self.assertEqual(len(attack_steps), 2)
        self.assertCountEqual(
            [s["roll"]["actor"] for s in attack_steps], [str(self.b), str(self.c)]
        )
        self.assertTrue(all(s["roll"]["target"] == str(self.a) for s in attack_steps))
        self.assertEqual(combat.engaged_with(self.a, state_path=self.path), [])

    def test_break_off_with_no_engagements_stages_nothing(self):
        result = combat.break_off(self.a, {}, state_path=self.path)
        self.assertEqual(result["steps"], [])
        self.assertEqual(result["mutations"], [])

    def test_break_off_mismatched_opponents_raises(self):
        combat.close(self.a, self.b, state_path=self.path)
        with self.assertRaises(ValueError):
            combat.break_off(
                self.a,
                {str(self.c): {"skill": "swordplay", "weapon_dice": "1d8", "armour_dice": "1d3"}},
                state_path=self.path,
            )


class RangedAttackDifficultyTest(unittest.TestCase):
    """research.md: shooter archery 50, target archery 10, weapon 1d8, armour 1d3, seed 2 --
    engaged shooter is Difficult (-20)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        self.shooter = pathlib.Path(self._tmp.name) / "shooter.md"
        self.target = pathlib.Path(self._tmp.name) / "target.md"
        self.ally = pathlib.Path(self._tmp.name) / "ally.md"
        character.save({"id": "shooter", "skills": {"archery": 50}}, "", self.shooter)
        character.save(
            {
                "id": "target",
                "skills": {"archery": 10},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.target,
        )
        character.save(
            {
                "id": "ally",
                "skills": {"archery": 10},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.ally,
        )
        combat.start_combat(
            sides={"party": {"armed": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_unengaged_shot_is_average(self):
        self.assertEqual(
            combat.ranged_attack_difficulty(self.shooter, self.target, state_path=self.path),
            "average",
        )

    def test_engaged_shooter_is_difficult(self):
        combat.close(self.shooter, self.ally, state_path=self.path)
        self.assertEqual(
            combat.ranged_attack_difficulty(self.shooter, self.target, state_path=self.path),
            "difficult",
        )

    def test_target_engaged_with_someone_else_is_challenging(self):
        combat.close(self.target, self.ally, state_path=self.path)
        self.assertEqual(
            combat.ranged_attack_difficulty(self.shooter, self.target, state_path=self.path),
            "challenging",
        )

    def test_shooter_own_engagement_takes_precedence(self):
        combat.close(self.shooter, self.ally, state_path=self.path)
        combat.advance_round(state_path=self.path)
        combat.close(self.target, self.ally, state_path=self.path)
        self.assertEqual(
            combat.ranged_attack_difficulty(self.shooter, self.target, state_path=self.path),
            "difficult",
        )

    def test_engaged_shooter_applies_the_difficult_modifier(self):
        baseline = resolution.propose(
            actor=self.shooter,
            mechanic="combat-attack",
            skill="archery",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
        )
        combat.close(self.shooter, self.ally, state_path=self.path)
        engaged = combat.resolve_ranged_attack(
            self.shooter,
            self.target,
            "archery",
            "1d8",
            "1d3",
            seed=2,
            state_path=self.path,
        )
        self.assertEqual(engaged["roll"]["effective_pct"], baseline["roll"]["effective_pct"] - 20)


class RangedAttackAllyRedirectTest(unittest.TestCase):
    """research.md: target engaged with a separate ally -- seed 5 redirects on Ill Omen, seed 1
    does not."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        self.shooter = pathlib.Path(self._tmp.name) / "shooter.md"
        self.target = pathlib.Path(self._tmp.name) / "target.md"
        self.ally = pathlib.Path(self._tmp.name) / "ally.md"
        character.save({"id": "shooter", "skills": {"archery": 50}}, "", self.shooter)
        character.save(
            {
                "id": "target",
                "skills": {"archery": 10},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.target,
        )
        character.save(
            {
                "id": "ally",
                "skills": {"archery": 10},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.ally,
        )
        combat.start_combat(
            sides={"party": {"armed": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )
        combat.close(self.target, self.ally, state_path=self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_ill_omen_redirects_to_the_ally(self):
        result = combat.resolve_ranged_attack(
            self.shooter,
            self.target,
            "archery",
            "1d8",
            "1d3",
            seed=5,
            state_path=self.path,
        )
        self.assertEqual(result["roll"]["target"], str(self.ally))

    def test_no_omen_keeps_the_original_target(self):
        result = combat.resolve_ranged_attack(
            self.shooter,
            self.target,
            "archery",
            "1d8",
            "1d3",
            seed=1,
            state_path=self.path,
        )
        self.assertEqual(result["roll"]["target"], str(self.target))


if __name__ == "__main__":
    unittest.main()
