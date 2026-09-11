#!/usr/bin/env python3
"""Tests for tools/check_no_implicit_chronicle.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). No fixtures on disk: each
case is built in a temporary tree, matching test_check_dangling_mechanics.py's own convention.

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_no_implicit_chronicle as chk  # noqa: E402


class TreeCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write_engine_module(self, name: str, text: str) -> pathlib.Path:
        path = self.root / "engine" / "wyrd" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def problems(self):
        return chk.find_problems(self.root)


class UnjustifiedGlobalTests(TreeCase):
    def test_dict_literal_flagged(self):
        self.write_engine_module("bad.py", "_cache: dict = {}\n")
        problems = self.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("_cache", problems[0])
        self.assertIn("bad.py", problems[0])

    def test_list_literal_flagged(self):
        self.write_engine_module("bad.py", "_queue = []\n")
        problems = self.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("_queue", problems[0])

    def test_set_call_flagged(self):
        self.write_engine_module("bad.py", "_seen = set()\n")
        problems = self.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("_seen", problems[0])

    def test_unrelated_comment_does_not_justify(self):
        text = "# just a note about this cache\n_cache: dict = {}\n"
        self.write_engine_module("bad.py", text)
        problems = self.problems()
        self.assertEqual(len(problems), 1)


class JustifiedGlobalTests(TreeCase):
    def test_process_local_comment_justifies(self):
        text = "#: Process-local scratch store, never persisted.\n_scratch: dict = {}\n"
        self.write_engine_module("good.py", text)
        self.assertEqual(self.problems(), [])

    def test_marker_is_case_insensitive(self):
        text = "# PROCESS-LOCAL cache only.\n_scratch: dict = {}\n"
        self.write_engine_module("good.py", text)
        self.assertEqual(self.problems(), [])


class NonCandidateTests(TreeCase):
    def test_populated_frozenset_not_flagged(self):
        text = '_STOP_WORDS = frozenset({"the", "a"})\n'
        self.write_engine_module("terms.py", text)
        self.assertEqual(self.problems(), [])

    def test_string_constant_not_flagged(self):
        self.write_engine_module("mod.py", '_NAME = "some-name"\n')
        self.assertEqual(self.problems(), [])

    def test_function_local_dict_not_flagged(self):
        text = "def f():\n    _cache = {}\n    return _cache\n"
        self.write_engine_module("mod.py", text)
        self.assertEqual(self.problems(), [])

    def test_class_body_dict_not_flagged(self):
        text = "class C:\n    _cache = {}\n"
        self.write_engine_module("mod.py", text)
        self.assertEqual(self.problems(), [])

    def test_no_engine_dir_returns_empty(self):
        self.assertEqual(chk.find_problems(self.root), [])


class RealRepoTest(unittest.TestCase):
    def test_real_repo_passes_clean(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        problems = chk.find_problems(root)
        self.assertEqual(problems, [], f"unexpected unjustified globals: {problems}")


if __name__ == "__main__":
    unittest.main()
