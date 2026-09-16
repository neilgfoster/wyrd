"""Tests for engine/wyrd/generation_checks.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_scenario, generation, generation_checks  # noqa: E402

FORBIDDEN_TONE = {"prophecy": "forbidden", "scale_drift": "suppressed"}
ALLOWED_TONE = {"prophecy": "rare", "scale_drift": "allowed"}


def _live_play_request(**overrides) -> dict:
    base = generation.new_request(
        scale="beat",
        mode="live-play",
        setting_ref="a-setting",
        tone_contract=FORBIDDEN_TONE,
        written_for=4,
        threads=[{"id": "the-ledger", "heat": 2}],
        threat_state=[{"entity_id": "the-cartel", "imminence": 3, "clues_progress": 1}],
        danger_rating=3,
        era="era-1",
    )
    base.update(overrides)
    return base


def _setting_authoring_request(**overrides) -> dict:
    base = generation.new_request(
        scale="beat",
        mode="setting-authoring",
        setting_ref="a-setting",
        tone_contract=FORBIDDEN_TONE,
        voice="terse, unsentimental",
        existing_entities=["the-old-keep"],
        invention_permitted=True,
    )
    base.update(overrides)
    return base


def _candidate(**overrides) -> dict:
    base = {
        "danger": 2,
        "named_entities": [],
        "prophecy_claim": "none",
        "threat_updates": [],
        "coincidences": [],
    }
    base.update(overrides)
    return base


class EntityMembershipTests(unittest.TestCase):
    """User Story 1: FR-007, entity-membership."""

    def test_unknown_entity_is_rejected(self) -> None:
        request = _live_play_request()
        candidate = _candidate(named_entities=["a-stranger"])
        entry = generation_checks.check_entity_membership(
            request, candidate, known_entities=["the-old-keep"]
        )
        self.assertEqual(entry["rule"], "FR-007")
        self.assertEqual(entry["outcome"], "reject")
        self.assertIn("a-stranger", entry["detail"])

    def test_known_setting_entity_passes(self) -> None:
        request = _live_play_request()
        candidate = _candidate(named_entities=["the-old-keep"])
        entry = generation_checks.check_entity_membership(
            request, candidate, known_entities=["the-old-keep"]
        )
        self.assertEqual(entry["outcome"], "pass")

    def test_entity_grounded_in_live_thread_passes(self) -> None:
        request = _live_play_request()
        candidate = _candidate(named_entities=["the-ledger"])
        entry = generation_checks.check_entity_membership(request, candidate, known_entities=[])
        self.assertEqual(entry["outcome"], "pass")

    def test_entity_grounded_in_threat_state_passes(self) -> None:
        request = _live_play_request()
        candidate = _candidate(named_entities=["the-cartel"])
        entry = generation_checks.check_entity_membership(request, candidate, known_entities=[])
        self.assertEqual(entry["outcome"], "pass")

    def test_labelled_invention_passes_when_permitted(self) -> None:
        request = _setting_authoring_request()
        candidate = _candidate(
            named_entities=[{"name": "a-new-smuggler", "invented": True}],
        )
        entry = generation_checks.check_entity_membership(
            request, candidate, known_entities=["the-old-keep"]
        )
        self.assertEqual(entry["outcome"], "pass")

    def test_unlabelled_invention_is_rejected_even_when_permitted(self) -> None:
        request = _setting_authoring_request()
        candidate = _candidate(
            named_entities=[{"name": "a-new-smuggler", "invented": False}],
        )
        entry = generation_checks.check_entity_membership(
            request, candidate, known_entities=["the-old-keep"]
        )
        self.assertEqual(entry["outcome"], "reject")


class ProphecyTests(unittest.TestCase):
    """User Story 2: FR-008, tone/prophecy, and its detail requirement."""

    def test_destiny_claim_rejected_under_forbidden(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate(prophecy_claim="destiny")
        entry = generation_checks.check_prophecy(request, candidate)
        self.assertEqual(entry["outcome"], "reject")
        self.assertIn("destiny", entry["detail"])

    def test_hidden_bloodline_and_prewritten_fate_also_rejected(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        for claim in ("hidden_bloodline", "prewritten_fate"):
            with self.subTest(claim=claim):
                candidate = _candidate(prophecy_claim=claim)
                entry = generation_checks.check_prophecy(request, candidate)
                self.assertEqual(entry["outcome"], "reject")

    def test_same_claims_pass_under_rare_or_central(self) -> None:
        for prophecy in ("rare", "central"):
            with self.subTest(prophecy=prophecy):
                request = _live_play_request(
                    tone_contract={"prophecy": prophecy, "scale_drift": "allowed"}
                )
                candidate = _candidate(prophecy_claim="destiny")
                entry = generation_checks.check_prophecy(request, candidate)
                self.assertEqual(entry["outcome"], "pass")

    def test_known_to_player_understood_rejected_under_forbidden(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate(
            threat_updates=[
                {
                    "entity_id": "the-cartel",
                    "imminence_delta": 0,
                    "ambient_add": [],
                    "connection": None,
                    "known_to_player": "understood",
                }
            ]
        )
        entry = generation_checks.check_prophecy(request, candidate)
        self.assertEqual(entry["outcome"], "reject")
        self.assertIn("the-cartel", entry["detail"])

    def test_clean_candidate_passes(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate()
        entry = generation_checks.check_prophecy(request, candidate)
        self.assertEqual(entry["outcome"], "pass")


class DangerBandTests(unittest.TestCase):
    """User Story 2: FR-009, reusing the engine's existing danger-scaling arithmetic."""

    def test_danger_above_rating_is_rejected(self) -> None:
        request = _live_play_request(written_for=4, danger_rating=3)
        candidate = _candidate(danger=5)
        entry = generation_checks.check_danger_band(request, candidate)
        self.assertEqual(entry["outcome"], "reject")
        self.assertIn("5", entry["detail"])
        self.assertIn("3", entry["detail"])

    def test_danger_at_or_below_rating_passes(self) -> None:
        request = _live_play_request(written_for=4, danger_rating=3)
        candidate = _candidate(danger=3)
        entry = generation_checks.check_danger_band(request, candidate)
        self.assertEqual(entry["outcome"], "pass")

    def test_matches_existing_scale_danger_output(self) -> None:
        """SC-002: identical banding numbers to the existing arithmetic, not a hand-computed one."""
        request = _live_play_request(written_for=6, danger_rating=10)
        candidate = _candidate(danger=4)
        expected = corpus_scenario.scale_danger(
            {"danger": 4, "written_for": 6}, request["written_for"]
        )
        record = {"danger": candidate["danger"], "written_for": request["written_for"]}
        actual = corpus_scenario.scale_danger(record, request["written_for"])
        self.assertEqual(actual, expected)
        entry = generation_checks.check_danger_band(request, candidate)
        self.assertEqual(entry["outcome"], "pass")


class ScaleDriftTests(unittest.TestCase):
    """User Story 3: FR-010, reject vs. narrow under scale_drift: suppressed."""

    def test_existing_threat_escalation_is_narrowed(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate(
            threat_updates=[
                {
                    "entity_id": "the-cartel",
                    "imminence_delta": 3,
                    "ambient_add": [],
                    "connection": None,
                }
            ]
        )
        entry = generation_checks.check_scale_drift(request, candidate)
        self.assertEqual(entry["outcome"], "narrowed")
        self.assertIn("1", entry["detail"])

    def test_new_connectionless_threat_is_rejected(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate(
            threat_updates=[
                {
                    "entity_id": None,
                    "imminence_delta": 1,
                    "ambient_add": [],
                    "connection": None,
                }
            ]
        )
        entry = generation_checks.check_scale_drift(request, candidate)
        self.assertEqual(entry["outcome"], "reject")

    def test_new_threat_with_connection_is_not_rejected_by_connection_leg(self) -> None:
        request = _live_play_request(tone_contract=FORBIDDEN_TONE)
        candidate = _candidate(
            threat_updates=[
                {
                    "entity_id": None,
                    "imminence_delta": 1,
                    "ambient_add": [],
                    "connection": "an old debt to the player character",
                }
            ]
        )
        entry = generation_checks.check_scale_drift(request, candidate)
        self.assertEqual(entry["outcome"], "pass")

    def test_never_gates_under_scale_drift_allowed(self) -> None:
        request = _live_play_request(tone_contract={"prophecy": "rare", "scale_drift": "allowed"})
        for candidate in (
            _candidate(
                threat_updates=[
                    {
                        "entity_id": "the-cartel",
                        "imminence_delta": 3,
                        "ambient_add": [],
                        "connection": None,
                    }
                ]
            ),
            _candidate(
                threat_updates=[
                    {"entity_id": None, "imminence_delta": 1, "ambient_add": [], "connection": None}
                ]
            ),
        ):
            with self.subTest(candidate=candidate):
                entry = generation_checks.check_scale_drift(request, candidate)
                self.assertEqual(entry["outcome"], "pass")


class FavourableCoincidenceTests(unittest.TestCase):
    """User Story 2: FR-011, favourable coincidence."""

    def test_ungrounded_coincidence_is_rejected(self) -> None:
        request = _live_play_request()
        candidate = _candidate(
            coincidences=[{"claim": "an ally happens to be present", "supported_by": None}]
        )
        entry = generation_checks.check_favourable_coincidence(request, candidate)
        self.assertEqual(entry["outcome"], "reject")

    def test_coincidence_not_in_request_state_is_rejected(self) -> None:
        request = _live_play_request()
        candidate = _candidate(
            coincidences=[{"claim": "a clue surfaces unprompted", "supported_by": "a-stranger"}]
        )
        entry = generation_checks.check_favourable_coincidence(request, candidate)
        self.assertEqual(entry["outcome"], "reject")

    def test_coincidence_grounded_in_live_thread_passes(self) -> None:
        request = _live_play_request()
        candidate = _candidate(
            coincidences=[
                {"claim": "the contact was already watching", "supported_by": "the-ledger"}
            ]
        )
        entry = generation_checks.check_favourable_coincidence(request, candidate)
        self.assertEqual(entry["outcome"], "pass")

    def test_coincidence_grounded_in_existing_entity_passes(self) -> None:
        request = _setting_authoring_request()
        candidate = _candidate(
            coincidences=[{"claim": "the keep was already watched", "supported_by": "the-old-keep"}]
        )
        entry = generation_checks.check_favourable_coincidence(request, candidate)
        self.assertEqual(entry["outcome"], "pass")


class RunChecksTests(unittest.TestCase):
    """FR-008 spec requirement: the aggregator runs all five, in order, no logic of its own."""

    def test_returns_five_entries_in_order_for_a_clean_candidate(self) -> None:
        request = _live_play_request(danger_rating=10)
        candidate = _candidate(danger=2)
        entries = generation_checks.run_checks(request, candidate, known_entities=[])
        self.assertEqual(
            [entry["rule"] for entry in entries],
            ["FR-007", "FR-008", "FR-009", "FR-010", "FR-011"],
        )
        self.assertTrue(all(entry["outcome"] == "pass" for entry in entries))

    def test_output_matches_new_result_checks_field_unchanged(self) -> None:
        request = _live_play_request(danger_rating=10)
        candidate = _candidate(danger=2)
        checks = generation_checks.run_checks(request, candidate, known_entities=[])
        result = generation.new_result(candidate, checks=checks)
        self.assertEqual(result["checks"], checks)


if __name__ == "__main__":
    unittest.main()
