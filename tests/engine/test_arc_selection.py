"""Tests for engine/wyrd/arc_selection.py: entry/exit schema and thread-matched selection.

stdlib unittest, no pytest (matches tests/engine/test_entity.py). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import arc_selection  # noqa: E402


def _beat(beat_id: str, **overrides) -> dict:
    base = {
        "id": beat_id,
        "type": "beat",
        "name": beat_id.title(),
        "setting": "example-setting",
        "status": "drafted",
    }
    base.update(overrides)
    return base


class ValidateEntryExitTests(unittest.TestCase):
    """User Story 1: a beat or arc declares what it needs and what it leaves behind."""

    def test_full_block_accepted(self):
        beat = _beat(
            "the-cut-page",
            entry={
                "requires_threads": ["records"],
                "requires_state": [],
                "hooks": ["the player asks about the ledger"],
            },
            exit={
                "emits_threads": [
                    {"tag": "the-hinge", "if": "the player character recalls the door"}
                ],
                "changes": ["the gap is public knowledge"],
                "leads_to": "[[the-tavern]]",
            },
        )
        self.assertEqual(arc_selection.validate_entry_exit(beat), {"valid": True})

    def test_absent_entry_exit_accepted(self):
        self.assertEqual(arc_selection.validate_entry_exit(_beat("a-stub")), {"valid": True})

    def test_entry_not_a_mapping_rejected(self):
        result = arc_selection.validate_entry_exit(_beat("bad", entry="not-a-mapping"))
        self.assertFalse(result["valid"])

    def test_entry_requires_threads_not_a_list_rejected(self):
        result = arc_selection.validate_entry_exit(
            _beat("bad", entry={"requires_threads": "records"})
        )
        self.assertFalse(result["valid"])
        self.assertIn("requires_threads", result["error"])

    def test_exit_emits_threads_missing_tag_rejected(self):
        result = arc_selection.validate_entry_exit(
            _beat("bad", exit={"emits_threads": [{"if": "something"}]})
        )
        self.assertFalse(result["valid"])
        self.assertIn("emits_threads", result["error"])

    def test_exit_leads_to_not_a_string_rejected(self):
        result = arc_selection.validate_entry_exit(_beat("bad", exit={"leads_to": 5}))
        self.assertFalse(result["valid"])
        self.assertIn("leads_to", result["error"])


class SelectThreadMatchTests(unittest.TestCase):
    """User Story 2: the engine picks the next beat by matching live threads."""

    def test_select_returns_matching_candidates(self):
        matched = _beat("matched", entry={"requires_threads": ["water"]})
        unmatched = _beat("unmatched", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(live_threads={"water"}, candidates=[matched, unmatched])
        self.assertEqual(result, [matched])

    def test_empty_requires_threads_always_eligible(self):
        candidate = _beat("no-requirement")
        result = arc_selection.select(live_threads=set(), candidates=[candidate])
        self.assertEqual(result, [candidate])

    def test_partial_match_excluded(self):
        candidate = _beat("needs-two", entry={"requires_threads": ["water", "sickness"]})
        result = arc_selection.select(live_threads={"water"}, candidates=[candidate])
        self.assertEqual(result, [])


class SelectLeadsToFallbackTests(unittest.TestCase):
    """User Story 3: leads_to is a fallback, never an equal-weight candidate source."""

    def test_thread_match_wins_over_leads_to(self):
        current = _beat("current", exit={"leads_to": "[[hinted]]"})
        matched = _beat("matched", entry={"requires_threads": ["water"]})
        hinted = _beat("hinted", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(
            live_threads={"water"}, candidates=[matched, hinted], current=current
        )
        self.assertEqual(result, [matched])

    def test_falls_back_to_leads_to(self):
        current = _beat("current", exit={"leads_to": "[[hinted]]"})
        hinted = _beat("hinted")
        unrelated = _beat("unrelated", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(
            live_threads=set(), candidates=[unrelated, hinted], current=current
        )
        self.assertEqual(result, [hinted])

    def test_no_match_returns_empty(self):
        current = _beat("current")
        unrelated = _beat("unrelated", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(live_threads=set(), candidates=[unrelated], current=current)
        self.assertEqual(result, [])

    def test_dangling_leads_to_returns_empty(self):
        current = _beat("current", exit={"leads_to": "[[nowhere]]"})
        unrelated = _beat("unrelated", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(live_threads=set(), candidates=[unrelated], current=current)
        self.assertEqual(result, [])


class SelectRecursionAndStubTests(unittest.TestCase):
    """User Story 4: selection works at every nesting level, including an undecomposed stub."""

    def test_stub_arc_selectable_without_children(self):
        stub_arc = {
            "id": "the-drowned-town",
            "type": "arc",
            "name": "The Drowned Town",
            "setting": "example-setting",
            "status": "stub",
            "entry": {"requires_threads": ["water"]},
        }
        decomposed_beat = _beat("a-beat", entry={"requires_threads": ["fire"]})
        result = arc_selection.select(
            live_threads={"water"}, candidates=[stub_arc, decomposed_beat]
        )
        self.assertEqual(result, [stub_arc])

    def test_does_not_descend_into_children(self):
        # select() only ever sees the flat pool it is given -- confirm a selected arc's own
        # frontmatter carries no expanded children, i.e. selection performs no recursion of its
        # own beyond the single candidate pool passed in.
        parent_arc = _beat("parent-arc", type="arc", entry={"requires_threads": ["water"]})
        child_beat = _beat("child-beat", entry={"requires_threads": ["water"]})
        result = arc_selection.select(live_threads={"water"}, candidates=[parent_arc, child_beat])
        self.assertEqual(result, [parent_arc, child_beat])
        self.assertNotIn("children", parent_arc)


if __name__ == "__main__":
    unittest.main()
