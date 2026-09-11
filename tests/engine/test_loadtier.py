"""Tests for engine/wyrd/loadtier.py: always-tier query, on-demand fetch/search, recap.md.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import loadtier  # noqa: E402


def _character(entity_id: str, **overrides) -> dict:
    base = {
        "id": entity_id,
        "type": "character",
        "name": entity_id.replace("-", " ").title(),
        "setting": "example-setting",
        "status": "complete",
    }
    base.update(overrides)
    return base


def _thread(entity_id: str, heat: int, **overrides) -> dict:
    base = {
        "id": entity_id,
        "type": "thread",
        "name": entity_id.replace("-", " ").title(),
        "setting": "example-setting",
        "status": "open",
        "heat": heat,
    }
    base.update(overrides)
    return base


def _sample_entities() -> dict[str, dict]:
    pc = _character("the-player", role="player")
    with_party_1 = _character("ally-one", role="companion", status="with-party")
    with_party_2 = _character("ally-two", role="companion", status="with-party")
    departed = _character("ally-three", role="companion", status="departed")
    hot_thread = _thread("the-fire", 5)
    warm_thread = _thread("the-debt", 3)
    cold_thread = _thread("the-rumour", 2)
    entities = {
        e["id"]: e
        for e in (pc, with_party_1, with_party_2, departed, hot_thread, warm_thread, cold_thread)
    }
    return entities


class AlwaysTierTest(unittest.TestCase):
    def test_returns_player_companions_and_hot_threads(self):
        entities = _sample_entities()
        tier = loadtier.always_tier(entities)
        self.assertEqual(tier["player_character"]["id"], "the-player")
        self.assertEqual(set(tier["companions"]), {"ally-one", "ally-two"})
        self.assertEqual(set(tier["threads"]), {"the-fire", "the-debt"})

    def test_status_or_heat_change_changes_result_on_next_call(self):
        entities = _sample_entities()
        tier = loadtier.always_tier(entities)
        self.assertIn("ally-one", tier["companions"])

        entities["ally-one"]["status"] = "departed"
        entities["the-debt"]["heat"] = 2

        tier_again = loadtier.always_tier(entities)
        self.assertNotIn("ally-one", tier_again["companions"])
        self.assertNotIn("the-debt", tier_again["threads"])

    def test_empty_companions_and_threads_is_valid(self):
        pc = _character("the-player", role="player")
        entities = {pc["id"]: pc}
        tier = loadtier.always_tier(entities)
        self.assertEqual(tier["player_character"]["id"], "the-player")
        self.assertEqual(tier["companions"], {})
        self.assertEqual(tier["threads"], {})

    def test_no_player_character_returns_none(self):
        entities = {"ally-one": _character("ally-one", role="companion", status="with-party")}
        tier = loadtier.always_tier(entities)
        self.assertIsNone(tier["player_character"])

    def test_two_players_raises(self):
        entities = {
            "pc-one": _character("pc-one", role="player"),
            "pc-two": _character("pc-two", role="player"),
        }
        with self.assertRaises(ValueError):
            loadtier.always_tier(entities)


class LookupTest(unittest.TestCase):
    def test_lookup_returns_full_frontmatter(self):
        entities = _sample_entities()
        self.assertEqual(loadtier.lookup("ally-three", entities)["status"], "departed")

    def test_lookup_absent_id_returns_none(self):
        entities = _sample_entities()
        self.assertIsNone(loadtier.lookup("nobody", entities))


class SearchTest(unittest.TestCase):
    def test_search_matches_frontmatter_value(self):
        entities = _sample_entities()
        results = loadtier.search("departed", entities)
        self.assertEqual(results, ["ally-three"])

    def test_search_matches_body_text(self):
        entities = _sample_entities()
        bodies = {"the-rumour": "a whisper about a burned mill"}
        results = loadtier.search("burned mill", entities, bodies)
        self.assertEqual(results, ["the-rumour"])

    def test_search_is_case_insensitive(self):
        entities = _sample_entities()
        self.assertEqual(loadtier.search("DEPARTED", entities), ["ally-three"])

    def test_empty_term_matches_nothing(self):
        entities = _sample_entities()
        self.assertEqual(loadtier.search("", entities), [])


class GenerateRecapTest(unittest.TestCase):
    def test_includes_supplied_sections_and_present_companions(self):
        entities = _sample_entities()
        text = loadtier.generate_recap(
            entities,
            {},
            where="the old quarter, three days after the fire",
            changes=["the mill burned"],
            body_mind="tired but steady",
        )
        self.assertIn("the old quarter, three days after the fire", text)
        self.assertIn("the mill burned", text)
        self.assertIn("tired but steady", text)
        self.assertIn("Ally One", text)
        self.assertIn("Ally Two", text)

    def test_caps_at_three_hottest_open_threads(self):
        entities = _sample_entities()
        for i in range(5):
            entities[f"thread-{i}"] = _thread(f"thread-{i}", heat=4 + i)
        text = loadtier.generate_recap(entities, {})
        threads_section = text.split("## Hottest threads")[1].split("## What changed")[0]
        lines = [line for line in threads_section.splitlines() if line.startswith("- ")]
        self.assertEqual(len(lines), 3)

    def test_no_open_threads_names_none_not_placeholders(self):
        entities = {"the-player": _character("the-player", role="player")}
        text = loadtier.generate_recap(entities, {})
        threads_section = text.split("## Hottest threads")[1].split("## What changed")[0]
        self.assertIn(loadtier._RECAP_PLACEHOLDER, threads_section)

    def test_omitted_sections_fall_back_to_placeholder(self):
        entities = {"the-player": _character("the-player", role="player")}
        text = loadtier.generate_recap(entities, {})
        self.assertIn(loadtier._RECAP_PLACEHOLDER, text)

    def test_word_count_near_two_hundred_for_typical_chronicle(self):
        entities = _sample_entities()
        text = loadtier.generate_recap(
            entities,
            {},
            where="the old quarter, three days after the fire, in the third week of autumn",
            changes=[
                "the mill burned",
                "a companion left the party",
                "word came of a debt called in",
            ]
            * 8,
            body_mind="tired but steady, favouring the left arm since the fall from the wall",
        )
        word_count = len(text.split())
        self.assertGreater(word_count, 100)
        self.assertLess(word_count, 300)


class RecapCloseStepTest(unittest.TestCase):
    def test_writes_recap_file(self):
        import tempfile

        entities = _sample_entities()
        with tempfile.TemporaryDirectory() as tmp:
            recap_path = pathlib.Path(tmp) / "recap.md"
            step = loadtier.recap_close_step(entities, {}, recap_path, where="the old quarter")
            step()
            self.assertTrue(recap_path.exists())
            self.assertIn("the old quarter", recap_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
