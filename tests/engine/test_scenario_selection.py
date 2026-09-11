"""Tests for engine/wyrd/scenario_selection.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import adversary, scenario_selection  # noqa: E402


class RankByHeatTests(unittest.TestCase):
    def test_descending_order(self) -> None:
        threads = [{"id": "cold", "heat": 1}, {"id": "hot", "heat": 4}]
        ranked = scenario_selection.rank_by_heat(threads)
        self.assertEqual([t["id"] for t in ranked], ["hot", "cold"])

    def test_stable_on_tie(self) -> None:
        threads = [{"id": "first", "heat": 2}, {"id": "second", "heat": 2}]
        ranked = scenario_selection.rank_by_heat(threads)
        self.assertEqual([t["id"] for t in ranked], ["first", "second"])


THREADS = [
    {"id": "the-one-who-paid", "hooks": ["money", "influence"], "heat": 4},
    {"id": "an-old-debt", "hooks": ["debt"], "heat": 1},
]


class SelectScenarioTests(unittest.TestCase):
    def test_hottest_match_wins(self) -> None:
        candidates = [
            {"id": "corrupt-official", "hooks": ["money"]},
            {"id": "debt-collector", "hooks": ["debt"]},
        ]
        selected = scenario_selection.select_scenario(THREADS, candidates)
        self.assertEqual(selected["id"], "corrupt-official")

    def test_unmatched_candidate_never_beats_a_match(self) -> None:
        candidates = [
            {"id": "corrupt-official", "hooks": ["money"]},
            {"id": "unrelated-heist", "hooks": ["heist"]},
        ]
        selected = scenario_selection.select_scenario(THREADS, candidates)
        self.assertEqual(selected["id"], "corrupt-official")

    def test_deterministic_tie_break_by_earliest_position(self) -> None:
        candidates = [
            {"id": "first", "hooks": ["money"]},
            {"id": "second", "hooks": ["influence"]},
        ]
        # both match "the-one-who-paid" (heat 4) exactly once -- tie
        selected = scenario_selection.select_scenario(THREADS, candidates)
        self.assertEqual(selected["id"], "first")

    def test_none_when_no_candidate_matches(self) -> None:
        candidates = [{"id": "unrelated-heist", "hooks": ["heist"]}]
        self.assertIsNone(scenario_selection.select_scenario(THREADS, candidates))

    def test_none_on_empty_threads(self) -> None:
        candidates = [{"id": "corrupt-official", "hooks": ["money"]}]
        self.assertIsNone(scenario_selection.select_scenario([], candidates))

    def test_none_on_empty_candidates(self) -> None:
        self.assertIsNone(scenario_selection.select_scenario(THREADS, []))


class ScaleEncountersTests(unittest.TestCase):
    def test_unchanged_ratio(self) -> None:
        scenario = {"written_for": 4, "encounters": [{"written_count": 4}]}
        scaled = scenario_selection.scale_encounters(scenario, danger=4, party=4)
        self.assertEqual(scaled["encounters"][0]["scaled_count"], 4)
        self.assertEqual(scaled["encounters"][0]["written_count"], 4)

    def test_matches_adversary_scaled_count_exactly(self) -> None:
        scenario = {"written_for": 4, "encounters": [{"written_count": 3}]}
        scaled = scenario_selection.scale_encounters(scenario, danger=5, party=6)
        expected = adversary.scaled_count(3, 5, 6, 4)
        self.assertEqual(scaled["encounters"][0]["scaled_count"], expected)

    def test_empty_encounters_list(self) -> None:
        scenario = {"written_for": 4, "encounters": []}
        scaled = scenario_selection.scale_encounters(scenario, danger=4, party=4)
        self.assertEqual(scaled["encounters"], [])

    def test_other_fields_unchanged(self) -> None:
        scenario = {"id": "corrupt-official", "written_for": 4, "encounters": []}
        scaled = scenario_selection.scale_encounters(scenario, danger=4, party=4)
        self.assertEqual(scaled["id"], "corrupt-official")


class RecordSourceTests(unittest.TestCase):
    def test_source_block_attached(self) -> None:
        scenario = {"id": "corrupt-official"}
        recorded = scenario_selection.record_source(
            scenario, adapted_from="a fanzine six-pager", changed="renamed the official"
        )
        self.assertEqual(
            recorded["source"],
            {"adapted_from": "a fanzine six-pager", "changed": "renamed the official"},
        )

    def test_other_fields_unchanged(self) -> None:
        scenario = {"id": "corrupt-official", "hooks": ["money"]}
        recorded = scenario_selection.record_source(scenario, adapted_from="x", changed="y")
        self.assertEqual(recorded["id"], "corrupt-official")
        self.assertEqual(recorded["hooks"], ["money"])


if __name__ == "__main__":
    unittest.main()
