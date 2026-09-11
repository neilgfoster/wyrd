"""Tests for engine/wyrd/corpus_find.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_find as cf  # noqa: E402


class FindNounTests(unittest.TestCase):
    def test_multi_document_postings_flattened(self) -> None:
        nouns_index = {
            "Osric": [
                {"doc": "doc-a", "setting": "s1", "count": 1, "offsets": [10]},
                {"doc": "doc-b", "setting": "s1", "count": 2, "offsets": [5, 40]},
            ]
        }
        results = cf.find_noun(nouns_index, "Osric")
        self.assertEqual(len(results), 3)
        self.assertIn({"doc": "doc-a", "offset": 10}, results)
        self.assertIn({"doc": "doc-b", "offset": 5}, results)
        self.assertIn({"doc": "doc-b", "offset": 40}, results)

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_noun({}, "Osric"), [])

    def test_no_match(self) -> None:
        nouns_index = {"Brannoc": [{"doc": "d1", "setting": "s1", "count": 1, "offsets": [0]}]}
        self.assertEqual(cf.find_noun(nouns_index, "Osric"), [])


class FindRuleTests(unittest.TestCase):
    def test_definition_before_mention(self) -> None:
        terms_index = {
            "fear": [
                {"doc": "d1", "setting": "s1", "offset": 10, "rank": "mention"},
                {"doc": "d1", "setting": "s1", "offset": 3, "rank": "definition"},
            ]
        }
        results = cf.find_rule(terms_index, "Fear")
        self.assertEqual(results[0]["rank"], "definition")
        self.assertEqual(results[1]["rank"], "mention")

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_rule({}, "fear"), [])


TABLES_INDEX = [
    {
        "doc": "d1",
        "setting": "s1",
        "offset": 0,
        "dice": "d100",
        "row_count": 5,
        "caption": "Roll Table",
    },
    {
        "doc": "d1",
        "setting": "s1",
        "offset": 50,
        "dice": "d6",
        "row_count": 6,
        "caption": "Outcome",
    },
    {"doc": "d1", "setting": "s1", "offset": 100, "dice": "d100", "row_count": 3, "caption": None},
]


class FindTableTests(unittest.TestCase):
    def test_dice_filter(self) -> None:
        results = cf.find_table(TABLES_INDEX, dice="d6")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["dice"], "d6")

    def test_about_filter_case_insensitive(self) -> None:
        results = cf.find_table(TABLES_INDEX, about="roll")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["caption"], "Roll Table")

    def test_none_caption_never_matches_about(self) -> None:
        results = cf.find_table(TABLES_INDEX, about="anything")
        for record in results:
            self.assertIsNotNone(record["caption"])

    def test_combined_filters(self) -> None:
        results = cf.find_table(TABLES_INDEX, dice="d100", about="roll")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["offset"], 0)

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_table([], dice="d100"), [])


SCENARIOS_INDEX = [
    {"id": "the-drowning-well", "settings": ["my-setting"], "scale": "village"},
    {"id": "the-empty-tower", "settings": ["another-setting"], "scale": "fortress"},
]


class FindScenarioTests(unittest.TestCase):
    def test_exact_field_match(self) -> None:
        results = cf.find_scenario(SCENARIOS_INDEX, scale="village")
        self.assertEqual([r["id"] for r in results], ["the-drowning-well"])

    def test_setting_in_membership_match(self) -> None:
        results = cf.find_scenario(SCENARIOS_INDEX, setting_in="another-setting")
        self.assertEqual([r["id"] for r in results], ["the-empty-tower"])

    def test_no_filters_returns_everything(self) -> None:
        results = cf.find_scenario(SCENARIOS_INDEX)
        self.assertEqual(results, SCENARIOS_INDEX)

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_scenario([], scale="village"), [])


DOCUMENTS_INDEX = [
    {"id": "wd-098", "system": "a periodical", "edition": "98"},
    {"id": "wd-099", "system": "a periodical", "edition": "99"},
]


class FindDocTests(unittest.TestCase):
    def test_work_and_issue_match(self) -> None:
        results = cf.find_doc(DOCUMENTS_INDEX, work="a periodical", issue="98")
        self.assertEqual(results, [{"doc": "wd-098"}])

    def test_no_offset_in_result(self) -> None:
        results = cf.find_doc(DOCUMENTS_INDEX, work="a periodical", issue="98")
        self.assertNotIn("offset", results[0])

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_doc([], work="a periodical"), [])


if __name__ == "__main__":
    unittest.main()
