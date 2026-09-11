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


class ChronicleStateTest(unittest.TestCase):
    """Tests for the chronicle.yaml schema (docs/design/22-state.md,
    specs/122-chronicle-yaml-schema)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def _fresh(self):
        return state.default_chronicle_state(
            name="test-chronicle",
            engine_repo="wyrd",
            engine_version="0.4.0",
            setting_repo="some-setting",
            setting_version="0.3.1",
        )

    # -- User Story 1: round-trip a chronicle's full identity --

    def test_default_chronicle_state_shape(self):
        fresh = self._fresh()
        self.assertEqual(fresh["schema_version"], 1)
        self.assertEqual(fresh["name"], "test-chronicle")
        self.assertEqual(fresh["engine"]["created_under"], "0.4.0")
        self.assertEqual(fresh["setting"]["created_under"], "0.3.1")
        self.assertEqual(fresh["migrations"], [])
        self.assertEqual(fresh["sessions"], 0)
        self.assertIsNone(fresh["pending"])

    def test_save_then_load_round_trips_a_fully_populated_chronicle(self):
        fresh = self._fresh()
        state.save_chronicle(fresh, self.path)
        loaded = state.load_chronicle(self.path)
        self.assertEqual(loaded, fresh)

    def test_load_fills_missing_optional_fields_with_documented_defaults(self):
        minimal = self._fresh()
        del minimal["era"]
        del minimal["intent"]
        del minimal["pending"]
        del minimal["eras"]
        del minimal["era_crossings"]
        state.save(minimal, self.path)  # bypass save_chronicle's own validation
        loaded = state.load_chronicle(self.path)
        self.assertIsNone(loaded["era"])
        self.assertIsNone(loaded["pending"])
        self.assertEqual(loaded["intent"], state._INTENT_DEFAULTS)
        self.assertEqual(loaded["eras"], [])
        self.assertEqual(loaded["era_crossings"], [])

    def test_eras_and_era_crossings_round_trip_when_populated(self):
        populated = self._fresh()
        populated["eras"] = [{"id": "the-long-thaw", "name": "The Long Thaw", "ambient": "hope"}]
        populated["era"] = "the-long-thaw"
        populated["era_crossings"] = [
            {"from": None, "to": "the-long-thaw", "at": {"year": 1, "month": 3}}
        ]
        state.save_chronicle(populated, self.path)
        loaded = state.load_chronicle(self.path)
        self.assertEqual(loaded["eras"], populated["eras"])
        self.assertEqual(loaded["era_crossings"], populated["era_crossings"])

    def test_load_missing_required_field_raises_naming_it(self):
        broken = self._fresh()
        del broken["schema_version"]
        state.save(broken, self.path)
        with self.assertRaises(state.StateError) as ctx:
            state.load_chronicle(self.path)
        self.assertIn("schema_version", str(ctx.exception))

    def test_load_chronicle_missing_file_raises(self):
        with self.assertRaises(state.StateError):
            state.load_chronicle(self.path)

    def test_save_rejects_negative_sessions_without_writing(self):
        bad = self._fresh()
        bad["sessions"] = -1
        with self.assertRaises(state.StateError):
            state.save_chronicle(bad, self.path)
        self.assertFalse(self.path.exists())

    def test_save_rejects_negative_danger_rating(self):
        bad = self._fresh()
        bad["danger_rating"] = -1
        with self.assertRaises(state.StateError):
            state.save_chronicle(bad, self.path)

    # -- User Story 2: current version vs. created_under --

    def test_bumping_engine_version_leaves_created_under_unchanged(self):
        fresh = self._fresh()
        state.save_chronicle(fresh, self.path)
        loaded = state.load_chronicle(self.path)
        loaded["engine"]["version"] = "0.5.0"
        state.save_chronicle(loaded, self.path)
        reloaded = state.load_chronicle(self.path)
        self.assertEqual(reloaded["engine"]["created_under"], "0.4.0")
        self.assertEqual(reloaded["engine"]["version"], "0.5.0")

    def test_bumping_setting_version_leaves_created_under_unchanged(self):
        fresh = self._fresh()
        state.save_chronicle(fresh, self.path)
        loaded = state.load_chronicle(self.path)
        loaded["setting"]["version"] = "0.4.0"
        state.save_chronicle(loaded, self.path)
        reloaded = state.load_chronicle(self.path)
        self.assertEqual(reloaded["setting"]["created_under"], "0.3.1")
        self.assertEqual(reloaded["setting"]["version"], "0.4.0")

    # -- User Story 3: append-only migrations --

    def test_append_migration_preserves_prior_entries_in_order(self):
        fresh = self._fresh()
        first = {
            "from": {"engine": "0.1.0"},
            "to": {"engine": "0.2.0"},
            "class": "tuning",
            "applied": "2026-01-01",
            "note": "first",
        }
        second = {
            "from": {"engine": "0.2.0"},
            "to": {"engine": "0.3.0"},
            "class": "additive",
            "applied": "2026-02-01",
            "note": "second",
        }
        with_two = state.append_migration(state.append_migration(fresh, first), second)
        state.save_chronicle(with_two, self.path)

        third = {
            "from": {"engine": "0.3.0"},
            "to": {"engine": "0.4.0"},
            "class": "structural",
            "applied": "2026-03-01",
            "note": "third",
        }
        loaded = state.load_chronicle(self.path)
        with_three = state.append_migration(loaded, third)
        state.save_chronicle(with_three, self.path)

        reloaded = state.load_chronicle(self.path)
        self.assertEqual(reloaded["migrations"], [first, second, third])

    def test_append_migration_rejects_invalid_class(self):
        fresh = self._fresh()
        with self.assertRaises(state.StateError):
            state.append_migration(fresh, {"class": "not-a-real-class"})

    def test_validate_chronicle_rejects_invalid_migration_class(self):
        fresh = self._fresh()
        fresh["migrations"] = [{"class": "not-a-real-class"}]
        with self.assertRaises(state.StateError):
            state.validate_chronicle(fresh)

    def test_save_rejects_edited_prior_migration_entry(self):
        fresh = self._fresh()
        entry = {
            "from": {"engine": "0.1.0"},
            "to": {"engine": "0.2.0"},
            "class": "tuning",
            "applied": "2026-01-01",
            "note": "original",
        }
        with_entry = state.append_migration(fresh, entry)
        state.save_chronicle(with_entry, self.path)

        tampered = state.load_chronicle(self.path)
        tampered["migrations"][0] = {**entry, "note": "rewritten"}
        with self.assertRaises(state.StateError):
            state.save_chronicle(tampered, self.path)

        # File on disk is unchanged.
        unchanged = state.load_chronicle(self.path)
        self.assertEqual(unchanged["migrations"][0]["note"], "original")

    def test_save_rejects_reordered_prior_migrations(self):
        fresh = self._fresh()
        first = {
            "from": {"engine": "0.1.0"},
            "to": {"engine": "0.2.0"},
            "class": "tuning",
            "applied": "2026-01-01",
            "note": "first",
        }
        second = {
            "from": {"engine": "0.2.0"},
            "to": {"engine": "0.3.0"},
            "class": "additive",
            "applied": "2026-02-01",
            "note": "second",
        }
        with_two = state.append_migration(state.append_migration(fresh, first), second)
        state.save_chronicle(with_two, self.path)

        reordered = state.load_chronicle(self.path)
        reordered["migrations"] = [second, first]
        with self.assertRaises(state.StateError):
            state.save_chronicle(reordered, self.path)

    # -- User Story 4: opaque pending marker --

    def test_populated_pending_round_trips_unchanged(self):
        fresh = self._fresh()
        fresh["pending"] = {"beat": "beat-42", "awaiting": "a decision", "rolled": None}
        state.save_chronicle(fresh, self.path)
        loaded = state.load_chronicle(self.path)
        self.assertEqual(
            loaded["pending"], {"beat": "beat-42", "awaiting": "a decision", "rolled": None}
        )

    def test_null_pending_round_trips_as_none(self):
        fresh = self._fresh()
        fresh["pending"] = None
        state.save_chronicle(fresh, self.path)
        loaded = state.load_chronicle(self.path)
        self.assertIsNone(loaded["pending"])


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


class FlowStyleCollectionTest(unittest.TestCase):
    """A setting.yaml `overrides:` block uses flow-style lists/mappings
    (docs/design/24-authoring-a-setting.md), which this restricted reader must parse."""

    def test_flow_list_of_scalars(self):
        parsed = state.parse_yaml("disable: [taint, trauma]\n")
        self.assertEqual(parsed["disable"], ["taint", "trauma"])

    def test_empty_flow_list(self):
        parsed = state.parse_yaml("disable: []\n")
        self.assertEqual(parsed["disable"], [])

    def test_flow_mapping_of_scalars(self):
        parsed = state.parse_yaml("rename: {taint: shadow}\n")
        self.assertEqual(parsed["rename"], {"taint": "shadow"})

    def test_flow_mapping_with_multiple_entries(self):
        parsed = state.parse_yaml(
            "extend: {skills: setting/rules/skills.yaml, "
            "oracle-prompt-npc-objective: setting/rules/tables/extra.yaml}\n"
        )
        self.assertEqual(
            parsed["extend"],
            {
                "skills": "setting/rules/skills.yaml",
                "oracle-prompt-npc-objective": "setting/rules/tables/extra.yaml",
            },
        )

    def test_empty_flow_mapping(self):
        parsed = state.parse_yaml("rename: {}\n")
        self.assertEqual(parsed["rename"], {})


if __name__ == "__main__":
    unittest.main()
