#!/usr/bin/env python3
"""Tests for tools/harvest_friction.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). The two GitHub-calling
functions (`gh api` reads, the `github-issue-dedup-check` shell-out) are exercised via injected
fakes -- no network call, no real kord installation required.

Run: python3 -m unittest discover -s tools -p 'test_harvest_friction.py'
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import harvest_friction as hf  # noqa: E402

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "friction"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class FakeProcess:
    """A stand-in for subprocess.CompletedProcess, for injected runners."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ParseFrictionLogTests(unittest.TestCase):
    def test_qualifying_entry_parses_all_three_fields(self):
        entries, malformed = hf.parse_friction_log(load_fixture("qualifying.md"), "chronicle-a")
        self.assertEqual(malformed, [])
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.mechanic, "opposed test resolution (03-rules.md §1)")
        self.assertIn("65% skill and a 40% skill", entry.what_happened)
        self.assertIn("played it as written", entry.what_gm_did)
        self.assertEqual(entry.source_repo, "chronicle-a")

    def test_malformed_entry_reports_missing_field(self):
        entries, malformed = hf.parse_friction_log(load_fixture("malformed.md"), "chronicle-a")
        self.assertEqual(entries, [])
        self.assertEqual(len(malformed), 1)
        self.assertIn("what the GM did", malformed[0].missing_fields)

    def test_no_entries_in_empty_text(self):
        entries, malformed = hf.parse_friction_log("", "chronicle-a")
        self.assertEqual(entries, [])
        self.assertEqual(malformed, [])


class ReadChronicleFrictionLogTests(unittest.TestCase):
    def test_missing_file_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = hf.read_chronicle_friction_log(tmp)
        self.assertIsNone(result)

    def test_reads_local_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_dir = pathlib.Path(tmp) / "log"
            log_dir.mkdir()
            content = load_fixture("qualifying.md")
            (log_dir / "friction.md").write_text(content, encoding="utf-8")
            result = hf.read_chronicle_friction_log(tmp)
        self.assertEqual(result, content)

    def test_gh_api_branch_returns_none_on_failure(self):
        def fake_runner(*args, **kwargs):
            return FakeProcess(returncode=1, stdout="", stderr="not found")

        result = hf.read_chronicle_friction_log("owner/repo", runner=fake_runner)
        self.assertIsNone(result)

    def test_gh_api_branch_decodes_content(self):
        import base64

        content = "- mechanic: x\n  what happened: y\n  what the GM did: z\n"
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")

        def fake_runner(*args, **kwargs):
            return FakeProcess(returncode=0, stdout=json.dumps({"content": encoded}))

        result = hf.read_chronicle_friction_log("owner/repo", runner=fake_runner)
        self.assertEqual(result, content)


class TriageTests(unittest.TestCase):
    def test_qualifying_example_from_design_doc(self):
        entry = hf.FrictionEntry(
            mechanic="opposed test resolution (03-rules.md §1)",
            what_happened=(
                "the difficulty table gave a result the GM had not expected for an opposed "
                "test between a 65% skill and a 40% skill"
            ),
            what_gm_did="played it as written, noted the surprise for review",
            source_repo="chronicle-a",
            raw_index=0,
        )
        verdict = hf.triage(entry)
        self.assertEqual(verdict.verdict, "qualifies")

    def test_non_qualifying_example_from_design_doc(self):
        entry = hf.FrictionEntry(
            mechanic="none",
            what_happened=(
                "the player described their character's coat catching on a nail on the way "
                "out the door"
            ),
            what_gm_did="narrated it and moved on",
            source_repo="chronicle-a",
            raw_index=0,
        )
        verdict = hf.triage(entry)
        self.assertEqual(verdict.verdict, "does_not_qualify")

    def test_ambiguous_entry_needs_review_not_silently_dropped(self):
        entry = hf.FrictionEntry(
            mechanic="companion behavior",
            what_happened="the companion did something nobody expected",
            what_gm_did="went with it",
            source_repo="chronicle-a",
            raw_index=0,
        )
        verdict = hf.triage(entry)
        self.assertEqual(verdict.verdict, "needs_review")


class BuildProposalTests(unittest.TestCase):
    def test_proposal_contains_only_source_fields(self):
        entry = hf.FrictionEntry(
            mechanic="opposed test resolution",
            what_happened="a 65% skill beat a 40% skill unexpectedly",
            what_gm_did="played it as written",
            source_repo="chronicle-a",
            raw_index=0,
        )
        proposal = hf.build_proposal([entry])
        self.assertIn(entry.mechanic, proposal.title)
        combined = proposal.title + "\n" + proposal.body
        # Narrative-leakage guard: nothing in the proposal besides the three source fields,
        # the literal scaffolding words, and the source_repo tag.
        allowed_words = set(
            (
                "Friction: Mechanic What happened the GM did Source "
                + entry.mechanic
                + " "
                + entry.what_happened
                + " "
                + entry.what_gm_did
                + " "
                + entry.source_repo
            )
            .replace(":", "")
            .replace("-", "")
            .split()
        )
        for word in combined.replace(":", "").replace("-", "").split():
            self.assertIn(word, allowed_words, f"unexpected word leaked into proposal: {word!r}")

    def test_multiple_entries_all_represented(self):
        entry_a = hf.FrictionEntry("m", "happened a", "did a", "chronicle-a", 0)
        entry_b = hf.FrictionEntry("m", "happened b", "did b", "chronicle-a", 1)
        proposal = hf.build_proposal([entry_a, entry_b])
        self.assertIn("happened a", proposal.body)
        self.assertIn("happened b", proposal.body)


class GroupQualifyingEntriesTests(unittest.TestCase):
    def test_same_mechanic_same_repo_merges(self):
        entry_a = hf.FrictionEntry("Opposed test", "happened a", "did a", "chronicle-a", 0)
        entry_b = hf.FrictionEntry("opposed   test", "happened b", "did b", "chronicle-a", 1)
        groups = hf.group_qualifying_entries([entry_a, entry_b])
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)

    def test_same_mechanic_different_repo_does_not_merge(self):
        entry_a = hf.FrictionEntry("opposed test", "happened a", "did a", "chronicle-a", 0)
        entry_b = hf.FrictionEntry("opposed test", "happened b", "did b", "chronicle-b", 0)
        groups = hf.group_qualifying_entries([entry_a, entry_b])
        self.assertEqual(len(groups), 2)


class CheckDuplicateTests(unittest.TestCase):
    def _proposal(self) -> hf.HarvestProposal:
        entry = hf.FrictionEntry("opposed test", "happened", "did", "chronicle-a", 0)
        return hf.build_proposal([entry])

    def test_match_reports_not_new(self):
        def fake_runner(*args, **kwargs):
            return FakeProcess(
                returncode=0,
                stdout=json.dumps({"match": {"number": 42, "url": "https://x/42", "title": "t"}}),
            )

        verdict = hf.check_duplicate(
            self._proposal(), runner=fake_runner, client_path=pathlib.Path(__file__)
        )
        self.assertFalse(verdict.is_new)
        self.assertEqual(verdict.matched_issue["number"], 42)

    def test_no_match_reports_new(self):
        def fake_runner(*args, **kwargs):
            return FakeProcess(returncode=0, stdout=json.dumps({"match": None}))

        verdict = hf.check_duplicate(
            self._proposal(), runner=fake_runner, client_path=pathlib.Path(__file__)
        )
        self.assertTrue(verdict.is_new)
        self.assertIsNone(verdict.matched_issue)

    def test_missing_client_fails_open_to_new(self):
        verdict = hf.check_duplicate(self._proposal(), client_path=pathlib.Path("/no/such/file"))
        self.assertTrue(verdict.is_new)


class HarvestChronicleEndToEndTests(unittest.TestCase):
    def test_missing_log_reports_nothing_without_error(self):
        report = hf.harvest_chronicle("chronicle-a", read=lambda _: None)
        self.assertEqual(report.new_proposals, [])
        self.assertEqual(report.duplicate_proposals, [])
        self.assertEqual(report.malformed_entries, [])

    def test_combined_fixture_buckets_correctly(self):
        combined = "\n".join(
            [
                load_fixture("qualifying.md"),
                load_fixture("color_only.md"),
                load_fixture("malformed.md"),
            ]
        )

        def fake_dedup_runner(*args, **kwargs):
            return FakeProcess(returncode=0, stdout=json.dumps({"match": None}))

        report = hf.harvest_chronicle(
            "chronicle-a",
            read=lambda _: combined,
            dedup_runner=fake_dedup_runner,
            dedup_client_path=pathlib.Path(__file__),
        )
        self.assertEqual(len(report.new_proposals), 1)
        self.assertEqual(len(report.duplicate_proposals), 0)
        self.assertEqual(len(report.non_qualifying_entries), 1)
        self.assertEqual(len(report.malformed_entries), 1)

    def test_duplicate_is_separated_from_new(self):
        def fake_dedup_runner(*args, **kwargs):
            return FakeProcess(
                returncode=0,
                stdout=json.dumps({"match": {"number": 7, "url": "https://x/7", "title": "t"}}),
            )

        report = hf.harvest_chronicle(
            "chronicle-a",
            read=lambda _: load_fixture("qualifying.md"),
            dedup_runner=fake_dedup_runner,
            dedup_client_path=pathlib.Path(__file__),
        )
        self.assertEqual(len(report.new_proposals), 0)
        self.assertEqual(len(report.duplicate_proposals), 1)


class MultiChronicleAttributionTests(unittest.TestCase):
    def test_two_chronicles_attributed_and_not_merged(self):
        def read(chronicle: str) -> str | None:
            if chronicle == "chronicle-a":
                return load_fixture("qualifying.md")
            return None

        def fake_dedup_runner(*args, **kwargs):
            return FakeProcess(returncode=0, stdout=json.dumps({"match": None}))

        report_a = hf.harvest_chronicle(
            "chronicle-a",
            read=read,
            dedup_runner=fake_dedup_runner,
            dedup_client_path=pathlib.Path(__file__),
        )
        report_b = hf.harvest_chronicle(
            "chronicle-b",
            read=read,
            dedup_runner=fake_dedup_runner,
            dedup_client_path=pathlib.Path(__file__),
        )
        self.assertEqual(len(report_a.new_proposals), 1)
        self.assertEqual(report_a.new_proposals[0].source_entries[0].source_repo, "chronicle-a")
        self.assertEqual(len(report_b.new_proposals), 0)


class FormatReportTests(unittest.TestCase):
    def test_empty_report_says_nothing_to_harvest(self):
        report = hf.HarvestReport(
            source_repo="chronicle-a",
            new_proposals=[],
            duplicate_proposals=[],
            malformed_entries=[],
            non_qualifying_entries=[],
            needs_review_entries=[],
        )
        text = hf.format_report(report)
        self.assertIn("nothing to harvest", text)


if __name__ == "__main__":
    unittest.main()
