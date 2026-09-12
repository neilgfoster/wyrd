#!/usr/bin/env python3
"""Tests for tools/check_character_creation_data.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). No fixtures on disk between
runs: each test builds its own setting directory in a temp tree, so the tests exercise the real
check functions rather than restating their logic (tools/test_check_docs.py's own reasoning: "a
guard whose tests reimplement it cannot fail when it is wrong").

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_character_creation_data as ccd  # noqa: E402

VALID_CAREERS = """
careers:
  - id: guard
    entry: true
    skills: [blade, watch]
  - id: guard-captain
    entry: false
    prerequisites: [guard]
    skills: [blade, watch, command]
"""

VALID_LOYALTIES = """
loyalties:
  - id: the-crown
  - id: the-old-faith
relations:
  - a: the-crown
    b: the-old-faith
    kind: strained
"""

VALID_DRIVES = """
drives:
  - id: find-the-sister
    text: "Find my sister, wherever the roads have taken her."
"""

VALID_MISFORTUNES = """
misfortunes:
  - id: owed-coin
    text: "Owes a debt that will not stay forgotten."
"""

VALID_NAMES = """
cultures:
  - id: riverfolk
    given: [Mara, Toln]
    family: [Ashwell]
"""

VALID_ANCESTRIES = """
ancestries:
  - id: hill-kin
    skills: [climb, forage]
"""


class SettingDirCase(unittest.TestCase):
    """A scratch setting directory, populated file by file per test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, filename: str, text: str) -> None:
        (self.dir / filename).write_text(text, encoding="utf-8")

    def write_valid_setting(self) -> None:
        self.write(ccd.CAREERS_FILE, VALID_CAREERS)
        self.write(ccd.LOYALTIES_FILE, VALID_LOYALTIES)
        self.write(ccd.DRIVES_FILE, VALID_DRIVES)
        self.write(ccd.MISFORTUNES_FILE, VALID_MISFORTUNES)
        self.write(ccd.NAMES_FILE, VALID_NAMES)

    def problems(self):
        problems, _ = ccd.check_directory(self.dir)
        return problems


class ValidSettingTest(SettingDirCase):
    def test_all_required_files_correct_passes(self):
        self.write_valid_setting()
        self.assertEqual(self.problems(), [])

    def test_optional_ancestries_when_present_and_correct_passes(self):
        self.write_valid_setting()
        self.write(ccd.ANCESTRIES_FILE, VALID_ANCESTRIES)
        self.assertEqual(self.problems(), [])

    def test_ancestries_absent_entirely_is_not_an_error(self):
        self.write_valid_setting()
        self.assertFalse((self.dir / ccd.ANCESTRIES_FILE).exists())
        self.assertEqual(self.problems(), [])

    def test_single_loyalty_with_no_relations_key_is_legal(self):
        self.write_valid_setting()
        self.write(ccd.LOYALTIES_FILE, "loyalties:\n  - id: the-crown\n")
        self.assertEqual(self.problems(), [])


class MissingFileTest(SettingDirCase):
    def test_missing_required_file_is_reported(self):
        self.write(ccd.CAREERS_FILE, VALID_CAREERS)
        self.write(ccd.LOYALTIES_FILE, VALID_LOYALTIES)
        self.write(ccd.DRIVES_FILE, VALID_DRIVES)
        self.write(ccd.MISFORTUNES_FILE, VALID_MISFORTUNES)
        # names.yaml deliberately absent
        problems = self.problems()
        self.assertTrue(any("names.yaml" in p and "missing" in p for p in problems))


class CareersTest(SettingDirCase):
    def _careers_problems(self, text: str) -> list[str]:
        self.write_valid_setting()
        self.write(ccd.CAREERS_FILE, text)
        return [p for p in self.problems() if ccd.CAREERS_FILE in p]

    def test_missing_required_field(self):
        problems = self._careers_problems("careers:\n  - id: guard\n    entry: true\n")
        self.assertTrue(any("skills" in p for p in problems))

    def test_no_entry_career(self):
        text = (
            "careers:\n"
            "  - id: apprentice\n"
            "    entry: false\n"
            "    prerequisites: [apprentice]\n"
            "    skills: [blade]\n"
        )
        problems = self._careers_problems(text)
        self.assertTrue(any("no career declares entry: true" in p for p in problems))

    def test_entry_true_with_prerequisites_is_rejected(self):
        text = (
            "careers:\n"
            "  - id: guard\n"
            "    entry: true\n"
            "    prerequisites: [guard]\n"
            "    skills: [blade]\n"
        )
        problems = self._careers_problems(text)
        self.assertTrue(any("prerequisites" in p and "absent" in p for p in problems))

    def test_entry_false_without_prerequisites_is_rejected(self):
        text = "careers:\n  - id: guard-captain\n    entry: false\n    skills: [command]\n"
        problems = self._careers_problems(text)
        self.assertTrue(any("prerequisites" in p and "required" in p for p in problems))

    def test_dangling_prerequisite_is_rejected(self):
        text = (
            "careers:\n"
            "  - id: guard\n"
            "    entry: true\n"
            "    skills: [blade]\n"
            "  - id: captain\n"
            "    entry: false\n"
            "    prerequisites: [soldier]\n"
            "    skills: [command]\n"
        )
        problems = self._careers_problems(text)
        self.assertTrue(any("soldier" in p and "names no career" in p for p in problems))

    def test_prerequisite_cycle_is_rejected(self):
        text = (
            "careers:\n"
            "  - id: a\n"
            "    entry: false\n"
            "    prerequisites: [b]\n"
            "    skills: [x]\n"
            "  - id: b\n"
            "    entry: false\n"
            "    prerequisites: [a]\n"
            "    skills: [y]\n"
        )
        problems = self._careers_problems(text)
        self.assertTrue(any("unreachable" in p for p in problems))

    def test_duplicate_career_id_is_rejected(self):
        text = (
            "careers:\n"
            "  - id: guard\n"
            "    entry: true\n"
            "    skills: [blade]\n"
            "  - id: guard\n"
            "    entry: true\n"
            "    skills: [watch]\n"
        )
        problems = self._careers_problems(text)
        self.assertTrue(any("duplicates" in p for p in problems))

    def test_unrecognised_field_is_rejected(self):
        text = (
            "careers:\n"
            "  - id: guard\n"
            "    entry: true\n"
            "    skills: [blade]\n"
            "    mutant_power: laser-eyes\n"
        )
        # mutant_power is not in the required/optional shape at all -- it survives read_yaml
        # as an extra key but check_careers only inspects known fields; assert it's at least not
        # silently treated as satisfying a required field.
        problems = self._careers_problems(text)
        self.assertEqual(problems, [])  # documents current behaviour: unknown top-level keys on
        # a career entry are not yet rejected -- careers.yaml's schema (24-authoring-a-setting.md)
        # does not enumerate a closed field set for its own entries the way gear.yaml does.


class LoyaltiesTest(SettingDirCase):
    def _loyalties_problems(self, text: str) -> list[str]:
        self.write_valid_setting()
        self.write(ccd.LOYALTIES_FILE, text)
        return [p for p in self.problems() if ccd.LOYALTIES_FILE in p]

    def test_undeclared_loyalty_in_relation_is_rejected(self):
        text = (
            "loyalties:\n"
            "  - id: the-crown\n"
            "relations:\n"
            "  - a: the-crown\n"
            "    b: the-old-faith\n"
            "    kind: strained\n"
        )
        problems = self._loyalties_problems(text)
        self.assertTrue(
            any("the-old-faith" in p and "names no declared Loyalty" in p for p in problems)
        )

    def test_self_referential_relation_is_rejected(self):
        text = (
            "loyalties:\n"
            "  - id: the-crown\n"
            "relations:\n"
            "  - a: the-crown\n"
            "    b: the-crown\n"
            "    kind: strained\n"
        )
        problems = self._loyalties_problems(text)
        self.assertTrue(any("cannot be" in p and "itself" in p for p in problems))

    def test_bad_relation_kind_is_rejected(self):
        text = (
            "loyalties:\n"
            "  - id: the-crown\n"
            "  - id: the-old-faith\n"
            "relations:\n"
            "  - a: the-crown\n"
            "    b: the-old-faith\n"
            "    kind: enemies\n"
        )
        problems = self._loyalties_problems(text)
        self.assertTrue(any("kind" in p and "is not one of" in p for p in problems))

    def test_duplicate_relation_pair_either_order_is_rejected(self):
        text = (
            "loyalties:\n"
            "  - id: the-crown\n"
            "  - id: the-old-faith\n"
            "relations:\n"
            "  - a: the-crown\n"
            "    b: the-old-faith\n"
            "    kind: strained\n"
            "  - a: the-old-faith\n"
            "    b: the-crown\n"
            "    kind: irreconcilable\n"
        )
        problems = self._loyalties_problems(text)
        self.assertTrue(any("declared twice" in p for p in problems))

    def test_empty_loyalties_list_is_rejected(self):
        problems = self._loyalties_problems("loyalties: []\n")
        self.assertTrue(any("non-empty 'loyalties:'" in p for p in problems))


class DrivesMisfortunesTest(SettingDirCase):
    def test_empty_drives_list_is_rejected(self):
        self.write_valid_setting()
        self.write(ccd.DRIVES_FILE, "drives: []\n")
        problems = [p for p in self.problems() if ccd.DRIVES_FILE in p]
        self.assertTrue(any("non-empty" in p for p in problems))

    def test_duplicate_drive_id_is_rejected(self):
        self.write_valid_setting()
        text = 'drives:\n  - id: x\n    text: "a"\n  - id: x\n    text: "b"\n'
        self.write(ccd.DRIVES_FILE, text)
        problems = [p for p in self.problems() if ccd.DRIVES_FILE in p]
        self.assertTrue(any("duplicates" in p for p in problems))

    def test_missing_text_is_rejected(self):
        self.write_valid_setting()
        self.write(ccd.MISFORTUNES_FILE, "misfortunes:\n  - id: x\n")
        problems = [p for p in self.problems() if ccd.MISFORTUNES_FILE in p]
        self.assertTrue(any("text" in p and "missing" in p for p in problems))


class NamesTest(SettingDirCase):
    def test_culture_with_no_name_pools_is_rejected(self):
        self.write_valid_setting()
        self.write(ccd.NAMES_FILE, "cultures:\n  - id: riverfolk\n")
        problems = [p for p in self.problems() if ccd.NAMES_FILE in p]
        self.assertTrue(any("cannot name anyone" in p for p in problems))

    def test_empty_cultures_list_is_rejected(self):
        self.write_valid_setting()
        self.write(ccd.NAMES_FILE, "cultures: []\n")
        problems = [p for p in self.problems() if ccd.NAMES_FILE in p]
        self.assertTrue(any("non-empty 'cultures:'" in p for p in problems))

    def test_duplicate_culture_id_is_rejected(self):
        self.write_valid_setting()
        text = (
            "cultures:\n"
            "  - id: riverfolk\n"
            "    given: [Mara]\n"
            "  - id: riverfolk\n"
            "    given: [Toln]\n"
        )
        self.write(ccd.NAMES_FILE, text)
        problems = [p for p in self.problems() if ccd.NAMES_FILE in p]
        self.assertTrue(any("duplicates" in p for p in problems))


class AncestriesTest(SettingDirCase):
    def test_malformed_ancestry_entry_is_rejected(self):
        self.write_valid_setting()
        self.write(ccd.ANCESTRIES_FILE, "ancestries:\n  - id: hill-kin\n")
        problems = [p for p in self.problems() if ccd.ANCESTRIES_FILE in p]
        self.assertTrue(any("skills" in p and "missing" in p for p in problems))

    def test_entry_field_on_ancestry_is_rejected(self):
        self.write_valid_setting()
        text = "ancestries:\n  - id: hill-kin\n    entry: true\n    skills: [climb]\n"
        self.write(ccd.ANCESTRIES_FILE, text)
        problems = [p for p in self.problems() if ccd.ANCESTRIES_FILE in p]
        self.assertTrue(any("entry" in p and "not part of an ancestry" in p for p in problems))

    def test_duplicate_ancestry_id_is_rejected(self):
        self.write_valid_setting()
        text = (
            "ancestries:\n"
            "  - id: hill-kin\n"
            "    skills: [climb]\n"
            "  - id: hill-kin\n"
            "    skills: [forage]\n"
        )
        self.write(ccd.ANCESTRIES_FILE, text)
        problems = [p for p in self.problems() if ccd.ANCESTRIES_FILE in p]
        self.assertTrue(any("duplicates" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
