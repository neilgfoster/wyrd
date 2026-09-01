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


if __name__ == "__main__":
    unittest.main()
