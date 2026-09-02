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
                    "field": "pending_omen",
                    "op": "set",
                    "value": -10,
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

    def test_declaration_bonus_reaches_the_attacker_skill(self):
        # specs/087-action-economy-engagement/spec.md's own Assumptions: combat-attack
        # previously silently dropped a caller-stated declaration_bonus, only ever applying a
        # reroll-resource/Omen delta. Uses a fresh, unclipped skill pairing (60-vs-60 -> eff. 50)
        # since CombatChainTest's own 60-vs-0 pairing already sits at the 95 ceiling, where a
        # further +/-20 wouldn't move effective_pct linearly.
        frontmatter, _ = character.load(self.target)
        frontmatter["skills"]["swordplay"] = 60
        character.save(frontmatter, "", self.target)

        unmodified = resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
        )
        modified = resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            declaration_bonus=-20,
            seed=2,
        )
        self.assertEqual(
            modified["steps"][0]["roll"]["effective_pct"],
            unmodified["steps"][0]["roll"]["effective_pct"] - 20,
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
                    "field": "pending_omen",
                    "op": "set",
                    "value": -10,
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


class OmenCarryoverTest(ResolutionTestBase):
    """research.md: alertness 10, climbing 45, pending_omen None, seed 40 -- an Omen produced by
    step 0 modifies step 1, and unwinds correctly on reroll."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"] = {"alertness": 10, "climbing": 45}
        frontmatter["pending_omen"] = None
        frontmatter["resolve"] = {"current": 2}
        character.save(frontmatter, "", self.path)

    def propose_batch(self):
        return resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "alertness"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "climbing"},
            ],
            seed=40,
        )

    def test_omen_modifies_and_depends_on_the_producing_step(self):
        result = self.propose_batch()
        self.assertEqual(result["steps"][0]["roll"]["wyrd_die"], "fair_omen")
        self.assertEqual(result["steps"][1]["roll"]["effective_pct"], 55)  # 45 + 10
        self.assertEqual(result["steps"][1]["depends_on"], [0])

    def test_batch_stages_the_pending_omen_mutation(self):
        # step 0 produces the token (Fair Omen, value 10); step 1 consumes it and its own roll
        # also reads Fair Omen -- the *same* value, so no second mutation is needed (staging one
        # only on an actual value change, per FR-006).
        result = self.propose_batch()
        self.assertIn(
            {
                "entity": str(self.path),
                "field": "pending_omen",
                "op": "set",
                "value": 10,
                "produced_by_step": 0,
            },
            result["mutations"],
        )

    def test_reroll_discards_the_stale_consumer_and_re_resolves_it(self):
        result = self.propose_batch()
        original_step_1 = next(s for s in result["steps"] if s["step_id"] == 1)
        revised = resolution.reroll(result["proposal_id"], step=0, resource="resolve", seed=1)

        step_0 = next(s for s in revised["steps"] if s["step_id"] == 0)
        self.assertEqual(step_0["roll"]["wyrd_die"], "none")  # no Omen this time
        self.assertEqual(step_0["roll"]["effective_pct"], 30)  # 10 + 20 (Resolve)

        # step 1's original result is gone; a fresh one, no longer depending on step 0, replaces it.
        fresh_step_1_candidates = [
            s for s in revised["steps"] if s["step_id"] != 0 and s["mechanic"] == "ordinary-test"
        ]
        self.assertEqual(len(fresh_step_1_candidates), 1)
        fresh_step_1 = fresh_step_1_candidates[0]
        self.assertNotEqual(fresh_step_1["roll"], original_step_1["roll"])
        self.assertEqual(fresh_step_1["roll"]["effective_pct"], 45)  # unmodified
        self.assertEqual(fresh_step_1["depends_on"], [])

    def test_reroll_stages_no_pending_omen_mutation_when_the_token_returns_to_original(self):
        result = self.propose_batch()
        revised = resolution.reroll(result["proposal_id"], step=0, resource="resolve", seed=1)
        fields = [mutation["field"] for mutation in revised["mutations"]]
        self.assertNotIn("pending_omen", fields)
        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertIsNone(after["pending_omen"])  # untouched -- was already None


class PersistedOmenTest(ResolutionTestBase):
    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"]["bargaining"] = 10
        frontmatter["pending_omen"] = 10
        character.save(frontmatter, "", self.path)

    def test_persisted_omen_applies_with_no_depends_on(self):
        result = resolution.propose(
            actor=self.path, mechanic="ordinary-test", skill="bargaining", seed=1
        )
        self.assertEqual(result["roll"]["effective_pct"], 20)  # 10 + 10
        self.assertEqual(result["steps"][0]["depends_on"], [])

    def test_discard_leaves_the_persisted_omen_untouched(self):
        result = resolution.propose(
            actor=self.path, mechanic="ordinary-test", skill="bargaining", seed=1
        )
        resolution.discard(result["proposal_id"])
        after = self.load()
        self.assertEqual(after["pending_omen"], 10)


class OmenReplaceNotStackTest(ResolutionTestBase):
    """research.md: three same-actor requests, all skill 50, seed 59 -- replace, not stack, and
    no spurious mutation when the final token returns to the original."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"] = {"a": 50, "b": 50, "c": 50}
        frontmatter["pending_omen"] = None
        character.save(frontmatter, "", self.path)

    def test_third_request_is_modified_by_the_second_omen_not_the_first(self):
        result = resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "a"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "b"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "c"},
            ],
            seed=59,
        )
        self.assertEqual(result["steps"][0]["roll"]["wyrd_die"], "fair_omen")
        self.assertEqual(result["steps"][1]["roll"]["effective_pct"], 60)  # 50 + 10
        self.assertEqual(result["steps"][1]["depends_on"], [0])
        self.assertEqual(result["steps"][1]["roll"]["wyrd_die"], "ill_omen")
        self.assertEqual(result["steps"][2]["roll"]["effective_pct"], 40)  # 50 - 10
        self.assertEqual(result["steps"][2]["depends_on"], [1])  # not [0]

    def test_every_real_transition_is_staged_even_though_the_net_effect_cancels_out(self):
        # Each of the three requests genuinely changes the token in turn (None -> 10 -> -10 ->
        # None); every one of those transitions is staged on its own step (not only the net
        # no-op), which is what lets a *later* reroll of just the third request correctly
        # recover the second's still-pending -10 by replaying kept steps' own mutations
        # (see RerollAcrossOmenProducersTest) -- committing them in sequence still lands on
        # exactly the same final value (None) a single net mutation would have.
        result = resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "a"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "b"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "c"},
            ],
            seed=59,
        )
        self.assertEqual(
            result["mutations"],
            [
                {
                    "entity": str(self.path),
                    "field": "pending_omen",
                    "op": "set",
                    "value": 10,
                    "produced_by_step": 0,
                },
                {
                    "entity": str(self.path),
                    "field": "pending_omen",
                    "op": "set",
                    "value": -10,
                    "produced_by_step": 1,
                },
                {
                    "entity": str(self.path),
                    "field": "pending_omen",
                    "op": "set",
                    "value": None,
                    "produced_by_step": 2,
                },
            ],
        )

    def test_commit_still_lands_on_the_original_value(self):
        before = self.load()
        result = resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "a"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "b"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "c"},
            ],
            seed=59,
        )
        resolution.commit(result["proposal_id"])
        after = self.load()
        self.assertEqual(after["pending_omen"], before["pending_omen"])  # both None


class OmenPerActorIsolationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.a = pathlib.Path(self._tmp.name) / "a.md"
        self.b = pathlib.Path(self._tmp.name) / "b.md"
        for path in (self.a, self.b):
            frontmatter = dict(SENNA)
            frontmatter["skills"] = {"alertness": 10}
            frontmatter["pending_omen"] = None
            character.save(frontmatter, "", path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_one_actors_omen_never_reaches_another_actors_request(self):
        result = resolution.propose_batch(
            [
                {"actor": self.a, "mechanic": "ordinary-test", "skill": "alertness"},
                {"actor": self.b, "mechanic": "ordinary-test", "skill": "alertness"},
            ],
            seed=40,
        )
        self.assertEqual(result["steps"][0]["roll"]["wyrd_die"], "fair_omen")
        # Step 1 belongs to a different actor -- it must never see step 0's Omen.
        self.assertEqual(result["steps"][1]["depends_on"], [])
        self.assertEqual(result["steps"][1]["roll"]["effective_pct"], 10)  # unmodified


class RerollAcrossOmenProducersTest(ResolutionTestBase):
    """Rerolling a step downstream of an untouched *kept* step must still see that kept step's
    own genuinely-pending Omen -- even when the original call's own net token change happened
    to cancel out to nothing (so no single mutation alone would carry that intermediate value)."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"] = {"a": 50, "b": 50, "c": 50}
        frontmatter["pending_omen"] = None
        frontmatter["fortune"] = {"current": 2}
        character.save(frontmatter, "", self.path)

    def propose_batch(self):
        return resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "a"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "b"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "c"},
            ],
            seed=59,
        )

    def test_reroll_of_the_third_request_still_consumes_the_kept_second_requests_omen(self):
        result = self.propose_batch()
        # Sanity: step 1 (kept, untouched by this reroll) genuinely produced an Ill Omen.
        self.assertEqual(result["steps"][1]["roll"]["wyrd_die"], "ill_omen")

        revised = resolution.reroll(result["proposal_id"], step=2, resource="fortune", seed=100)
        step_1 = next(s for s in revised["steps"] if s["step_id"] == 1)
        step_2 = next(s for s in revised["steps"] if s["step_id"] == 2)
        # Step 1 is untouched -- same content as the original call produced.
        self.assertEqual(step_1["roll"], result["steps"][1]["roll"])
        # Step 2's fresh roll must still be modified by step 1's still-pending Ill Omen, and
        # depends_on the real, still-present step 1 -- not treated as if nothing was pending.
        self.assertEqual(step_2["roll"]["effective_pct"], 40)  # 50 - 10
        self.assertEqual(step_2["depends_on"], [1])

    def test_commit_after_that_reroll_lands_on_the_correct_final_pending_omen(self):
        result = self.propose_batch()
        pid = result["proposal_id"]
        resolution.reroll(pid, step=2, resource="fortune", seed=100)
        resolution.commit(pid)
        after = self.load()
        # Step 0 (kept) set it to 10; step 1 (kept) replaced it with -10; the fresh step 2 (seed
        # 100, fortune reroll) consumes it and its own roll reads a fresh Fair Omen, replacing
        # it back to 10 -- computed, not asserted (CLAUDE.md "check the maths").
        self.assertEqual(after["pending_omen"], 10)


class OmenAttributionSameValueTest(ResolutionTestBase):
    """A step that consumes a pending Omen and then rolls a fresh Omen of the *same* value must
    still become the new attributed producer -- a later step's depends_on must point at it, not
    at the earlier step whose value merely happened to match (adversarial review's second pass
    on PR 242)."""

    def setUp(self):
        super().setUp()
        frontmatter = self.load()
        frontmatter["skills"] = {"a": 10, "b": 45, "c": 45}
        frontmatter["pending_omen"] = None
        character.save(frontmatter, "", self.path)

    def test_third_request_depends_on_the_second_not_the_first(self):
        result = resolution.propose_batch(
            [
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "a"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "b"},
                {"actor": self.path, "mechanic": "ordinary-test", "skill": "c"},
            ],
            seed=40,
        )
        self.assertEqual(result["steps"][0]["roll"]["wyrd_die"], "fair_omen")
        self.assertEqual(result["steps"][1]["roll"]["wyrd_die"], "fair_omen")  # same value, +10
        # No mutation staged for step 1 -- the value didn't actually change (FR-006) -- but
        # attribution must still move to step 1.
        self.assertEqual([m["produced_by_step"] for m in result["steps"][1]["mutations"]], [])
        self.assertEqual(result["steps"][2]["depends_on"], [1])  # not [0]


class DamageTypeCriticalTest(unittest.TestCase):
    """specs/090-damage-type-criticals: each of the four closed damage types reads its own
    table, an unrecognized type is a load error, and omitting damage_type keeps
    critical-slashing's existing behaviour unchanged."""

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

    def propose_attack(self, damage_type=None):
        kwargs = {}
        if damage_type is not None:
            kwargs["damage_type"] = damage_type
        return resolution.propose(
            actor=self.attacker,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.target,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=2,
            **kwargs,
        )

    def test_no_damage_type_defaults_to_slashing(self):
        # research.md's own seed-2 scenario, reproduced with no damage_type supplied at all --
        # every caller/test that predates this parameter must keep resolving against
        # critical-slashing exactly as before (FR-001b).
        result = self.propose_attack()
        critical_step = [s for s in result["steps"] if s["mechanic"] == "critical"][0]
        self.assertEqual(critical_step["roll"]["table"], "critical-slashing")
        self.assertEqual(critical_step["roll"]["key"], "slashing-scored")

    def test_each_damage_type_reads_its_own_table(self):
        # Same seed (same dice throughout -- damage_type never affects a roll, only which table
        # answers it), so the critical total is always 7 (d6 5 + 2 points below zero): each
        # table's own row containing 7, computed from resolution.CRITICAL_TABLES directly rather
        # than hardcoded (CLAUDE.md "check the maths"), so this test can't silently drift from
        # the table data itself.
        for damage_type in ("slashing", "piercing", "blunt", "searing"):
            with self.subTest(damage_type=damage_type):
                result = self.propose_attack(damage_type=damage_type)
                critical_step = [s for s in result["steps"] if s["mechanic"] == "critical"][0]
                self.assertEqual(critical_step["roll"]["total"], 7)
                self.assertEqual(critical_step["roll"]["table"], f"critical-{damage_type}")
                expected_key, expected_effect = resolution._critical_band(damage_type, 7)
                self.assertEqual(critical_step["roll"]["key"], expected_key)
                if expected_effect is None:
                    self.assertEqual(critical_step["mutations"], [])
                else:
                    self.assertEqual(len(critical_step["mutations"]), 1)
                    self.assertEqual(
                        critical_step["mutations"][0]["value"]["effect"], expected_effect
                    )

    def test_a_nothing_lasting_row_stages_no_wound_for_a_non_slashing_table(self):
        # critical-blunt's 2-6 band carries no effect, unlike slashing's narrower 2-5 band --
        # confirms a table whose row *shape* differs from slashing's at the same total stages the
        # correct (here: nothing) mutation. Target Stamina 1 with a light weapon keeps the total
        # low without a telling blow.
        target = pathlib.Path(self._tmp.name) / "fragile.md"
        fragile = dict(SENNA)
        fragile["id"] = "fragile"
        fragile["skills"] = {"swordplay": 0}
        fragile["stamina"] = {"current": 1, "max": 1}
        character.save(fragile, "", target)
        found = None
        for seed in range(1, 200):
            result = resolution.propose(
                actor=self.attacker,
                mechanic="combat-attack",
                skill="swordplay",
                target=target,
                weapon_dice="1d3",
                armour_dice="1d1",
                damage_type="blunt",
                seed=seed,
            )
            critical_steps = [step for step in result["steps"] if step["mechanic"] == "critical"]
            if critical_steps and critical_steps[0]["roll"]["total"] <= 6:
                found = result
                break
        self.assertIsNotNone(found, "no low-total blunt scenario found in the scanned range")
        critical_step = [s for s in found["steps"] if s["mechanic"] == "critical"][0]
        self.assertEqual(critical_step["roll"]["key"], "blunt-winded")
        self.assertEqual(critical_step["mutations"], [])

    def test_unrecognized_damage_type_is_a_load_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.propose_attack(damage_type="acid")
        self.assertIn("acid", str(ctx.exception))

    def test_mortal_row_reads_from_the_correct_table_for_each_type(self):
        # Same seed-search shape as MortalCriticalTest, generalized across all four damage
        # types -- computed, not assumed (CLAUDE.md "check the maths").
        attacker = pathlib.Path(self._tmp.name) / "hard-attacker.md"
        target = pathlib.Path(self._tmp.name) / "fragile-target.md"
        hard_attacker = dict(SENNA)
        hard_attacker["id"] = "hard-attacker"
        hard_attacker["skills"] = {"swordplay": 90}
        character.save(hard_attacker, "", attacker)
        fragile_target = dict(SENNA)
        fragile_target["id"] = "fragile-target"
        fragile_target["skills"] = {"swordplay": 0}
        fragile_target["stamina"] = {"current": 1, "max": 1}
        character.save(fragile_target, "", target)

        for damage_type in ("slashing", "piercing", "blunt", "searing"):
            with self.subTest(damage_type=damage_type):
                found = None
                for seed in range(1, 200):
                    result = resolution.propose(
                        actor=attacker,
                        mechanic="combat-attack",
                        skill="swordplay",
                        target=target,
                        weapon_dice="6d8",
                        armour_dice="1d2",
                        damage_type=damage_type,
                        seed=seed,
                    )
                    critical_steps = [
                        step for step in result["steps"] if step["mechanic"] == "critical"
                    ]
                    if critical_steps and critical_steps[0]["roll"]["mortal"]:
                        found = result
                        break
                self.assertIsNotNone(
                    found, f"no mortal scenario found for {damage_type} in the scanned range"
                )
                critical_step = [s for s in found["steps"] if s["mechanic"] == "critical"][0]
                self.assertEqual(critical_step["mutations"], [])
                self.assertTrue(critical_step["roll"]["key"].endswith("-mortal"))
                self.assertEqual(critical_step["roll"]["table"], f"critical-{damage_type}")


class AftermathTest(unittest.TestCase):
    """specs/091-aftermath-wound-records: the post-fight aftermath roll and its 8 rows.

    `_stage_aftermath` is not yet wired into any caller (spec.md's T008: a future feature wires
    it into companion status/mortal-critical/Fate machinery), so it is exercised directly here,
    the same way `resolution._critical_band` is already exercised directly in
    `DamageTypeCriticalTest`.
    """

    def test_boundaries_resolve_to_the_correct_row(self):
        # docs/design/06-aftermath.md's own boundaries, both sides of each.
        for total, expected_key in (
            (6, "out-of-action"),
            (30, "out-of-action"),
            (31, "lasting-wound"),
            (52, "lasting-wound"),
            (53, "left-for-dead"),
            (66, "left-for-dead"),
            (67, "new-enemy"),
            (78, "new-enemy"),
            (79, "taken"),
            (88, "taken"),
            (89, "disfigured"),
            (98, "disfigured"),
            (99, "recurring-wound"),
            (110, "recurring-wound"),
            (111, "death"),
            (250, "death"),  # well above 111: the open row still resolves, never errors
        ):
            with self.subTest(total=total):
                key, _ = resolution._aftermath_band(total)
                self.assertEqual(key, expected_key)

    def test_rejects_non_positive_points_below_zero(self):
        for pbz in (0, -1):
            with self.subTest(points_below_zero=pbz):
                with self.assertRaises(ValueError):
                    resolution._stage_aftermath(
                        [],
                        entity="pc",
                        points_below_zero=pbz,
                        depends_on_step=0,
                        seed_cursor=resolution._SeedCursor(seed=1),
                        bears_on_skill="swordplay",
                    )

    def test_roll_and_modifier(self):
        steps: list[dict] = []
        # seed=1 -> rules.roll_d100(seed=1) is deterministic; the exact face isn't the point,
        # the modifier arithmetic is.
        resolution._stage_aftermath(
            steps,
            entity="pc",
            points_below_zero=3,
            depends_on_step=0,
            seed_cursor=resolution._SeedCursor(seed=1),
            bears_on_skill="swordplay",
        )
        step = steps[0]
        self.assertEqual(step["mechanic"], "aftermath")
        self.assertEqual(step["roll"]["table"], "aftermath")
        self.assertEqual(step["roll"]["modifier"], 15)
        self.assertEqual(step["roll"]["total"], step["roll"]["roll"] + 15)
        self.assertEqual(step["depends_on"], [0])

    def _stage_at_total(self, total: int, *, bears_on_skill: str = "swordplay") -> dict:
        """Force a specific total by choosing points_below_zero so seed=1's natural roll plus
        the modifier lands exactly on `total`."""
        natural = resolution.rules.roll_d100(seed=1)
        pbz, remainder = divmod(total - natural, 5)
        self.assertEqual(
            remainder, 0, f"total {total} is not reachable from a natural roll of {natural}"
        )
        steps: list[dict] = []
        resolution._stage_aftermath(
            steps,
            entity="pc",
            points_below_zero=pbz,
            depends_on_step=0,
            seed_cursor=resolution._SeedCursor(seed=1),
            bears_on_skill=bears_on_skill,
        )
        return steps[0]

    def test_out_of_action_produces_no_wound(self):
        step = self._stage_at_total(23)
        self.assertEqual(step["roll"]["key"], "out-of-action")
        self.assertEqual(step["mutations"], [])

    def test_taken_produces_no_wound(self):
        step = self._stage_at_total(83)
        self.assertEqual(step["roll"]["key"], "taken")
        self.assertEqual(step["mutations"], [])

    def test_death_produces_no_wound(self):
        step = self._stage_at_total(113)
        self.assertEqual(step["roll"]["key"], "death")
        self.assertEqual(step["mutations"], [])

    def test_lasting_wound_produces_a_bare_wound_record(self):
        step = self._stage_at_total(33)
        self.assertEqual(step["roll"]["key"], "lasting-wound")
        self.assertEqual(len(step["mutations"]), 1)
        wound = step["mutations"][0]["value"]
        self.assertEqual(wound["from"], {"table": "aftermath", "beat": 0})
        self.assertNotIn("effect", wound)
        self.assertNotIn("recurring", wound)
        character.validate_wound(wound)

    def test_disfigured_produces_dread_wound(self):
        step = self._stage_at_total(93)
        self.assertEqual(step["roll"]["key"], "disfigured")
        wound = step["mutations"][0]["value"]
        self.assertEqual(wound["effect"], {"dread": 1})
        self.assertNotIn("bears_on", wound)
        character.validate_wound(wound)

    def test_recurring_wound_produces_recurring_skill_wound(self):
        step = self._stage_at_total(103)
        self.assertEqual(step["roll"]["key"], "recurring-wound")
        wound = step["mutations"][0]["value"]
        self.assertEqual(wound["effect"], {"skill": -10})
        self.assertEqual(wound["recurring"], True)
        self.assertEqual(wound["bears_on"], "swordplay")
        self.assertIsNone(wound["closed"])
        character.validate_wound(wound)

    def test_new_enemy_and_left_for_dead_produce_bare_wound_records(self):
        for total, key in ((58, "left-for-dead"), (68, "new-enemy")):
            with self.subTest(key=key):
                step = self._stage_at_total(total)
                self.assertEqual(step["roll"]["key"], key)
                wound = step["mutations"][0]["value"]
                self.assertNotIn("effect", wound)
                character.validate_wound(wound)


class MortalBlowsFateDeathTest(unittest.TestCase):
    """specs/092-mortal-blows-fate-death: mortal-critical forcing, the Fate-spend re-read,
    `mortality: low`'s unconditional closure, and companion status transitions."""

    def _stage(self, *, points_below_zero=3, mortal=False, mortality="standard", seed=1):
        steps: list[dict] = []
        resolution._stage_aftermath(
            steps,
            entity="pc",
            points_below_zero=points_below_zero,
            depends_on_step=0,
            seed_cursor=resolution._SeedCursor(seed=seed),
            bears_on_skill="swordplay",
            mortal=mortal,
            mortality=mortality,
        )
        return steps

    # -- Story 1: a mortal critical forces death ---------------------------------------------

    def test_mortal_forces_death_regardless_of_roll(self):
        # points_below_zero=1 -> a low total that would ordinarily land on out-of-action.
        steps = self._stage(points_below_zero=1, mortal=True)
        roll = steps[0]["roll"]
        self.assertEqual(roll["key"], "death")
        self.assertTrue(roll["forced_mortal"])
        # the underlying roll/total are still recorded as actually rolled.
        self.assertEqual(roll["total"], roll["roll"] + roll["modifier"])

    def test_non_mortal_leaves_existing_behaviour_untouched(self):
        steps = self._stage(points_below_zero=1, mortal=False)
        roll = steps[0]["roll"]
        self.assertFalse(roll["forced_mortal"])
        self.assertIsNone(roll["closed_by"])
        self.assertFalse(roll["fate_spent"])

    # -- Story 4: mortality: low closes death unconditionally --------------------------------

    def test_mortality_low_closes_a_rolled_death(self):
        steps = self._stage(points_below_zero=25, mortality="low")  # well past 111
        roll = steps[0]["roll"]
        self.assertEqual(roll["key"], "recurring-wound")
        self.assertEqual(roll["closed_by"], "mortality")
        self.assertFalse(roll["fate_spent"])
        wound = steps[0]["mutations"][0]["value"]
        self.assertEqual(wound["effect"], {"skill": -10})

    def test_mortality_low_closes_a_mortal_forced_death(self):
        steps = self._stage(points_below_zero=1, mortal=True, mortality="low")
        roll = steps[0]["roll"]
        self.assertEqual(roll["key"], "recurring-wound")
        self.assertTrue(roll["forced_mortal"])
        self.assertEqual(roll["closed_by"], "mortality")

    def test_mortality_standard_and_high_leave_death_standing(self):
        for mortality in ("standard", "high"):
            with self.subTest(mortality=mortality):
                steps = self._stage(points_below_zero=25, mortality=mortality)
                self.assertEqual(steps[0]["roll"]["key"], "death")
                self.assertIsNone(steps[0]["roll"]["closed_by"])

    def test_invalid_mortality_rejected(self):
        with self.assertRaises(ValueError):
            self._stage(mortality="grim")

    # -- Story 2: a spent Fate point re-reads death -------------------------------------------

    def test_close_death_row_rewrites_and_spends_fate(self):
        steps = self._stage(points_below_zero=25)
        pc_state = {"fate": {"current": 2}}
        mutations = resolution.close_death_row(
            steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
        )
        roll = steps[0]["roll"]
        self.assertEqual(roll["key"], "recurring-wound")
        self.assertEqual(roll["closed_by"], "fate")
        self.assertTrue(roll["fate_spent"])
        self.assertEqual(pc_state["fate"]["current"], 1)
        self.assertEqual(pc_state["wounds"][0]["effect"], {"skill": -10})
        fate_mutation = next(m for m in mutations if m["field"] == "fate.current")
        self.assertEqual(fate_mutation["entity"], "pc")
        self.assertEqual(fate_mutation["value"], 1)

    def test_close_death_row_rejects_no_fate(self):
        steps = self._stage(points_below_zero=25)
        pc_state = {"fate": {"current": 0}}
        with self.assertRaises(ValueError):
            resolution.close_death_row(
                steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
            )
        self.assertEqual(steps[0]["roll"]["key"], "death")

    def test_close_death_row_rejects_non_death_step(self):
        steps = self._stage(points_below_zero=1)  # out-of-action
        pc_state = {"fate": {"current": 2}}
        with self.assertRaises(ValueError):
            resolution.close_death_row(
                steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
            )

    def test_close_death_row_rejects_already_closed(self):
        for mortality in ("mortality-closed", "fate-closed"):
            with self.subTest(mortality=mortality):
                if mortality == "mortality-closed":
                    steps = self._stage(points_below_zero=25, mortality="low")
                    pc_state = {"fate": {"current": 2}}
                else:
                    steps = self._stage(points_below_zero=25)
                    pc_state = {"fate": {"current": 2}}
                    resolution.close_death_row(
                        steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
                    )
                with self.assertRaises(ValueError):
                    resolution.close_death_row(
                        steps, 0, "pc", pc_state, spender_state=pc_state, spender_entity="pc"
                    )

    # -- Story 3: a Fate spend for a companion requires presence and ability -----------------

    def test_companion_spend_succeeds_when_player_present_and_able(self):
        steps = self._stage(points_below_zero=25)
        companion_state = {"role": "companion"}
        pc_state = {"fate": {"current": 2}, "stamina": {"current": 3}}
        resolution.close_death_row(
            steps,
            0,
            "companion",
            companion_state,
            spender_state=pc_state,
            spender_entity="pc",
            spender_present=True,
        )
        self.assertEqual(steps[0]["roll"]["key"], "recurring-wound")
        self.assertEqual(pc_state["fate"]["current"], 1)
        self.assertEqual(companion_state["wounds"][0]["effect"], {"skill": -10})

    def test_companion_spend_rejected_when_player_absent(self):
        steps = self._stage(points_below_zero=25)
        companion_state = {"role": "companion"}
        pc_state = {"fate": {"current": 2}, "stamina": {"current": 3}}
        with self.assertRaises(ValueError):
            resolution.close_death_row(
                steps,
                0,
                "companion",
                companion_state,
                spender_state=pc_state,
                spender_entity="pc",
                spender_present=False,
            )
        self.assertEqual(steps[0]["roll"]["key"], "death")
        self.assertEqual(pc_state["fate"]["current"], 2)

    def test_companion_spend_rejected_when_player_unable_to_act(self):
        steps = self._stage(points_below_zero=25)
        companion_state = {"role": "companion"}
        pc_state = {"fate": {"current": 2}, "stamina": {"current": -1}}
        with self.assertRaises(ValueError):
            resolution.close_death_row(
                steps,
                0,
                "companion",
                companion_state,
                spender_state=pc_state,
                spender_entity="pc",
                spender_present=True,
            )
        self.assertEqual(steps[0]["roll"]["key"], "death")

    def test_companion_spend_deducts_the_players_own_fate(self):
        steps = self._stage(points_below_zero=25)
        companion_state = {"role": "companion", "fate": {"current": 99}}
        pc_state = {"fate": {"current": 2}, "stamina": {"current": 0}}
        resolution.close_death_row(
            steps,
            0,
            "companion",
            companion_state,
            spender_state=pc_state,
            spender_entity="pc",
        )
        self.assertEqual(pc_state["fate"]["current"], 1)
        self.assertEqual(companion_state["fate"]["current"], 99)

    # -- Story 5: companion status transitions -----------------------------------------------

    def test_standing_death_sets_companion_status_dead(self):
        companion_state = {"role": "companion"}
        mutation = resolution.apply_companion_status(companion_state, "death")
        self.assertEqual(mutation["value"], "dead")
        self.assertEqual(companion_state["status"], "dead")

    def test_taken_sets_companion_status_away(self):
        companion_state = {"role": "companion"}
        mutation = resolution.apply_companion_status(companion_state, "taken")
        self.assertEqual(mutation["value"], "away")
        self.assertEqual(companion_state["status"], "away")

    def test_other_rows_leave_status_unchanged(self):
        for key in (
            "out-of-action",
            "lasting-wound",
            "left-for-dead",
            "new-enemy",
            "disfigured",
            "recurring-wound",
        ):
            with self.subTest(key=key):
                companion_state = {"role": "companion", "status": "with-party"}
                mutation = resolution.apply_companion_status(companion_state, key)
                self.assertIsNone(mutation)
                self.assertEqual(companion_state["status"], "with-party")


if __name__ == "__main__":
    unittest.main()
