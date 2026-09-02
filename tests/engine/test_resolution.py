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


class IndependentBranchTest(ResolutionTestBase):
    """research.md: Taint 0, bargaining 35 / stealth 45, two minor Exposure sources batched,
    seed 20260854 -- reproduces docs/design/31-action-resolution.md's own worked example."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"] = {"bargaining": 35, "stealth": 45}
        frontmatter["taint"] = 0
        frontmatter["resolve"] = {"current": 2}
        frontmatter["fortune"] = {"current": 2}
        character.save(frontmatter, "", self.path)

    def propose_batch(self):
        return resolution.propose_batch(
            [
                {
                    "actor": self.path,
                    "mechanic": "exposure",
                    "skill": "bargaining",
                    "tier": "minor",
                },
                {"actor": self.path, "mechanic": "exposure", "skill": "stealth", "tier": "minor"},
            ],
            seed=20260854,
        )

    def test_batch_reproduces_the_two_rolls(self):
        result = self.propose_batch()
        self.assertEqual(result["steps"][0]["roll"]["roll"], 91)
        self.assertEqual(result["steps"][0]["roll"]["outcome"], "fail")
        self.assertEqual(result["steps"][1]["roll"]["roll"], 38)
        self.assertEqual(result["steps"][1]["roll"]["outcome"], "success")

    def test_reroll_leaves_the_independent_step_untouched(self):
        result = self.propose_batch()
        original_step_1 = result["steps"][1]
        revised = resolution.reroll(result["proposal_id"], step=0, resource="bargain", seed=5)
        step_1 = next(s for s in revised["steps"] if s["step_id"] == 1)
        self.assertEqual(step_1["roll"], original_step_1["roll"])
        self.assertEqual(step_1["mutations"], original_step_1["mutations"])

    def test_reroll_combines_the_fresh_roll_with_the_bargain_cost(self):
        result = self.propose_batch()
        revised = resolution.reroll(result["proposal_id"], step=0, resource="bargain", seed=5)
        step_0 = next(s for s in revised["steps"] if s["step_id"] == 0)
        self.assertEqual(step_0["roll"]["roll"], 80)
        self.assertEqual(step_0["roll"]["outcome"], "fail")
        self.assertEqual(
            step_0["mutations"],
            [
                {
                    "entity": str(self.path),
                    "field": "taint",
                    "op": "+",
                    "value": 1,
                    "produced_by_step": 0,
                },
                {
                    "entity": str(self.path),
                    "field": "taint",
                    "op": "+",
                    "value": 1,
                    "produced_by_step": 0,
                },
            ],
        )

    def test_commit_after_reroll_applies_the_revised_mutations(self):
        before = self.load()
        result = resolution.propose_batch(
            [
                {
                    "actor": self.path,
                    "mechanic": "exposure",
                    "skill": "bargaining",
                    "tier": "minor",
                },
                {"actor": self.path, "mechanic": "exposure", "skill": "stealth", "tier": "minor"},
            ],
            seed=20260854,
        )
        resolution.reroll(result["proposal_id"], step=0, resource="bargain", seed=5)
        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertEqual(after["taint"], before["taint"] + 2)

    def test_reroll_does_not_invalidate_the_proposal_id(self):
        result = self.propose_batch()
        pid = result["proposal_id"]
        resolution.reroll(pid, step=0, resource="bargain", seed=5)
        # A second reroll, against the other step, must still succeed -- the id is still open.
        resolution.reroll(pid, step=1, resource="fortune", seed=2)
        commit_result = resolution.commit(pid)
        self.assertTrue(commit_result["mutations"])  # did not raise ProposalError


class RerollCascadeTest(ResolutionTestBase):
    """research.md: Taint 1, major Exposure, seed 5 -- a reroll discards the stale Transformation
    and stages a fresh one."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 35
        frontmatter["taint"] = 1
        frontmatter["fortune"] = {"current": 2}
        character.save(frontmatter, "", self.path)

    def test_reroll_replaces_the_stale_cascade_with_a_fresh_one(self):
        original = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        original_transformation = original["steps"][1]
        self.assertEqual(original_transformation["roll"]["row"], 5)

        revised = resolution.reroll(original["proposal_id"], step=0, resource="fortune", seed=6)
        mechanics_by_id = {s["step_id"]: s["mechanic"] for s in revised["steps"]}
        self.assertEqual(mechanics_by_id, {0: "exposure", 1: "transformation"})
        fresh_transformation = next(s for s in revised["steps"] if s["step_id"] == 1)
        self.assertEqual(fresh_transformation["roll"]["row"], 3)
        self.assertNotEqual(fresh_transformation["roll"], original_transformation["roll"])
        self.assertEqual(fresh_transformation["depends_on"], [0])

    def test_no_stale_step_survives_alongside_the_fresh_one(self):
        original = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        revised = resolution.reroll(original["proposal_id"], step=0, resource="fortune", seed=6)
        self.assertEqual(len(revised["steps"]), 2)  # not 3 -- the original step 1 is gone


class ResourceModifierTest(ResolutionTestBase):
    """research.md: Taint 0, bargaining 35, minor Exposure, original seed 5, reroll seed 1 --
    each resource's own effective_pct modifier and cost mutation."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 35
        frontmatter["taint"] = 0
        frontmatter["resolve"] = {"current": 2}
        frontmatter["fortune"] = {"current": 2}
        character.save(frontmatter, "", self.path)

    def propose_original(self):
        return resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="minor", seed=5
        )

    def test_resolve_adds_20_and_spends_resolve(self):
        result = self.propose_original()
        revised = resolution.reroll(result["proposal_id"], step=0, resource="resolve", seed=1)
        step_0 = revised["steps"][0]
        self.assertEqual(step_0["roll"]["effective_pct"], 55)
        self.assertIn(
            {
                "entity": str(self.path),
                "field": "resolve.current",
                "op": "-",
                "value": 1,
                "produced_by_step": 0,
            },
            step_0["mutations"],
        )

    def test_fortune_is_a_plain_reroll_and_spends_fortune(self):
        result = self.propose_original()
        revised = resolution.reroll(result["proposal_id"], step=0, resource="fortune", seed=1)
        step_0 = revised["steps"][0]
        self.assertEqual(step_0["roll"]["effective_pct"], 35)
        self.assertIn(
            {
                "entity": str(self.path),
                "field": "fortune.current",
                "op": "-",
                "value": 1,
                "produced_by_step": 0,
            },
            step_0["mutations"],
        )

    def test_bargain_is_a_plain_reroll_and_gains_taint(self):
        result = self.propose_original()
        revised = resolution.reroll(result["proposal_id"], step=0, resource="bargain", seed=1)
        step_0 = revised["steps"][0]
        self.assertEqual(step_0["roll"]["effective_pct"], 35)
        self.assertIn(
            {
                "entity": str(self.path),
                "field": "taint",
                "op": "+",
                "value": 1,
                "produced_by_step": 0,
            },
            step_0["mutations"],
        )

    def test_unknown_resource_raises_value_error(self):
        result = self.propose_original()
        with self.assertRaises(ValueError):
            resolution.reroll(result["proposal_id"], step=0, resource="luck")


class RerollErrorCaseTest(ResolutionTestBase):
    def test_reroll_unknown_step_raises(self):
        result = resolution.propose(
            actor=self.path, mechanic="ordinary-test", skill="bargaining", seed=1
        )
        with self.assertRaises(ValueError):
            resolution.reroll(result["proposal_id"], step=99, resource="fortune")

    def test_reroll_internal_cascade_step_raises(self):
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 35
        frontmatter["taint"] = 1
        character.save(frontmatter, "", self.path)
        result = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="major", seed=5
        )
        transformation_step_id = result["steps"][1]["step_id"]
        with self.assertRaises(ValueError):
            resolution.reroll(
                result["proposal_id"], step=transformation_step_id, resource="fortune"
            )

    def test_reroll_on_closed_proposal_raises_proposal_error(self):
        result = resolution.propose(
            actor=self.path, mechanic="ordinary-test", skill="bargaining", seed=1
        )
        resolution.commit(result["proposal_id"])
        with self.assertRaises(resolution.ProposalError):
            resolution.reroll(result["proposal_id"], step=0, resource="fortune")

    def test_reroll_on_fabricated_proposal_id_raises(self):
        with self.assertRaises(resolution.ProposalError):
            resolution.reroll("p-does-not-exist", step=0, resource="fortune")


if __name__ == "__main__":
    unittest.main()
