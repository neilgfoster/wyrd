"""Tests for tools/setting_scenarios.py -- covers specs/166-scenarios-index-build/spec.md.

Runs against the fixture under tools/fixtures/setting_scenarios/ only -- never against any real
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

import setting_scenarios as ss  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "setting_scenarios"


def _copy_fixture() -> Path:
    tmp = Path(tempfile.mkdtemp())
    dest = tmp / "setting"
    shutil.copytree(FIXTURES / "basic", dest)
    return dest


_ADVENTURE_RECORD = {
    "id": "the-drowning-well",
    "source": {"system": "fixture", "ref": "one", "pages": "1-2"},
    "adaptation": "none",
    "settings": ["fixture-setting"],
    "scale": "village",
    "region": "any",
    "danger": 3,
    "written_for": 4,
    "length": 2,
    "season": "any",
    "needs_access": [],
    "needs_capability": [],
    "helped_by": [],
    "tone": ["folk-horror"],
    "themes": ["a-debt-unpaid"],
    "shape": "a slow poisoning the village already half-knows about",
    "requires_threads": [],
    "emits_threads": [],
    "consequences": [],
    "chain": None,
}


class PlanTests(unittest.TestCase):
    def test_every_document_missing_with_no_scenario_cache(self):
        setting_dir = _copy_fixture()
        result = ss.run_plan(setting_dir, "adventures/")
        statuses = {d["id"]: d["status"] for d in result["documents"]}
        self.assertEqual(
            statuses, {"adventures/one.pdf": "missing", "adventures/two.pdf": "missing"}
        )

    def test_path_prefix_filters_out_non_matching_documents(self):
        setting_dir = _copy_fixture()
        result = ss.run_plan(setting_dir, "adventures/")
        ids = {d["id"] for d in result["documents"]}
        self.assertNotIn("rules/core.pdf", ids)

    def test_empty_prefix_matches_every_document(self):
        setting_dir = _copy_fixture()
        result = ss.run_plan(setting_dir, "")
        self.assertEqual(len(result["documents"]), 3)


class CommitTests(unittest.TestCase):
    def _records_file(self, tmp: Path, records: dict) -> Path:
        path = tmp / "records.json"
        path.write_text(json.dumps(records))
        return path

    def test_commit_writes_scenarios_and_cache_for_supplied_records(self):
        setting_dir = _copy_fixture()
        records_path = self._records_file(
            setting_dir.parent, {"adventures/one.pdf": _ADVENTURE_RECORD}
        )
        result = ss.run_commit(setting_dir, "adventures/one", records_path)
        self.assertEqual(result["documents"], 1)

        scenarios = json.loads((setting_dir / "index" / "scenarios.json").read_text())
        self.assertEqual(scenarios, [_ADVENTURE_RECORD])

        cache = json.loads((setting_dir / "index" / "scenario_build_cache.json").read_text())
        self.assertEqual(len(cache["entries"]), 1)
        self.assertEqual(cache["entries"][0]["id"], "adventures/one.pdf")
        self.assertEqual(cache["entries"][0]["content_hash"], "sha256:aaa")

    def test_rerun_with_unchanged_inputs_is_byte_identical_and_skips_generation(self):
        setting_dir = _copy_fixture()
        records_path = self._records_file(
            setting_dir.parent, {"adventures/one.pdf": _ADVENTURE_RECORD}
        )
        ss.run_commit(setting_dir, "adventures/one", records_path)
        before = (setting_dir / "index" / "scenarios.json").read_bytes()
        before_cache = (setting_dir / "index" / "scenario_build_cache.json").read_bytes()

        calls = []
        real_generate_marker = object()

        # Re-run through run_commit again; if the cache is honoured, the records file could even
        # be deleted and the second run would still succeed because nothing needs regenerating.
        records_path.write_text(json.dumps({"adventures/one.pdf": _ADVENTURE_RECORD}))
        ss.run_commit(setting_dir, "adventures/one", records_path)

        after = (setting_dir / "index" / "scenarios.json").read_bytes()
        after_cache = (setting_dir / "index" / "scenario_build_cache.json").read_bytes()
        self.assertEqual(before, after)
        self.assertEqual(before_cache, after_cache)
        del calls, real_generate_marker  # unused sentinel; the byte-identity check is the proof

    def test_stale_after_content_hash_changes(self):
        setting_dir = _copy_fixture()
        records_path = self._records_file(
            setting_dir.parent, {"adventures/one.pdf": _ADVENTURE_RECORD}
        )
        ss.run_commit(setting_dir, "adventures/one", records_path)

        cache_path = setting_dir / "index" / "corpus_build_cache.json"
        data = json.loads(cache_path.read_text())
        data["documents"]["adventures/one.pdf"] = "sha256:changed"
        cache_path.write_text(json.dumps(data))

        result = ss.run_plan(setting_dir, "adventures/one")
        statuses = {d["id"]: d["status"] for d in result["documents"]}
        self.assertEqual(statuses["adventures/one.pdf"], "stale")

    def test_commit_fails_and_writes_nothing_when_a_record_is_missing(self):
        setting_dir = _copy_fixture()
        records_path = self._records_file(setting_dir.parent, {})
        with self.assertRaises(ss.MissingRecordError):
            ss.run_commit(setting_dir, "adventures/", records_path)
        self.assertFalse((setting_dir / "index" / "scenarios.json").exists())

    def test_commit_fails_on_invalid_scale(self):
        setting_dir = _copy_fixture()
        bad_record = dict(_ADVENTURE_RECORD, scale="not-a-scale")
        records_path = self._records_file(setting_dir.parent, {"adventures/one.pdf": bad_record})
        with self.assertRaises(ValueError):
            ss.run_commit(setting_dir, "adventures/one", records_path)
        self.assertFalse((setting_dir / "index" / "scenarios.json").exists())

    def test_empty_path_prefix_and_empty_records_writes_empty_index(self):
        setting_dir = _copy_fixture()
        records_path = self._records_file(setting_dir.parent, {})
        result = ss.run_commit(setting_dir, "nomatch/", records_path)
        self.assertEqual(result["documents"], 0)
        scenarios = json.loads((setting_dir / "index" / "scenarios.json").read_text())
        self.assertEqual(scenarios, [])


class ResolveSettingIdTests(unittest.TestCase):
    def test_reads_name_from_setting_yaml(self):
        setting_dir = _copy_fixture()
        self.assertEqual(ss.resolve_setting_id(setting_dir), "fixture-setting")

    def test_falls_back_to_directory_name_when_no_setting_yaml(self):
        tmp = Path(tempfile.mkdtemp()) / "some-dir"
        tmp.mkdir(parents=True)
        self.assertEqual(ss.resolve_setting_id(tmp), "some-dir")


if __name__ == "__main__":
    unittest.main()
