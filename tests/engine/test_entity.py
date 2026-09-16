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


def _minimal_valid_status(entity_type: str, **overrides) -> dict:
    """Like `_minimal()`, but with a `status` legal for `entity_type`'s own vocabulary.

    `_minimal()`'s default `status: stub` is only legal for types using the default vocabulary --
    a `thread` needs `status: open` instead (entity.THREAD_STATUSES). Every other type keeps
    `_minimal()`'s default. Callers that also want `role: companion` must pass a companion-legal
    `status` themselves; this helper only accounts for `entity_type`.
    """
    status_by_type = {"thread": "open"}
    overrides.setdefault("status", status_by_type.get(entity_type, "stub"))
    return _minimal(entity_type, **overrides)


class ValidateTest(unittest.TestCase):
    def test_accepts_minimal_entity_of_each_type(self):
        for entity_type in entity.ENTITY_TYPES:
            with self.subTest(entity_type=entity_type):
                record = _minimal_valid_status(entity_type)
                self.assertEqual(entity.validate(record), {"valid": True})

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


class CompanionStatusVocabularyTest(unittest.TestCase):
    """#408: a companion's own documented status vocabulary (22-state.md), not the default."""

    def test_accepts_every_documented_companion_status(self):
        for status in entity.COMPANION_STATUSES:
            with self.subTest(status=status):
                record = _minimal("character", role="companion", status=status)
                self.assertEqual(entity.validate(record), {"valid": True})

    def test_rejects_default_vocabulary_status_for_companion(self):
        # "complete" is legal for the *default* vocabulary but the companion vocabulary
        # replaces the default for companions rather than extending it.
        record = _minimal("character", role="companion", status="complete")
        result = entity.validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("complete", result["error"])

    def test_non_companion_character_keeps_default_vocabulary(self):
        for role in ("player", "nemesis", None):
            with self.subTest(role=role):
                record = _minimal("character", status="complete")
                if role is not None:
                    record["role"] = role
                self.assertEqual(entity.validate(record), {"valid": True})

    def test_non_companion_character_rejects_companion_status(self):
        record = _minimal("character", role="nemesis", status="with-party")
        result = entity.validate(record)
        self.assertFalse(result["valid"])


class ThreadStatusVocabularyTest(unittest.TestCase):
    """#408: a thread's own documented status vocabulary (22-state.md), not the default."""

    def test_accepts_every_documented_thread_status(self):
        for status in entity.THREAD_STATUSES:
            with self.subTest(status=status):
                record = _minimal("thread", status=status)
                self.assertEqual(entity.validate(record), {"valid": True})

    def test_rejects_default_vocabulary_status_for_thread(self):
        # "stub" is legal for the *default* vocabulary but not for threads.
        record = _minimal("thread", status="stub")
        result = entity.validate(record)
        self.assertFalse(result["valid"])
        self.assertIn("stub", result["error"])


class OtherTypesKeepDefaultStatusVocabularyTest(unittest.TestCase):
    """#408 Acceptance Criterion 3 / User Story 3: no other type's validation narrows or changes."""

    def test_every_default_status_still_accepted_for_every_other_type(self):
        other_types = [t for t in entity.ENTITY_TYPES if t != "thread"]
        for entity_type in other_types:
            for status in entity.STATUSES:
                with self.subTest(entity_type=entity_type, status=status):
                    record = _minimal(entity_type, status=status)
                    self.assertEqual(entity.validate(record), {"valid": True})

    def test_still_rejects_an_unrecognised_status_for_a_non_overridden_type(self):
        result = entity.validate(_minimal("place", status="active"))
        self.assertFalse(result["valid"])


class EndToEndStatusVocabularyTest(unittest.TestCase):
    """#408: the exact gap that let the bug ship -- no prior test loaded such a file from disk.

    Writes a real companion entity file and a real thread entity file to a temporary directory,
    loads each with `entity.load()` (which round-trips through `wyrd.state.load_entity` and then
    calls `validate()`), and confirms both pass -- not an in-memory frontmatter dict.
    """

    def test_real_companion_file_with_documented_status_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = _minimal(
                "character",
                id="hallam",
                role="companion",
                status="with-party",
                bond=1,
            )
            path = pathlib.Path(tmp) / "hallam.md"
            state.save_entity(record, "A companion who travels with the party.", path)
            loaded = entity.load(path)
            self.assertEqual(loaded["status"], "with-party")

    def test_real_thread_file_with_documented_status_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = _minimal(
                "thread",
                id="the-missing-envoy",
                status="open",
                heat=3,
            )
            path = pathlib.Path(tmp) / "the-missing-envoy.md"
            state.save_entity(record, "An open loop the chronicle is carrying.", path)
            loaded = entity.load(path)
            self.assertEqual(loaded["status"], "open")


class LoadTest(unittest.TestCase):
    def test_round_trips_each_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            for entity_type in entity.ENTITY_TYPES:
                with self.subTest(entity_type=entity_type):
                    record = _minimal_valid_status(entity_type)
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


def _valid_source(**overrides) -> dict:
    base = {"work": "Corpus Vol. 3", "licence": "internal", "path": "corpus/vol3.md"}
    base.update(overrides)
    return base


class ValidateSourceTest(unittest.TestCase):
    def test_accepts_minimal_source_at_stub(self):
        self.assertEqual(entity.validate_source(_valid_source(), status="stub"), {"valid": True})

    def test_rejects_missing_work(self):
        source = _valid_source()
        del source["work"]
        result = entity.validate_source(source, status="stub")
        self.assertFalse(result["valid"])
        self.assertIn("work", result["error"])

    def test_rejects_missing_licence(self):
        source = _valid_source()
        del source["licence"]
        result = entity.validate_source(source, status="stub")
        self.assertFalse(result["valid"])
        self.assertIn("licence", result["error"])

    def test_rejects_missing_path(self):
        source = _valid_source()
        del source["path"]
        result = entity.validate_source(source, status="stub")
        self.assertFalse(result["valid"])
        self.assertIn("path", result["error"])

    def test_pages_not_required_at_stub(self):
        self.assertEqual(entity.validate_source(_valid_source(), status="stub"), {"valid": True})

    def test_pages_required_at_drafted(self):
        result = entity.validate_source(_valid_source(), status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("pages", result["error"])

    def test_pages_required_at_complete(self):
        result = entity.validate_source(_valid_source(), status="complete")
        self.assertFalse(result["valid"])
        self.assertIn("pages", result["error"])

    def test_accepts_source_with_pages_at_drafted(self):
        source = _valid_source(pages="12-14")
        self.assertEqual(entity.validate_source(source, status="drafted"), {"valid": True})

    def test_rejects_unexpected_field(self):
        source = _valid_source(author="someone")
        result = entity.validate_source(source, status="stub")
        self.assertFalse(result["valid"])
        self.assertIn("author", result["error"])


def _valid_generated_source(**overrides) -> dict:
    base = {"generated": True, "mode": "live-play", "consumed": ["the-ledger"]}
    base.update(overrides)
    return base


class ValidateGeneratedSourceTest(unittest.TestCase):
    """specs/164-commit-back-path-for-generated-content FR-002/T004."""

    def test_accepts_well_formed_generated_entry(self):
        result = entity.validate_source(_valid_generated_source(), status="drafted")
        self.assertEqual(result, {"valid": True})

    def test_rejects_missing_mode(self):
        source = _valid_generated_source()
        del source["mode"]
        result = entity.validate_source(source, status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("mode", result["error"])

    def test_rejects_missing_consumed(self):
        source = _valid_generated_source()
        del source["consumed"]
        result = entity.validate_source(source, status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("consumed", result["error"])

    def test_rejects_invalid_mode_value(self):
        source = _valid_generated_source(mode="dreamed-up")
        result = entity.validate_source(source, status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("mode", result["error"])

    def test_rejects_non_list_consumed(self):
        source = _valid_generated_source(consumed="the-ledger")
        result = entity.validate_source(source, status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("consumed", result["error"])

    def test_rejects_unexpected_field(self):
        source = _valid_generated_source(pages="12-14")
        result = entity.validate_source(source, status="drafted")
        self.assertFalse(result["valid"])
        self.assertIn("pages", result["error"])

    def test_pages_never_required_for_generated_entry(self):
        # Unlike the authored shape, a generated entry never requires 'pages', at any status.
        result = entity.validate_source(_valid_generated_source(), status="complete")
        self.assertEqual(result, {"valid": True})

    def test_authored_shape_tests_still_pass_unchanged(self):
        # Sanity check: the additive change does not alter the pre-existing authored-shape gate.
        self.assertEqual(entity.validate_source(_valid_source(), status="stub"), {"valid": True})


def _sufficient_stub(**overrides) -> dict:
    base = _minimal("beat")
    base.update(tags=["combat", "travel"], sources=[_valid_source()])
    base.update(overrides)
    return base


_SUMMARY_BODY = "A river crossing goes wrong."


class CheckStubSufficiencyTest(unittest.TestCase):
    def test_accepts_sufficient_stub(self):
        result = entity.check_stub_sufficiency(_sufficient_stub(), _SUMMARY_BODY)
        self.assertEqual(result, {"valid": True})

    def test_rejects_missing_summary_body(self):
        result = entity.check_stub_sufficiency(_sufficient_stub(), "")
        self.assertFalse(result["valid"])
        self.assertIn("summary", result["error"])

    def test_rejects_whitespace_only_summary_body(self):
        result = entity.check_stub_sufficiency(_sufficient_stub(), "   \n")
        self.assertFalse(result["valid"])
        self.assertIn("summary", result["error"])

    def test_rejects_missing_tags(self):
        record = _sufficient_stub()
        del record["tags"]
        result = entity.check_stub_sufficiency(record, _SUMMARY_BODY)
        self.assertFalse(result["valid"])
        self.assertIn("tags", result["error"])

    def test_rejects_missing_sources(self):
        record = _sufficient_stub()
        del record["sources"]
        result = entity.check_stub_sufficiency(record, _SUMMARY_BODY)
        self.assertFalse(result["valid"])
        self.assertIn("sources", result["error"])

    def test_rejects_source_with_empty_path(self):
        record = _sufficient_stub(sources=[_valid_source(path="")])
        result = entity.check_stub_sufficiency(record, _SUMMARY_BODY)
        self.assertFalse(result["valid"])
        self.assertIn("sources", result["error"])

    def test_exempts_non_stub_entity_missing_everything(self):
        record = _minimal("beat", status="drafted")
        self.assertEqual(entity.check_stub_sufficiency(record, ""), {"valid": True})


class LegalTransitionTest(unittest.TestCase):
    def test_accepts_stub_to_drafted(self):
        self.assertEqual(entity.legal_transition("stub", "drafted"), {"valid": True})

    def test_accepts_drafted_to_complete(self):
        self.assertEqual(entity.legal_transition("drafted", "complete"), {"valid": True})

    def test_rejects_stub_to_complete_as_skip(self):
        result = entity.legal_transition("stub", "complete")
        self.assertFalse(result["valid"])
        self.assertIn("skips a state", result["error"])

    def test_rejects_backward_moves(self):
        for from_status, to_status in (
            ("complete", "stub"),
            ("drafted", "stub"),
            ("complete", "drafted"),
        ):
            with self.subTest(from_status=from_status, to_status=to_status):
                result = entity.legal_transition(from_status, to_status)
                self.assertFalse(result["valid"])
                self.assertIn("moves backward", result["error"])

    def test_rejects_identical_statuses(self):
        for status in entity.STATUSES:
            with self.subTest(status=status):
                result = entity.legal_transition(status, status)
                self.assertFalse(result["valid"])

    def test_rejects_unrecognised_status(self):
        result = entity.legal_transition("stub", "finished")
        self.assertFalse(result["valid"])


class StatusCountsTest(unittest.TestCase):
    def test_reports_mixed_status_set(self):
        entities = {
            "a": {"status": "stub"},
            "b": {"status": "stub"},
            "c": {"status": "drafted"},
            "d": {"status": "complete"},
        }
        result = entity.status_counts(entities)
        self.assertEqual(result["stub"]["count"], 2)
        self.assertEqual(result["drafted"]["count"], 1)
        self.assertEqual(result["complete"]["count"], 1)
        self.assertAlmostEqual(result["stub"]["proportion"], 0.5)
        self.assertAlmostEqual(result["drafted"]["proportion"], 0.25)
        self.assertAlmostEqual(result["complete"]["proportion"], 0.25)

    def test_reports_zero_on_empty_set(self):
        result = entity.status_counts({})
        for status in entity.STATUSES:
            self.assertEqual(result[status]["count"], 0)
            self.assertEqual(result[status]["proportion"], 0.0)


if __name__ == "__main__":
    unittest.main()
