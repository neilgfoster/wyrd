#!/usr/bin/env python3
"""Tests for tools/check_setting.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "engine"))

import check_setting  # noqa: E402

VALID_TONE = """tone:
  register: dry
  prophecy: rare
  victory: mixed
  power_curve: moderate
  scope: regional
  scale_drift: suppressed
  mortality: standard
"""

BASE = (
    "name: test\n"
    "title: Test\n"
    "line: A line\n"
    'requires_engine: ">=0.1.0"\n'
    'version: "1.0.0"\n'
    "description: desc\n" + VALID_TONE
)


class OverridesValidationTest(unittest.TestCase):
    def _check(self, text: str) -> list[str]:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as handle:
            handle.write(text)
            path = pathlib.Path(handle.name)
        try:
            return check_setting.check_file(path)
        finally:
            path.unlink()

    def test_absent_overrides_block_is_valid(self):
        self.assertEqual(self._check(BASE), [])

    def test_valid_overrides_block_of_every_kind(self):
        text = BASE + (
            "overrides:\n"
            "  disable: [trauma]\n"
            "  rename: {taint: shadow}\n"
            "  tables: {oracle-prompt-npc-objective: setting/rules/tables/x.yaml}\n"
            "  extend: {skills: setting/rules/skills.yaml}\n"
        )
        self.assertEqual(self._check(text), [])

    def test_mechanism_outside_the_closed_set_fails(self):
        text = BASE + "overrides:\n  disable: [not-a-mechanism]\n"
        problems = self._check(text)
        self.assertTrue(any("not-a-mechanism" in p for p in problems))

    def test_kind_not_supported_by_the_mechanism_fails(self):
        # "skills" only supports extend, not disable.
        text = BASE + "overrides:\n  disable: [skills]\n"
        problems = self._check(text)
        self.assertTrue(any("skills" in p for p in problems))

    def test_disabling_and_overriding_the_same_mechanism_fails(self):
        text = BASE + "overrides:\n  disable: [taint]\n  rename: {taint: shadow}\n"
        problems = self._check(text)
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
