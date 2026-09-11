"""Tests for engine/wyrd/succession.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import succession  # noqa: E402


class RankCandidatesTests(unittest.TestCase):
    def test_priority_order(self) -> None:
        candidates = [
            {"id": "rival", "entanglement": "rival"},
            {"id": "companion", "entanglement": "companion"},
            {"id": "wronged", "entanglement": "wronged"},
        ]
        ranked = succession.rank_candidates(candidates)
        self.assertEqual([c["id"] for c in ranked], ["wronged", "rival", "companion"])

    def test_stable_on_tie(self) -> None:
        candidates = [
            {"id": "first", "entanglement": "bystander"},
            {"id": "second", "entanglement": "bystander"},
        ]
        ranked = succession.rank_candidates(candidates)
        self.assertEqual([c["id"] for c in ranked], ["first", "second"])

    def test_rejects_unknown_entanglement(self) -> None:
        candidates = [{"id": "x", "entanglement": "heir"}]
        with self.assertRaises(ValueError):
            succession.rank_candidates(candidates)

    def test_full_priority_order(self) -> None:
        candidates = [
            {"id": "companion", "entanglement": "companion"},
            {"id": "found_evidence", "entanglement": "found_evidence"},
            {"id": "rival", "entanglement": "rival"},
            {"id": "bystander", "entanglement": "bystander"},
            {"id": "investigating", "entanglement": "investigating"},
            {"id": "wronged", "entanglement": "wronged"},
        ]
        ranked = succession.rank_candidates(candidates)
        self.assertEqual(
            [c["id"] for c in ranked],
            ["wronged", "investigating", "bystander", "rival", "found_evidence", "companion"],
        )


class ProposeSuccessorsTests(unittest.TestCase):
    def test_caps_at_three(self) -> None:
        ranked = [{"id": str(i)} for i in range(5)]
        self.assertEqual(len(succession.propose_successors(ranked)), 3)

    def test_returns_fewer_when_fewer_exist(self) -> None:
        ranked = [{"id": "only-one"}]
        self.assertEqual(succession.propose_successors(ranked), ranked)

    def test_empty_input(self) -> None:
        self.assertEqual(succession.propose_successors([]), [])


class InheritTests(unittest.TestCase):
    def test_inherited_fields_carried(self) -> None:
        predecessor = {
            "threads": ["the-one-who-paid"],
            "enemies": ["the-drowned-count"],
            "active_threats": ["x"],
            "world_belief": "a hero of the flood",
        }
        result = succession.inherit(predecessor)
        for field in ("threads", "enemies", "active_threats", "world_belief"):
            self.assertEqual(result[field], predecessor[field])

    def test_excluded_fields_absent(self) -> None:
        predecessor = {
            "threads": [],
            "skills": {"athletics": 40},
            "careers": ["soldier"],
            "advances": 12,
            "stamina": 5,
            "fate": 2,
            "taint": 3,
            "transformations": [],
            "afflictions": [],
            "holdings": ["the-mill"],
        }
        result = succession.inherit(predecessor)
        for field in (
            "skills",
            "careers",
            "advances",
            "stamina",
            "fate",
            "taint",
            "transformations",
            "afflictions",
            "holdings",
        ):
            self.assertNotIn(field, result)

    def test_reputation_preserved_separately(self) -> None:
        predecessor = {"reputation": "a notorious killing"}
        result = succession.inherit(predecessor)
        self.assertEqual(result["predecessor_reputation"], "a notorious killing")
        self.assertNotIn("reputation", result)

    def test_no_reputation_means_no_predecessor_reputation_key(self) -> None:
        result = succession.inherit({})
        self.assertNotIn("predecessor_reputation", result)

    def test_holding_only_when_explicitly_passed(self) -> None:
        predecessor = {"holdings": ["the-mill", "a-boat"]}
        result = succession.inherit(predecessor)
        self.assertNotIn("holding", result)
        self.assertNotIn("holdings", result)

    def test_passed_holding_marked_encumbered(self) -> None:
        result = succession.inherit({}, inherited_holding={"id": "the-mill"})
        self.assertEqual(result["holding"], {"id": "the-mill", "encumbered": True})


class RecordPredecessorTests(unittest.TestCase):
    def test_lost(self) -> None:
        self.assertEqual(succession.record_predecessor("lost"), {"status": "gm-controlled"})

    def test_retired(self) -> None:
        self.assertEqual(succession.record_predecessor("retired"), {"status": "findable"})

    def test_died_with_fact_and_rumour(self) -> None:
        result = succession.record_predecessor(
            "died", fact="killed in the flood", rumour="vanished, some say taken"
        )
        self.assertEqual(result["status"], "died")
        self.assertEqual(result["fact"], "killed in the flood")
        self.assertEqual(result["rumour"], "vanished, some say taken")
        self.assertNotEqual(result["fact"], result["rumour"])

    def test_rejects_unknown_outcome(self) -> None:
        with self.assertRaises(ValueError):
            succession.record_predecessor("ascended")


if __name__ == "__main__":
    unittest.main()
