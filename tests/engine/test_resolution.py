"""Tests for engine/wyrd/resolution.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, resolution  # noqa: E402

SENNA = {
    "id": "senna-vask",
    "type": "character",
    "role": "player",
    "loyalty": "the-old-guard",
    "career": "wanderer",
    "career_history": [],
    "skills": {"bargaining": 40},
    "stamina": {"current": 8, "max": 10},
    "fate": {"current": 1, "max": 3},
    "fortune": {"current": 2},
    "resolve": {"current": 1},
    "taint": 0,
    "trauma": 0,
    "strain": 0,
    "pending_omen": None,
    "hidden_threshold": None,
    "fault_line": "",
    "transformations": [],
    "afflictions": [],
    "dread": 0,
    "reputation": 0,
    "drives": [],
    "misfortune": None,
    "wounds": [],
    "holdings": [],
    "allegiances": [],
    "marks": [],
    "advances_unspent": 0,
}


class ResolutionTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "senna-vask.md"
        character.save(dict(SENNA), "", self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def load(self):
        frontmatter, _ = character.load(self.path)
        return frontmatter


class WorkedExampleTest(ResolutionTestBase):
    """docs/design/31-action-resolution.md "A worked example": Senna Vask, bargaining: 40,
    moderate (2) Exposure, seed 20260852 -- roll 77, fails against eff. 40, taint +2."""

    def test_propose_reproduces_the_worked_example(self):
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        self.assertEqual(result["roll"]["roll"], 77)
        self.assertEqual(result["roll"]["effective_pct"], 40)
        self.assertEqual(result["roll"]["outcome"], "fail")
        self.assertEqual(
            result["mutations"],
            [
                {
                    "entity": str(self.path),
                    "field": "taint",
                    "op": "+",
                    "value": 2,
                    "produced_by_step": 0,
                }
            ],
        )

    def test_propose_writes_nothing(self):
        before = self.load()
        resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        self.assertEqual(self.load(), before)

    def test_commit_applies_exactly_the_staged_mutation(self):
        before = self.load()
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertEqual(after["taint"], before["taint"] + 2)
        after.pop("taint")
        before.pop("taint")
        self.assertEqual(after, before)


class NoMutationOutcomeTest(ResolutionTestBase):
    def test_ordinary_test_returns_empty_mutations_on_either_outcome(self):
        # eff% = 40 (skill) + 0 (average) = 40; a high roll fails, a low roll succeeds -- both
        # imply nothing for an ordinary-test.
        for seed in (20260852, 1):
            with self.subTest(seed=seed):
                result = resolution.propose(
                    actor=self.path,
                    mechanic="ordinary-test",
                    skill="bargaining",
                    seed=seed,
                )
                self.assertEqual(result["mutations"], [])

    def test_propose_writes_nothing_for_a_no_mutation_outcome(self):
        before = self.load()
        resolution.propose(actor=self.path, mechanic="ordinary-test", skill="bargaining", seed=1)
        self.assertEqual(self.load(), before)


class CommitDiscardTest(ResolutionTestBase):
    def test_discard_leaves_state_exactly_as_before_propose(self):
        before = self.load()
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        resolution.discard(result["proposal_id"])
        self.assertEqual(self.load(), before)

    def test_commit_then_commit_raises(self):
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        resolution.commit(result["proposal_id"])
        with self.assertRaises(resolution.ProposalError):
            resolution.commit(result["proposal_id"])

    def test_commit_then_discard_raises(self):
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        resolution.commit(result["proposal_id"])
        with self.assertRaises(resolution.ProposalError):
            resolution.discard(result["proposal_id"])

    def test_discard_then_commit_raises(self):
        result = resolution.propose(
            actor=self.path,
            mechanic="exposure",
            skill="bargaining",
            tier="moderate",
            seed=20260852,
        )
        resolution.discard(result["proposal_id"])
        with self.assertRaises(resolution.ProposalError):
            resolution.commit(result["proposal_id"])

    def test_fabricated_id_raises_on_commit_and_discard(self):
        with self.assertRaises(resolution.ProposalError):
            resolution.commit("p-does-not-exist")
        with self.assertRaises(resolution.ProposalError):
            resolution.discard("p-does-not-exist")


class ErrorCaseTest(ResolutionTestBase):
    def test_unknown_mechanic_raises_value_error(self):
        with self.assertRaises(ValueError):
            resolution.propose(actor=self.path, mechanic="no-such-mechanic", skill="bargaining")

    def test_nonexistent_target_raises(self):
        missing = pathlib.Path(self._tmp.name) / "nobody.md"
        with self.assertRaises(Exception):
            resolution.propose(
                actor=self.path,
                mechanic="ordinary-test",
                skill="bargaining",
                target=missing,
            )

    def test_unknown_difficulty_raises_value_error(self):
        with self.assertRaises(ValueError):
            resolution.propose(
                actor=self.path,
                mechanic="ordinary-test",
                skill="bargaining",
                difficulty="impossible",
            )

    def test_unknown_exposure_tier_raises_value_error(self):
        with self.assertRaises(ValueError):
            resolution.propose(
                actor=self.path,
                mechanic="exposure",
                skill="bargaining",
                tier="catastrophic",
            )


class TransformationCascadeTest(ResolutionTestBase):
    """research.md: Taint 1, major (3) Exposure, eff. 35, seed 5 -- roll 80 fails, Taint 1 -> 4
    crosses the threshold at 3, one Transformation clears it."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 35
        frontmatter["taint"] = 1
        character.save(frontmatter, "", self.path)

    def test_taint_crossing_stages_a_transformation_step(self):
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        self.assertEqual(
            [step["mechanic"] for step in result["steps"]], ["exposure", "transformation"]
        )
        transformation = result["steps"][1]
        self.assertEqual(transformation["depends_on"], [0])
        self.assertEqual(transformation["roll"], {"roll": 5, "row": 5, "severity": 3})

    def test_mutations_reduce_taint_raise_dread_and_set_hidden_threshold_once(self):
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        self.assertEqual(
            result["mutations"],
            [
                {
                    "entity": str(self.path),
                    "field": "taint",
                    "op": "+",
                    "value": 3,
                    "produced_by_step": 0,
                },
                {
                    "entity": str(self.path),
                    "field": "taint",
                    "op": "-",
                    "value": 3,
                    "produced_by_step": 1,
                },
                {
                    "entity": str(self.path),
                    "field": "dread",
                    "op": "+",
                    "value": 3,
                    "produced_by_step": 1,
                },
                {
                    "entity": str(self.path),
                    "field": "hidden_threshold",
                    "op": "set",
                    "value": 5,
                    "produced_by_step": 1,
                },
            ],
        )

    def test_commit_applies_the_whole_cascade_atomically(self):
        before = self.load()
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertEqual(after["taint"], before["taint"])  # +3 then -3
        self.assertEqual(after["dread"], before["dread"] + 3)
        self.assertEqual(after["hidden_threshold"], 5)

    def test_second_transformation_does_not_re_set_hidden_threshold(self):
        frontmatter = self.load()
        frontmatter["hidden_threshold"] = 4
        character.save(frontmatter, "", self.path)
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        transformation_mutations = result["steps"][1]["mutations"]
        fields = [mutation["field"] for mutation in transformation_mutations]
        self.assertNotIn("hidden_threshold", fields)

    def test_no_crossing_stages_no_transformation_step(self):
        frontmatter = self.load()
        frontmatter["taint"] = 0
        character.save(frontmatter, "", self.path)
        # minor tier (+1) from 0 never reaches the threshold at 3
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="minor", seed=5
        )
        self.assertEqual([step["mechanic"] for step in result["steps"]], ["exposure"])


class MultiRerollTransformationTest(ResolutionTestBase):
    """research.md: same setup, seed 7 -- two Transformation re-rolls needed to clear Taint."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 35
        frontmatter["taint"] = 1
        character.save(frontmatter, "", self.path)

    def test_two_distinct_rows_clear_the_threshold_in_one_call(self):
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=7
        )
        transformation_steps = [
            step for step in result["steps"] if step["mechanic"] == "transformation"
        ]
        self.assertEqual(len(transformation_steps), 2)
        rows = [step["roll"]["row"] for step in transformation_steps]
        self.assertEqual(len(set(rows)), 2)  # distinct rows -- unique per character
        self.assertEqual(
            transformation_steps[1]["depends_on"], [transformation_steps[0]["step_id"]]
        )

        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertLess(after["taint"], resolution.TAINT_THRESHOLD_SPACING)


class CombatChainTest(unittest.TestCase):
    """research.md: attacker swordplay 60 vs target swordplay 0, Stamina 5, weapon 1d8, armour
    1d3, seed 2 -- a telling blow, doubled damage, armour reduction, Stamina crossing below 0,
    and a critical-slashing 6-9 result."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.attacker = pathlib.Path(self._tmp.name) / "attacker.md"
        self.target = pathlib.Path(self._tmp.name) / "target.md"
        attacker = dict(SENNA)
        attacker["id"] = "attacker"
        attacker["skills"] = {"swordplay": 60}
        character.save(attacker, "", self.attacker)
        target = dict(SENNA)
        target["id"] = "target"
        target["skills"] = {"swordplay": 0}
        target["stamina"] = {"current": 5, "max": 5}
        character.save(target, "", self.target)

    def tearDown(self):
        self._tmp.cleanup()

    def propose_attack(self):
        return resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
        )

    def test_full_chain_resolves_in_one_call(self):
        result = self.propose_attack()
        mechanics = [step["mechanic"] for step in result["steps"]]
        self.assertEqual(mechanics, ["combat-attack", "weapon-damage", "armour", "critical"])
        self.assertTrue(result["steps"][0]["roll"]["telling"])
        self.assertEqual(result["steps"][1]["roll"]["total"], 8)  # 4 doubled
        self.assertEqual(result["steps"][2]["roll"]["total"], 1)
        self.assertEqual(result["steps"][2]["roll"]["net_damage"], 7)
        self.assertEqual(result["steps"][3]["roll"]["key"], "slashing-scored")
        self.assertFalse(result["steps"][3]["roll"]["mortal"])

    def test_depends_on_edges(self):
        result = self.propose_attack()
        self.assertEqual(result["steps"][1]["depends_on"], [0])
        self.assertEqual(result["steps"][2]["depends_on"], [0])
        self.assertEqual(result["steps"][3]["depends_on"], [2])

    def test_commit_applies_stamina_and_wound_to_the_target_not_the_actor(self):
        result = self.propose_attack()
        resolution.commit(result["proposal_id"])
        attacker_frontmatter, _ = character.load(self.attacker)
        target_frontmatter, _ = character.load(self.target)
        self.assertEqual(attacker_frontmatter["stamina"]["current"], 8)  # untouched
        self.assertEqual(target_frontmatter["stamina"]["current"], -2)
        self.assertEqual(len(target_frontmatter["wounds"]), 1)
        self.assertEqual(target_frontmatter["wounds"][0]["effect"], {"dread": 1})

    def test_attack_that_does_not_land_stages_nothing_further(self):
        # A low attacker skill against a high defender skill practically guarantees a miss.
        frontmatter, _ = character.load(self.attacker)
        frontmatter["skills"]["swordplay"] = 5
        character.save(frontmatter, "", self.attacker)
        defender_frontmatter, _ = character.load(self.target)
        defender_frontmatter["skills"]["swordplay"] = 95
        character.save(defender_frontmatter, "", self.target)
        result = resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=999,
        )
        landed = result["steps"][0]["roll"]["landed"]
        if landed:
            self.skipTest("seed happened to land despite the skill gap; not this test's concern")
        self.assertEqual(len(result["steps"]), 1)
        self.assertEqual(result["mutations"], [])

    def test_missing_weapon_or_armour_dice_raises(self):
        with self.assertRaises(ValueError):
            resolution.propose(
                actor=self.attacker,
                mechanic="combat-attack",
                skill="swordplay",
                target=self.target,
                seed=2,
            )


class MortalCriticalTest(unittest.TestCase):
    """A critical rolling into the 21+ band stages no further step (FR-009, User Story 3)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.attacker = pathlib.Path(self._tmp.name) / "attacker.md"
        self.target = pathlib.Path(self._tmp.name) / "target.md"
        attacker = dict(SENNA)
        attacker["id"] = "attacker"
        attacker["skills"] = {"swordplay": 90}
        character.save(attacker, "", self.attacker)
        target = dict(SENNA)
        target["id"] = "target"
        target["skills"] = {"swordplay": 0}
        target["stamina"] = {"current": 1, "max": 1}
        character.save(target, "", self.target)

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_mortal_result_stages_no_wound_and_nothing_further(self):
        # Search a small seed range for a scenario landing a telling blow with enough net
        # damage, and a critical d6 draw that reads mortal (21+ with a large points-below-zero
        # modifier) -- computed, not asserted (CLAUDE.md "check the maths").
        found = None
        for seed in range(1, 200):
            result = resolution.propose(
                actor=self.attacker,
                mechanic="combat-attack",
                skill="swordplay",
                target=self.target,
                weapon_dice="6d8",
                armour_dice="1d2",
                seed=seed,
            )
            critical_steps = [step for step in result["steps"] if step["mechanic"] == "critical"]
            if critical_steps and critical_steps[0]["roll"]["mortal"]:
                found = result
                break
        self.assertIsNotNone(found, "no mortal scenario found in the scanned seed range")
        critical_step = [s for s in found["steps"] if s["mechanic"] == "critical"][0]
        self.assertEqual(critical_step["mutations"], [])
        self.assertEqual(found["steps"][-1]["mechanic"], "critical")


if __name__ == "__main__":
    unittest.main()
