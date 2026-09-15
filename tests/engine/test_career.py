"""Tests for engine/wyrd/career.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import career, rules  # noqa: E402

#: docs/design/24-authoring-a-setting.md's careers.yaml schema, matched by every real setting: a
#: career's `skills` is a plain list of names, never a per-skill dict of caps (#411) -- every
#: skill it grants shares the one flat cap in rules.CAREER_SKILL_CAP.
CAREER = {"skills": ["stealth", "swordplay", "lore"], "entry_point": True}


def _open(skill):
    return {"action": "open", "skill": skill}


def _raise(skill):
    return {"action": "raise", "skill": skill}


class WorkedSpreadsTest(unittest.TestCase):
    def test_open_two_everything_into_one(self):
        # open stealth, open swordplay, raise stealth x6 -> 55%/25%
        actions = [_open("stealth"), _open("swordplay")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 55)
        self.assertEqual(result["skills"]["swordplay"], 25)

    def test_open_two_split_evenly(self):
        # open both, raise each x3 -> 40%/40%
        actions = (
            [_open("stealth"), _open("swordplay")]
            + [_raise("stealth")] * 3
            + [_raise("swordplay")] * 3
        )
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 40)
        self.assertEqual(result["skills"]["swordplay"], 40)

    def test_open_three(self):
        # open 3, raise stealth x2, swordplay x2, lore x1 -> 35/35/30
        actions = (
            [_open("stealth"), _open("swordplay"), _open("lore")]
            + [_raise("stealth")] * 2
            + [_raise("swordplay")] * 2
            + [_raise("lore")] * 1
        )
        result = career.validate_allocation(actions, CAREER)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["stealth"], 35)
        self.assertEqual(result["skills"]["swordplay"], 35)
        self.assertEqual(result["skills"]["lore"], 30)

    def test_open_four(self):
        four_career = {"skills": ["a", "b", "c", "d"], "entry_point": True}
        actions = [_open("a"), _open("b"), _open("c"), _open("d")] + [_raise(s) for s in "abcd"]
        result = career.validate_allocation(actions, four_career)
        self.assertTrue(result["valid"], result.get("error"))
        for skill in "abcd":
            self.assertEqual(result["skills"][skill], 30)


class RejectionTest(unittest.TestCase):
    def test_wrong_total_rejected(self):
        actions = [_open("stealth"), _open("swordplay")] + [_raise("stealth")] * 5  # 7 total
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("7", result["error"])

    def test_fewer_than_two_opened_rejected(self):
        actions = [_open("stealth")] + [_raise("stealth")] * 7
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])

    def test_exceeding_cap_rejected(self):
        # The 8-advance creation budget alone can never reach the real 70% cap (open + 7 raises
        # tops out at 60%), so this exercises the rejection path against a lower cap via a patch
        # rather than via an unreachable-in-creation real value.
        with mock.patch.object(rules, "CAREER_SKILL_CAP", 45):
            # swordplay cap 45; opening + 4 raises = 45 (at cap); one more raise exceeds it
            actions = [_open("stealth"), _open("swordplay")] + [_raise("swordplay")] * 6
            result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("swordplay", result["error"])

    def test_skill_outside_union_rejected(self):
        actions = [_open("stealth"), _open("alchemy")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("alchemy", result["error"])

    def test_opening_already_open_skill_rejected(self):
        actions = [_open("stealth"), _open("stealth")] + [_raise("stealth")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])

    def test_raising_unopened_skill_rejected(self):
        actions = [_open("stealth"), _open("swordplay")] + [_raise("lore")] * 6
        result = career.validate_allocation(actions, CAREER)
        self.assertFalse(result["valid"])
        self.assertIn("lore", result["error"])

    def test_empty_allocation_rejected(self):
        result = career.validate_allocation([], CAREER)
        self.assertFalse(result["valid"])


class AncestryTest(unittest.TestCase):
    def test_ancestry_skill_accepted_without_extra_budget(self):
        ancestry = {"skills": ["herbalism"]}
        actions = (
            [_open("stealth"), _open("herbalism")]
            + [_raise("stealth")] * 4
            + [_raise("herbalism")] * 2
        )
        result = career.validate_allocation(actions, CAREER, ancestry)
        self.assertTrue(result["valid"], result.get("error"))
        self.assertEqual(result["skills"]["herbalism"], 35)
        self.assertEqual(len(actions), 8)

    def test_ancestry_and_career_grant_the_same_flat_cap(self):
        # docs/design/03-rules.md section 6: one figure applies to every skill a career (or
        # ancestry) grants -- there is no longer a "higher of two differing caps" case (#411).
        ancestry = {"skills": ["swordplay"]}
        self.assertEqual(
            career.effective_cap("swordplay", CAREER, ancestry),
            career.effective_cap("swordplay", CAREER),
        )
        self.assertEqual(
            career.effective_cap("swordplay", CAREER, ancestry), rules.CAREER_SKILL_CAP
        )


class EffectiveCapTest(unittest.TestCase):
    def test_a_skill_granted_by_neither_has_no_cap(self):
        self.assertIsNone(career.effective_cap("alchemy", CAREER))

    def test_a_skill_granted_only_by_ancestry_gets_the_flat_cap(self):
        ancestry = {"skills": ["herbalism"]}
        self.assertEqual(
            career.effective_cap("herbalism", CAREER, ancestry), rules.CAREER_SKILL_CAP
        )
        self.assertIsNone(career.effective_cap("herbalism", CAREER))


if __name__ == "__main__":
    unittest.main()


GUARD = {"id": "guard", "entry": True, "skills": ["blade", "watch"]}
SOLDIER = {"id": "soldier", "entry": True, "skills": ["blade", "drill"]}
GUARD_CAPTAIN = {
    "id": "guard-captain",
    "entry": False,
    "prerequisites": ["guard", "soldier"],
    "skills": ["blade", "watch", "command"],
}
CAREERS = [GUARD, SOLDIER, GUARD_CAPTAIN]


class CareerGraphTest(unittest.TestCase):
    def test_an_entry_career_is_entry_and_a_successor_is_not(self):
        self.assertTrue(career.is_entry(GUARD))
        self.assertFalse(career.is_entry(GUARD_CAPTAIN))

    def test_find_career_returns_none_for_an_id_the_table_does_not_hold(self):
        self.assertIs(career.find_career("guard", CAREERS), GUARD)
        self.assertIsNone(career.find_career("magister", CAREERS))

    def test_a_career_is_complete_only_when_every_granted_skill_is_at_its_cap(self):
        # spec.md FR-009 / docs/design/03-rules.md section 6.
        self.assertTrue(career.career_complete({"blade": 70, "watch": 70}, GUARD))
        self.assertFalse(career.career_complete({"blade": 70, "watch": 65}, GUARD))
        self.assertFalse(career.career_complete({"blade": 70}, GUARD))

    def test_a_career_granting_nothing_is_never_complete(self):
        # specs/104 research.md R4: all() over an empty grant list is vacuously true, which would
        # pay a completion's Stamina and Mark to anyone who entered a malformed career.
        self.assertFalse(career.career_complete({"blade": 70}, {"id": "hollow", "skills": []}))

    def test_a_skill_above_the_cap_still_completes_the_career(self):
        # A percentage earned under a more generous grant is never clawed back (research.md), so
        # it cannot leave a career permanently incompletable either.
        self.assertTrue(career.career_complete({"blade": 75, "watch": 70}, GUARD))

    def test_completion_is_read_off_the_history_not_re_derived(self):
        history = [
            {"career": "guard", "completed": True},
            {"career": "soldier", "completed": False},
        ]
        self.assertEqual(career.completed_career_ids(history), {"guard"})

    def test_any_entry_career_is_reachable_from_any_history(self):
        # spec.md FR-005: starting over from a fresh entry point is always legal.
        for history in ([], [{"career": "guard", "completed": False}]):
            self.assertTrue(career.change_career_legality("soldier", CAREERS, history)["legal"])

    def test_completing_any_one_prerequisite_qualifies(self):
        # spec.md FR-006: prerequisites are OR, not AND.
        for done in ("guard", "soldier"):
            history = [{"career": done, "completed": True}]
            result = career.change_career_legality("guard-captain", CAREERS, history)
            self.assertTrue(result["legal"], done)

    def test_a_career_merely_entered_does_not_qualify(self):
        history = [{"career": "guard", "completed": False}]
        result = career.change_career_legality("guard-captain", CAREERS, history)
        self.assertFalse(result["legal"])
        self.assertEqual(result["refusal"], "prerequisites_unmet")
        self.assertIn("guard", result["error"])

    def test_an_unknown_career_is_refused_by_name(self):
        result = career.change_career_legality("magister", CAREERS, [])
        self.assertFalse(result["legal"])
        self.assertEqual(result["refusal"], "unknown_career")
        self.assertIn("magister", result["error"])


class RealSettingDataTest(unittest.TestCase):
    """#411: this exact bug class -- passes against a hand-rolled fixture, breaks against real
    setting data -- shipped unnoticed until #403's manual verification hit it live. Load an actual
    career from a real setting's careers.yaml so this regression can't recur silently.
    """

    #: Sibling checkout of the real setting repo (#411's own reproduction environment). This
    #: repository's own worktree may be nested arbitrarily deep (e.g. under
    #: .claude/worktrees/<id>/), so walk upward from this file looking for a "wyrd-setting-
    #: darkfuture" sibling of any ancestor rather than assuming a fixed relative depth.
    @staticmethod
    def _find_careers_yaml():
        for ancestor in pathlib.Path(__file__).resolve().parents:
            candidate = ancestor.parent / "wyrd-setting-darkfuture" / "setting" / "careers.yaml"
            if candidate.exists():
                return candidate
        return pathlib.Path("/root/source/neilgfoster/wyrd-setting-darkfuture/setting/careers.yaml")

    CAREERS_YAML = _find_careers_yaml.__func__()

    def _load_first_entry_career(self):
        if not self.CAREERS_YAML.exists():
            self.skipTest(f"real setting checkout not present at {self.CAREERS_YAML}")
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        data = yaml.safe_load(self.CAREERS_YAML.read_text())
        careers = data["careers"]
        entry_career = next(c for c in careers if c.get("entry"))
        self.assertIsInstance(entry_career["skills"], list, "careers.yaml skills must be a list")
        return entry_career

    def test_effective_cap_against_a_real_career_does_not_raise(self):
        real_career = self._load_first_entry_career()
        skill = real_career["skills"][0]
        self.assertEqual(career.effective_cap(skill, real_career), rules.CAREER_SKILL_CAP)
        self.assertIsNone(career.effective_cap("no-such-skill-anywhere", real_career))

    def test_validate_allocation_against_a_real_career_does_not_raise(self):
        real_career = self._load_first_entry_career()
        skills = real_career["skills"]
        self.assertGreaterEqual(len(skills), 2, "fixture assumption: at least two granted skills")
        actions = [_open(skills[0]), _open(skills[1])] + [_raise(skills[0])] * 6
        result = career.validate_allocation(actions, real_career)
        self.assertTrue(result["valid"], result.get("error"))

    def test_career_complete_against_a_real_career_does_not_raise(self):
        real_career = self._load_first_entry_career()
        at_cap = dict.fromkeys(real_career["skills"], rules.CAREER_SKILL_CAP)
        self.assertTrue(career.career_complete(at_cap, real_career))
        self.assertFalse(career.career_complete({}, real_career))
