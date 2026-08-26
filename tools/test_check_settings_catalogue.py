#!/usr/bin/env python3
"""Tests for tools/check_settings_catalogue.py.

stdlib unittest, no pytest (docs/design/20-tooling.md section 6). No network: the reader and the
drift computation are exercised against tools/fixtures/settings_catalogue.json.

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_settings_catalogue as check  # noqa: E402

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "settings_catalogue.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text())


class ParseCatalogueTests(unittest.TestCase):
    def test_reads_every_entry(self):
        raw = load_fixture()
        entries = check.parse_catalogue(raw["catalogue_text"])
        self.assertEqual([e["id"] for e in entries], ["alpha", "beta", "gone"])

    def test_reads_optional_group_field(self):
        raw = load_fixture()
        entries = check.parse_catalogue(raw["catalogue_text"])
        beta = next(e for e in entries if e["id"] == "beta")
        self.assertEqual(beta["group"], "shared-world")

    def test_entry_without_group_omits_it(self):
        raw = load_fixture()
        entries = check.parse_catalogue(raw["catalogue_text"])
        alpha = next(e for e in entries if e["id"] == "alpha")
        self.assertNotIn("group", alpha)

    def test_comments_and_blank_lines_ignored(self):
        text = "# header comment\nsettings:\n  # a comment inside the list\n  - id: x\n    repo: r\n"
        entries = check.parse_catalogue(text)
        self.assertEqual(entries, [{"id": "x", "repo": "r"}])

    def test_trailing_candidates_comment_does_not_leak_in(self):
        text = "settings:\n  - id: x\n    repo: r\n\n# Candidates, unstarted: Foo, Bar.\n"
        entries = check.parse_catalogue(text)
        self.assertEqual(entries, [{"id": "x", "repo": "r"}])


class ComputeDriftTests(unittest.TestCase):
    def setUp(self):
        raw = load_fixture()
        self.entries = check.parse_catalogue(raw["catalogue_text"])
        self.live = raw["live_repos"]

    def test_clean_when_everything_matches(self):
        drift = check.compute_drift(
            [e for e in self.entries if e["id"] != "gone"],
            ["wyrd-setting-alpha", "wyrd-setting-beta"],
        )
        self.assertTrue(drift["clean"])
        self.assertEqual(drift["missing_from_catalogue"], [])
        self.assertEqual(drift["dangling_catalogue_entries"], [])

    def test_live_repo_missing_from_catalogue_is_reported(self):
        drift = check.compute_drift(self.entries, self.live)
        self.assertIn("wyrd-setting-orphan", drift["missing_from_catalogue"])

    def test_dangling_catalogue_entry_is_reported(self):
        drift = check.compute_drift(self.entries, self.live)
        dangling_ids = [e["id"] for e in drift["dangling_catalogue_entries"]]
        self.assertEqual(dangling_ids, ["gone"])

    def test_drift_present_means_not_clean(self):
        drift = check.compute_drift(self.entries, self.live)
        self.assertFalse(drift["clean"])


if __name__ == "__main__":
    unittest.main()
