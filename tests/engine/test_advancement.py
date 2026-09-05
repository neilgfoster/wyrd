"""Tests for engine/wyrd/advancement.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))
sys.path.insert(0, str(_ROOT / "tools"))

import check_advancement  # noqa: E402
from wyrd import advancement, rules  # noqa: E402


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


GUARD = {"id": "guard", "entry": True, "skills": {"blade": 70, "watch": 70}}
SOLDIER = {"id": "soldier", "entry": True, "skills": {"blade": 70, "drill": 70}}
GUARD_CAPTAIN = {
    "id": "guard-captain",
    "entry": False,
    "prerequisites": ["guard", "soldier"],
    "skills": {"blade": 70, "watch": 70, "command": 70},
}
CAREERS = [GUARD, SOLDIER, GUARD_CAPTAIN]


def _view(skills=None, advances=1, career="guard", history=None):
    return advancement.new_view(career, skills or {"blade": 30}, advances, history)


class SpendRaiseTest(unittest.TestCase):
    def test_a_raise_moves_the_skill_by_one_step_and_costs_one_advance(self):
        # spec.md FR-003.
        result = advancement.spend_advance("raise", _view(), GUARD, skill="blade")
        self.assertTrue(result["spent"])
        self.assertEqual(result["view"]["skills"]["blade"], 30 + rules.SKILL_ADVANCE_STEP)
        self.assertEqual(result["view"]["advances_unspent"], 0)

    def test_a_raise_is_refused_at_the_career_cap(self):
        result = advancement.spend_advance(
            "raise", _view(skills={"blade": 70}), GUARD, skill="blade"
        )
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "at_cap")
        self.assertIn("70%", result["error"])

    def test_a_skill_the_career_does_not_grant_cannot_be_raised_even_when_held(self):
        # spec.md User Story 1 scenario 3 / Edge Cases: a skill kept from an earlier career stays
        # on the sheet and is simply unspendable-on.
        result = advancement.spend_advance(
            "raise", _view(skills={"drill": 40}), GUARD, skill="drill"
        )
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "not_granted")

    def test_a_skill_the_character_does_not_hold_cannot_be_raised(self):
        result = advancement.spend_advance("raise", _view(), GUARD, skill="watch")
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "not_open")

    def test_an_ancestry_widens_what_a_spend_may_raise(self):
        # spec.md Assumptions: the spend reuses career.effective_cap rather than a second rule.
        ancestry = {"skills": {"drill": 60}}
        result = advancement.spend_advance(
            "raise", _view(skills={"drill": 40}), GUARD, ancestry=ancestry, skill="drill"
        )
        self.assertTrue(result["spent"])
        self.assertEqual(result["view"]["skills"]["drill"], 45)

    def test_nine_advances_carry_an_opened_skill_to_the_seventy_percent_cap(self):
        # spec.md SC-001, asserted against the figure tools/check_advancement.py publishes rather
        # than restated by eye.
        expected = check_advancement.advances_to_cap()
        view = _view(skills={"blade": rules.SKILL_OPEN_VALUE}, advances=expected + 1)
        for _ in range(expected):
            result = advancement.spend_advance("raise", view, GUARD, skill="blade")
            self.assertTrue(result["spent"])
            view = result["view"]
        self.assertEqual(view["skills"]["blade"], 70)
        self.assertFalse(advancement.spend_advance("raise", view, GUARD, skill="blade")["spent"])


class SpendOpenTest(unittest.TestCase):
    def test_an_open_starts_the_skill_at_its_opening_value(self):
        # spec.md FR-004.
        result = advancement.spend_advance("open", _view(), GUARD, skill="watch")
        self.assertTrue(result["spent"])
        self.assertEqual(result["view"]["skills"]["watch"], rules.SKILL_OPEN_VALUE)
        self.assertEqual(result["view"]["advances_unspent"], 0)

    def test_a_skill_already_held_cannot_be_opened_again(self):
        result = advancement.spend_advance("open", _view(), GUARD, skill="blade")
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "already_open")

    def test_a_skill_outside_the_grant_cannot_be_opened(self):
        result = advancement.spend_advance("open", _view(), GUARD, skill="command")
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "not_granted")


class SpendChangeCareerTest(unittest.TestCase):
    def test_a_change_to_an_entry_career_is_always_legal(self):
        result = advancement.spend_advance(
            "change_career", _view(), GUARD, careers=CAREERS, target="soldier"
        )
        self.assertTrue(result["spent"])
        self.assertEqual(result["view"]["career"], "soldier")

    def test_a_change_records_the_departed_career_and_whether_it_was_complete(self):
        # spec.md FR-008.
        complete = _view(skills={"blade": 70, "watch": 70})
        result = advancement.spend_advance(
            "change_career", complete, GUARD, careers=CAREERS, target="soldier"
        )
        self.assertEqual(result["view"]["career_history"], [{"career": "guard", "completed": True}])

        incomplete = _view(skills={"blade": 70, "watch": 30})
        result = advancement.spend_advance(
            "change_career", incomplete, GUARD, careers=CAREERS, target="soldier"
        )
        self.assertEqual(
            result["view"]["career_history"], [{"career": "guard", "completed": False}]
        )

    def test_a_change_alters_no_skill_percentage(self):
        skills = {"blade": 70, "watch": 40}
        result = advancement.spend_advance(
            "change_career", _view(skills=skills), GUARD, careers=CAREERS, target="soldier"
        )
        self.assertEqual(result["view"]["skills"], skills)

    def test_a_non_entry_career_needs_one_prerequisite_completed(self):
        # spec.md FR-006 -- the history, not the current sheet, decides.
        history = [{"career": "soldier", "completed": True}]
        result = advancement.spend_advance(
            "change_career",
            _view(history=history),
            GUARD,
            careers=CAREERS,
            target="guard-captain",
        )
        self.assertTrue(result["spent"])

        result = advancement.spend_advance(
            "change_career", _view(), GUARD, careers=CAREERS, target="guard-captain"
        )
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "prerequisites_unmet")

    def test_a_career_completed_on_departure_qualifies_the_next_change(self):
        # The two paths agree: completing guard and leaving it records the completion that a
        # later move to guard-captain reads.
        view = _view(skills={"blade": 70, "watch": 70}, advances=2)
        view = advancement.spend_advance(
            "change_career", view, GUARD, careers=CAREERS, target="soldier"
        )["view"]
        result = advancement.spend_advance(
            "change_career", view, SOLDIER, careers=CAREERS, target="guard-captain"
        )
        self.assertTrue(result["spent"])

    def test_an_unknown_target_career_is_refused(self):
        result = advancement.spend_advance(
            "change_career", _view(), GUARD, careers=CAREERS, target="magister"
        )
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "unknown_career")

    def test_re_entering_a_completed_career_is_legal_and_appends_a_fresh_instance(self):
        # spec.md Edge Cases: eligibility once earned never expires, and each departure is its
        # own instance -- what a second completion grants is #278's.
        history = [{"career": "guard", "completed": True}]
        result = advancement.spend_advance(
            "change_career",
            _view(skills={"blade": 70, "watch": 70}, history=history),
            GUARD,
            careers=CAREERS,
            target="guard",
        )
        self.assertTrue(result["spent"])
        self.assertEqual(len(result["view"]["career_history"]), 2)


class SpendRefusalTest(unittest.TestCase):
    def test_there_are_exactly_three_spends(self):
        # spec.md FR-001.
        self.assertEqual(advancement.SPENDS, ("raise", "open", "change_career"))
        result = advancement.spend_advance("study", _view(), GUARD, skill="blade")
        self.assertFalse(result["spent"])
        self.assertEqual(result["refusal"], "unknown_spend")
        for spend in advancement.SPENDS:
            self.assertIn(spend, result["error"])

    def test_every_spend_costs_one_advance(self):
        self.assertEqual(advancement.ADVANCE_COST, 1)
        for spend, kwargs in (
            ("raise", {"skill": "blade"}),
            ("open", {"skill": "watch"}),
            ("change_career", {"careers": CAREERS, "target": "soldier"}),
        ):
            result = advancement.spend_advance(
                "...".replace("...", spend), _view(), GUARD, **kwargs
            )
            self.assertEqual(result["view"]["advances_unspent"], 0, spend)

    def test_an_empty_purse_refuses_every_spend_before_its_own_legality(self):
        # spec.md FR-002 / research.md: telling a broke character their chosen skill was
        # ineligible only invites them to pick another and be refused again.
        for spend, kwargs in (
            ("raise", {"skill": "command"}),
            ("open", {"skill": "command"}),
            ("change_career", {"careers": CAREERS, "target": "magister"}),
        ):
            result = advancement.spend_advance(spend, _view(advances=0), GUARD, **kwargs)
            self.assertFalse(result["spent"], spend)
            self.assertEqual(result["refusal"], "no_advance", spend)

    def test_a_refusal_returns_the_view_unchanged_and_mutates_nothing(self):
        # spec.md FR-012 / SC-004.
        view = _view(skills={"blade": 70}, history=[{"career": "watch", "completed": True}])
        before = json.loads(json.dumps(view))
        result = advancement.spend_advance("raise", view, GUARD, skill="blade")
        self.assertEqual(view, before)
        self.assertEqual(result["view"], before)

    def test_an_accepted_spend_mutates_nothing_it_was_given(self):
        view = _view()
        before = json.loads(json.dumps(view))
        advancement.spend_advance("open", view, GUARD, skill="watch")
        self.assertEqual(view, before)


if __name__ == "__main__":
    unittest.main()
