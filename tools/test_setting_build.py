"""Tests for tools/setting_build.py -- covers every FR/SC in specs/150-.../spec.md.

Runs against fixture library trees under tools/fixtures/setting_build/ and tools/fixtures/pass0/
only -- never against any real wyrd-setting-* repository's content (CLAUDE.md's repository
table).
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))

import setting_build as sb  # noqa: E402
import setting_pass0 as pass0  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "setting_build"
PASS0_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "pass0"


def _copy_fixture(base: Path, name: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "setting"
    shutil.copytree(base / name, dest)
    return dest


def _snapshot_index(setting_dir: Path) -> dict[str, bytes]:
    index_dir = setting_dir / "index"
    if not index_dir.is_dir():
        return {}
    return {p.name: p.read_bytes() for p in index_dir.iterdir() if p.is_file()}


class BuildCorpusDocumentTests(unittest.TestCase):
    def test_document_dict_carries_every_required_field(self):
        record = pass0.CatalogueRecord(
            id="core/rulebook.md",
            path="core/rulebook.md",
            kind="core-rules",
            authority_tier=0,
            subject="fear-rules",
            content_hash="sha256:abc",
            status="present",
            provides=["bestiary"],
        )
        doc = sb.build_corpus_document(record, "Fear the dark.", "demo-setting")
        self.assertEqual(doc["id"], "core/rulebook.md")
        self.assertEqual(doc["path"], "core/rulebook.md")
        self.assertEqual(doc["document_type"], "core-rules")
        self.assertEqual(doc["text"], "Fear the dark.")
        self.assertEqual(doc["setting"], "demo-setting")
        self.assertIsNone(doc["world_category"])
        for key in ("system", "edition", "page_count", "extraction_method"):
            self.assertIn(key, doc)


class EndToEndBuildTests(unittest.TestCase):
    def test_full_build_produces_every_index_file(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        summary = sb.run(setting_dir)

        self.assertTrue(summary["corpus"]["built"])
        index_dir = setting_dir / "index"
        for name in (
            "catalogue.json",
            "gap_report.json",
            "documents.json",
            "nouns.json",
            "terms.json",
            "tables.json",
            "corpus_build_cache.json",
        ):
            self.assertTrue((index_dir / name).exists(), f"missing {name}")

        documents = json.loads((index_dir / "documents.json").read_text())
        catalogue = json.loads((index_dir / "catalogue.json").read_text())
        present_paths = {r["path"] for r in catalogue["records"] if r["status"] == "present"}
        self.assertEqual({d["path"] for d in documents}, present_paths)


class IdempotenceTests(unittest.TestCase):
    def test_second_run_is_a_no_op(self):
        """The feature's own Definition of Done (epic #28): run twice, second run a no-op."""
        setting_dir = _copy_fixture(FIXTURES, "basic")
        sb.run(setting_dir)
        before = _snapshot_index(setting_dir)

        summary = sb.run(setting_dir)

        self.assertEqual(summary["processed"], [])
        self.assertEqual(summary["removed"], [])
        self.assertFalse(summary["corpus"]["built"])
        self.assertIsNotNone(summary["corpus"]["skipped_reason"])
        after = _snapshot_index(setting_dir)
        self.assertEqual(before, after, "second run must write byte-identical index/ contents")

    def test_cli_main_second_invocation_is_a_no_op(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        self.assertEqual(sb.main([str(setting_dir)]), 0)
        before = _snapshot_index(setting_dir)
        self.assertEqual(sb.main([str(setting_dir)]), 0)
        after = _snapshot_index(setting_dir)
        self.assertEqual(before, after)


class ChangeInvalidatesCacheTests(unittest.TestCase):
    def test_changed_file_triggers_rebuild_then_settles(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        sb.run(setting_dir)

        rulebook = setting_dir / "corpus" / "core" / "rulebook.txt"
        rulebook.write_text(rulebook.read_text() + "\nAn added sentence about dread.\n")

        summary = sb.run(setting_dir)
        self.assertTrue(summary["corpus"]["built"])

        before = _snapshot_index(setting_dir)
        summary_again = sb.run(setting_dir)
        self.assertFalse(summary_again["corpus"]["built"])
        after = _snapshot_index(setting_dir)
        self.assertEqual(before, after)


class ReportingTests(unittest.TestCase):
    def test_text_report_distinguishes_built_and_skipped(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        summary = sb.run(setting_dir)
        text = sb._format_text(summary)
        self.assertIn("Pass 0:", text)
        self.assertIn("Corpus indexes: built", text)

        summary2 = sb.run(setting_dir)
        text2 = sb._format_text(summary2)
        self.assertIn("Corpus indexes: skipped", text2)
        self.assertIn("no catalogue or corpus-index changes", text2)

    def test_json_report_carries_corpus_subobject(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        summary = sb.run(setting_dir)
        self.assertIn("corpus", summary)
        self.assertIn("built", summary["corpus"])
        self.assertIn("documents", summary["corpus"])
        self.assertIn("skipped_reason", summary["corpus"])
        self.assertIn("not_yet_extracted", summary["corpus"])

    def test_text_report_names_the_gap(self):
        setting_dir = _copy_fixture(FIXTURES, "partial_extraction")
        summary = sb.run(setting_dir)
        text = sb._format_text(summary)
        self.assertIn("Not yet extracted", text)
        self.assertIn("community/unextracted.md", text)


class WorldCategoryAlwaysNoneTests(unittest.TestCase):
    def test_document_still_contributes_to_terms(self):
        setting_dir = _copy_fixture(FIXTURES, "world_building")
        summary = sb.run(setting_dir)
        self.assertTrue(summary["corpus"]["built"])
        terms = json.loads((setting_dir / "index" / "terms.json").read_text())
        self.assertIn("fear", terms)


class CorpusPipelineErrorPropagationTests(unittest.TestCase):
    def test_error_is_propagated_and_nothing_partial_is_written(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        with mock.patch.object(
            sb.corpus_pipeline,
            "build_setting_corpus_indexes",
            side_effect=ValueError("duplicate document id"),
        ):
            with self.assertRaises(ValueError):
                sb.run(setting_dir)
        index_dir = setting_dir / "index"
        for name in ("documents.json", "nouns.json", "terms.json", "tables.json"):
            self.assertFalse((index_dir / name).exists(), f"{name} must not be written on error")

    def test_cli_exits_1_on_pipeline_error(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        with mock.patch.object(
            sb.corpus_pipeline,
            "build_setting_corpus_indexes",
            side_effect=ValueError("duplicate document id"),
        ):
            self.assertEqual(sb.main([str(setting_dir)]), 1)


class NoLibraryDirTests(unittest.TestCase):
    def test_missing_library_dir_exits_1(self):
        tmp = Path(tempfile.mkdtemp())
        self.assertEqual(sb.main([str(tmp)]), 1)


class NotYetExtractedTests(unittest.TestCase):
    def test_missing_corpus_file_is_reported_not_raised(self):
        setting_dir = _copy_fixture(FIXTURES, "partial_extraction")
        summary = sb.run(setting_dir)

        self.assertIn("community/unextracted.md", summary["corpus"]["not_yet_extracted"])
        documents = json.loads((setting_dir / "index" / "documents.json").read_text())
        paths = {d["path"] for d in documents}
        self.assertIn("core/rulebook.md", paths)
        self.assertNotIn("community/unextracted.md", paths)

    def test_extraction_appearing_later_triggers_rebuild_and_clears_the_gap(self):
        setting_dir = _copy_fixture(FIXTURES, "partial_extraction")
        sb.run(setting_dir)

        missing = setting_dir / "corpus" / "community" / "unextracted.txt"
        missing.parent.mkdir(parents=True, exist_ok=True)
        missing.write_text("Now extracted.", encoding="utf-8")

        summary = sb.run(setting_dir)
        self.assertTrue(summary["corpus"]["built"])
        self.assertEqual(summary["corpus"]["not_yet_extracted"], [])
        documents = json.loads((setting_dir / "index" / "documents.json").read_text())
        self.assertIn("community/unextracted.md", {d["path"] for d in documents})

    def test_extraction_disappearing_reverts_to_not_yet_extracted(self):
        setting_dir = _copy_fixture(FIXTURES, "basic")
        sb.run(setting_dir)

        (setting_dir / "corpus" / "core" / "rulebook.txt").unlink()

        summary = sb.run(setting_dir)
        self.assertIn("core/rulebook.md", summary["corpus"]["not_yet_extracted"])
        documents = json.loads((setting_dir / "index" / "documents.json").read_text())
        self.assertNotIn("core/rulebook.md", {d["path"] for d in documents})


class NonPresentRecordsExcludedTests(unittest.TestCase):
    def test_removed_and_unreadable_records_are_excluded(self):
        setting_dir = _copy_fixture(PASS0_FIXTURES, "basic")
        sb.run(setting_dir)

        removed_file = setting_dir / "library" / "miscellany.txt"
        removed_file.unlink()

        summary = sb.run(setting_dir)
        self.assertIn("miscellany.txt", summary["removed"])
        documents = json.loads((setting_dir / "index" / "documents.json").read_text())
        self.assertNotIn("miscellany.txt", {d["path"] for d in documents})


if __name__ == "__main__":
    unittest.main()
