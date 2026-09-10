#!/usr/bin/env python3
"""Tests for tools/check_conversion.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_conversion  # noqa: E402

VALID = """
from: {system: "an old system", edition: "2nd"}
version: 1
skills:
  method: direct
  note: "source is already percentile"
  map: {perception: awareness}
difficulty:
  map: {easy: 20, average: 0, challenging: -10, difficult: -20, hard: -30}
damage:
  method: direct
  wounds_to_stamina: direct
armour:
  method: table
  map: {1: light, 2: light, 3: modest, 4: modest, 5: heavy}
danger:
  derive_from: "the source's stated party level"
  formula: "danger = ceil(source_level / 2)"
rename: {taint: taint, trauma: shock}
arcs:
  chapter: "arc(scale=adventure)"
  encounter: beat
drop: [talents, hit-locations]
drop_note: "Dropped mechanics are recorded on the converted entity as prose."
manual: [setting-specific-subsystems]
"""


class ConversionValidationTest(unittest.TestCase):
    def _check(self, text: str) -> list[str]:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as handle:
            handle.write(text)
            path = pathlib.Path(handle.name)
        try:
            return check_conversion.check_file(path)
        finally:
            path.unlink()

    def test_worked_example_is_valid(self):
        self.assertEqual(self._check(VALID), [])

    def test_missing_from_fails(self):
        text = "version: 1\n"
        problems = self._check(text)
        self.assertTrue(any("from" in p for p in problems))

    def test_missing_version_fails(self):
        text = 'from: {system: "x"}\n'
        problems = self._check(text)
        self.assertTrue(any("version" in p for p in problems))

    def test_unrecognised_top_level_field_fails(self):
        text = 'from: {system: "x"}\nversion: 1\nnot_a_field: true\n'
        problems = self._check(text)
        self.assertTrue(any("not_a_field" in p for p in problems))

    def test_bad_damage_type_fails(self):
        text = 'from: {system: "x"}\nversion: 1\ndamage:\n  method: direct\n  damage_type: fire\n'
        problems = self._check(text)
        self.assertTrue(any("damage_type" in p and "fire" in p for p in problems))

    def test_bad_skills_method_fails(self):
        text = 'from: {system: "x"}\nversion: 1\nskills:\n  method: guess\n'
        problems = self._check(text)
        self.assertTrue(any("skills.method" in p for p in problems))

    def test_bad_armour_method_fails(self):
        text = 'from: {system: "x"}\nversion: 1\narmour:\n  method: guess\n'
        problems = self._check(text)
        self.assertTrue(any("armour.method" in p for p in problems))

    def test_non_positive_version_fails(self):
        text = 'from: {system: "x"}\nversion: 0\n'
        problems = self._check(text)
        self.assertTrue(any("version" in p for p in problems))

    def test_non_integer_version_fails(self):
        text = 'from: {system: "x"}\nversion: "1"\n'
        problems = self._check(text)
        self.assertTrue(any("version" in p for p in problems))

    def test_drop_not_a_list_of_strings_fails(self):
        text = 'from: {system: "x"}\nversion: 1\ndrop: {a: b}\n'
        problems = self._check(text)
        self.assertTrue(any("drop" in p for p in problems))

    def test_manual_not_a_list_of_strings_fails(self):
        text = 'from: {system: "x"}\nversion: 1\nmanual: [1, 2]\n'
        problems = self._check(text)
        self.assertTrue(any("manual" in p for p in problems))

    def test_malformed_yaml_fails(self):
        problems = self._check("from: [unclosed\n")
        self.assertTrue(problems)


if __name__ == "__main__":
    unittest.main()
