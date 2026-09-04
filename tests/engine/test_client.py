"""Tests for engine/wyrd/client.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Invokes `main()` directly
(no subprocess) and captures stdout, per the CLI contract in
specs/075-engine-scaffolding/contracts/cli.md.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import client, state  # noqa: E402


def _run(argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = client.main(argv)
    return exit_code, buffer.getvalue().strip()


class DescribeTest(unittest.TestCase):
    def test_describe_returns_full_catalog_with_roll_entry(self):
        exit_code, output = _run(["describe"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        names = [tool["name"] for tool in payload["tools"]]
        self.assertIn("roll", names)

    def test_describe_by_name_returns_single_entry(self):
        exit_code, output = _run(["describe", "--name", "roll"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "roll")
        self.assertIn("inputSchema", payload)
        self.assertIn("annotations", payload)

    def test_describe_unknown_name_is_structured_error_not_traceback(self):
        exit_code, output = _run(["describe", "--name", "bogus"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["verb"], "describe")

    def test_describe_by_name_returns_opposed_test_entry(self):
        exit_code, output = _run(["describe", "--name", "opposed-test"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "opposed-test")
        self.assertTrue(payload["annotations"]["readOnlyHint"])


class RollCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._cwd = pathlib.Path.cwd()
        self._path = pathlib.Path(self._tmp.name)
        import os

        os.chdir(self._path)

    def tearDown(self):
        import os

        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_roll_json_output_shape(self):
        exit_code, output = _run(["roll", "--sides", "100", "--seed", "1"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["verb"], "roll")
        self.assertEqual(payload["sides"], 100)
        self.assertTrue(payload["state_written"])

    def test_roll_text_output(self):
        exit_code, output = _run(["--format", "text", "roll", "--sides", "100", "--seed", "1"])
        self.assertEqual(exit_code, 0)
        self.assertTrue(output.startswith("d100:"))

    def test_roll_invalid_sides_is_structured_error_exit_zero(self):
        exit_code, output = _run(["roll", "--sides", "0"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["verb"], "roll")

    def test_roll_writes_state_readable_via_state_module(self):
        exit_code, output = _run(["roll", "--sides", "100", "--seed", "7"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        loaded = state.load(state.DEFAULT_STATE_PATH)
        self.assertEqual(loaded["last_roll"]["result"], payload["result"])


class OpposedTestCliTest(unittest.TestCase):
    def test_json_output_shape(self):
        exit_code, output = _run(
            ["opposed-test", "--skill", "70", "--opponent", "30", "--seed", "1"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["verb"], "opposed-test")
        self.assertEqual(payload["effective_pct"], 90)

    def test_text_output(self):
        exit_code, output = _run(
            ["--format", "text", "opposed-test", "--skill", "70", "--opponent", "30", "--seed", "1"]
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue(output.startswith("opposed-test:"))

    def test_missing_required_argument_exits_non_zero(self):
        buffer = io.StringIO()
        with contextlib.redirect_stderr(buffer), self.assertRaises(SystemExit) as ctx:
            client.main(["opposed-test", "--skill", "70"])
        self.assertNotEqual(ctx.exception.code, 0)

    def test_declaration_and_helper_flags_compose(self):
        exit_code, output = _run(
            [
                "opposed-test",
                "--skill",
                "50",
                "--opponent",
                "50",
                "--declaration",
                "specific",
                "--helper-skill",
                "45",
                "--seed",
                "1",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["effective_pct"], 64)

    def test_removes_risk_flag_returns_no_roll(self):
        exit_code, output = _run(
            ["opposed-test", "--skill", "50", "--opponent", "50", "--declaration", "removes_risk"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertTrue(payload["no_roll"])
        self.assertIsNone(payload["roll"])


class DeclarationBonusCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "declaration-bonus"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "declaration-bonus")

    def test_specific_leveraging(self):
        exit_code, output = _run(["declaration-bonus", "--category", "specific_leveraging"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["bonus"], 20)

    def test_unrecognized_category_is_structured_error(self):
        exit_code, output = _run(["declaration-bonus", "--category", "bogus"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)


class AssistanceBonusCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "assistance-bonus"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "assistance-bonus")

    def test_helper_skill(self):
        exit_code, output = _run(["assistance-bonus", "--helper-skill", "45"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["bonus"], 4)

    def test_cannot_attempt_flag(self):
        exit_code, output = _run(
            ["assistance-bonus", "--helper-skill", "100", "--can-attempt", "false"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["bonus"], 0)


class GroupTestCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "group-test"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "group-test")

    def test_most_capable(self):
        exit_code, output = _run(
            [
                "group-test",
                "--member-skills",
                "70,45,30",
                "--mode",
                "most_capable",
                "--opponent",
                "50",
                "--seed",
                "1",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["selected_skill"], 70)

    def test_untrained_member_via_empty_entry(self):
        exit_code, output = _run(
            [
                "group-test",
                "--member-skills",
                "70,,30",
                "--mode",
                "least_capable",
                "--opponent",
                "50",
                "--seed",
                "1",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["selected_skill"], 10)

    def test_empty_member_list_is_structured_error(self):
        exit_code, output = _run(
            ["group-test", "--member-skills", "", "--mode", "most_capable", "--opponent", "50"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)

    def test_unrecognized_mode_is_structured_error(self):
        exit_code, output = _run(
            ["group-test", "--member-skills", "50", "--mode", "bogus", "--opponent", "50"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)


class ExtendedTaskIntervalCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "extended-task-interval"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "extended-task-interval")

    def test_interval_shape(self):
        exit_code, output = _run(
            [
                "extended-task-interval",
                "--skill",
                "45",
                "--opponent",
                "50",
                "--progress",
                "2",
                "--target",
                "4",
                "--seed",
                "1",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["target"], 4)
        self.assertIn("gained", payload)
        self.assertIn("done", payload)


class CharacterCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = str(pathlib.Path(self._tmp.name) / "aria.md")

    def tearDown(self):
        self._tmp.cleanup()

    def test_describe_by_name(self):
        for name in ("character-save", "character-load"):
            exit_code, output = _run(["describe", "--name", name])
            self.assertEqual(exit_code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["name"], name)

    def test_save_then_load_round_trip(self):
        exit_code, _ = _run(
            [
                "character-save",
                "--path",
                self.path,
                "--frontmatter-json",
                '{"id": "aria"}',
            ]
        )
        self.assertEqual(exit_code, 0)
        exit_code, output = _run(["character-load", "--path", self.path])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["frontmatter"], {"id": "aria"})

    def test_invalid_wound_is_structured_error(self):
        exit_code, output = _run(
            [
                "character-save",
                "--path",
                self.path,
                "--frontmatter-json",
                '{"id": "x", "wounds": [{"id": "w1", "effect": {"skill": -10}}]}',
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)


class SkillScaleCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "skill-scale"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "skill-scale")

    def test_returns_documented_values(self):
        exit_code, output = _run(["skill-scale"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["open_value"], 25)
        self.assertEqual(payload["advance_step"], 5)
        self.assertEqual(payload["untrained"], 10)


class ValidateAllocationCliTest(unittest.TestCase):
    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "validate-allocation"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "validate-allocation")

    def test_valid_allocation(self):
        career_json = json.dumps({"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True})
        actions_json = json.dumps(
            [{"action": "open", "skill": "stealth"}, {"action": "open", "skill": "swordplay"}]
            + [{"action": "raise", "skill": "stealth"}] * 6
        )
        exit_code, output = _run(
            [
                "validate-allocation",
                "--career-json",
                career_json,
                "--actions-json",
                actions_json,
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertTrue(payload["valid"])

    def test_invalid_allocation_still_exits_zero(self):
        career_json = json.dumps({"skills": {"stealth": 55}, "entry_point": True})
        exit_code, output = _run(
            ["validate-allocation", "--career-json", career_json, "--actions-json", "[]"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertFalse(payload["valid"])

    def test_malformed_json_exits_non_zero(self):
        with self.assertRaises(json.JSONDecodeError):
            client.main(
                ["validate-allocation", "--career-json", "not json", "--actions-json", "[]"]
            )


class CreateCharacterCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = str(pathlib.Path(self._tmp.name) / "aria.md")

    def tearDown(self):
        self._tmp.cleanup()

    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "create-character"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["name"], "create-character")

    def test_valid_creation_produces_a_loadable_file(self):
        career_json = json.dumps({"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True})
        actions_json = json.dumps(
            [{"action": "open", "skill": "stealth"}, {"action": "open", "skill": "swordplay"}]
            + [{"action": "raise", "skill": "stealth"}] * 6
        )
        exit_code, output = _run(
            [
                "create-character",
                "--path",
                self.path,
                "--name",
                "Aria",
                "--career-json",
                career_json,
                "--actions-json",
                actions_json,
                "--loyalty",
                "the-old-guard",
                "--mortality",
                "standard",
                "--fault-line",
                "She trusts no one.",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertTrue(payload["valid"])
        exit_code, load_output = _run(["character-load", "--path", self.path])
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(load_output)["frontmatter"]["name"], "Aria")

    def test_rejected_allocation_writes_no_file(self):
        career_json = json.dumps({"skills": {"stealth": 55}, "entry_point": True})
        exit_code, output = _run(
            [
                "create-character",
                "--path",
                self.path,
                "--name",
                "X",
                "--career-json",
                career_json,
                "--actions-json",
                "[]",
                "--loyalty",
                "x",
                "--mortality",
                "standard",
                "--fault-line",
                "x",
            ]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertFalse(payload["valid"])
        self.assertFalse(pathlib.Path(self.path).exists())


class ProposeCommitDiscardCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = str(pathlib.Path(self._tmp.name) / "senna.md")
        exit_code, _ = _run(
            [
                "character-save",
                "--path",
                self.path,
                "--frontmatter-json",
                '{"id": "senna", "skills": {"bargaining": 40}, "taint": 0}',
            ]
        )
        self.assertEqual(exit_code, 0)

    def tearDown(self):
        self._tmp.cleanup()

    def test_describe_by_name(self):
        for name in ("propose", "commit", "discard"):
            exit_code, output = _run(["describe", "--name", name])
            self.assertEqual(exit_code, 0)
            payload = json.loads(output)
            self.assertEqual(payload["name"], name)

    def test_propose_commit_round_trip(self):
        exit_code, output = _run(
            [
                "propose",
                "--actor",
                self.path,
                "--mechanic",
                "exposure",
                "--skill",
                "bargaining",
                "--tier",
                "moderate",
                "--seed",
                "20260852",
            ]
        )
        self.assertEqual(exit_code, 0)
        proposed = json.loads(output)
        self.assertEqual(proposed["roll"]["roll"], 77)
        self.assertEqual(
            proposed["mutations"],
            [
                {
                    "entity": self.path,
                    "field": "taint",
                    "op": "+",
                    "value": 2,
                    "produced_by_step": 0,
                }
            ],
        )

        exit_code, output = _run(["character-load", "--path", self.path])
        self.assertEqual(json.loads(output)["frontmatter"]["taint"], 0)

        exit_code, output = _run(["commit", proposed["proposal_id"]])
        self.assertEqual(exit_code, 0)
        committed = json.loads(output)
        self.assertEqual(committed["mutations"], proposed["mutations"])

        exit_code, output = _run(["character-load", "--path", self.path])
        self.assertEqual(json.loads(output)["frontmatter"]["taint"], 2)

    def test_discard_writes_nothing(self):
        exit_code, output = _run(
            [
                "propose",
                "--actor",
                self.path,
                "--mechanic",
                "ordinary-test",
                "--skill",
                "bargaining",
                "--seed",
                "1",
            ]
        )
        proposed = json.loads(output)
        exit_code, output = _run(["discard", proposed["proposal_id"]])
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output)["proposal_id"], proposed["proposal_id"])

    def test_commit_unknown_id_is_structured_error(self):
        exit_code, output = _run(["commit", "p-does-not-exist"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["verb"], "commit")

    def test_propose_unknown_mechanic_is_argparse_rejected(self):
        buffer = io.StringIO()
        argv = [
            "propose",
            "--actor",
            self.path,
            "--mechanic",
            "no-such-mechanic",
            "--skill",
            "bargaining",
        ]
        with contextlib.redirect_stderr(buffer), self.assertRaises(SystemExit) as ctx:
            client.main(argv)
        self.assertNotEqual(ctx.exception.code, 0)


class RerollCliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = str(pathlib.Path(self._tmp.name) / "senna.md")
        exit_code, _ = _run(
            [
                "character-save",
                "--path",
                self.path,
                "--frontmatter-json",
                (
                    '{"id": "senna", "skills": {"bargaining": 35, "stealth": 45}, "taint": 0, '
                    '"resolve": {"current": 2}, "fortune": {"current": 2}}'
                ),
            ]
        )
        self.assertEqual(exit_code, 0)

    def tearDown(self):
        self._tmp.cleanup()

    def test_describe_by_name(self):
        exit_code, output = _run(["describe", "--name", "reroll"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output)["name"], "reroll")

    def test_reroll_round_trip(self):
        exit_code, output = _run(
            [
                "propose",
                "--actor",
                self.path,
                "--mechanic",
                "exposure",
                "--skill",
                "bargaining",
                "--tier",
                "minor",
                "--seed",
                "5",
            ]
        )
        self.assertEqual(exit_code, 0)
        proposed = json.loads(output)

        exit_code, output = _run(
            [
                "reroll",
                proposed["proposal_id"],
                "--step",
                "0",
                "--resource",
                "resolve",
                "--seed",
                "1",
            ]
        )
        self.assertEqual(exit_code, 0)
        revised = json.loads(output)
        self.assertEqual(revised["steps"][0]["roll"]["effective_pct"], 55)

        exit_code, output = _run(["commit", proposed["proposal_id"]])
        self.assertEqual(exit_code, 0)

    def test_reroll_unknown_resource_is_argparse_rejected(self):
        exit_code, output = _run(
            [
                "propose",
                "--actor",
                self.path,
                "--mechanic",
                "exposure",
                "--skill",
                "bargaining",
                "--tier",
                "minor",
                "--seed",
                "5",
            ]
        )
        proposed = json.loads(output)
        buffer = io.StringIO()
        argv = ["reroll", proposed["proposal_id"], "--step", "0", "--resource", "luck"]
        with contextlib.redirect_stderr(buffer), self.assertRaises(SystemExit) as ctx:
            client.main(argv)
        self.assertNotEqual(ctx.exception.code, 0)

    def test_reroll_unknown_step_is_structured_error(self):
        exit_code, output = _run(
            [
                "propose",
                "--actor",
                self.path,
                "--mechanic",
                "exposure",
                "--skill",
                "bargaining",
                "--tier",
                "minor",
                "--seed",
                "5",
            ]
        )
        proposed = json.loads(output)
        exit_code, output = _run(
            ["reroll", proposed["proposal_id"], "--step", "99", "--resource", "fortune"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["verb"], "reroll")


if __name__ == "__main__":
    unittest.main()


class AdvanceAwardTest(unittest.TestCase):
    def test_award_advance_emits_the_documented_shape(self):
        exit_code, output = _run(["award-advance", "--trigger", "learned"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["verb"], "award-advance")
        self.assertTrue(payload["awarded"])
        self.assertEqual(payload["record"], {"triggers": ["learned"], "advances_unspent": 1})

    def test_award_advance_refusal_names_which_rule_refused_it(self):
        exit_code, output = _run(
            [
                "award-advance",
                "--trigger",
                "endured",
                "--awarded",
                "learned",
                "--awarded",
                "drove",
                "--awarded",
                "practised",
                "--advances-unspent",
                "3",
            ]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output)["refusal"], "session_ceiling")

    def test_begin_session_clears_triggers_and_keeps_the_balance(self):
        exit_code, output = _run(
            ["begin-session", "--awarded", "learned", "--advances-unspent", "2"]
        )
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["triggers"], [])
        self.assertEqual(payload["advances_unspent"], 2)

    def test_describe_lists_both_new_verbs(self):
        _, output = _run(["describe"])
        names = {entry["name"] for entry in json.loads(output)["tools"]}
        self.assertIn("award-advance", names)
        self.assertIn("begin-session", names)
