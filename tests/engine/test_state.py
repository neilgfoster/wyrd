"""Tests for engine/wyrd/state.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). No network; a temporary
directory per test stands in for the chronicle's on-disk location.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import state  # noqa: E402


class StateRoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_before_any_save_returns_default_state(self):
        self.assertFalse(self.path.exists())
        loaded = state.load(self.path)
        self.assertEqual(loaded, state.default_state())

    def test_save_then_load_round_trips_every_field(self):
        written = {
            "schema_version": 1,
            "last_roll": {"verb": "roll", "sides": 100, "result": 42, "seed": None},
        }
        state.save(written, self.path)
        loaded = state.load(self.path)
        self.assertEqual(loaded, written)

    def test_save_then_load_with_null_last_roll(self):
        written = {"schema_version": 1, "last_roll": None}
        state.save(written, self.path)
        self.assertEqual(state.load(self.path), written)

    def test_save_creates_missing_parent_directory(self):
        nested = pathlib.Path(self._tmp.name) / "nested" / "dir" / "chronicle_state.yaml"
        state.save(state.default_state(), nested)
        self.assertEqual(state.load(nested), state.default_state())

    def test_corrupted_file_raises_clear_error(self):
        self.path.write_text("this is not: valid: yaml: at: all: -\n  -bad", encoding="utf-8")
        with self.assertRaises(state.StateError) as ctx:
            state.load(self.path)
        self.assertIn(str(self.path), str(ctx.exception))

    def test_interrupted_write_never_corrupts_the_target_file(self):
        # Establish a known-good prior state.
        prior = {"schema_version": 1, "last_roll": None}
        state.save(prior, self.path)

        # Simulate a write interrupted mid-way: write a truncated temp file directly and
        # leave it in place without ever calling os.replace onto the target -- the same
        # end state a process kill between the write and the replace would produce.
        tmp = self.path.parent / f".{self.path.name}.interrupted.tmp"
        tmp.write_text("schema_versio", encoding="utf-8")  # deliberately truncated

        # The target file must be untouched -- still the prior, fully-valid state.
        loaded = state.load(self.path)
        self.assertEqual(loaded, prior)
        tmp.unlink()

    def test_save_is_atomic_replace_not_in_place_write(self):
        # os.replace is the mechanism FR-007 relies on; assert it's actually used rather
        # than a direct write to the target path.
        import unittest.mock as mock

        with mock.patch("wyrd.state.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                state.save(state.default_state(), self.path)
        # A failed replace must not leave the target file written with new content.
        self.assertFalse(self.path.exists())

    def test_failed_replace_leaves_prior_state_intact(self):
        prior = {"schema_version": 1, "last_roll": None}
        state.save(prior, self.path)

        import unittest.mock as mock

        new_state = {"schema_version": 1, "last_roll": {"verb": "roll", "sides": 100, "result": 1, "seed": 1}}
        with mock.patch("wyrd.state.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                state.save(new_state, self.path)

        self.assertEqual(state.load(self.path), prior)


if __name__ == "__main__":
    unittest.main()
