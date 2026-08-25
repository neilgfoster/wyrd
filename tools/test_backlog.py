#!/usr/bin/env python3
"""Tests for tools/backlog.py.

stdlib unittest, no pytest (design/07-tooling.md section 6). No network: the walk and the
parser are exercised against tools/fixtures/board.json, captured from the live board on
2026-08-25, plus small synthetic graphs for the cases the real board does not yet contain.

Run: python3 -m unittest discover -s tools -p 'test_*.py'
"""

from __future__ import annotations

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import backlog  # noqa: E402

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "board.json"


def load_fixture() -> tuple[dict[int, dict], dict[int, dict]]:
    """The captured board, plus the existence cache that keeps these tests off the network.

    `known_issue_numbers` records, for every number a `Depends on:` line references, whether
    that issue exists -- resolved once when the fixture was captured. Without it, checking a
    dependency on a CLOSED issue (#17 -> #15) would shell out to `gh` mid-test.
    """
    raw = json.loads(FIXTURE.read_text())
    issues = {
        int(n): {**i, "labels": set(i["labels"])} for n, i in raw["issues"].items()
    }
    board = {int(n): b for n, b in raw["board"].items()}
    backlog._exists_cache.update(
        {int(n): exists for n, exists in raw.get("known_issue_numbers", {}).items()}
    )
    return issues, board


def make_issue(number, *, title="t", parent=None, children=(), open_children=(),
               depends_on=(), labels=("kord-feature",)):
    return {
        "number": number,
        "title": title,
        "url": f"https://example.invalid/{number}",
        "labels": set(labels),
        "parent": parent,
        "children": list(children),
        "open_children": list(open_children),
        "depends_on": list(depends_on),
        "is_epic": "kord-epic" in labels,
    }


class TestDependsOnParser(unittest.TestCase):
    """The parser must read declarations and ignore prose. See research.md section 2."""

    def test_bare_first_line(self):
        self.assertEqual(backlog.parse_depends_on("Depends on: #5\n\nBody"), [5])

    def test_comma_separated_list(self):
        body = "Depends on: #5, #6, #7, #8, #9"
        self.assertEqual(backlog.parse_depends_on(body), [5, 6, 7, 8, 9])

    def test_bullet_form(self):
        body = "## Notes\n\n- Depends on: #15 (table conventions)\n"
        self.assertEqual(backlog.parse_depends_on(body), [15])

    def test_bold_form(self):
        self.assertEqual(backlog.parse_depends_on("- **Depends on #11.**"), [])
        self.assertEqual(backlog.parse_depends_on("- **Depends on:** #11"), [11])

    def test_prose_is_not_a_declaration(self):
        """The #11 trap.

        #11's body says R1.8 (the mob rule) depends on IT. Matching the word anywhere would
        record #11 as depending on #13 -- the exact inverse, since #13 declares Depends on:
        #11. Getting this backwards would make the tool recommend blocked work.
        """
        body = (
            "- R1.8 (the mob rule) depends on this landing: petty and weaker only mean\n"
            "  something once an exchange has a turn order.\n"
            "- [ ] R1.8 (mob rule) has the turn-order footing it depends on.\n"
        )
        self.assertEqual(backlog.parse_depends_on(body), [])

    def test_prose_mentioning_a_number_is_not_a_declaration(self):
        body = "R1.2 (Stamina recovery) depends on the Aftermath table #16 landing here."
        self.assertEqual(backlog.parse_depends_on(body), [])

    def test_duplicates_collapse(self):
        self.assertEqual(backlog.parse_depends_on("Depends on: #5, #5, #6"), [5, 6])

    def test_empty_body(self):
        self.assertEqual(backlog.parse_depends_on(""), [])


class TestOpenBlockers(unittest.TestCase):
    def test_closed_dependency_is_satisfied(self):
        """`issues` holds only open issues, so an absent number is closed."""
        issues = {1: make_issue(1, depends_on=[99])}
        self.assertEqual(backlog.open_blockers(issues[1], issues), [])

    def test_open_dependency_blocks(self):
        issues = {1: make_issue(1, depends_on=[2]), 2: make_issue(2)}
        self.assertEqual(backlog.open_blockers(issues[1], issues), [2])


class TestSortKey(unittest.TestCase):
    def test_rank_ascending(self):
        board = {1: {"rank": 20}, 2: {"rank": 10}}
        self.assertEqual(sorted([1, 2], key=lambda n: backlog.sort_key(n, board)), [2, 1])

    def test_unranked_sorts_last(self):
        board = {1: {"rank": None}, 2: {"rank": 999}}
        self.assertEqual(sorted([1, 2], key=lambda n: backlog.sort_key(n, board)), [2, 1])

    def test_number_breaks_ties_so_the_walk_is_reproducible(self):
        board = {7: {"rank": 10}, 3: {"rank": 10}}
        self.assertEqual(sorted([7, 3], key=lambda n: backlog.sort_key(n, board)), [3, 7])


class TestWalk(unittest.TestCase):
    def test_descends_to_a_leaf_not_the_epic(self):
        """An epic is never the answer; the answer is something you can start."""
        issues = {
            1: make_issue(1, title="epic", children=[2], open_children=[2],
                          labels=("kord-epic",)),
            2: make_issue(2, title="leaf", parent=1),
        }
        board = {1: {"rank": 10}}
        chosen, blocked = backlog.walk(issues, board)
        self.assertEqual(chosen["number"], 2)
        self.assertEqual(chosen["path"], [1, 2])
        self.assertEqual(blocked, [])

    def test_dependency_beats_priority(self):
        """FR-3. The top-ranked root's only leaf is blocked, so a lower-ranked root wins."""
        issues = {
            1: make_issue(1, title="urgent", children=[2], open_children=[2],
                          labels=("kord-epic",)),
            2: make_issue(2, title="blocked leaf", parent=1, depends_on=[9]),
            9: make_issue(9, title="the blocker"),
            5: make_issue(5, title="lower priority", labels=("kord-epic",)),
        }
        board = {1: {"rank": 10}, 5: {"rank": 20}, 9: {"rank": None}}
        chosen, blocked = backlog.walk(issues, board)
        self.assertEqual(chosen["number"], 5)
        self.assertEqual([b["number"] for b in blocked], [2])
        self.assertEqual(blocked[0]["blocked_by"], [9])

    def test_blocked_items_are_reported_not_dropped(self):
        """A skipped item has to explain itself, or the answer is unauditable."""
        issues = {
            1: make_issue(1, children=[2, 3], open_children=[2, 3], labels=("kord-epic",)),
            2: make_issue(2, title="blocked", parent=1, depends_on=[9]),
            3: make_issue(3, title="ready", parent=1),
            9: make_issue(9),
        }
        board = {1: {"rank": 10}}
        chosen, blocked = backlog.walk(issues, board)
        self.assertEqual(chosen["number"], 3)
        self.assertEqual([b["number"] for b in blocked], [2])

    def test_nothing_ready_returns_none(self):
        """The blocker is a kord-task, so it is not itself a root the walk could fall to."""
        issues = {
            1: make_issue(1, children=[2], open_children=[2], labels=("kord-epic",)),
            2: make_issue(2, parent=1, depends_on=[9]),
            9: make_issue(9, labels=("kord-task",)),
        }
        board = {1: {"rank": 10}}
        chosen, blocked = backlog.walk(issues, board)
        self.assertIsNone(chosen)
        self.assertEqual([b["number"] for b in blocked], [2])

    def test_a_cycle_blocks_both_sides_rather_than_looping(self):
        """Two children declaring a dependency on each other must terminate, not recurse."""
        issues = {
            1: make_issue(1, children=[2, 3], open_children=[2, 3], labels=("kord-epic",)),
            2: make_issue(2, parent=1, depends_on=[3]),
            3: make_issue(3, parent=1, depends_on=[2]),
        }
        chosen, blocked = backlog.walk(issues, {1: {"rank": 10}})
        self.assertIsNone(chosen)
        self.assertEqual(sorted(b["number"] for b in blocked), [2, 3])

    def test_children_are_visited_in_rank_then_number_order(self):
        issues = {
            1: make_issue(1, children=[5, 3], open_children=[5, 3], labels=("kord-epic",)),
            3: make_issue(3, parent=1),
            5: make_issue(5, parent=1),
        }
        # Neither child is ranked, so the issue number decides -- reproducibly.
        chosen, _ = backlog.walk(issues, {1: {"rank": 10}})
        self.assertEqual(chosen["number"], 3)

    def test_walk_is_deterministic(self):
        issues, board = load_fixture()
        first, _ = backlog.walk(issues, board)
        second, _ = backlog.walk(issues, board)
        self.assertEqual(first, second)


class TestAgainstCapturedBoard(unittest.TestCase):
    """The real graph, as of 2026-08-25. These assert the shape, not the seeded order."""

    def setUp(self):
        self.issues, self.board = load_fixture()

    def test_roots_are_the_five_unparented_issues(self):
        self.assertEqual(sorted(backlog.roots(self.issues)), [1, 2, 3, 4, 24])

    def test_issue_17_through_21_are_not_roots(self):
        """Issue #24's own body claimed they were. They are children of #6."""
        for number in (17, 18, 19, 20, 21):
            self.assertEqual(self.issues[number]["parent"], 6)

    def test_declared_dependencies_match_the_board(self):
        self.assertEqual(self.issues[9]["depends_on"], [5])
        self.assertEqual(self.issues[10]["depends_on"], [6])
        self.assertEqual(self.issues[12]["depends_on"], [5])
        self.assertEqual(self.issues[13]["depends_on"], [11])
        self.assertEqual(self.issues[17]["depends_on"], [15])

    def test_11_does_not_depend_on_13(self):
        """The inversion the prose invites. #13 depends on #11, never the reverse."""
        self.assertEqual(self.issues[11]["depends_on"], [])
        self.assertEqual(self.issues[13]["depends_on"], [11])

    def test_17_is_ready_because_15_is_closed(self):
        """#15 merged, so a declared dependency on it no longer blocks."""
        self.assertNotIn(15, self.issues)
        self.assertEqual(backlog.open_blockers(self.issues[17], self.issues), [])

    def test_next_is_a_ready_leaf_under_the_top_ranked_root(self):
        chosen, _ = backlog.walk(self.issues, self.board)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen["path"][0], 1)
        self.assertEqual(self.issues[chosen["number"]]["open_children"], [])
        self.assertEqual(backlog.open_blockers(self.issues[chosen["number"]], self.issues), [])

    def test_every_root_is_ranked(self):
        for number in backlog.roots(self.issues):
            self.assertIsNotNone(
                self.board.get(number, {}).get("rank"),
                f"#{number} has no rank",
            )

    def test_ranks_are_unique(self):
        ranks = [self.board[n]["rank"] for n in backlog.roots(self.issues)]
        self.assertEqual(len(ranks), len(set(ranks)))


class TestDriftDetection(unittest.TestCase):
    """FR-4, exercised through find_problems itself.

    These call the real function rather than restating its logic, because a drift guard whose
    tests reimplement it cannot fail when it is wrong -- the fault fixed in 8864357.
    """

    def problems(self, issues, board):
        return backlog.find_problems(issues, board)

    def test_healthy_board_reports_nothing(self):
        issues, board = load_fixture()
        self.assertEqual(self.problems(issues, board), [])

    def test_unranked_root_is_caught(self):
        issues, board = load_fixture()
        board[2] = {**board[2], "rank": None}
        found = self.problems(issues, board)
        self.assertTrue(any("#2" in p and "no Rank" in p for p in found), found)

    def test_duplicate_rank_is_caught(self):
        issues, board = load_fixture()
        board[2] = {**board[2], "rank": board[1]["rank"]}
        found = self.problems(issues, board)
        self.assertTrue(any("shared by #1, #2" in p for p in found), found)

    def test_issue_missing_from_the_board_is_caught(self):
        """The kord-feature-create hole -- #24 was itself missing when this was built."""
        issues, board = load_fixture()
        del board[24]
        found = self.problems(issues, board)
        self.assertTrue(any("#24" in p and "not on the board" in p for p in found), found)

    def test_dangling_dependency_is_caught(self):
        """A typo'd number is absent from the OPEN set, so it otherwise reads as satisfied."""
        issues, board = load_fixture()
        issues[7] = {**issues[7], "depends_on": [9999]}
        # open_blockers sees nothing wrong -- that is the whole danger.
        self.assertEqual(backlog.open_blockers(issues[7], issues), [])
        backlog._exists_cache[9999] = False  # stand in for the `gh` lookup
        try:
            found = self.problems(issues, board)
        finally:
            backlog._exists_cache.pop(9999, None)
        self.assertTrue(any("#9999 does not exist" in p for p in found), found)

    def test_closed_dependency_is_not_reported_as_dangling(self):
        """#17 depends on #15, which is closed and merged. That is healthy, not drift."""
        issues, board = load_fixture()
        self.assertNotIn(15, issues)          # closed, so absent from the open set
        self.assertTrue(backlog._exists_cache[15])  # but it does exist
        self.assertEqual(self.problems(issues, board), [])

    def test_a_kord_task_is_not_expected_on_the_board(self):
        """Only epics and features are backlog items; tasks live inside a feature."""
        issues, board = load_fixture()
        issues[500] = {
            "number": 500, "title": "a task", "url": "", "labels": {"kord-task"},
            "parent": 7, "children": [], "open_children": [], "depends_on": [],
            "is_epic": False,
        }
        self.assertEqual(self.problems(issues, board), [])


if __name__ == "__main__":
    unittest.main()
