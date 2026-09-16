"""Tests for engine/wyrd/generation.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import generation  # noqa: E402

TONE_CONTRACT = {"prophecy": "forbidden", "scale_drift": "suppressed"}


def _live_play_request(**overrides) -> dict:
    base = generation.new_request(
        scale="beat",
        mode="live-play",
        setting_ref="a-setting",
        tone_contract=TONE_CONTRACT,
        written_for=4,
        threads=[{"id": "t1", "heat": 2}],
        danger_rating=3,
        era="era-1",
    )
    base.update(overrides)
    return base


def _setting_authoring_request(**overrides) -> dict:
    base = generation.new_request(
        scale="campaign-spine",
        mode="setting-authoring",
        setting_ref="a-setting",
        tone_contract=TONE_CONTRACT,
        voice="terse, unsentimental",
        existing_entities=[],
        invention_permitted=True,
    )
    base.update(overrides)
    return base


class ScaleAndModeValidationTests(unittest.TestCase):
    """User Story 1: one shape validates correctly across all three scales."""

    def test_beat_missing_written_for_is_rejected(self) -> None:
        request = _live_play_request(written_for=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_written_for")

    def test_arc_missing_written_for_is_rejected(self) -> None:
        request = _live_play_request(scale="arc", written_for=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_written_for")

    def test_campaign_spine_live_play_missing_written_for_is_rejected(self) -> None:
        # Edge case: campaign-spine in live-play behaves as an ordinary live-play arc request.
        request = _live_play_request(scale="campaign-spine", written_for=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_written_for")

    def test_campaign_spine_setting_authoring_without_written_for_is_accepted(self) -> None:
        request = _setting_authoring_request(written_for=None)
        self.assertIsNone(generation.validate_request(request))

    def test_missing_scale_is_rejected(self) -> None:
        request = _live_play_request(scale=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "invalid_scale")

    def test_missing_mode_is_rejected(self) -> None:
        request = _live_play_request(mode=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "invalid_mode")

    def test_missing_setting_ref_is_rejected(self) -> None:
        request = _live_play_request(setting_ref=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_setting_ref")

    def test_missing_tone_contract_is_rejected(self) -> None:
        request = _live_play_request(tone_contract=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_tone_contract")


class CampaignSpineAliasTests(unittest.TestCase):
    """FR-002/SC-002: campaign-spine is an arc-with-no-parent alias, never a fourth type."""

    def test_campaign_spine_with_no_parent_is_confirmed(self) -> None:
        request = _setting_authoring_request()
        self.assertTrue(generation.is_campaign_spine_shape(request))

    def test_campaign_spine_with_a_parent_is_rejected(self) -> None:
        request = _setting_authoring_request(parent="some-arc")
        self.assertFalse(generation.is_campaign_spine_shape(request))

    def test_non_campaign_spine_scale_is_not_a_campaign_spine_shape(self) -> None:
        request = _live_play_request(scale="arc")
        self.assertFalse(generation.is_campaign_spine_shape(request))


class LivePlayGroundingTests(unittest.TestCase):
    """User Story 2: a live-play request with no threads and no threat state is rejected."""

    def test_no_threads_and_no_threat_state_is_rejected(self) -> None:
        request = _live_play_request(threads=[], threat_state=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "no_grounding_state")

    def test_one_live_thread_passes_grounding_check(self) -> None:
        request = _live_play_request(threads=[{"id": "t1", "heat": 1}])
        self.assertIsNone(generation.validate_request(request))

    def test_threat_state_alone_passes_grounding_check(self) -> None:
        request = _live_play_request(
            threads=[], threat_state=[{"entity_id": "threat-1", "imminence": 4}]
        )
        self.assertIsNone(generation.validate_request(request))

    def test_missing_danger_rating_is_rejected(self) -> None:
        request = _live_play_request(danger_rating=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_danger_rating")

    def test_missing_era_is_rejected(self) -> None:
        request = _live_play_request(era=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_era")


class SettingAuthoringPermissionTests(unittest.TestCase):
    """User Story 3: setting-authoring without the Q3 grant is rejected."""

    def test_absent_invention_permitted_is_rejected(self) -> None:
        request = _setting_authoring_request(invention_permitted=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "invention_not_permitted")

    def test_false_invention_permitted_is_rejected(self) -> None:
        request = _setting_authoring_request(invention_permitted=False)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "invention_not_permitted")

    def test_true_invention_permitted_with_state_passes(self) -> None:
        request = _setting_authoring_request()
        self.assertIsNone(generation.validate_request(request))

    def test_missing_voice_is_rejected(self) -> None:
        request = _setting_authoring_request(voice=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_voice")

    def test_missing_existing_entities_is_rejected(self) -> None:
        request = _setting_authoring_request(existing_entities=None)
        error = generation.validate_request(request)
        self.assertEqual(error.code, "missing_existing_entities")


class ModeBoundaryInvariantTests(unittest.TestCase):
    """FR-006: the two modes differ only in available state, never which rule would bind output."""

    def test_live_play_request_may_not_carry_setting_authoring_fields(self) -> None:
        for field, value in (
            ("voice", "terse"),
            ("existing_entities", []),
            ("invention_permitted", True),
        ):
            with self.subTest(field=field):
                request = _live_play_request(**{field: value})
                error = generation.validate_request(request)
                self.assertEqual(error.code, "foreign_mode_field")

    def test_setting_authoring_request_may_not_carry_live_play_fields(self) -> None:
        for field, value in (
            ("threads", [{"id": "t1", "heat": 1}]),
            ("threat_state", [{"entity_id": "threat-1", "imminence": 1}]),
            ("danger_rating", 2),
        ):
            with self.subTest(field=field):
                request = _setting_authoring_request(**{field: value})
                error = generation.validate_request(request)
                self.assertEqual(error.code, "foreign_mode_field")

    def test_the_only_difference_between_the_two_valid_modes_is_state_fields(self) -> None:
        # SC-004's own invariant, asserted directly: a minimal valid request of each mode
        # differs only in which of the mode-specific state fields are set -- everything else
        # (scale/setting_ref/tone_contract/written_for handling) is identical, and neither mode
        # carries any field that would gate which anti-inflation rule (FR-007-011, out of scope
        # here) applies -- this module defines no such gating at all.
        live_play = _live_play_request(scale="campaign-spine")
        setting_authoring = _setting_authoring_request()

        mode_specific_fields = set(generation._LIVE_PLAY_FIELDS) | set(
            generation._SETTING_AUTHORING_FIELDS
        )
        shared_fields = set(live_play) - mode_specific_fields

        for field in shared_fields - {"mode", "written_for"}:
            with self.subTest(field=field):
                self.assertEqual(live_play[field], setting_authoring[field])

        # Neither request's shape carries anything that names a downstream rule (FR-007-011) --
        # this module has no such field at all, which is the invariant itself.
        rule_referencing_fields = {"checks", "anti_inflation", "rule"}
        self.assertFalse(rule_referencing_fields & set(live_play))
        self.assertFalse(rule_referencing_fields & set(setting_authoring))

        self.assertIsNone(generation.validate_request(live_play))
        self.assertIsNone(generation.validate_request(setting_authoring))


class ResultShapeTests(unittest.TestCase):
    """FR-007: GenerationResult carries candidate/checks/consumed, checks never populated here."""

    def test_defaults_are_empty_lists(self) -> None:
        result = generation.new_result(candidate={"status": "drafted"})
        self.assertEqual(result["checks"], [])
        self.assertEqual(result["consumed"], [])
        self.assertEqual(result["candidate"], {"status": "drafted"})

    def test_explicit_checks_and_consumed_are_preserved(self) -> None:
        checks = [{"rule": "FR-009", "outcome": "pass", "detail": "within band"}]
        result = generation.new_result(
            candidate={"status": "drafted"}, checks=checks, consumed=["t1"]
        )
        self.assertEqual(result["checks"], checks)
        self.assertEqual(result["consumed"], ["t1"])


if __name__ == "__main__":
    unittest.main()
