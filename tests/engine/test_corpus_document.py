"""Tests for engine/wyrd/corpus_document.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_document as cd  # noqa: E402


class OcrConfidenceTests(unittest.TestCase):
    def test_well_formed_scores_higher_than_garbled(self) -> None:
        clean = "The quiet village kept its own counsel through the long winter season."
        garbled = "Tqe qvviet vlllage kkkpt xqz9 zzz1 wwwm through qqq wintter sssqqzz."
        self.assertGreater(cd.ocr_confidence(clean), cd.ocr_confidence(garbled))

    def test_empty_text(self) -> None:
        self.assertEqual(cd.ocr_confidence(""), 0.0)

    def test_all_plausible_words_scores_one(self) -> None:
        self.assertEqual(cd.ocr_confidence("the quiet village kept counsel"), 1.0)


class BuildDocumentRecordTests(unittest.TestCase):
    def test_all_fields_carried(self) -> None:
        record = cd.build_document_record(
            id="wd-098",
            path="periodicals/wd98.txt",
            system="a periodical",
            edition="98",
            document_type="magazine",
            page_count=40,
            extraction_method="text_layer",
            text="a clean passage of text",
            setting="my-setting",
        )
        self.assertEqual(record["id"], "wd-098")
        self.assertEqual(record["path"], "periodicals/wd98.txt")
        self.assertEqual(record["system"], "a periodical")
        self.assertEqual(record["edition"], "98")
        self.assertEqual(record["document_type"], "magazine")
        self.assertEqual(record["page_count"], 40)
        self.assertEqual(record["extraction_method"], "text_layer")
        self.assertEqual(record["setting"], "my-setting")
        self.assertIn("ocr_confidence", record)


TEXT = "It was Osric the Fair who swore he saw Brannoc take it."


class BuildConcordanceTests(unittest.TestCase):
    def test_mid_sentence_noun_recorded_with_offsets(self) -> None:
        concordance = cd.build_concordance(TEXT, doc="wd-098", setting="my-setting")
        self.assertIn("Osric", concordance)
        postings = concordance["Osric"][0]
        self.assertEqual(postings["doc"], "wd-098")
        self.assertEqual(postings["setting"], "my-setting")
        self.assertEqual(postings["count"], 1)
        self.assertEqual(TEXT[postings["offsets"][0] : postings["offsets"][0] + 5], "Osric")

    def test_offset_skips_leading_stripped_punctuation(self) -> None:
        text = "She saw (Osric) leave."
        concordance = cd.build_concordance(text, doc="d1", setting="s1")
        offset = concordance["Osric"][0]["offsets"][0]
        self.assertEqual(text[offset : offset + 5], "Osric")

    def test_offset_skips_leading_quote_punctuation(self) -> None:
        text = 'He said, "Brannoc lied."'
        concordance = cd.build_concordance(text, doc="d1", setting="s1")
        offset = concordance["Brannoc"][0]["offsets"][0]
        self.assertEqual(text[offset : offset + 7], "Brannoc")

    def test_sentence_initial_excluded(self) -> None:
        text = "The village was quiet. The well was old."
        concordance = cd.build_concordance(text, doc="d1", setting="s1")
        self.assertNotIn("The", concordance)

    def test_stop_listed_word_excluded_regardless_of_position(self) -> None:
        text = "Osric said The Fair was watching."  # "The" mid-sentence, still stop-listed
        concordance = cd.build_concordance(text, doc="d1", setting="s1")
        self.assertNotIn("The", concordance)

    def test_non_sentence_initial_non_stop_word_recorded(self) -> None:
        concordance = cd.build_concordance(TEXT, doc="wd-098", setting="my-setting")
        self.assertIn("Fair", concordance)
        self.assertIn("Brannoc", concordance)

    def test_empty_text(self) -> None:
        self.assertEqual(cd.build_concordance("", doc="d1", setting="s1"), {})


class MergeConcordancesTests(unittest.TestCase):
    def test_two_documents_kept_separate(self) -> None:
        first = cd.build_concordance("It was Osric who walked the road.", doc="doc-a", setting="s1")
        second = cd.build_concordance(
            "They saw Osric at the guard post.", doc="doc-b", setting="s1"
        )
        merged = cd.merge_concordances([first, second])
        self.assertEqual(len(merged["Osric"]), 2)
        docs = {posting["doc"] for posting in merged["Osric"]}
        self.assertEqual(docs, {"doc-a", "doc-b"})

    def test_no_double_counting_within_a_document(self) -> None:
        first = cd.build_concordance("It was Osric who walked the road.", doc="doc-a", setting="s1")
        merged = cd.merge_concordances([first])
        self.assertEqual(merged["Osric"][0]["count"], 1)


if __name__ == "__main__":
    unittest.main()
