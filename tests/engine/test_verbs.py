"""Tests for engine/wyrd/verbs.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import overrides, state, verbs  # noqa: E402


def _write_entity(path: pathlib.Path, frontmatter_lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + "\n".join(frontmatter_lines) + "\n---\n", encoding="utf-8")


def _make_chronicle_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """A minimal on-disk chronicle: setting/overlay/entities/engine/log dirs, a
    schema-conformant chronicle.yaml, and a handful of entities using type/status
    combinations `entity.validate()` already accepts (place/organisation, `status: complete`) --
    a real companion (`status: with-party`) or thread (`status: open`) file cannot currently be
    loaded through `entity.load_set` at all: `entity.py`'s single global `STATUSES =
    ("stub", "drafted", "complete")` check rejects both values outright, even though
    docs/design/22-state.md documents them as those two types' own status vocabularies. This is
    a real, pre-existing gap in `entity.py`, out of scope for #402's CLI-wiring feature to fix;
    verbs whose predicate depends on `with-party`/`open` are instead tested directly against
    in-memory entity dicts below, matching `tests/engine/test_loadtier.py`'s own convention.
    """
    for name in ("setting", "overlay", "entities", "engine", "log"):
        (tmp_path / name).mkdir(parents=True, exist_ok=True)
    (tmp_path / "engine" / "contract.md").write_text("# Contract\n", encoding="utf-8")
    _write_entity(
        tmp_path / "setting" / "place-1.md",
        [
            "id: place-1",
            "type: place",
            "name: Place One",
            "setting: example-setting",
            "status: complete",
            "tags: [waypoint]",
        ],
    )
    (tmp_path / "chronicle.yaml").write_text(
        "\n".join(
            [
                "schema_version: 1",
                "name: test-chronicle",
                "engine:",
                "  repo: wyrd",
                "  version: 0.1.0",
                "  created_under: 0.1.0",
                "setting:",
                "  repo: example-setting",
                "  version: 0.1.0",
                "  created_under: 0.1.0",
                "calendar:",
                "  year: 1",
                "  month: null",
                "  day: 0",
                "era: null",
                "eras: []",
                "era_crossings: []",
                "sessions: 0",
                "danger_rating: 2",
                "migrations: []",
                "intent:",
                "  lethality: standard",
                "  world_acts_offstage: true",
                "pending: null",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path


class LoadEffectiveEntitiesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_resolves_setting_entities(self):
        entities = verbs.load_effective_entities(self.chronicle_dir)
        self.assertIn("place-1", entities)
        self.assertEqual(entities["place-1"]["type"], "place")


class FindEntitiesTest(unittest.TestCase):
    def test_filters_by_type_only(self):
        entities = {
            "a": {"id": "a", "type": "place", "status": "complete"},
            "b": {"id": "b", "type": "character", "status": "complete"},
        }
        result = verbs.find_entities(entities, type="place")
        self.assertEqual(set(result), {"a"})

    def test_filters_by_type_and_status(self):
        entities = {
            "a": {"id": "a", "type": "place", "status": "complete"},
            "b": {"id": "b", "type": "place", "status": "stub"},
        }
        result = verbs.find_entities(entities, type="place", status="stub")
        self.assertEqual(set(result), {"b"})

    def test_filters_by_tag(self):
        entities = {
            "a": {"id": "a", "type": "place", "status": "complete", "tags": ["waypoint"]},
            "b": {"id": "b", "type": "place", "status": "complete", "tags": []},
        }
        result = verbs.find_entities(entities, type="place", tag="waypoint")
        self.assertEqual(set(result), {"a"})

    def test_no_matches_is_empty_not_an_error(self):
        entities = {"a": {"id": "a", "type": "place", "status": "complete"}}
        result = verbs.find_entities(entities, type="organisation")
        self.assertEqual(result, {})


class CompanionsWithPartyTest(unittest.TestCase):
    def test_only_role_companion_and_status_with_party(self):
        entities = {
            "c1": {"id": "c1", "type": "character", "role": "companion", "status": "with-party"},
            "c2": {"id": "c2", "type": "character", "role": "companion", "status": "away"},
            "c3": {"id": "c3", "type": "character", "role": "player", "status": "with-party"},
        }
        result = verbs.companions_with_party(entities)
        self.assertEqual(set(result), {"c1"})


class OpenThreadsByHeatTest(unittest.TestCase):
    def test_full_open_set_ordered_by_heat_descending(self):
        entities = {
            "t-hot": {"id": "t-hot", "type": "thread", "status": "open", "heat": 5},
            "t-warm": {"id": "t-warm", "type": "thread", "status": "open", "heat": 3},
            "t-cool": {"id": "t-cool", "type": "thread", "status": "open", "heat": 1},
            "t-resolved": {"id": "t-resolved", "type": "thread", "status": "resolved", "heat": 5},
        }
        result = verbs.open_threads_by_heat(entities)
        self.assertEqual([fm["id"] for fm in result], ["t-hot", "t-warm", "t-cool"])


class SessionContextVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_always_loaded_shape(self):
        result = verbs.session_context(self.chronicle_dir)
        self.assertEqual(result["verb"], "session-context")
        self.assertIn("player_character", result)
        self.assertIn("companions", result)
        self.assertIn("threads", result)
        self.assertEqual(result["contract"], "# Contract\n")

    def test_no_open_threads_is_empty_not_an_error(self):
        result = verbs.session_context(self.chronicle_dir)
        self.assertEqual(result["threads"], {})


class GetVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_resolves_known_id(self):
        result = verbs.get("place-1", self.chronicle_dir)
        self.assertEqual(result["verb"], "get")
        self.assertEqual(result["entity"]["id"], "place-1")

    def test_resolves_overlay_form_not_the_unmodified_setting_form(self):
        _write_entity(
            self.chronicle_dir / "overlay" / "place-1.md",
            ["id: place-1-overlay", "overlay_of: place-1", "tags: [waypoint, ruined]"],
        )
        result = verbs.get("place-1", self.chronicle_dir)
        self.assertEqual(result["entity"]["tags"], ["waypoint", "ruined"])

    def test_unresolvable_id_raises(self):
        with self.assertRaises(state.StateError):
            verbs.get("no-such-id", self.chronicle_dir)


class FindVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_matches_type_filter(self):
        result = verbs.find(self.chronicle_dir, type="place")
        self.assertIn("place-1", result["results"])

    def test_unmatched_combination_is_empty_not_an_error(self):
        result = verbs.find(self.chronicle_dir, type="organisation")
        self.assertEqual(result["results"], {})


class PartyVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_empty_results_shape(self):
        result = verbs.party(self.chronicle_dir)
        self.assertEqual(result["verb"], "party")
        self.assertEqual(result["results"], {})


class ThreadsVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_empty_results_shape(self):
        result = verbs.threads(self.chronicle_dir)
        self.assertEqual(result["verb"], "threads")
        self.assertEqual(result["results"], [])


class ThreatsVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_empty_results_shape(self):
        result = verbs.threats(self.chronicle_dir)
        self.assertEqual(result["verb"], "threats")
        self.assertEqual(result["results"], {})


class SaveLoadValidateVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_then_load_round_trips(self):
        loaded = verbs.load(self.chronicle_dir)["state"]
        modified = {**loaded, "sessions": loaded["sessions"] + 1}
        verbs.save(modified, self.chronicle_dir)
        reloaded = verbs.load(self.chronicle_dir)["state"]
        self.assertEqual(reloaded["sessions"], loaded["sessions"] + 1)

    def test_validate_reports_success_for_conformant_state(self):
        result = verbs.validate(self.chronicle_dir)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["error"])

    def test_validate_reports_the_specific_violation(self):
        path = self.chronicle_dir / "chronicle.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("sessions: 0", "sessions: -1"))
        result = verbs.validate(self.chronicle_dir)
        self.assertFalse(result["valid"])
        self.assertIn("sessions", result["error"])


class RecapVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_regenerates_recap_md(self):
        result = verbs.recap(self.chronicle_dir, where="a waypoint")
        self.assertEqual(result["verb"], "recap")
        self.assertIn("a waypoint", result["text"])
        written = (self.chronicle_dir / "recap.md").read_text(encoding="utf-8")
        self.assertEqual(written, result["text"])


class AdvanceTimeVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_advances_calendar_by_exactly_the_given_days(self):
        result = verbs.advance_time(self.chronicle_dir, 14, seed=1)
        self.assertEqual(result["verb"], "advance-time")
        self.assertEqual(result["calendar"]["day"], 14)

    def test_negative_days_raises(self):
        with self.assertRaises(ValueError):
            verbs.advance_time(self.chronicle_dir, -1)

    def test_persists_the_advanced_calendar(self):
        verbs.advance_time(self.chronicle_dir, 7, seed=1)
        reloaded = verbs.load(self.chronicle_dir)["state"]
        self.assertEqual(reloaded["calendar"]["day"], 7)


class ThreatCheckVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))
        _write_entity(
            self.chronicle_dir / "setting" / "nemesis-1.md",
            [
                "id: nemesis-1",
                "type: character",
                "name: Nemesis One",
                "setting: example-setting",
                "status: complete",
                "role: nemesis",
                "threat:",
                "  imminence: 4",
                '  connection: "left them for dead"',
            ],
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_deterministic_result_for_a_fixed_seed(self):
        first = verbs.threat_check(self.chronicle_dir, "nemesis-1", seed=1)
        second = verbs.threat_check(self.chronicle_dir, "nemesis-1", seed=1)
        self.assertEqual(first, second)
        self.assertIn(first["activated"], (True, False))

    def test_unknown_threat_id_raises(self):
        with self.assertRaises(state.StateError):
            verbs.threat_check(self.chronicle_dir, "no-such-threat")


class LogVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = _make_chronicle_dir(pathlib.Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_requires_exactly_one_of_last_or_since(self):
        with self.assertRaises(ValueError):
            verbs.log(self.chronicle_dir, "test-chronicle")
        with self.assertRaises(ValueError):
            verbs.log(self.chronicle_dir, "test-chronicle", last=1, since="beat-1")

    def test_last_returns_empty_list_for_no_entries(self):
        result = verbs.log(self.chronicle_dir, "test-chronicle", last=5)
        self.assertEqual(result["entries"], [])


class RollVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "chronicle_state.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def test_roll_returns_expected_shape(self):
        result = verbs.roll(sides=100, seed=1, state_path=self.path)
        self.assertEqual(result["verb"], "roll")
        self.assertEqual(result["sides"], 100)
        self.assertEqual(result["seed"], 1)
        self.assertTrue(result["state_written"])
        self.assertGreaterEqual(result["result"], 1)
        self.assertLessEqual(result["result"], 100)

    def test_roll_persists_last_roll_to_state(self):
        result = verbs.roll(sides=100, seed=1, state_path=self.path)
        loaded = state.load(self.path)
        self.assertEqual(loaded["last_roll"]["result"], result["result"])
        self.assertEqual(loaded["last_roll"]["sides"], 100)
        self.assertEqual(loaded["last_roll"]["seed"], 1)

    def test_roll_is_deterministic_given_same_seed_and_state_persists_each_time(self):
        first = verbs.roll(sides=100, seed=42, state_path=self.path)
        second = verbs.roll(sides=100, seed=42, state_path=self.path)
        self.assertEqual(first["result"], second["result"])

    def test_invalid_sides_raises_value_error(self):
        with self.assertRaises(ValueError):
            verbs.roll(sides=0, state_path=self.path)


class OpposedTestVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name)
        self._cwd = pathlib.Path.cwd()
        os.chdir(self.path)

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_returns_expected_shape(self):
        result = verbs.opposed_test(skill=70, opponent=30, seed=1)
        self.assertEqual(result["verb"], "opposed-test")
        self.assertEqual(result["skill"], 70)
        self.assertEqual(result["opponent"], 30)
        self.assertEqual(result["effective_pct"], 90)
        self.assertIn("roll", result)
        self.assertIn("success", result)
        self.assertIn("degrees", result)
        self.assertIn("wyrd", result)

    def test_performs_no_state_write(self):
        verbs.opposed_test(skill=70, opponent=30, seed=1)
        self.assertFalse((self.path / "chronicle_state.yaml").exists())

    def test_deterministic_given_same_seed(self):
        first = verbs.opposed_test(skill=70, opponent=30, seed=42)
        second = verbs.opposed_test(skill=70, opponent=30, seed=42)
        self.assertEqual(first, second)

    def test_passes_declaration_and_helper_through(self):
        result = verbs.opposed_test(
            skill=50, opponent=50, declaration="specific", helper_skill=45, seed=1
        )
        self.assertEqual(result["effective_pct"], 64)


class DeclarationBonusVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.declaration_bonus("specific")
        self.assertEqual(result["verb"], "declaration-bonus")
        self.assertEqual(result["category"], "specific")
        self.assertEqual(result["bonus"], 10)
        self.assertFalse(result["no_roll"])

    def test_removes_risk_shape(self):
        result = verbs.declaration_bonus("removes_risk")
        self.assertIsNone(result["bonus"])
        self.assertTrue(result["no_roll"])


class OraclePromptVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.oracle_prompt("oracle-prompt-npc-objective", seed=1)
        self.assertEqual(result["verb"], "oracle-prompt")
        self.assertEqual(result["family"], "oracle-prompt-npc-objective")
        self.assertIn(result["roll"], range(1, 101))
        self.assertTrue(result["effect"])
        self.assertTrue(result["description"])
        self.assertNotIn("state_written", result)

    def test_deterministic_given_same_seed(self):
        first = verbs.oracle_prompt("oracle-prompt-complication", seed=7)
        second = verbs.oracle_prompt("oracle-prompt-complication", seed=7)
        self.assertEqual(first["roll"], second["roll"])
        self.assertEqual(first["effect"], second["effect"])

    def test_unrecognized_family_raises(self):
        with self.assertRaises(ValueError):
            verbs.oracle_prompt("oracle-prompt-weather", seed=1)

    def test_performs_no_state_write(self):
        # verbs.oracle_prompt takes no state_path parameter at all -- confirms it can't
        # touch state.py the way verbs.roll does.
        self.assertNotIn("state_path", verbs.oracle_prompt.__code__.co_varnames)


class OracleAnswerVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.oracle_answer("Even", seed=1)
        self.assertEqual(result["verb"], "oracle-answer")
        self.assertEqual(result["band"], "Even")
        self.assertIn(result["roll"], range(1, 101))
        self.assertIn(result["outcome"], ("exceptional_yes", "yes", "no", "exceptional_no"))
        self.assertIn(result["wyrd"], ("ill_omen", "fair_omen", "none"))
        self.assertNotIn("state_written", result)

    def test_deterministic_given_same_seed(self):
        first = verbs.oracle_answer("Likely", seed=7)
        second = verbs.oracle_answer("Likely", seed=7)
        self.assertEqual(first["roll"], second["roll"])
        self.assertEqual(first["outcome"], second["outcome"])
        self.assertEqual(first["wyrd"], second["wyrd"])

    def test_unrecognized_band_raises(self):
        with self.assertRaises(ValueError):
            verbs.oracle_answer("Certain", seed=1)

    def test_performs_no_state_write(self):
        # verbs.oracle_answer takes no state_path parameter at all -- confirms it can't
        # touch state.py the way verbs.roll does.
        self.assertNotIn("state_path", verbs.oracle_answer.__code__.co_varnames)


class AssistanceBonusVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.assistance_bonus(45)
        self.assertEqual(result["verb"], "assistance-bonus")
        self.assertEqual(result["helper_skill"], 45)
        self.assertTrue(result["can_attempt"])
        self.assertEqual(result["bonus"], 4)


class GroupTestVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.group_test(
            member_skills=[70, 45, 30], mode="most_capable", opponent=50, seed=1
        )
        self.assertEqual(result["verb"], "group-test")
        self.assertEqual(result["selected_skill"], 70)
        self.assertEqual(result["mode"], "most_capable")
        self.assertEqual(result["member_skills"], [70, 45, 30])


class ResolveExtendedIntervalVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.resolve_extended_interval(
            skill=45, opponent=50, progress=2, target=4, seed=1
        )
        self.assertEqual(result["verb"], "extended-task-interval")
        self.assertEqual(result["target"], 4)
        self.assertIn("gained", result)
        self.assertIn("done", result)


class CharacterVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "aria.md"

    def tearDown(self):
        self._tmp.cleanup()

    def test_save_then_load_round_trip(self):
        verbs.character_save(path=self.path, frontmatter={"id": "aria"}, body="Prose.\n")
        loaded = verbs.character_load(path=self.path)
        self.assertEqual(loaded["verb"], "character-load")
        self.assertEqual(loaded["frontmatter"], {"id": "aria"})
        self.assertEqual(loaded["body"], "Prose.\n")


class SkillScaleVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.skill_scale()
        self.assertEqual(result["verb"], "skill-scale")
        self.assertEqual(result["open_value"], 25)
        self.assertEqual(result["advance_step"], 5)
        self.assertEqual(result["untrained"], 10)


class ValidateAllocationVerbTest(unittest.TestCase):
    def test_accepted_allocation_shape(self):
        career_data = {"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True}
        actions = [
            {"action": "open", "skill": "stealth"},
            {"action": "open", "skill": "swordplay"},
        ] + [{"action": "raise", "skill": "stealth"}] * 6
        result = verbs.validate_allocation(actions, career_data)
        self.assertEqual(result["verb"], "validate-allocation")
        self.assertTrue(result["valid"])
        self.assertEqual(result["skills"]["stealth"], 55)

    def test_rejected_allocation_shape(self):
        career_data = {"skills": {"stealth": 55}, "entry_point": True}
        result = verbs.validate_allocation([], career_data)
        self.assertEqual(result["verb"], "validate-allocation")
        self.assertFalse(result["valid"])
        self.assertIn("error", result)


class CreateCharacterVerbTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def test_accepted_creation_shape(self):
        path = pathlib.Path(self._tmp.name) / "aria.md"
        career_data = {"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True}
        actions = [
            {"action": "open", "skill": "stealth"},
            {"action": "open", "skill": "swordplay"},
        ] + [{"action": "raise", "skill": "stealth"}] * 6
        result = verbs.create_character(
            path=path,
            name="Aria",
            career_data=career_data,
            actions=actions,
            loyalty="x",
            mortality="standard",
            fault_line="x",
        )
        self.assertEqual(result["verb"], "create-character")
        self.assertTrue(result["valid"])
        self.assertTrue(path.exists())

    def test_rejected_creation_writes_nothing(self):
        path = pathlib.Path(self._tmp.name) / "bad.md"
        career_data = {"skills": {"stealth": 55}, "entry_point": True}
        result = verbs.create_character(
            path=path,
            name="X",
            career_data=career_data,
            actions=[],
            loyalty="x",
            mortality="standard",
            fault_line="x",
        )
        self.assertFalse(result["valid"])
        self.assertFalse(path.exists())


class TrackVerbTest(unittest.TestCase):
    def test_returns_expected_shape(self):
        result = verbs.track(value=3, mechanism="taint", delta=1)
        self.assertEqual(result["verb"], "track")
        self.assertEqual(result["mechanism"], "taint")
        self.assertEqual(result["label"], "taint")
        self.assertEqual(result["value"], 4)

    def test_untrackable_mechanism_is_a_structured_error(self):
        result = verbs.track(value=3, mechanism="skills", delta=1)
        self.assertIn("error", result)

    def test_disabled_mechanism_is_a_structured_error_not_a_silent_no_op(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"disable": ["taint"]})])
        result = verbs.track(value=3, mechanism="taint", delta=1, resolved=resolved)
        self.assertIn("error", result)
        self.assertIn("disabled", result["error"]["reason"])

    def test_renamed_mechanism_reports_the_setting_word_not_the_internal_one(self):
        resolved = overrides.resolve([("engine", {}), ("setting", {"rename": {"taint": "shadow"}})])
        result = verbs.track(value=3, mechanism="taint", delta=1, resolved=resolved)
        self.assertEqual(result["mechanism"], "taint")
        self.assertEqual(result["label"], "shadow")


if __name__ == "__main__":
    unittest.main()
