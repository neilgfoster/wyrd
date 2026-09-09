"""Tests for engine/wyrd/entity.py: common schema, the ten types, containment, connections.

stdlib unittest, no pytest (matches tests/engine/test_state.py, which this module builds on).
Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import entity, state  # noqa: E402


def _minimal(entity_type: str, **overrides) -> dict:
    base = {
        "id": f"the-{entity_type}",
        "type": entity_type,
        "name": f"The {entity_type.title()}",
        "setting": "example-setting",
        "status": "stub",
    }
    base.update(overrides)
    return base


class ValidateTest(unittest.TestCase):
    def test_accepts_minimal_entity_of_each_type(self):
        for entity_type in entity.ENTITY_TYPES:
            with self.subTest(entity_type=entity_type):
                self.assertEqual(entity.validate(_minimal(entity_type)), {"valid": True})

    def test_rejects_missing_common_field(self):
        record = _minimal("place")
        del record["name"]
        result = entity.validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("name", result["error"])

    def test_rejects_unknown_type(self):
        result = entity.validate(_minimal("place", type="nation"))
        self.assertFalse(result["valid"])

    def test_rejects_invalid_status(self):
        result = entity.validate(_minimal("place", status="finished"))
        self.assertFalse(result["valid"])

    def test_rejects_type_specific_enum_violation(self):
        result = entity.validate(_minimal("character", disposition="curious"))
        self.assertFalse(result["valid"])

    def test_accepts_place_with_connections(self):
        record = _minimal(
            "place",
            connections=[
                {"to": "[[the-old-quarter]]", "via": "the coast road"},
                {
                    "to": "[[the-undercroft]]",
                    "via": "a stair behind the shrine",
                    "hidden": True,
                },
            ],
        )
        self.assertEqual(entity.validate(record), {"valid": True})

    def test_preserves_hidden_flag_distinctly(self):
        record = _minimal(
            "place",
            connections=[
                {"to": "[[a]]"},
                {"to": "[[b]]", "hidden": True},
            ],
        )
        self.assertEqual(entity.validate(record), {"valid": True})
        self.assertNotIn("hidden", record["connections"][0])
        self.assertTrue(record["connections"][1]["hidden"])

    def test_accepts_connection_loop(self):
        a = _minimal("place", id="a", connections=[{"to": "[[b]]"}])
        b = _minimal("place", id="b", connections=[{"to": "[[a]]"}])
        self.assertEqual(entity.validate(a), {"valid": True})
        self.assertEqual(entity.validate(b), {"valid": True})

    def test_rejects_connection_missing_to(self):
        record = _minimal("place", connections=[{"via": "a path"}])
        result = entity.validate(record)
        self.assertFalse(result["valid"])

    def test_rejects_connection_with_unexpected_field(self):
        record = _minimal("place", connections=[{"to": "[[a]]", "danger": 2}])
        result = entity.validate(record)
        self.assertFalse(result["valid"])


class LoadTest(unittest.TestCase):
    def test_round_trips_each_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            for entity_type in entity.ENTITY_TYPES:
                with self.subTest(entity_type=entity_type):
                    record = _minimal(entity_type)
                    path = pathlib.Path(tmp) / f"{entity_type}.md"
                    state.save_entity(record, "", path)
                    loaded = entity.load(path)
                    self.assertEqual(loaded, record)

    def test_load_raises_on_invalid_entity(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = _minimal("place")
            del record["name"]
            path = pathlib.Path(tmp) / "bad.md"
            state.save_entity(record, "", path)
            with self.assertRaises(state.StateError):
                entity.load(path)


class WikilinkTest(unittest.TestCase):
    def test_strips_brackets(self):
        self.assertEqual(entity.resolve_wikilink("[[the-river-city]]"), "the-river-city")

    def test_passes_through_plain_id(self):
        self.assertEqual(entity.resolve_wikilink("the-river-city"), "the-river-city")


class ContainmentTest(unittest.TestCase):
    def test_children_of_returns_direct_children_only(self):
        entities = {
            "a": _minimal("place", id="a"),
            "b": _minimal("place", id="b", parent="[[a]]"),
            "c": _minimal("place", id="c", parent="[[b]]"),
        }
        self.assertEqual(entity.children_of("a", entities), ["b"])
        self.assertEqual(entity.children_of("b", entities), ["c"])
        self.assertEqual(entity.children_of("c", entities), [])

    def test_check_containment_accepts_rootless_entity(self):
        entities = {"a": _minimal("place", id="a")}
        self.assertEqual(entity.check_containment(entities), {"valid": True})

    def test_check_containment_accepts_tree(self):
        entities = {
            "a": _minimal("place", id="a"),
            "b": _minimal("place", id="b", parent="[[a]]"),
        }
        self.assertEqual(entity.check_containment(entities), {"valid": True})

    def test_check_containment_rejects_cycle(self):
        entities = {
            "a": _minimal("place", id="a", parent="[[b]]"),
            "b": _minimal("place", id="b", parent="[[a]]"),
        }
        result = entity.check_containment(entities)
        self.assertFalse(result["valid"])
        self.assertIn("cycle", result)


class UnresolvedReferencesTest(unittest.TestCase):
    def test_reports_absent_target(self):
        entities = {
            "a": _minimal(
                "place",
                id="a",
                parent="[[missing-parent]]",
                connections=[{"to": "[[missing-target]]"}],
            ),
        }
        problems = entity.unresolved_references(entities)
        targets = {p["target"] for p in problems}
        self.assertEqual(targets, {"missing-parent", "missing-target"})

    def test_reports_nothing_when_all_targets_present(self):
        entities = {
            "a": _minimal("place", id="a"),
            "b": _minimal("place", id="b", parent="[[a]]", links=["[[a]]"]),
        }
        self.assertEqual(entity.unresolved_references(entities), [])


class ResolveEntityTest(unittest.TestCase):
    def test_no_overlay_returns_setting_unchanged(self):
        setting = {"hallam": _minimal("character", id="hallam", role="bystander")}
        frontmatter, body = entity.resolve_entity("hallam", setting, overlays={})
        self.assertEqual(frontmatter, setting["hallam"])
        self.assertIsNot(frontmatter, setting["hallam"])
        self.assertEqual(body, "")

    def test_unknown_id_with_no_overlay_raises(self):
        with self.assertRaises(state.StateError):
            entity.resolve_entity("nobody", {}, overlays={})

    def test_overlay_overrides_one_field(self):
        setting = {
            "the-caretaker": _minimal(
                "character", id="the-caretaker", disposition="unaware", role="bystander"
            )
        }
        overlays = {
            "the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker", "disposition": "hunting"}
        }
        frontmatter, _body = entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(frontmatter["disposition"], "hunting")
        self.assertEqual(frontmatter["name"], setting["the-caretaker"]["name"])
        self.assertEqual(frontmatter["role"], "bystander")

    def test_overlay_overrides_multiple_fields(self):
        setting = {
            "the-caretaker": _minimal(
                "character", id="the-caretaker", disposition="unaware", role="bystander"
            )
        }
        overlays = {
            "the-caretaker": {
                "id": "ov-1",
                "overlay_of": "the-caretaker",
                "disposition": "hunting",
                "role": "quarry",
            }
        }
        frontmatter, _body = entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(frontmatter["disposition"], "hunting")
        self.assertEqual(frontmatter["role"], "quarry")
        self.assertEqual(frontmatter["name"], setting["the-caretaker"]["name"])

    def test_excludes_overlay_bookkeeping_fields(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker")}
        overlays = {
            "the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker", "status": "complete"}
        }
        frontmatter, _body = entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(frontmatter["id"], "the-caretaker")
        self.assertNotIn("overlay_of", frontmatter)

    def test_overlay_empty_value_still_overrides(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker", tags=["notable"])}
        overlays = {"the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker", "tags": []}}
        frontmatter, _body = entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(frontmatter["tags"], [])

    def test_overlay_invalid_merge_raises(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker")}
        overlays = {
            "the-caretaker": {
                "id": "ov-1",
                "overlay_of": "the-caretaker",
                "disposition": "curious",
            }
        }
        with self.assertRaises(state.StateError):
            entity.resolve_entity("the-caretaker", setting, overlays)

    def test_body_overlay_replaces_setting_body(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker")}
        overlays = {"the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker"}}
        _frontmatter, body = entity.resolve_entity(
            "the-caretaker",
            setting,
            overlays,
            setting_bodies={"the-caretaker": "the setting's account."},
            overlay_bodies={"the-caretaker": "what actually happened."},
        )
        self.assertEqual(body, "what actually happened.")

    def test_body_falls_through_when_overlay_body_empty(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker")}
        overlays = {"the-caretaker": {"id": "ov-1", "overlay_of": "the-caretaker"}}
        _frontmatter, body = entity.resolve_entity(
            "the-caretaker",
            setting,
            overlays,
            setting_bodies={"the-caretaker": "the setting's account."},
        )
        self.assertEqual(body, "the setting's account.")

    def test_promotion_adds_new_fields_and_validates(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker", role="bystander")}
        overlays = {
            "the-caretaker": {
                "id": "ov-2",
                "overlay_of": "the-caretaker",
                "role": "nemesis",
                "threat": {"imminence": 2, "connection": "left them for dead"},
            }
        }
        frontmatter, _body = entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(frontmatter["role"], "nemesis")
        self.assertEqual(frontmatter["threat"]["imminence"], 2)

    def test_promotion_does_not_mutate_setting_dict(self):
        setting = {"the-caretaker": _minimal("character", id="the-caretaker", role="bystander")}
        original = dict(setting["the-caretaker"])
        overlays = {
            "the-caretaker": {
                "id": "ov-2",
                "overlay_of": "the-caretaker",
                "role": "nemesis",
                "threat": {"imminence": 2, "connection": "left them for dead"},
            }
        }
        entity.resolve_entity("the-caretaker", setting, overlays)
        self.assertEqual(setting["the-caretaker"], original)

    def test_dangling_overlay_of_raises(self):
        overlays = {"ghost": {"id": "ov-3", "overlay_of": "ghost"}}
        with self.assertRaises(state.StateError):
            entity.resolve_entity("ghost", {}, overlays)


class LoadSetTest(unittest.TestCase):
    def test_loads_and_validates_every_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, entity_type in enumerate(("place", "character")):
                path = pathlib.Path(tmp) / f"{i}.md"
                state.save_entity(_minimal(entity_type, id=f"e{i}"), "", path)
                paths.append(path)
            loaded = entity.load_set(paths)
            self.assertEqual(set(loaded), {"e0", "e1"})

    def test_raises_on_first_invalid_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = _minimal("place")
            del record["name"]
            path = pathlib.Path(tmp) / "bad.md"
            state.save_entity(record, "", path)
            with self.assertRaises(state.StateError):
                entity.load_set([path])


if __name__ == "__main__":
    unittest.main()
