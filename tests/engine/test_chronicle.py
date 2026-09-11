"""Tests for engine/wyrd/chronicle.py: `pending` resume/discard semantics (#328).

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import character, chronicle, rally, resolution  # noqa: E402

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


class ResumeStateTest(unittest.TestCase):
    # User Story 1 - resume a mid-beat interruption

    def test_resume_state_with_both_fields_set(self):
        pending = {"beat": "open-the-door", "awaiting": "the lock-picking roll", "rolled": None}
        self.assertEqual(
            chronicle.resume_state(pending),
            {"beat": "open-the-door", "awaiting": "the lock-picking roll"},
        )

    def test_resume_state_none_when_pending_is_none(self):
        self.assertIsNone(chronicle.resume_state(None))

    def test_resume_state_none_when_beat_and_awaiting_are_both_null(self):
        pending = {"beat": None, "awaiting": None, "rolled": "p-1"}
        self.assertIsNone(chronicle.resume_state(pending))

    def test_resume_state_independent_of_rolled(self):
        # rolled being set alongside a resumable beat/awaiting changes nothing about resuming.
        pending = {"beat": "open-the-door", "awaiting": "the lock", "rolled": "p-1"}
        self.assertEqual(
            chronicle.resume_state(pending), {"beat": "open-the-door", "awaiting": "the lock"}
        )


class DiscardAtRallyTest(unittest.TestCase):
    # User Story 2 - an abandoned proposal is discarded at the next Rally

    def test_discard_at_rally_clears_rolled_and_reports_the_id(self):
        pending = {"beat": None, "awaiting": None, "rolled": "p-1"}
        result = chronicle.discard_at_rally(pending)
        self.assertEqual(result["to_discard"], "p-1")
        self.assertIsNone(result["pending"]["rolled"])

    def test_discard_at_rally_is_a_no_op_when_rolled_already_none(self):
        pending = {"beat": None, "awaiting": None, "rolled": None}
        result = chronicle.discard_at_rally(pending)
        self.assertIsNone(result["to_discard"])
        self.assertIsNone(result["pending"]["rolled"])

    def test_discard_at_rally_handles_pending_none(self):
        result = chronicle.discard_at_rally(None)
        self.assertIsNone(result["to_discard"])
        self.assertIsNone(result["pending"])

    def test_discard_at_rally_leaves_beat_and_awaiting_untouched(self):
        pending = {"beat": "open-the-door", "awaiting": "the lock", "rolled": "p-1"}
        result = chronicle.discard_at_rally(pending)
        self.assertEqual(result["pending"]["beat"], "open-the-door")
        self.assertEqual(result["pending"]["awaiting"], "the lock")
        self.assertIsNone(result["pending"]["rolled"])


class DiscardMootTest(unittest.TestCase):
    # User Story 3 - a moot in-session proposal is explicitly discarded

    def test_discard_moot_clears_rolled_and_reports_the_id(self):
        pending = {"beat": "open-the-door", "awaiting": "the lock", "rolled": "p-1"}
        result = chronicle.discard_moot(pending)
        self.assertEqual(result["to_discard"], "p-1")
        self.assertIsNone(result["pending"]["rolled"])

    def test_discard_moot_is_a_no_op_with_no_open_proposal(self):
        pending = {"beat": None, "awaiting": None, "rolled": None}
        result = chronicle.discard_moot(pending)
        self.assertIsNone(result["to_discard"])


class RecordRolledTest(unittest.TestCase):
    # User Story 4 - at most one open proposal per actor is ever representable

    def test_record_rolled_sets_the_field(self):
        pending = {"beat": None, "awaiting": None, "rolled": None}
        result = chronicle.record_rolled(pending, "p-1")
        self.assertEqual(result["rolled"], "p-1")

    def test_record_rolled_accepts_none_pending(self):
        result = chronicle.record_rolled(None, "p-1")
        self.assertEqual(result, {"beat": None, "awaiting": None, "rolled": "p-1"})

    def test_record_rolled_rejects_a_second_open_proposal(self):
        pending = chronicle.record_rolled(None, "p-1")
        with self.assertRaises(ValueError):
            chronicle.record_rolled(pending, "p-2")

    def test_record_rolled_succeeds_again_after_a_discard(self):
        pending = chronicle.record_rolled(None, "p-1")
        cleared = chronicle.discard_at_rally(pending)["pending"]
        reopened = chronicle.record_rolled(cleared, "p-2")
        self.assertEqual(reopened["rolled"], "p-2")


class RallyIntegrationTest(unittest.TestCase):
    """Integration with wyrd.rally.apply_rally and a real proposal from wyrd.resolution."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "senna-vask.md"
        character.save(dict(SENNA), "", self.path)

    def tearDown(self):
        self._tmp.cleanup()

    def test_apply_rally_discards_a_surviving_open_proposal(self):
        proposed = resolution.propose(
            actor=self.path, mechanic="exposure", skill="bargaining", tier="moderate", seed=1
        )
        proposal_id = proposed["proposal_id"]
        pending = chronicle.record_rolled(None, proposal_id)

        result = rally.apply_rally(
            strain=1, stamina=5, stamina_max=10, advancement_record={}, pending=pending
        )

        self.assertIsNone(result["pending"]["rolled"])
        with self.assertRaises(resolution.ProposalError):
            resolution.discard(proposal_id)  # already discarded by the Rally; id no longer open

    def test_apply_rally_is_a_no_op_on_pending_with_no_open_proposal(self):
        pending = {"beat": None, "awaiting": None, "rolled": None}
        result = rally.apply_rally(
            strain=1, stamina=5, stamina_max=10, advancement_record={}, pending=pending
        )
        self.assertEqual(result["pending"], pending)

    def test_apply_rally_defaults_pending_to_none_for_existing_callers(self):
        # every caller predating #328 must keep working unchanged.
        result = rally.apply_rally(strain=1, stamina=5, stamina_max=10, advancement_record={})
        self.assertIsNone(result["pending"])


if __name__ == "__main__":
    unittest.main()
