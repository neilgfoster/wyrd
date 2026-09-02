"""Tests for engine/wyrd/combat.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, combat, resolution, state  # noqa: E402


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


class EscapeSceneTest(unittest.TestCase):
    """docs/design/03-rules.md section 2's pursuit ladder. party_skills {a: 50, b: 30, c: 70};
    least_capable selects b's 30. One pursuer -> Challenging -> opponent 60 -> effective_pct 20.
    Seed 1 rolls 18 (success); seed 3 rolls 31 (failure)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        combat.start_combat(
            sides={"party": {"armed": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )
        self.party_skills = {"a": 50, "b": 30, "c": 70}

    def tearDown(self):
        self._tmp.cleanup()

    def test_difficulty_ladder(self):
        self.assertIsNone(combat.escape_difficulty(0))
        self.assertEqual(combat.escape_difficulty(1), "challenging")
        self.assertEqual(combat.escape_difficulty(2), "difficult")
        self.assertEqual(combat.escape_difficulty(3), "hard")
        self.assertEqual(combat.escape_difficulty(4), "very_hard")
        self.assertEqual(combat.escape_difficulty(5), "very_hard")
        self.assertEqual(combat.escape_difficulty(100), "very_hard")

    def test_difficulty_ladder_rejects_negative(self):
        with self.assertRaises(ValueError):
            combat.escape_difficulty(-1)

    def test_successful_escape_clears_the_scene(self):
        result = combat.escape_scene(
            self.party_skills, pursuer_count=1, seed=1, state_path=self.path
        )
        self.assertTrue(result["escaped"])
        self.assertFalse(result["no_test"])
        self.assertEqual(result["difficulty"], "challenging")
        self.assertEqual(result["slowest_member"], "b")
        self.assertNotIn("combat", state.load(self.path))

    def test_failed_escape_leaves_scene_untouched(self):
        before = state.load(self.path)
        result = combat.escape_scene(
            self.party_skills, pursuer_count=1, seed=3, state_path=self.path
        )
        self.assertFalse(result["escaped"])
        self.assertEqual(result["difficulty"], "challenging")
        self.assertEqual(result["slowest_member"], "b")
        after = state.load(self.path)
        self.assertEqual(before, after)

    def test_no_pursuer_skips_the_roll_and_clears_the_scene(self):
        result = combat.escape_scene(
            self.party_skills, pursuer_count=0, seed=1, state_path=self.path
        )
        self.assertTrue(result["escaped"])
        self.assertTrue(result["no_test"])
        self.assertIsNone(result["difficulty"])
        self.assertIsNone(result["roll"])
        self.assertNotIn("combat", state.load(self.path))

    def test_difficulty_used_matches_pursuer_count(self):
        for count, difficulty in [(2, "difficult"), (3, "hard"), (4, "very_hard")]:
            with self.subTest(count=count):
                fresh = tempfile.TemporaryDirectory()
                self.addCleanup(fresh.cleanup)
                path = pathlib.Path(fresh.name) / "chronicle_state.yaml"
                combat.start_combat(
                    sides={"party": {"armed": True}},
                    started_by="party",
                    player_side="party",
                    state_path=path,
                )
                result = combat.escape_scene(
                    self.party_skills, pursuer_count=count, seed=1, state_path=path
                )
                self.assertEqual(result["difficulty"], difficulty)


class CrowdRuleTest(unittest.TestCase):
    """docs/design/03-rules.md section 2 "Crowds". crowd_member (swordplay 10, Stamina 1, no
    armour) vs character (swordplay 50): gap 40 qualifies. crowd's own attack skill 30, weapon
    1d8, armour 1d3."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"
        self.actor = pathlib.Path(self._tmp.name) / "actor.md"
        self.crowd = pathlib.Path(self._tmp.name) / "crowd.md"
        character.save({"id": "actor", "skills": {"swordplay": 50}}, "", self.actor)
        character.save(
            {
                "id": "crowd",
                "skills": {"swordplay": 30},
                "stamina": {"current": 5, "max": 5},
                "wounds": [],
            },
            "",
            self.crowd,
        )
        combat.start_combat(
            sides={"party": {"armed": True}},
            started_by="party",
            player_side="party",
            state_path=self.path,
        )
        combat.close(self.actor, self.crowd, state_path=self.path)
        combat.advance_round(state_path=self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_qualification_lookup_boundary_values(self):
        # Stamina 1 vs 2
        self.assertTrue(combat.is_crowd_member(1, False, 50, 10))
        self.assertFalse(combat.is_crowd_member(2, False, 50, 10))
        # armoured vs not
        self.assertFalse(combat.is_crowd_member(1, True, 50, 10))
        # skill gap 20 (qualifies) vs 19 (does not)
        self.assertTrue(combat.is_crowd_member(1, False, 30, 10))
        self.assertFalse(combat.is_crowd_member(1, False, 29, 10))

    def test_crowd_ease_by_body_count(self):
        self.assertEqual(combat.crowd_ease(1), 0)
        self.assertEqual(combat.crowd_ease(2), 10)
        self.assertEqual(combat.crowd_ease(3), 20)
        self.assertEqual(combat.crowd_ease(4), 20)

    def test_crowd_ease_rejects_zero_or_negative(self):
        with self.assertRaises(ValueError):
            combat.crowd_ease(0)

    def test_register_and_query_body_count(self):
        combat.register_crowd(self.crowd, 5, state_path=self.path)
        self.assertEqual(combat.crowd_body_count(self.crowd, state_path=self.path), 5)

    def test_unregistered_crowd_has_zero_bodies(self):
        self.assertEqual(combat.crowd_body_count(self.crowd, state_path=self.path), 0)

    def test_multi_round_clear_sequence(self):
        combat.register_crowd(self.crowd, 3, state_path=self.path)
        combat.clear_crowd_member(self.actor, self.crowd, state_path=self.path)
        self.assertEqual(combat.crowd_body_count(self.crowd, state_path=self.path), 2)
        self.assertFalse(combat.has_acted(self.actor, state_path=self.path))
        combat.advance_round(state_path=self.path)
        combat.clear_crowd_member(self.actor, self.crowd, state_path=self.path)
        self.assertEqual(combat.crowd_body_count(self.crowd, state_path=self.path), 1)
        combat.advance_round(state_path=self.path)
        combat.clear_crowd_member(self.actor, self.crowd, state_path=self.path)
        self.assertEqual(combat.crowd_body_count(self.crowd, state_path=self.path), 0)

    def test_clear_raises_when_not_engaged(self):
        stranger = pathlib.Path(self._tmp.name) / "stranger.md"
        character.save({"id": "stranger", "skills": {"swordplay": 50}}, "", stranger)
        combat.register_crowd(self.crowd, 3, state_path=self.path)
        with self.assertRaises(ValueError):
            combat.clear_crowd_member(stranger, self.crowd, state_path=self.path)

    def test_clear_raises_when_crowd_empty(self):
        combat.register_crowd(self.crowd, 1, state_path=self.path)
        combat.clear_crowd_member(self.actor, self.crowd, state_path=self.path)
        with self.assertRaises(ValueError):
            combat.clear_crowd_member(self.actor, self.crowd, state_path=self.path)

    def test_crowd_attack_one_body_no_ease(self):
        combat.register_crowd(self.crowd, 1, state_path=self.path)
        result = combat.crowd_attack(
            self.crowd, self.actor, "swordplay", "1d8", "1d3", seed=1, state_path=self.path
        )
        attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
        self.assertEqual(len(attack_steps), 1)
        self.assertEqual(attack_steps[0]["roll"]["effective_pct"], 50 + (30 - 50))

    def test_crowd_attack_two_bodies_ten_ease(self):
        combat.register_crowd(self.crowd, 2, state_path=self.path)
        result = combat.crowd_attack(
            self.crowd, self.actor, "swordplay", "1d8", "1d3", seed=1, state_path=self.path
        )
        attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
        self.assertEqual(len(attack_steps), 1)
        self.assertEqual(attack_steps[0]["roll"]["effective_pct"], 50 + (40 - 50))

    def test_crowd_attack_three_plus_bodies_capped_at_twenty_ease(self):
        for body_count in (3, 5):
            with self.subTest(body_count=body_count):
                combat.register_crowd(self.crowd, body_count, state_path=self.path)
                result = combat.crowd_attack(
                    self.crowd,
                    self.actor,
                    "swordplay",
                    "1d8",
                    "1d3",
                    seed=1,
                    state_path=self.path,
                )
                attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
                self.assertEqual(len(attack_steps), 1)
                self.assertEqual(attack_steps[0]["roll"]["effective_pct"], 50 + (50 - 50))

    def test_crowd_parting_blow_is_one_attack_regardless_of_body_count(self):
        combat.register_crowd(self.crowd, 5, state_path=self.path)
        result = combat.crowd_parting_blow(
            self.crowd, self.actor, "swordplay", "1d8", "1d3", seed=1, state_path=self.path
        )
        attack_steps = [s for s in result["steps"] if s["mechanic"] == "combat-attack"]
        self.assertEqual(len(attack_steps), 1)
        self.assertEqual(attack_steps[0]["roll"]["actor"], str(self.crowd))
        self.assertEqual(attack_steps[0]["roll"]["target"], str(self.actor))


if __name__ == "__main__":
    unittest.main()
