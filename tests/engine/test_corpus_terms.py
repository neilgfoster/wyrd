"""Tests for engine/wyrd/corpus_terms.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_terms as ct  # noqa: E402


class BuildTermsIndexTests(unittest.TestCase):
    def test_heading_adjacent_ranked_definition(self) -> None:
        text = "Mechanics\n\nWhen a character faces something Fear-inducing, roll a test.\n"
        index = ct.build_terms_index(text, doc="core-rules", setting="my-setting")
        self.assertEqual(index["fear"][0]["rank"], "definition")

    def test_plain_prose_ranked_mention(self) -> None:
        text = (
            "This is an ordinary paragraph of narrative prose that goes on for a while before "
            "it eventually gets around to mentioning Fear only in passing, deep in the middle "
            "of a long sentence with no heading anywhere near it at all.\n"
        )
        index = ct.build_terms_index(text, doc="core-rules", setting="my-setting")
        self.assertEqual(index["fear"][0]["rank"], "mention")

    def test_non_curated_word_produces_no_entry(self) -> None:
        text = "The village was quiet and nothing else happened."
        index = ct.build_terms_index(text, doc="d1", setting="s1")
        self.assertEqual(index, {})

    def test_case_insensitive_match(self) -> None:
        text = "fear, Fear, and FEAR all appear here in one line without any heading nearby."
        index = ct.build_terms_index(text, doc="d1", setting="s1")
        self.assertEqual(len(index["fear"]), 3)

    def test_setting_present_on_every_posting(self) -> None:
        text = "Fear Tests\n\nRoll a Fear test.\n"
        index = ct.build_terms_index(text, doc="d1", setting="my-setting")
        for postings in index.values():
            for posting in postings:
                self.assertEqual(posting["setting"], "my-setting")


D100_TEXT = """Roll Table
01-10  You freeze.
11-30  You flee.
31-70  You fight through it.
71-90  You act rashly.
91-100 You are unshaken.
"""

D6_TEXT = """Outcome
1  Nothing happens.
2  A minor mishap.
3  You are delayed.
4  You lose an item.
5  You are noticed.
6  Disaster strikes.
"""

D66_TEXT = """Rumour Table
11  It was the miller.
12  It was the priest.
21  It was a stranger.
66  It was you.
"""

D10_TEXT = """d10 Table
1  Result one.
2  Result two.
3  Result three.
4  Result four.
5  Result five.
6  Result six.
7  Result seven.
8  Result eight.
9  Result nine.
10 Result ten.
"""


class BuildTablesIndexTests(unittest.TestCase):
    def test_d100_table(self) -> None:
        tables = ct.build_tables_index(D100_TEXT, doc="d1", setting="s1")
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["dice"], "d100")
        self.assertEqual(tables[0]["row_count"], 5)
        self.assertEqual(tables[0]["caption"], "Roll Table")

    def test_d6_table(self) -> None:
        tables = ct.build_tables_index(D6_TEXT, doc="d1", setting="s1")
        self.assertEqual(tables[0]["dice"], "d6")
        self.assertEqual(tables[0]["row_count"], 6)

    def test_d66_table(self) -> None:
        tables = ct.build_tables_index(D66_TEXT, doc="d1", setting="s1")
        self.assertEqual(tables[0]["dice"], "d66")
        self.assertEqual(tables[0]["row_count"], 4)

    def test_d10_table(self) -> None:
        tables = ct.build_tables_index(D10_TEXT, doc="d1", setting="s1")
        self.assertEqual(tables[0]["dice"], "d10")
        self.assertEqual(tables[0]["row_count"], 10)

    def test_single_stray_row_produces_no_table(self) -> None:
        text = "Some ordinary prose.\n42 is the answer to everything, apparently.\nMore prose.\n"
        tables = ct.build_tables_index(text, doc="d1", setting="s1")
        self.assertEqual(tables, [])

    def test_no_row_shaped_lines_at_all(self) -> None:
        tables = ct.build_tables_index(
            "Just ordinary prose, nothing structural.", doc="d1", setting="s1"
        )
        self.assertEqual(tables, [])

    def test_setting_present(self) -> None:
        tables = ct.build_tables_index(D6_TEXT, doc="d1", setting="my-setting")
        self.assertEqual(tables[0]["setting"], "my-setting")


if __name__ == "__main__":
    unittest.main()
