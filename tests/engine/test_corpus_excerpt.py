"""Tests for engine/wyrd/corpus_excerpt.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6), matching
tests/engine/test_corpus_find.py's existing style.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_excerpt as ce  # noqa: E402

SETTING_A = "setting-a"
SETTING_B = "setting-b"

FIXTURE_DIR = pathlib.Path(__file__).resolve().parent / "fixtures" / "corpus_excerpt"
SETTING_DIR = FIXTURE_DIR / "setting-dir"

DOC_A_PHRASE_OFFSET = 154
DOC_A_LENGTH = 562
DOC_B_PHRASE_OFFSET = 172


def _documents_index() -> list[dict]:
    return [
        {"id": "doc-a", "path": "doc-a.md", "setting": SETTING_A},
        {"id": "doc-b", "path": "nested/doc-b.md", "setting": SETTING_A},
        {"id": "doc-other-setting", "path": "doc-a.md", "setting": SETTING_B},
    ]


class ReadExcerptRealTextTests(unittest.TestCase):
    """User Story 1: a query result carries its own excerpt."""

    def test_known_offset_returns_expected_phrase(self) -> None:
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_PHRASE_OFFSET
        )
        self.assertIsNotNone(excerpt)
        assert excerpt is not None
        self.assertIn("the wandering lantern-keeper", excerpt)

    def test_nested_path_resolves(self) -> None:
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-b", DOC_B_PHRASE_OFFSET
        )
        self.assertIsNotNone(excerpt)
        assert excerpt is not None
        self.assertIn("the copper key", excerpt)

    def test_deterministic(self) -> None:
        first = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_PHRASE_OFFSET
        )
        second = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_PHRASE_OFFSET
        )
        self.assertEqual(first, second)

    def test_other_setting_never_returned(self) -> None:
        # doc-other-setting has the same path as doc-a but belongs to SETTING_B; requesting it
        # under SETTING_A must not resolve, even though a record with that path does exist.
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-other-setting", 0
        )
        self.assertIsNone(excerpt)

    def test_matching_setting_for_other_document_does_resolve(self) -> None:
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_B, SETTING_DIR, "doc-other-setting", 0
        )
        self.assertIsNotNone(excerpt)


class ReadExcerptFailureModeTests(unittest.TestCase):
    """User Story 2: out-of-bounds requests are quiet, never a crash."""

    def test_unknown_doc_id_returns_none(self) -> None:
        excerpt = ce.read_excerpt(_documents_index(), SETTING_A, SETTING_DIR, "no-such-doc", 0)
        self.assertIsNone(excerpt)

    def test_offset_past_end_returns_none(self) -> None:
        excerpt = ce.read_excerpt(_documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_LENGTH)
        self.assertIsNone(excerpt)

    def test_offset_far_past_end_returns_none(self) -> None:
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_LENGTH + 10_000
        )
        self.assertIsNone(excerpt)

    def test_negative_offset_returns_none(self) -> None:
        excerpt = ce.read_excerpt(_documents_index(), SETTING_A, SETTING_DIR, "doc-a", -1)
        self.assertIsNone(excerpt)

    def test_missing_corpus_file_returns_none(self) -> None:
        documents = [{"id": "doc-missing", "path": "nowhere.md", "setting": SETTING_A}]
        excerpt = ce.read_excerpt(documents, SETTING_A, SETTING_DIR, "doc-missing", 0)
        self.assertIsNone(excerpt)

    def test_empty_index_returns_none(self) -> None:
        excerpt = ce.read_excerpt([], SETTING_A, SETTING_DIR, "doc-a", 0)
        self.assertIsNone(excerpt)

    def test_offset_zero_is_valid(self) -> None:
        excerpt = ce.read_excerpt(_documents_index(), SETTING_A, SETTING_DIR, "doc-a", 0)
        self.assertIsNotNone(excerpt)
        assert excerpt is not None
        self.assertTrue(excerpt.startswith("This is the opening line"))

    def test_window_zero_returns_minimal_string_not_none(self) -> None:
        excerpt = ce.read_excerpt(
            _documents_index(), SETTING_A, SETTING_DIR, "doc-a", DOC_A_PHRASE_OFFSET, window=0
        )
        self.assertIsNotNone(excerpt)
        self.assertEqual(excerpt, "")


class RealSettingCorpusTests(unittest.TestCase):
    """SC-001: verified against a real, already-populated setting's corpus, not only fixtures.

    Skipped (not failed) when no sibling wyrd-setting-titan checkout is present, so this test
    suite stays runnable in an environment without one.
    """

    def test_against_real_titan_corpus(self) -> None:
        import json

        titan_dir = _ROOT.parent / "wyrd-setting-titan"
        documents_path = titan_dir / "index" / "documents.json"
        if not documents_path.exists():
            self.skipTest("no sibling wyrd-setting-titan checkout with a built index")

        raw = json.loads(documents_path.read_text(encoding="utf-8"))
        documents = raw["documents"] if isinstance(raw, dict) and "documents" in raw else raw
        self.assertTrue(documents, "titan's documents.json is unexpectedly empty")

        record = documents[0]
        excerpt = ce.read_excerpt(documents, record["setting"], titan_dir, record["id"], 1000)
        self.assertIsNotNone(excerpt)
        self.assertGreater(len(excerpt or ""), 0)


if __name__ == "__main__":
    unittest.main()
