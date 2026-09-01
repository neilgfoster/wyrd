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
            [{"entity": str(self.path), "field": "taint", "op": "+", "value": 2}],
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


if __name__ == "__main__":
    unittest.main()
