#!/usr/bin/env python3
"""Tests for tools/check_docs.py.

stdlib unittest, no pytest (doc/design/07-tooling.md section 6). No fixtures on disk: each failure
class is built in a temporary tree, so the tests exercise the real check functions rather than
restating their logic. A guard whose tests reimplement it cannot fail when it is wrong -- a
fault already fixed twice in this repo (8864357, and the rank check in #60).

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import check_docs  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parent.parent


class TreeCase(unittest.TestCase):
    """A scratch repo, built file by file so each test states exactly what it is testing."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, rel: str, text: str) -> pathlib.Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def problems(self):
        return [str(p) for p in check_docs.find_problems(self.root)]


class TestReachability(TreeCase):
    def test_linked_document_is_reachable(self):
        self.write("README.md", "[rules](doc/design/03-rules.md)")
        self.write("doc/design/03-rules.md", "# Rules")
        self.assertEqual(self.problems(), [])

    def test_orphan_design_document_is_caught(self):
        self.write("README.md", "[rules](doc/design/03-rules.md)")
        self.write("doc/design/03-rules.md", "# Rules")
        self.write("doc/design/04-session.md", "# Session")
        found = self.problems()
        self.assertTrue(any("04-session.md is not reachable" in p for p in found), found)

    def test_reachability_is_transitive(self):
        """Two hops. This is how the decision records are reached."""
        self.write("README.md", "[index](doc/README.md)")
        self.write("doc/README.md", "[a record](adr/0001-x.md)")
        self.write("doc/adr/0001-x.md", "# A record")
        self.assertEqual([p for p in self.problems() if "reachable" in p], [])

    def test_directory_link_does_not_reach_its_contents(self):
        """Linking a folder is not linking what is in it.

        This is precisely why doc/README.md's record index is load-bearing: README links
        the adr/ directory, and that alone must not count as reaching each record.
        """
        self.write("README.md", "[records](doc/adr/)")
        self.write("doc/adr/0001-x.md", "# A record")
        found = self.problems()
        self.assertTrue(any("0001-x.md is not reachable" in p for p in found), found)

    def test_specs_are_exempt_from_reachability(self):
        """A spec records one past change; requiring an index entry each would be noise."""
        self.write("README.md", "# Wyrd")
        self.write("specs/001-thing/spec.md", "# Spec")
        self.assertEqual(self.problems(), [])

    def test_anchor_is_stripped_before_resolving(self):
        self.write("README.md", "[rules](doc/design/03-rules.md#resolution)")
        self.write("doc/design/03-rules.md", "# Rules")
        self.assertEqual(self.problems(), [])


class TestDeadLinks(TreeCase):
    def test_missing_target_is_caught(self):
        """The real instance: README linked playtest/, which did not exist."""
        self.write("README.md", "Findings are in [playtest/](playtest/).")
        found = self.problems()
        self.assertTrue(any("playtest/" in p and "does not exist" in p for p in found), found)

    def test_external_links_are_not_checked(self):
        self.write("README.md", "[site](https://example.invalid) [mail](mailto:a@b.c)")
        self.assertEqual(self.problems(), [])

    def test_dead_link_inside_specs_is_still_caught(self):
        """specs/ is exempt from reachability, never from link rot."""
        self.write("README.md", "# Wyrd")
        self.write("specs/001-thing/spec.md", "[gone](../../nowhere.md)")
        found = self.problems()
        self.assertTrue(any("nowhere.md" in p for p in found), found)


class TestAdrIndex(TreeCase):
    def test_unindexed_record_is_caught(self):
        """The real instance: the index stopped at 0008 while 0009 and 0010 existed."""
        self.write("README.md", "[index](doc/README.md)")
        self.write("doc/README.md", "[0008](adr/0008-a.md)")
        self.write("doc/adr/0008-a.md", "# 8")
        self.write("doc/adr/0009-b.md", "# 9")
        found = self.problems()
        self.assertTrue(any("0009-b.md is not listed" in p for p in found), found)

    def test_fully_indexed_passes(self):
        self.write("README.md", "[index](doc/README.md)")
        self.write("doc/README.md", "[0008](adr/0008-a.md) [0009](adr/0009-b.md)")
        self.write("doc/adr/0008-a.md", "# 8")
        self.write("doc/adr/0009-b.md", "# 9")
        self.assertEqual(self.problems(), [])


class TestAdrReferences(TreeCase):
    """Prose references, which the link check cannot see. See ADR 0012."""

    def scaffold(self):
        self.write("README.md", "[index](doc/README.md)")
        self.write("doc/README.md", "[0005](adr/0005-determinism.md)")
        self.write("doc/adr/0005-determinism.md", "# 5")

    def test_reference_to_an_existing_record_passes(self):
        self.scaffold()
        self.write("doc/design/03-rules.md", "Computed rather than inferred (ADR 0005).")
        self.write("doc/README.md", "[0005](adr/0005-determinism.md) [rules](design/03-rules.md)")
        self.assertEqual(self.problems(), [])

    def test_reference_to_a_missing_record_is_caught(self):
        """What renumbering breaks, and what nothing noticed before this check."""
        self.scaffold()
        self.write("doc/README.md",
                   "[0005](adr/0005-determinism.md) [rules](design/03-rules.md)")
        self.write("doc/design/03-rules.md", "As set out in ADR 0099.")
        found = self.problems()
        self.assertTrue(any("ADR 0099, which does not exist" in p for p in found), found)

    def test_a_superseded_record_still_satisfies_a_reference(self):
        """The archive keeps its numbers so old references keep resolving (ADR 0012)."""
        self.scaffold()
        self.write("doc/README.md",
                   "[0005](adr/0005-determinism.md) [rules](design/03-rules.md) "
                   "[archive](adr/superseded/README.md)")
        self.write("doc/adr/superseded/README.md", "[0003](0003-old.md)")
        self.write("doc/adr/superseded/0003-old.md", "# 3, superseded")
        self.write("doc/design/03-rules.md", "The earlier position was ADR 0003.")
        self.assertEqual(self.problems(), [])

    def test_absent_archive_is_not_an_error(self):
        """Nothing has been superseded yet; that must not fail the build."""
        self.scaffold()
        self.assertEqual(self.problems(), [])

    def test_archive_index_must_list_its_records(self):
        self.scaffold()
        self.write("doc/README.md",
                   "[0005](adr/0005-determinism.md) [archive](adr/superseded/README.md)")
        self.write("doc/adr/superseded/README.md", "nothing listed here")
        self.write("doc/adr/superseded/0003-old.md", "# 3")
        found = self.problems()
        self.assertTrue(any("0003-old.md is not listed" in p for p in found), found)

    def test_archive_readme_is_not_itself_treated_as_a_record(self):
        self.scaffold()
        self.write("doc/README.md",
                   "[0005](adr/0005-determinism.md) [archive](adr/superseded/README.md)")
        self.write("doc/adr/superseded/README.md", "*(none yet)*")
        self.assertEqual(self.problems(), [])


class TestLinkPolicy(TreeCase):
    def test_wikilink_in_prose_is_caught(self):
        self.write("README.md", "See [[03-rules]] for the ruleset.")
        found = self.problems()
        self.assertTrue(any("[[03-rules]]" in p and "in prose" in p for p in found), found)

    def test_wikilink_in_a_fenced_block_is_allowed(self):
        """doc/design/14-entities.md's YAML examples are full of these, legitimately."""
        self.write("README.md", "Entities link like this:\n\n```yaml\nparent: [[the-river-city]]\n```\n")
        self.assertEqual(self.problems(), [])

    def test_wikilink_in_an_inline_span_is_allowed(self):
        """07-tooling.md describes the convention as `[[wikilink]]` frontmatter."""
        self.write("README.md", "State is YAML with `[[wikilink]]` frontmatter.")
        self.assertEqual(self.problems(), [])

    def test_a_closed_fence_does_not_swallow_the_prose_after_it(self):
        self.write("README.md", "```\ncode\n```\nSee [[03-rules]].")
        found = self.problems()
        self.assertTrue(any("[[03-rules]]" in p for p in found), found)


class TestAgainstTheRealRepo(unittest.TestCase):
    """The repo as this branch leaves it must be clean, and must stay that way."""

    def test_repo_passes_all_checks(self):
        self.assertEqual([str(p) for p in check_docs.find_problems(REPO)], [])

    def test_every_design_document_is_reachable(self):
        seen = check_docs.reachable_from_hub(REPO)
        for path in (REPO / "doc" / "design").rglob("*.md"):
            self.assertIn(path.resolve(), seen, f"{path.name} unreachable from README")

    def test_every_adr_reference_in_the_repo_resolves(self):
        """All 11 prose references, checked. This is the renumbering mitigation."""
        self.assertEqual([str(p) for p in check_docs.check_adr_references(REPO)], [])

    def test_the_archive_exists_and_is_documented(self):
        archive = REPO / check_docs.ADR_ARCHIVE
        self.assertTrue(archive.is_dir(), "superseded/ must exist before a stage needs it")
        self.assertTrue((archive / "README.md").exists())

    def test_every_decision_record_is_indexed(self):
        index = (REPO / check_docs.ADR_INDEX).read_text(encoding="utf-8")
        records = sorted((REPO / check_docs.ADR_DIR).glob("*.md"))
        self.assertGreaterEqual(len(records), 11)
        for record in records:
            self.assertIn(record.name, index)


if __name__ == "__main__":
    unittest.main()
