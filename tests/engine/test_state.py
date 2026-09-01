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

        new_state = {
            "schema_version": 1,
            "last_roll": {"verb": "roll", "sides": 100, "result": 1, "seed": 1},
        }
        with mock.patch("wyrd.state.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                state.save(new_state, self.path)

        self.assertEqual(state.load(self.path), prior)


class EntityFrontmatterTest(unittest.TestCase):
    def test_parse_entity_splits_frontmatter_and_body(self):
        text = "---\nid: aria\n---\nSome prose.\n"
        frontmatter, body = state.parse_entity(text)
        self.assertEqual(frontmatter, {"id": "aria"})
        self.assertEqual(body, "Some prose.\n")

    def test_body_may_contain_further_dashes_unsplit(self):
        text = "---\nid: aria\n---\nBefore.\n\n---\n\nAfter.\n"
        frontmatter, body = state.parse_entity(text)
        self.assertEqual(frontmatter, {"id": "aria"})
        self.assertEqual(body, "Before.\n\n---\n\nAfter.\n")

    def test_dump_entity_round_trips_through_parse_entity(self):
        frontmatter = {"id": "aria", "skills": {"stealth": 45}}
        body = "Prose.\n"
        text = state.dump_entity(frontmatter, body)
        parsed_frontmatter, parsed_body = state.parse_entity(text)
        self.assertEqual(parsed_frontmatter, frontmatter)
        self.assertEqual(parsed_body, body)

    def test_missing_opening_delimiter_raises(self):
        with self.assertRaises(state.StateError):
            state.parse_entity("id: aria\n")

    def test_missing_closing_delimiter_raises(self):
        with self.assertRaises(state.StateError):
            state.parse_entity("---\nid: aria\n")

    def test_save_entity_and_load_entity_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "aria.md"
            state.save_entity({"id": "aria"}, "Prose.\n", path)
            frontmatter, body = state.load_entity(path)
            self.assertEqual(frontmatter, {"id": "aria"})
            self.assertEqual(body, "Prose.\n")

    def test_load_entity_missing_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(state.StateError):
                state.load_entity(pathlib.Path(tmp) / "missing.md")


class ListOfMappingRoundTripTest(unittest.TestCase):
    def test_list_of_mappings_round_trips(self):
        data = {
            "wounds": [
                {"id": "a", "effect": {"skill": -10}, "bears_on": "stealth"},
                {"id": "b", "effect": {"dread": 1}},
            ]
        }
        text = state.dump_yaml(data)
        self.assertEqual(state.parse_yaml(text), data)

    def test_list_of_scalars_still_round_trips(self):
        data = {"career_history": ["soldier", "wanderer"]}
        text = state.dump_yaml(data)
        self.assertEqual(state.parse_yaml(text), data)

    def test_empty_list_round_trips_as_empty_list_not_null(self):
        data = {"transformations": []}
        text = state.dump_yaml(data)
        self.assertEqual(state.parse_yaml(text), data)

    def test_empty_dict_round_trips_as_empty_dict_not_null(self):
        data = {"reputation": {}}
        text = state.dump_yaml(data)
        self.assertEqual(state.parse_yaml(text), data)

    def test_sequence_sharing_parent_key_indentation_parses(self):
        # Legal YAML lets a sequence sit at its parent key's own indentation rather than
        # nested under it -- both forms are valid, and a hand-edited file might use either.
        text = "career_history:\n- soldier\n- wanderer\nskills:\n  stealth: 45\n"
        parsed = state.parse_yaml(text)
        self.assertEqual(parsed["career_history"], ["soldier", "wanderer"])
        self.assertEqual(parsed["skills"], {"stealth": 45})


if __name__ == "__main__":
    unittest.main()
