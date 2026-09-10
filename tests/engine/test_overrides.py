"""Tests for engine/wyrd/overrides.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import overrides  # noqa: E402


class DescribeOverridableTest(unittest.TestCase):
    def test_reports_every_closed_set_entry(self):
        entries = overrides.describe_overridable()
        names = {entry["name"] for entry in entries}
        self.assertEqual(names, set(overrides.OVERRIDABLE))

    def test_each_entry_names_its_kinds(self):
        entries = {entry["name"]: entry for entry in overrides.describe_overridable()}
        self.assertEqual(sorted(entries["taint"]["kinds"]), ["disable", "rename"])


class ValidateBlockTest(unittest.TestCase):
    def test_empty_block_is_valid(self):
        self.assertEqual(overrides.validate_block({}), [])

    def test_unknown_top_level_key_is_rejected(self):
        problems = overrides.validate_block({"bogus": []})
        self.assertTrue(any("bogus" in p for p in problems))

    def test_mechanism_outside_closed_set_is_rejected(self):
        problems = overrides.validate_block({"disable": ["prophecy-engine"]})
        self.assertTrue(any("prophecy-engine" in p for p in problems))

    def test_kind_not_supported_by_mechanism_is_rejected(self):
        # "skills" only supports extend, not disable.
        problems = overrides.validate_block({"disable": ["skills"]})
        self.assertTrue(any("skills" in p and "disable" in p for p in problems))

    def test_disabling_and_overriding_the_same_mechanism_is_a_contradiction(self):
        problems = overrides.validate_block({"disable": ["taint"], "rename": {"taint": "shadow"}})
        self.assertTrue(any("taint" in p for p in problems))

    def test_valid_block_of_each_kind(self):
        block = {
            "disable": ["trauma"],
            "rename": {"taint": "shadow"},
            "tables": {"oracle-prompt-npc-objective": "setting/rules/tables/x.yaml"},
            "extend": {"skills": "setting/rules/skills.yaml"},
        }
        self.assertEqual(overrides.validate_block(block), [])


class ResolveTest(unittest.TestCase):
    def test_no_layers_beyond_defaults_yields_empty_config(self):
        resolved = overrides.resolve([("engine", {})])
        self.assertEqual(resolved.disabled, frozenset())
        self.assertEqual(resolved.renames, {})

    def test_setting_disable_is_reflected(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"disable": ["taint"]})])
        self.assertFalse(resolved.is_enabled("taint"))
        self.assertTrue(resolved.is_enabled("trauma"))

    def test_rename_is_presentation_only(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"rename": {"taint": "shadow"}})])
        self.assertEqual(resolved.label("taint"), "shadow")
        # The internal identifier is untouched -- nothing renames "taint" itself.
        self.assertIn("taint", overrides.OVERRIDABLE)

    def test_chronicle_houserule_wins_over_setting_override(self):
        resolved = overrides.resolve(
            [
                ("engine", {}),
                ("setting", {"rename": {"taint": "shadow"}}),
                ("chronicle", {"rename": {"taint": "corruption"}}),
            ]
        )
        self.assertEqual(resolved.label("taint"), "corruption")

    def test_extend_accumulates_across_layers(self):
        resolved = overrides.resolve(
            [
                ("engine", {}),
                ("setting", {"extend": {"skills": "setting/rules/skills.yaml"}}),
                ("chronicle", {"extend": {"skills": "chronicle/extra-skills.yaml"}}),
            ]
        )
        self.assertEqual(
            resolved.extends["skills"],
            ["setting/rules/skills.yaml", "chronicle/extra-skills.yaml"],
        )

    def test_no_chronicle_houserules_leaves_setting_layer_as_final(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"disable": ["trauma"]})])
        self.assertEqual(resolved.disabled, frozenset({"trauma"}))

    def test_override_naming_outside_closed_set_raises(self):
        with self.assertRaises(overrides.OverrideError):
            overrides.resolve([("engine", {}), ("setting", {"disable": ["not-a-mechanism"]})])

    def test_chronicle_cannot_widen_what_setting_disabled(self):
        with self.assertRaises(overrides.OverrideError):
            overrides.resolve(
                [
                    ("engine", {}),
                    ("setting", {"disable": ["taint"]}),
                    ("chronicle", {"rename": {"taint": "shadow"}}),
                ]
            )

    def test_disabling_something_already_disabled_by_an_earlier_layer_raises(self):
        with self.assertRaises(overrides.OverrideError):
            overrides.resolve(
                [
                    ("engine", {}),
                    ("setting", {"disable": ["taint"]}),
                    ("chronicle", {"disable": ["taint"]}),
                ]
            )


class FilterToolsTest(unittest.TestCase):
    def _tools(self):
        return {
            "roll": {"name": "roll"},
            "track": {
                "name": "track",
                "mechanisms": ["taint", "trauma"],
                "inputSchema": {
                    "type": "object",
                    "properties": {"mechanism": {"type": "string", "enum": ["taint", "trauma"]}},
                },
            },
        }

    def test_no_disabled_mechanisms_leaves_catalog_untouched(self):
        resolved = overrides.resolve([("engine", {})])
        filtered = overrides.filter_tools(self._tools(), resolved)
        self.assertEqual(filtered["track"]["mechanisms"], ["taint", "trauma"])

    def test_disabling_every_mechanism_a_tool_offers_removes_it(self):
        resolved = overrides.resolve(
            [("engine", {}), ("setting", {"disable": ["taint", "trauma"]})]
        )
        filtered = overrides.filter_tools(self._tools(), resolved)
        self.assertNotIn("track", filtered)
        self.assertIn("roll", filtered)

    def test_disabling_one_of_several_narrows_the_tool_rather_than_removing_it(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"disable": ["taint"]})])
        filtered = overrides.filter_tools(self._tools(), resolved)
        self.assertEqual(filtered["track"]["mechanisms"], ["trauma"])
        self.assertEqual(
            filtered["track"]["inputSchema"]["properties"]["mechanism"]["enum"], ["trauma"]
        )
        # The original tool dict passed in is not mutated.
        self.assertEqual(self._tools()["track"]["mechanisms"], ["taint", "trauma"])


if __name__ == "__main__":
    unittest.main()
