#!/usr/bin/env python3
"""Tests for tools/fleet_rollout.py.

stdlib unittest, no pytest (design/07-tooling.md section 6). No network: pure logic
(YAML parsing, manifest validation, state computation, rollout planning) is exercised
directly against tools/fixtures/fleet.json and small synthetic dicts for the cases the
fixture does not cover, the same split tools/test_backlog.py uses. The two functions that
must talk to `gh` for real (`apply_rollout`'s git/PR mechanics) are exercised only via
specs/032-fleet-rollout/quickstart.md against a disposable repo, not here; the thin `gh`-
calling wrappers around them (`find_existing_rollout_pr`, `read_version_marker`'s error path)
are tested with `gh` itself mocked out, so no network call happens during the test run.

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import fleet_rollout as fr  # noqa: E402

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "fleet.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text())


def make_entry(entry_id, *, cls="additive", sha=None, add=None, migrate=None, summary="t"):
    entry = {
        "id": entry_id,
        "class": cls,
        "sha": sha or f"sha-{entry_id}",
        "summary": summary,
    }
    if cls == "additive":
        entry["add"] = add if add is not None else [f"setting/{entry_id}.md"]
    else:
        entry["migrate"] = migrate if migrate is not None else f"rollout/migrations/{entry_id}.md"
    return entry


class ParseSimpleYamlTests(unittest.TestCase):
    def test_flat_scalars(self):
        text = "template_source: wyrd-setting-template\ntemplate_sha: abc123\n"
        self.assertEqual(
            fr.parse_simple_yaml(text),
            {"template_source": "wyrd-setting-template", "template_sha": "abc123"},
        )

    def test_null_scalar(self):
        self.assertEqual(fr.parse_simple_yaml("diverged_at: null\n"), {"diverged_at": None})

    def test_quoted_scalar(self):
        self.assertEqual(
            fr.parse_simple_yaml('summary: "Add setting/voice.md skeleton"\n'),
            {"summary": "Add setting/voice.md skeleton"},
        )

    def test_list_under_key(self):
        text = "add:\n  - setting/voice.md\n  - setting/glossary.md\nmigrate: null\n"
        self.assertEqual(
            fr.parse_simple_yaml(text),
            {"add": ["setting/voice.md", "setting/glossary.md"], "migrate": None},
        )

    def test_comments_and_blank_lines_ignored(self):
        text = "# a comment\n\nid: 001-x\n"
        self.assertEqual(fr.parse_simple_yaml(text), {"id": "001-x"})

    def test_malformed_line_raises(self):
        with self.assertRaises(fr.YamlParseError):
            fr.parse_simple_yaml("not a key value line\n")

    def test_stray_list_item_raises(self):
        with self.assertRaises(fr.YamlParseError):
            fr.parse_simple_yaml("- stray\n")


class ValidateManifestEntryTests(unittest.TestCase):
    def test_valid_additive(self):
        entry = make_entry("001-add-voice-guide")
        self.assertEqual(fr.validate_manifest_entry(entry, "wyrd-setting-template"), entry)

    def test_valid_structural(self):
        entry = make_entry("002-rename-index-dir", cls="structural")
        self.assertEqual(fr.validate_manifest_entry(entry, "wyrd-setting-template"), entry)

    def test_forbidden_path_rejected(self):
        entry = make_entry("003-bad", add=["library/book.pdf"])
        with self.assertRaises(fr.ManifestError):
            fr.validate_manifest_entry(entry, "wyrd-setting-template")

    def test_additive_missing_add_rejected(self):
        entry = {"id": "004-x", "class": "additive", "sha": "s", "summary": "t"}
        with self.assertRaises(fr.ManifestError):
            fr.validate_manifest_entry(entry, "wyrd-setting-template")

    def test_structural_missing_migrate_rejected(self):
        entry = {"id": "005-x", "class": "structural", "sha": "s", "summary": "t"}
        with self.assertRaises(fr.ManifestError):
            fr.validate_manifest_entry(entry, "wyrd-setting-template")

    def test_unknown_class_rejected(self):
        entry = {"id": "006-x", "class": "tuning", "sha": "s", "summary": "t"}
        with self.assertRaises(fr.ManifestError):
            fr.validate_manifest_entry(entry, "wyrd-setting-template")

    def test_missing_id_rejected(self):
        entry = {"class": "additive", "sha": "s", "add": ["x"]}
        with self.assertRaises(fr.ManifestError):
            fr.validate_manifest_entry(entry, "wyrd-setting-template")


class SortManifestTests(unittest.TestCase):
    def test_orders_by_sequence_prefix(self):
        entries = [make_entry("003-c"), make_entry("001-a"), make_entry("002-b")]
        ordered = fr.sort_manifest(entries)
        self.assertEqual([e["id"] for e in ordered], ["001-a", "002-b", "003-c"])


class ComputeRepoStateTests(unittest.TestCase):
    def setUp(self):
        raw = load_fixture()
        self.manifest = fr.sort_manifest(
            [fr.validate_manifest_entry(dict(e), "wyrd-setting-template") for e in raw["manifest"]["wyrd-setting-template"]]
        )

    def test_current(self):
        marker = {"template_source": "wyrd-setting-template", "template_sha": self.manifest[-1]["sha"], "diverged_at": None}
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "current")
        self.assertEqual(state["missing"], [])

    def test_behind_names_missing_entries_in_order(self):
        marker = {"template_source": "wyrd-setting-template", "template_sha": self.manifest[0]["sha"], "diverged_at": None}
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "behind")
        self.assertEqual([e["id"] for e in state["missing"]], [self.manifest[1]["id"], self.manifest[2]["id"]])

    def test_unversioned(self):
        state = fr.compute_repo_state(fr.MARKER_ABSENT, self.manifest)
        self.assertEqual(state["state"], "unversioned")
        self.assertEqual(state["missing"], [])

    def test_unresolvable_sha(self):
        marker = {"template_source": "wyrd-setting-template", "template_sha": "0" * 40, "diverged_at": None}
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "unresolvable")
        self.assertEqual(state["missing"], [])

    def test_unreachable(self):
        state = fr.compute_repo_state(fr.MARKER_ABSENT, self.manifest, reachable=False)
        self.assertEqual(state["state"], "unreachable")

    def test_baseline_before_manifest_reports_everything_outstanding(self):
        marker = {"template_source": "wyrd-setting-template", "template_sha": None, "diverged_at": None}
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "behind")
        self.assertEqual(len(state["missing"]), 3)

    def test_diverged_at_only_outstanding_entry(self):
        # Recorded at entry [0]; diverged at the last entry means every remaining outstanding
        # entry is covered by the accepted divergence, so nothing is genuinely missing.
        marker = {
            "template_source": "wyrd-setting-template",
            "template_sha": self.manifest[0]["sha"],
            "diverged_at": self.manifest[-1]["id"],
        }
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "diverged")
        self.assertEqual(state["missing"], [])

    def test_diverged_does_not_exempt_later_entries(self):
        marker = {
            "template_source": "wyrd-setting-template",
            "template_sha": self.manifest[0]["sha"],
            "diverged_at": self.manifest[1]["id"],
        }
        state = fr.compute_repo_state(marker, self.manifest)
        self.assertEqual(state["state"], "behind")
        self.assertEqual([e["id"] for e in state["missing"]], [self.manifest[2]["id"]])


class PlanRolloutTests(unittest.TestCase):
    def setUp(self):
        self.additive = make_entry("001-a", cls="additive")
        self.structural = make_entry("002-b", cls="structural")
        self.manifest = fr.sort_manifest([self.additive, self.structural])

    def test_additive_only_bundle_names_every_path(self):
        marker = {"template_source": "s", "template_sha": None, "diverged_at": self.structural["id"]}
        # Diverge past the structural entry so only the additive one is outstanding.
        actions = fr.plan_rollout(marker, [self.additive])
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["class"], "additive")
        self.assertEqual(actions[0]["add"], self.additive["add"])

    def test_structural_entry_uses_migrate_not_raw_copy(self):
        marker = {"template_source": "s", "template_sha": None, "diverged_at": None}
        actions = fr.plan_rollout(marker, self.manifest)
        self.assertEqual([a["class"] for a in actions], ["additive", "structural"])
        self.assertEqual(actions[1]["migrate"], self.structural["migrate"])
        self.assertNotIn("add", actions[1])

    def test_current_repo_has_empty_plan(self):
        marker = {"template_source": "s", "template_sha": self.manifest[-1]["sha"], "diverged_at": None}
        self.assertEqual(fr.plan_rollout(marker, self.manifest), [])

    def test_diverged_repo_has_empty_plan(self):
        marker = {"template_source": "s", "template_sha": None, "diverged_at": self.manifest[-1]["id"]}
        self.assertEqual(fr.plan_rollout(marker, self.manifest), [])

    def test_plan_never_touches_forbidden_directories(self):
        # A manifest that passed validate_manifest_entry can never contain a forbidden path,
        # so the plan built from it can't either -- assert that invariant end to end.
        marker = {"template_source": "s", "template_sha": None, "diverged_at": None}
        actions = fr.plan_rollout(marker, self.manifest)
        for action in actions:
            for path in action.get("add", []):
                self.assertFalse(path.startswith(fr.FORBIDDEN_PATH_PREFIXES))


class FindExistingRolloutPrTests(unittest.TestCase):
    def test_returns_url_when_open_pr_exists(self):
        with mock.patch.object(fr, "gh", return_value=json.dumps([{"url": "https://example.invalid/pr/1"}])):
            url = fr.find_existing_rollout_pr("wyrd-setting-hemmelfurt", "003-add-glossary")
        self.assertEqual(url, "https://example.invalid/pr/1")

    def test_returns_none_when_no_open_pr(self):
        with mock.patch.object(fr, "gh", return_value="[]"):
            url = fr.find_existing_rollout_pr("wyrd-setting-hemmelfurt", "003-add-glossary")
        self.assertIsNone(url)


class FindClosedRolloutPrTests(unittest.TestCase):
    def test_returns_url_for_closed_unmerged_pr(self):
        raw = json.dumps([{"url": "https://example.invalid/pr/2", "mergedAt": None}])
        with mock.patch.object(fr, "gh", return_value=raw):
            url = fr.find_closed_rollout_pr("wyrd-setting-hemmelfurt", "003-add-glossary")
        self.assertEqual(url, "https://example.invalid/pr/2")

    def test_ignores_a_merged_pr(self):
        raw = json.dumps([{"url": "https://example.invalid/pr/2", "mergedAt": "2026-01-01T00:00:00Z"}])
        with mock.patch.object(fr, "gh", return_value=raw):
            url = fr.find_closed_rollout_pr("wyrd-setting-hemmelfurt", "003-add-glossary")
        self.assertIsNone(url)

    def test_returns_none_when_no_closed_pr(self):
        with mock.patch.object(fr, "gh", return_value="[]"):
            url = fr.find_closed_rollout_pr("wyrd-setting-hemmelfurt", "003-add-glossary")
        self.assertIsNone(url)


class ReadVersionMarkerTests(unittest.TestCase):
    def test_absent_on_404(self):
        with mock.patch.object(fr, "gh", side_effect=fr.GhError("gh api ... failed (1): HTTP 404: Not Found")):
            self.assertIs(fr.read_version_marker("wyrd-setting-new"), fr.MARKER_ABSENT)

    def test_other_gh_error_propagates(self):
        with mock.patch.object(fr, "gh", side_effect=fr.GhError("gh api ... failed (1): rate limit exceeded")):
            with self.assertRaises(fr.GhError):
                fr.read_version_marker("wyrd-setting-hemmelfurt")


class FleetDiscoveryTests(unittest.TestCase):
    def test_filters_to_known_prefixes_and_names(self):
        raw = load_fixture()["repos"]
        names = {r["name"] for r in fr.filter_fleet_repos(raw)}
        self.assertIn("wyrd-setting-template", names)
        self.assertIn("wyrd-setting-hemmelfurt", names)
        self.assertIn("wyrd-chronicle-template", names)
        self.assertNotIn("wyrd", names)
        self.assertNotIn("wyrd-chronicle-hemmelfurt", names)

    def test_archived_repo_kept_not_dropped(self):
        raw = load_fixture()["repos"]
        names = {r["name"] for r in fr.filter_fleet_repos(raw)}
        self.assertIn("wyrd-setting-renamed-away", names)


class FleetRepoRecordTests(unittest.TestCase):
    def test_shape_matches_data_model(self):
        raw = load_fixture()
        manifest = fr.sort_manifest(
            [fr.validate_manifest_entry(dict(e), "wyrd-setting-template") for e in raw["manifest"]["wyrd-setting-template"]]
        )
        marker = raw["markers"]["wyrd-setting-hemmelfurt"]
        repo = {"name": "wyrd-setting-hemmelfurt", "visibility": "PRIVATE"}
        record = fr.fleet_repo_record(repo, marker, manifest)
        self.assertEqual(record["repo"], "wyrd-setting-hemmelfurt")
        self.assertEqual(record["state"], "current")
        self.assertEqual(record["missing"], [])


if __name__ == "__main__":
    unittest.main()
