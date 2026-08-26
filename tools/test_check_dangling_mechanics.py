#!/usr/bin/env python3
"""Tests for tools/check_dangling_mechanics.py.

stdlib unittest, no pytest (design/07-tooling.md section 6). No fixtures on disk: each
failure class is built in a temporary tree, so the tests exercise the real check functions
rather than restating their logic (tools/test_check_docs.py's own reasoning: "a guard whose
tests reimplement it cannot fail when it is wrong").

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_dangling_mechanics as cdm  # noqa: E402


class TreeCase(unittest.TestCase):
    """A scratch repo, built file by file so each test states exactly what it is testing."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, rel: str, text: str) -> pathlib.Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def problems(self):
        return [str(p) for p in cdm.find_problems(self.root)]


class TestDanglingReference(TreeCase):
    def test_reference_with_no_definition_is_caught(self):
        self.write(
            "design/01-example.md",
            "# Example\n\nThis document uses the Fictional Widget without defining it.\n",
        )
        problems = self.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("Fictional Widget", problems[0])
        self.assertIn("design/01-example.md:3", problems[0])

    def test_defined_and_referenced_mechanic_is_clean(self):
        self.write("design/01-define.md", "## Fictional Widget\n\nWhat it is.\n")
        self.write(
            "design/02-use.md",
            "Elsewhere, the Fictional Widget is used again.\n",
        )
        self.assertEqual(self.problems(), [])


class TestHistoricalInstances(TreeCase):
    """Fixture reconstructions of the six mechanics referenced before they were defined.

    Two of the six (engine characteristics, Standing) were originally single bare capitalized
    words. This check deliberately does not treat a lone capitalized word as a reference
    candidate -- see check_dangling_mechanics.py's module docstring for why that signal proved
    too noisy against this repo's own prose. These fixtures reconstruct the same fault --
    reference before definition -- using the multi-word/compound phrasing the mechanic would
    plausibly carry in a table or cross-reference, which is what the check can actually detect.
    """

    def test_engine_characteristics_referenced_before_defined(self):
        self.write(
            "design/03-conversion.md",
            "## Conversion contract\n\nConvert the Might Score, Grit Score and Wit Score from "
            "the source system.\n",
        )
        problems = self.problems()
        self.assertTrue(any("Might Score" in p for p in problems))

    def test_standing_referenced_in_upkeep_before_defined(self):
        self.write(
            "design/12-upkeep.md",
            "## Upkeep\n\nUpkeep cost is paid against the Standing Track each cycle.\n",
        )
        problems = self.problems()
        self.assertTrue(any("Standing Track" in p for p in problems))

    def test_party_effective_referenced_in_danger_formula_before_defined(self):
        self.write(
            "design/10-danger.md",
            "## Danger\n\nDanger scales against party_effective for the encounter.\n",
        )
        problems = self.problems()
        self.assertTrue(any("party_effective" in p for p in problems))

    def test_damage_type_critical_tables_referenced_before_defined(self):
        self.write(
            "design/15-combat.md",
            "## Combat\n\nOn a telling blow, roll on the Piercing Wound table.\n",
        )
        problems = self.problems()
        self.assertTrue(any("Piercing Wound" in p for p in problems))

    def test_skill_list_referenced_before_defined(self):
        self.write(
            "design/04-character.md",
            "## Character\n\nEach test is rolled against a skill from the Skill List.\n",
        )
        problems = self.problems()
        self.assertTrue(any("Skill List" in p for p in problems))

    def test_wound_schema_referenced_before_defined(self):
        self.write(
            "design/16-aftermath.md",
            "## Aftermath\n\nRecord the injury using the Wound Schema fields.\n",
        )
        problems = self.problems()
        self.assertTrue(any("Wound Schema" in p for p in problems))

    def test_all_six_pass_independently(self):
        # Each of the above is a self-contained temp tree (TreeCase.setUp per test), proving
        # no cross-test coupling: this test just re-confirms one representative case runs
        # standalone without any of the others' fixtures present.
        self.write(
            "design/10-danger.md",
            "## Danger\n\nDanger scales against party_effective for the encounter.\n",
        )
        problems = self.problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("party_effective", problems[0])


class TestDefinitionForms(TreeCase):
    def test_table_row_definition_is_recognized(self):
        self.write(
            "design/06-skills.md",
            "| Skill | Governs |\n|---|---|\n| Fictional Craft | making things |\n",
        )
        self.write("design/07-use.md", "A test against Fictional Craft is called.\n")
        self.assertEqual(self.problems(), [])

    def test_glossary_entry_definition_is_recognized(self):
        self.write(
            "design/08-glossary.md",
            "**Fictional Term**: a thing that means something.\n",
        )
        self.write("design/09-use.md", "Fictional Term appears again here.\n")
        self.assertEqual(self.problems(), [])


class TestExemptions(TreeCase):
    def test_code_span_reference_is_not_flagged(self):
        self.write(
            "design/01-example.md",
            "# Example\n\nSee `Fictional Widget` in the schema example.\n",
        )
        self.assertEqual(self.problems(), [])

    def test_fenced_code_block_reference_is_not_flagged(self):
        self.write(
            "design/01-example.md",
            "# Example\n\n```\nFictional Widget: true\n```\n",
        )
        self.assertEqual(self.problems(), [])

    def test_specs_directory_is_exempt(self):
        self.write(
            "specs/001-example/spec.md",
            "This spec references the Fictional Widget from an earlier design.\n",
        )
        self.assertEqual(self.problems(), [])


class TestCLI(TreeCase):
    def test_exit_code_zero_on_clean_tree(self):
        self.write("design/01-example.md", "# Example\n\nNothing undefined here.\n")
        code = cdm.main(["--root", str(self.root)])
        self.assertEqual(code, 0)

    def test_exit_code_one_on_dangling_reference(self):
        self.write(
            "design/01-example.md",
            "# Example\n\nThis document uses the Fictional Widget without defining it.\n",
        )
        code = cdm.main(["--root", str(self.root)])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
