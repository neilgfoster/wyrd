"""Tests for engine/wyrd/advancement.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import advancement  # noqa: E402


def _fresh():
    return advancement.new_record()


class AwardTest(unittest.TestCase):
    def test_each_trigger_awards_once_and_raises_the_balance_by_one(self):
        # spec.md US1/SC-001/FR-005: all four triggers are awardable, each worth exactly 1.
        for trigger in advancement.TRIGGERS:
            result = advancement.award_advance(trigger, _fresh())
            self.assertTrue(result["awarded"], trigger)
            self.assertEqual(result["trigger"], trigger)
            self.assertEqual(result["record"]["advances_unspent"], 1)
            self.assertEqual(result["record"]["triggers"], [trigger])

    def test_the_trigger_vocabulary_is_the_design_documents_four(self):
        self.assertEqual(advancement.TRIGGERS, ("learned", "drove", "practised", "endured"))

    def test_unknown_trigger_is_refused_and_leaves_the_record_alone(self):
        # spec.md US1 scenario 3/FR-001: the engine never awards against a reason it doesn't know.
        record = {"triggers": ["learned"], "advances_unspent": 1}
        result = advancement.award_advance("improvised", record)
        self.assertFalse(result["awarded"])
        self.assertEqual(result["refusal"], "unknown_trigger")
        self.assertEqual(result["record"], record)

    def test_a_repeated_trigger_is_refused(self):
        # spec.md US2: however often the fiction supplies it, a trigger pays once a session.
        record = advancement.award_advance("endured", _fresh())["record"]
        result = advancement.award_advance("endured", record)
        self.assertFalse(result["awarded"])
        self.assertEqual(result["refusal"], "already_awarded")
        self.assertEqual(result["record"]["advances_unspent"], 1)

    def test_a_repeated_trigger_is_available_again_next_session(self):
        record = advancement.award_advance("endured", _fresh())["record"]
        result = advancement.award_advance("endured", advancement.begin_session(record))
        self.assertTrue(result["awarded"])
        self.assertEqual(result["record"]["advances_unspent"], 2)

    def test_a_fourth_distinct_trigger_is_refused_on_the_ceiling_not_repetition(self):
        # spec.md US3/SC-002/SC-003: four triggers, ceiling of three -- and the two refusals are
        # distinguishable, because one says "you already had this" and the other "that is all
        # this session pays".
        record = _fresh()
        for trigger in advancement.TRIGGERS[:3]:
            record = advancement.award_advance(trigger, record)["record"]
        result = advancement.award_advance(advancement.TRIGGERS[3], record)
        self.assertFalse(result["awarded"])
        self.assertEqual(result["refusal"], "session_ceiling")
        self.assertNotEqual(result["refusal"], "already_awarded")
        self.assertEqual(result["record"]["advances_unspent"], 3)

    def test_an_unknown_trigger_at_the_ceiling_is_reported_as_the_typo_it_is(self):
        record = _fresh()
        for trigger in advancement.TRIGGERS[:3]:
            record = advancement.award_advance(trigger, record)["record"]
        self.assertEqual(
            advancement.award_advance("improvised", record)["refusal"], "unknown_trigger"
        )

    def test_no_ordering_of_the_four_triggers_drives_a_session_above_three(self):
        # spec.md SC-002, exhaustively rather than on one representative ordering.
        for ordering in itertools.permutations(advancement.TRIGGERS):
            record = _fresh()
            for trigger in ordering:
                result = advancement.award_advance(trigger, record)
                record = result["record"]
            self.assertEqual(record["advances_unspent"], advancement.SESSION_ADVANCE_CEILING)
            self.assertEqual(len(record["triggers"]), advancement.SESSION_ADVANCE_CEILING)

    def test_the_record_holds_no_experience_point_total(self):
        # spec.md FR-007: the only stored quantities are the balance and this session's triggers.
        record = advancement.award_advance("drove", _fresh())["record"]
        self.assertEqual(set(record), {"triggers", "advances_unspent"})

    def test_award_never_mutates_the_record_it_was_given(self):
        record = {"triggers": [], "advances_unspent": 0}
        advancement.award_advance("learned", record)
        self.assertEqual(record, {"triggers": [], "advances_unspent": 0})


class SessionBoundaryTest(unittest.TestCase):
    def test_a_new_session_clears_the_triggers_and_keeps_the_balance(self):
        # spec.md FR-006: the economy caps the rate, not the balance.
        record = {"triggers": ["learned", "drove"], "advances_unspent": 7}
        opened = advancement.begin_session(record)
        self.assertEqual(opened["triggers"], [])
        self.assertEqual(opened["advances_unspent"], 7)

    def test_begin_session_never_mutates_the_record_it_was_given(self):
        record = {"triggers": ["learned"], "advances_unspent": 1}
        advancement.begin_session(record)
        self.assertEqual(record["triggers"], ["learned"])

    def test_a_session_awarding_nothing_is_legal(self):
        # spec.md Assumptions: "1-3" is a ceiling, not a quota -- the engine never mints an
        # advance nobody claimed.
        self.assertEqual(advancement.begin_session(_fresh())["advances_unspent"], 0)


if __name__ == "__main__":
    unittest.main()
