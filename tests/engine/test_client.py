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


if __name__ == "__main__":
    unittest.main()
