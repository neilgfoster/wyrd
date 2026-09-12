"""Tests for tools/setting_pass0.py -- covers every FR/SC in specs/147-.../spec.md.

Runs against fixture library trees under tools/fixtures/pass0/ only -- never against any real
wyrd-setting-* repository's content (CLAUDE.md's repository table).
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import setting_pass0 as pass0  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "pass0"


def _copy_fixture(name: str) -> Path:
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "setting"
    shutil.copytree(FIXTURES / name, dest)
    return dest


class ClassifyDocumentTests(unittest.TestCase):
    def test_classifies_every_file_in_basic_fixture(self):
        setting_dir = _copy_fixture("basic")
        catalogue, processed, removed = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        self.assertEqual(removed, [])
        kinds = {r.path: r.kind for r in catalogue.records.values()}
        self.assertEqual(kinds["core/rulebook.md"], "core-rules")
        self.assertEqual(kinds["expansions/monster-manual.md"], "expansion")
        self.assertEqual(kinds["community/house-fear-rules.md"], "community")
        self.assertEqual(kinds["scenarios/the-drowning-well.md"], "scenario")
        self.assertEqual(len(processed), 5)

    def test_unclassified_file_gets_lowest_tier(self):
        setting_dir = _copy_fixture("basic")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        record = catalogue.records["miscellany.txt"]
        self.assertEqual(record.kind, "unclassified")
        self.assertEqual(record.authority_tier, pass0.AUTHORITY_TIERS["unclassified"])
        self.assertEqual(
            record.authority_tier, max(pass0.AUTHORITY_TIERS.values()), "unclassified is lowest"
        )


class ProcessingOrderTests(unittest.TestCase):
    def test_higher_authority_precedes_lower(self):
        setting_dir = _copy_fixture("basic")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        ordered = pass0.processing_order(catalogue)
        tiers = [r.authority_tier for r in ordered]
        self.assertEqual(tiers, sorted(tiers), "processing order must be non-decreasing by tier")
        self.assertEqual(ordered[0].kind, "core-rules")
        self.assertEqual(ordered[-1].kind, "unclassified")


class GapReportTests(unittest.TestCase):
    def test_missing_requirements_are_named(self):
        setting_dir = _copy_fixture("basic")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        gaps = pass0.build_gap_report(catalogue)
        gap_ids = {g["requirement"] for g in gaps}
        self.assertIn("gear", gap_ids)  # nothing in the basic fixture provides gear
        for gap in gaps:
            self.assertTrue(gap["reason"])

    def test_full_coverage_produces_no_gaps(self):
        setting_dir = _copy_fixture("covers-requirements")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        gaps = pass0.build_gap_report(catalogue)
        self.assertEqual(gaps, [])

    def test_empty_library_reports_every_requirement_as_a_gap(self):
        setting_dir = _copy_fixture("empty")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        gaps = pass0.build_gap_report(catalogue)
        self.assertEqual({g["requirement"] for g in gaps}, set(pass0.SETTING_REQUIREMENTS))


class IdempotenceTests(unittest.TestCase):
    def test_second_run_with_no_changes_processes_nothing(self):
        setting_dir = _copy_fixture("basic")
        summary1 = pass0.run(setting_dir)
        self.assertGreater(len(summary1["processed"]), 0)
        catalogue_path = setting_dir / "index" / "catalogue.json"
        before = catalogue_path.read_text(encoding="utf-8")

        summary2 = pass0.run(setting_dir)
        self.assertEqual(summary2["processed"], [])
        self.assertEqual(summary2["removed"], [])
        after = catalogue_path.read_text(encoding="utf-8")
        self.assertEqual(before, after, "no-op re-run must not rewrite the catalogue")

    def test_changed_file_reprocesses_only_that_file(self):
        setting_dir = _copy_fixture("basic")
        pass0.run(setting_dir)
        before = json.loads((setting_dir / "index" / "catalogue.json").read_text())
        before_hashes = {r["path"]: r["content_hash"] for r in before["records"]}

        target = setting_dir / "library" / "core" / "rulebook.md"
        target.write_text(target.read_text() + "\nAn added line.\n", encoding="utf-8")

        summary = pass0.run(setting_dir)
        self.assertEqual(summary["processed"], ["core/rulebook.md"])

        after = json.loads((setting_dir / "index" / "catalogue.json").read_text())
        after_hashes = {r["path"]: r["content_hash"] for r in after["records"]}
        self.assertNotEqual(before_hashes["core/rulebook.md"], after_hashes["core/rulebook.md"])
        for path, hash_ in before_hashes.items():
            if path == "core/rulebook.md":
                continue
            self.assertEqual(after_hashes[path], hash_, f"{path} hash must be untouched")

    def test_new_file_processes_only_the_new_file(self):
        setting_dir = _copy_fixture("basic")
        pass0.run(setting_dir)

        new_file = setting_dir / "library" / "community" / "new-supplement.md"
        new_file.write_text("---\nkind: community\nprovides: []\n---\n\nNew.\n", encoding="utf-8")

        summary = pass0.run(setting_dir)
        self.assertEqual(summary["processed"], ["community/new-supplement.md"])


class RemovedFileTests(unittest.TestCase):
    def test_removed_file_is_marked_not_deleted(self):
        setting_dir = _copy_fixture("basic")
        pass0.run(setting_dir)

        removed_path = setting_dir / "library" / "scenarios" / "the-drowning-well.md"
        removed_path.unlink()

        summary = pass0.run(setting_dir)
        self.assertIn("scenarios/the-drowning-well.md", summary["removed"])

        catalogue = json.loads((setting_dir / "index" / "catalogue.json").read_text())
        record = next(
            r for r in catalogue["records"] if r["path"] == "scenarios/the-drowning-well.md"
        )
        self.assertEqual(record["status"], "removed")


class ConflictDetectionTests(unittest.TestCase):
    def test_conflict_names_both_documents_without_mutating_either(self):
        setting_dir = _copy_fixture("conflicting")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        conflicts = pass0.detect_conflicts(catalogue)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(
            set(conflicts[0]["documents"]), {"core/rulebook.md", "community/house-fear-rules.md"}
        )
        core = catalogue.records["core/rulebook.md"]
        community = catalogue.records["community/house-fear-rules.md"]
        self.assertEqual(core.kind, "core-rules")
        self.assertEqual(community.kind, "community")
        self.assertNotEqual(core.authority_tier, community.authority_tier)

    def test_basic_fixture_has_no_cross_tier_conflict(self):
        setting_dir = _copy_fixture("basic")
        catalogue, _, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))
        self.assertEqual(pass0.detect_conflicts(catalogue), [])


class UnreadableFileTests(unittest.TestCase):
    def test_unreadable_file_is_recorded_not_skipped(self):
        setting_dir = _copy_fixture("basic")
        target = str((setting_dir / "library" / "miscellany.txt").resolve())
        real_hash_file = pass0.hash_file

        def failing_hash_file(path):
            if str(path.resolve()) == target:
                raise OSError("simulated unreadable file")
            return real_hash_file(path)

        import unittest.mock as mock

        with mock.patch.object(pass0, "hash_file", side_effect=failing_hash_file):
            catalogue, processed, _ = pass0.build_catalogue(setting_dir, pass0.Catalogue("", {}))

        record = catalogue.records["miscellany.txt"]
        self.assertEqual(record.status, "unreadable")
        self.assertIn("miscellany.txt", processed)


class CliContractTests(unittest.TestCase):
    def test_missing_library_dir_exits_1(self):
        tmp = Path(tempfile.mkdtemp())
        exit_code = pass0.main([str(tmp)])
        self.assertEqual(exit_code, 1)

    def test_run_writes_documented_artefact_shapes(self):
        setting_dir = _copy_fixture("basic")
        exit_code = pass0.main([str(setting_dir), "--format", "json"])
        self.assertEqual(exit_code, 0)

        catalogue = json.loads((setting_dir / "index" / "catalogue.json").read_text())
        self.assertIn("generated_at", catalogue)
        self.assertIn("records", catalogue)
        record = catalogue["records"][0]
        for field_name in (
            "id",
            "path",
            "kind",
            "authority_tier",
            "subject",
            "content_hash",
            "status",
            "provides",
        ):
            self.assertIn(field_name, record)

        gap_report = json.loads((setting_dir / "index" / "gap_report.json").read_text())
        self.assertIn("gaps", gap_report)
        self.assertIn("conflicts", gap_report)


if __name__ == "__main__":
    unittest.main()
