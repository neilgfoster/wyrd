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

SETTING_A = "setting-a"
SETTING_B = "setting-b"


class FindNounTests(unittest.TestCase):
    def setUp(self) -> None:
        self.nouns_index = {
            "Osric": [
                {"doc": "doc-a", "setting": SETTING_A, "count": 1, "offsets": [10]},
                {"doc": "doc-b", "setting": SETTING_B, "count": 1, "offsets": [20]},
            ],
            "NoSetting": [{"doc": "doc-c", "count": 1, "offsets": [30]}],
        }

    def test_only_matching_setting_returned(self) -> None:
        results = cf.find_noun(self.nouns_index, SETTING_A, "Osric")
        self.assertEqual(results, [{"doc": "doc-a", "offset": 10}])

    def test_other_setting_never_returned(self) -> None:
        results = cf.find_noun(self.nouns_index, SETTING_A, "Osric")
        self.assertNotIn({"doc": "doc-b", "offset": 20}, results)

    def test_missing_setting_field_never_matches(self) -> None:
        results = cf.find_noun(self.nouns_index, SETTING_A, "NoSetting")
        self.assertEqual(results, [])

    def test_setting_required(self) -> None:
        with self.assertRaises(TypeError):
            cf.find_noun(self.nouns_index, "Osric")  # type: ignore[call-arg]

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_noun({}, SETTING_A, "Osric"), [])


class FindRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.terms_index = {
            "fear": [
                {"doc": "d1", "setting": SETTING_A, "offset": 10, "rank": "mention"},
                {"doc": "d1", "setting": SETTING_A, "offset": 3, "rank": "definition"},
                {"doc": "d2", "setting": SETTING_B, "offset": 5, "rank": "definition"},
            ]
        }

    def test_only_matching_setting_returned_definition_first(self) -> None:
        results = cf.find_rule(self.terms_index, SETTING_A, "Fear")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["rank"], "definition")
        self.assertTrue(all(r["setting"] == SETTING_A for r in results))

    def test_other_setting_never_returned(self) -> None:
        results = cf.find_rule(self.terms_index, SETTING_A, "fear")
        self.assertNotIn("d2", [r["doc"] for r in results])

    def test_setting_required(self) -> None:
        with self.assertRaises(TypeError):
            cf.find_rule(self.terms_index, "fear")  # type: ignore[call-arg]

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_rule({}, SETTING_A, "fear"), [])


class FindTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tables_index = [
            {
                "doc": "d1",
                "setting": SETTING_A,
                "offset": 0,
                "dice": "d100",
                "row_count": 5,
                "caption": "Roll Table",
            },
            {
                "doc": "d2",
                "setting": SETTING_B,
                "offset": 50,
                "dice": "d6",
                "row_count": 6,
                "caption": "Outcome",
            },
            {
                "doc": "d3",
                "setting": SETTING_A,
                "offset": 100,
                "dice": "d100",
                "row_count": 3,
                "caption": None,
            },
        ]

    def test_only_matching_setting_returned(self) -> None:
        results = cf.find_table(self.tables_index, SETTING_A)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r["setting"] == SETTING_A for r in results))

    def test_combined_with_dice_filter(self) -> None:
        results = cf.find_table(self.tables_index, SETTING_A, dice="d100")
        self.assertEqual(len(results), 2)

    def test_other_setting_never_returned_even_matching_dice(self) -> None:
        results = cf.find_table(self.tables_index, SETTING_A, dice="d6")
        self.assertEqual(results, [])  # d6 record belongs to setting-b

    def test_setting_required(self) -> None:
        with self.assertRaises(TypeError):
            cf.find_table(self.tables_index, dice="d100")  # type: ignore[call-arg]

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_table([], SETTING_A), [])


class FindScenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios_index = [
            {"id": "the-drowning-well", "settings": [SETTING_A], "scale": "village"},
            {"id": "the-empty-tower", "settings": [SETTING_B], "scale": "fortress"},
            {"id": "shared-scenario", "settings": [SETTING_A, SETTING_B], "scale": "village"},
        ]

    def test_only_matching_setting_returned(self) -> None:
        results = cf.find_scenario(self.scenarios_index, SETTING_A)
        ids = {r["id"] for r in results}
        self.assertEqual(ids, {"the-drowning-well", "shared-scenario"})

    def test_other_setting_never_returned(self) -> None:
        results = cf.find_scenario(self.scenarios_index, SETTING_A)
        self.assertNotIn("the-empty-tower", {r["id"] for r in results})

    def test_combined_with_field_filter(self) -> None:
        results = cf.find_scenario(self.scenarios_index, SETTING_A, scale="village")
        ids = {r["id"] for r in results}
        self.assertEqual(ids, {"the-drowning-well", "shared-scenario"})

    def test_setting_required(self) -> None:
        with self.assertRaises(TypeError):
            cf.find_scenario(self.scenarios_index, scale="village")  # type: ignore[call-arg]

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_scenario([], SETTING_A), [])


class FindDocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.documents_index = [
            {"id": "wd-098", "setting": SETTING_A, "system": "a periodical", "edition": "98"},
            {"id": "wd-099", "setting": SETTING_B, "system": "a periodical", "edition": "98"},
        ]

    def test_only_matching_setting_returned(self) -> None:
        results = cf.find_doc(self.documents_index, SETTING_A, work="a periodical", issue="98")
        self.assertEqual(results, [{"doc": "wd-098"}])

    def test_other_setting_never_returned_even_matching_work_issue(self) -> None:
        results = cf.find_doc(self.documents_index, SETTING_A, work="a periodical", issue="98")
        self.assertNotIn({"doc": "wd-099"}, results)

    def test_setting_required(self) -> None:
        with self.assertRaises(TypeError):
            cf.find_doc(self.documents_index, work="a periodical")  # type: ignore[call-arg]

    def test_empty_index(self) -> None:
        self.assertEqual(cf.find_doc([], SETTING_A), [])


if __name__ == "__main__":
    unittest.main()
