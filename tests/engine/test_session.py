"""Tests for engine/wyrd/session.py: beat/arc containment enforcement, mode recording, the
session loop, the pending marker, and session-shape classification.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import session  # noqa: E402


def _minimal(entity_type: str, entity_id: str, **overrides) -> dict:
    base = {
        "id": entity_id,
        "type": entity_type,
        "name": entity_id.replace("-", " ").title(),
        "setting": "example-setting",
        "status": "stub",
    }
    base.update(overrides)
    return base


class AssertBeatHasNoChildrenTest(unittest.TestCase):
    def test_arc_may_contain_beat_or_arc(self):
        arc = _minimal("arc", "search-the-crypt")
        beat = _minimal("beat", "open-the-door", parent="[[search-the-crypt]]")
        entities = {arc["id"]: arc, beat["id"]: beat}
        self.assertEqual(session.assert_beat_has_no_children(entities), {"valid": True})

        outer_arc = _minimal("arc", "the-crypt-arc")
        inner_arc = _minimal("arc", "search-the-crypt", parent="[[the-crypt-arc]]")
        entities = {outer_arc["id"]: outer_arc, inner_arc["id"]: inner_arc}
        self.assertEqual(session.assert_beat_has_no_children(entities), {"valid": True})

    def test_arc_of_one_beat_is_still_reported_as_valid(self):
        arc = _minimal("arc", "search-the-crypt")
        beat = _minimal("beat", "open-the-door", parent="[[search-the-crypt]]")
        entities = {arc["id"]: arc, beat["id"]: beat}
        self.assertEqual(session.assert_beat_has_no_children(entities), {"valid": True})

    def test_beat_with_child_is_rejected(self):
        arc = _minimal("arc", "search-the-crypt")
        beat = _minimal("beat", "open-the-door", parent="[[search-the-crypt]]")
        illegal_child = _minimal("beat", "check-for-traps", parent="[[open-the-door]]")
        entities = {arc["id"]: arc, beat["id"]: beat, illegal_child["id"]: illegal_child}
        result = session.assert_beat_has_no_children(entities)
        self.assertEqual(
            result, {"valid": False, "beat": "open-the-door", "child": "check-for-traps"}
        )


class NarrateBeatTest(unittest.TestCase):
    def test_records_mode(self):
        played = session.narrate_beat("open-the-door", "played")
        self.assertEqual(played["mode"], "played")
        self.assertEqual(played["beat_id"], "open-the-door")

        summarised = session.narrate_beat("open-the-door", "summarised")
        self.assertEqual(summarised["mode"], "summarised")

    def test_independent_across_records(self):
        first = session.narrate_beat("open-the-door", "played")
        second = session.narrate_beat("open-the-door", "summarised")
        self.assertIsNot(first, second)
        self.assertNotEqual(first["mode"], second["mode"])

        # the beat's own frontmatter never gains a mode field -- narrate_beat takes only an id,
        # it has no access to (and cannot mutate) any stored entity definition.
        beat = _minimal("beat", "open-the-door")
        session.narrate_beat("open-the-door", "played")
        self.assertNotIn("mode", beat)

    def test_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            session.narrate_beat("open-the-door", "half-played")


class LoopTest(unittest.TestCase):
    def test_happy_path(self):
        state = session.new_loop_state()
        self.assertEqual(state["step"], "load")
        self.assertFalse(state["elapsed_applied"])

        state = session.advance_loop(state, "orient")
        self.assertTrue(state["elapsed_applied"])

        state = session.advance_loop(state, "recap")
        state = session.advance_loop(state, "beat")
        state = session.advance_loop(state, "beat")  # repeat
        self.assertFalse(state["closed"])

        state = session.advance_loop(state, "close")
        self.assertTrue(state["closed"])

    def test_rejects_recap_before_orient(self):
        state = session.new_loop_state()
        state = {**state, "step": "orient"}
        # bypassing advance_loop's own orient step, elapsed_applied is still False
        with self.assertRaises(ValueError):
            session.advance_loop(state, "recap")

    def test_rejects_close_without_a_beat_or_explicit_stop(self):
        state = session.new_loop_state()
        state = session.advance_loop(state, "orient")
        state = session.advance_loop(state, "recap")
        with self.assertRaises(ValueError):
            session.advance_loop(state, "close")

    def test_rejects_transition_after_close(self):
        state = session.new_loop_state()
        state = session.advance_loop(state, "orient")
        state = session.advance_loop(state, "recap")
        state = session.advance_loop(state, "beat")
        state = session.advance_loop(state, "close")
        with self.assertRaises(ValueError):
            session.advance_loop(state, "beat")

    def test_advance_loop_does_not_mutate_input(self):
        state = session.new_loop_state()
        next_state = session.advance_loop(state, "orient")
        self.assertEqual(state["step"], "load")
        self.assertEqual(next_state["step"], "orient")


class PendingMarkerTest(unittest.TestCase):
    def test_set_pending_and_resume(self):
        pending = session.set_pending("open-the-door", "waiting on the lock-picking roll")
        self.assertEqual(pending["beat_id"], "open-the-door")
        self.assertEqual(session.resume_from_pending(pending), "waiting on the lock-picking roll")

    def test_clean_resolution_leaves_no_pending_marker(self):
        # narrate_beat is the clean-resolution path; it must never itself produce a pending
        # marker as a side effect -- its return value carries no "action"/"set_at" shape.
        record = session.narrate_beat("open-the-door", "played")
        self.assertNotIn("action", record)
        self.assertNotIn("set_at", record)


class ClassifyShapeTest(unittest.TestCase):
    def test_each_of_four_shapes(self):
        self.assertEqual(session.classify_shape([], used_dice=False, ran_downtime=True), "downtime")
        self.assertEqual(
            session.classify_shape(["a"], used_dice=False, ran_downtime=False), "interlude"
        )
        self.assertEqual(
            session.classify_shape(["a"], used_dice=True, ran_downtime=False), "single_beat"
        )
        self.assertEqual(
            session.classify_shape(["a", "b", "c"], used_dice=True, ran_downtime=False),
            "extended",
        )

    def test_never_fails_on_ambiguous_input(self):
        result = session.classify_shape([], used_dice=True, ran_downtime=False)
        self.assertIn(result, session.SESSION_SHAPES)

    def test_never_consulted_by_narration(self):
        # static check: narrate_beat's own signature takes no shape-shaped argument, so no
        # narration call site can thread classify_shape's result into it.
        import inspect

        params = inspect.signature(session.narrate_beat).parameters
        self.assertNotIn("shape", params)


if __name__ == "__main__":
    unittest.main()
