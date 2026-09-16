"""Tests for engine/wyrd/generation_pipeline.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import (  # noqa: E402
    arc_selection,
    generation,
    generation_checks,
    generation_commit,
    generation_pipeline,
)


def _live_play_request(**overrides) -> dict:
    base = generation.new_request(
        scale="beat",
        mode="live-play",
        setting_ref="some-setting",
        tone_contract={"prophecy": "rare", "scale_drift": "allowed"},
        written_for=4,
        threads=[{"id": "thread-a"}],
        danger_rating=30,
        era="present",
    )
    base.update(overrides)
    return base


def _setting_authoring_request(**overrides) -> dict:
    base = generation.new_request(
        scale="beat",
        mode="setting-authoring",
        setting_ref="some-setting",
        tone_contract={"prophecy": "rare", "scale_drift": "allowed"},
        voice="terse",
        existing_entities=["a-known-place"],
        invention_permitted=True,
    )
    base.update(overrides)
    return base


class SelectGroundingTests(unittest.TestCase):
    def test_no_model_response_parameter(self) -> None:
        # FR-020: the no-model steps accept no model-response argument at all -- an extra
        # positional argument is a TypeError from Python's own signature checking.
        with self.assertRaises(TypeError):
            generation_pipeline.select_grounding(_live_play_request(), "not a model response")

    def test_deterministic_over_request_grounding(self) -> None:
        request = _live_play_request()
        first = generation_pipeline.select_grounding(request)
        second = generation_pipeline.select_grounding(request)
        self.assertEqual(first, second)
        self.assertEqual(first["consumed"], ["thread-a"])
        self.assertEqual(first["selected_candidates"], [])

    def test_setting_authoring_grounds_on_existing_entities(self) -> None:
        selection = generation_pipeline.select_grounding(_setting_authoring_request())
        self.assertEqual(selection["consumed"], ["a-known-place"])

    def test_empty_grounding_never_raises(self) -> None:
        request = _live_play_request(threads=[], threat_state=[{"entity_id": "threat-a"}])
        selection = generation_pipeline.select_grounding(request)
        self.assertEqual(selection["consumed"], ["threat-a"])

    def test_reuses_arc_selection_select_unchanged(self) -> None:
        # A candidate reachable only via arc_selection.select's leads_to fallback -- proving this
        # module calls arc_selection.select's real logic, not a re-derived subset match.
        current = {"id": "prior-beat", "exit": {"leads_to": "[[next-beat]]"}}
        candidates = [{"id": "next-beat", "entry": {"requires_threads": ["some-other-thread"]}}]
        request = _live_play_request(threads=[{"id": "thread-a"}])

        selection = generation_pipeline.select_grounding(
            request, candidate_pool=candidates, current=current
        )
        expected = arc_selection.select({"thread-a"}, candidates, current=current)
        self.assertEqual(selection["selected_candidates"], expected)
        self.assertEqual(selection["selected_candidates"], candidates)


class ComputeStructuralFieldsTests(unittest.TestCase):
    def test_no_model_response_parameter(self) -> None:
        request = _live_play_request()
        selection = generation_pipeline.select_grounding(request)
        with self.assertRaises(TypeError):
            generation_pipeline.compute_structural_fields(request, selection, "not a response")

    def test_danger_matches_request_danger_rating_through_shared_arithmetic(self) -> None:
        # FR-017: reuses generation_checks.check_danger_band's own arithmetic identity --
        # danger_ratio(x, x) == 1, so a candidate built at this step's own danger/written_for
        # bands to exactly danger_rating when check_danger_band later runs.
        request = _live_play_request(danger_rating=30, written_for=4)
        selection = generation_pipeline.select_grounding(request)
        structural = generation_pipeline.compute_structural_fields(request, selection)
        candidate = {"danger": structural["danger"], "written_for": structural["written_for"]}
        entry = generation_checks.check_danger_band(request, candidate)
        self.assertEqual(entry["outcome"], "pass")
        self.assertEqual(structural["danger"], 30)

    def test_setting_authoring_has_no_danger_rating_to_band(self) -> None:
        request = _setting_authoring_request()
        selection = generation_pipeline.select_grounding(request)
        structural = generation_pipeline.compute_structural_fields(request, selection)
        self.assertIsNone(structural["danger"])
        self.assertIsNone(structural["written_for"])

    def test_scale_drift_bounds_none_when_allowed(self) -> None:
        request = _live_play_request()
        selection = generation_pipeline.select_grounding(request)
        structural = generation_pipeline.compute_structural_fields(request, selection)
        self.assertIsNone(structural["scale_drift_bounds"])

    def test_scale_drift_bounds_reuse_generation_checks_constants(self) -> None:
        request = _live_play_request(
            tone_contract={"prophecy": "rare", "scale_drift": "suppressed"}
        )
        selection = generation_pipeline.select_grounding(request)
        structural = generation_pipeline.compute_structural_fields(request, selection)
        self.assertEqual(
            structural["scale_drift_bounds"],
            {
                "imminence_delta_max": generation_checks._MAX_SUPPRESSED_IMMINENCE_DELTA,
                "ambient_add_max": generation_checks._MAX_SUPPRESSED_AMBIENT_ADD,
            },
        )

    def test_status_is_drafted(self) -> None:
        request = _live_play_request()
        selection = generation_pipeline.select_grounding(request)
        structural = generation_pipeline.compute_structural_fields(request, selection)
        self.assertEqual(structural["status"], "drafted")


class AssemblePacingTests(unittest.TestCase):
    def _structural(self, request: dict) -> dict:
        selection = generation_pipeline.select_grounding(request)
        return generation_pipeline.compute_structural_fields(request, selection)

    def test_rejects_free_form_string_as_haiku_response(self) -> None:
        # FR-020: the Haiku-tier step accepts a structured mapping only, never free prose.
        request = _live_play_request()
        structural = self._structural(request)
        with self.assertRaises(TypeError):
            generation_pipeline.assemble_pacing(
                request, {}, structural, "this is free-form prose, not structured input"
            )

    def test_merges_structured_haiku_response(self) -> None:
        request = _live_play_request()
        structural = self._structural(request)
        haiku_response = {
            "entry_requires_threads": ["thread-a"],
            "exit_emits_threads": [{"tag": "new-lead", "if": None}],
            "beat_count": 3,
        }
        paced = generation_pipeline.assemble_pacing(request, {}, structural, haiku_response)
        self.assertEqual(paced["entry"], {"requires_threads": ["thread-a"]})
        self.assertEqual(paced["exit"], {"emits_threads": [{"tag": "new-lead", "if": None}]})
        self.assertEqual(paced["beat_count"], 3)
        self.assertEqual(paced["danger"], structural["danger"])

    def test_absent_haiku_fields_default_to_none(self) -> None:
        request = _live_play_request()
        structural = self._structural(request)
        paced = generation_pipeline.assemble_pacing(request, {}, structural, {})
        self.assertIsNone(paced["entry"])
        self.assertIsNone(paced["exit"])
        self.assertIsNone(paced["beat_count"])


class WriteProseTests(unittest.TestCase):
    def test_rejects_non_string_capable_response(self) -> None:
        # FR-020: the capable-tier step is the only step accepting free-form prose -- and
        # requires that it actually be a string, not a structured mapping.
        request = _live_play_request()
        with self.assertRaises(TypeError):
            generation_pipeline.write_prose(request, {}, {"not": "a string"}, [])

    def test_accepts_free_form_prose_and_returns_generation_result_shape(self) -> None:
        request = _live_play_request()
        result = generation_pipeline.write_prose(
            request, {"danger": 30, "written_for": 4}, "The warehouse is quiet.", ["thread-a"]
        )
        self.assertEqual(set(result.keys()), {"candidate", "checks", "consumed"})
        self.assertEqual(result["checks"], [])
        self.assertEqual(result["candidate"]["body"], "The warehouse is quiet.")
        self.assertEqual(result["candidate"]["prophecy_claim"], "none")
        self.assertEqual(result["consumed"], [])

    def test_threads_structured_extraction_through_to_candidate(self) -> None:
        # A real bug this guards: write_prose must not hardcode named_entities/threat_updates/
        # coincidences/prophecy_claim to empty/none regardless of what the caller supplies --
        # doing so would make every one of generation_checks' five checks pass vacuously.
        request = _live_play_request()
        result = generation_pipeline.write_prose(
            request,
            {"danger": 30, "written_for": 4},
            "A stranger asks after the ledger.",
            ["thread-a"],
            named_entities=["thread-a", {"name": "an invented name", "invented": True}],
            threat_updates=[{"entity_id": "thread-a", "imminence_delta": 1}],
            coincidences=[{"claim": "a lucky break", "supported_by": "thread-a"}],
            prophecy_claim="destiny",
            consumed=["thread-a"],
        )
        candidate = result["candidate"]
        self.assertEqual(
            candidate["named_entities"],
            ["thread-a", {"name": "an invented name", "invented": True}],
        )
        self.assertEqual(
            candidate["threat_updates"], [{"entity_id": "thread-a", "imminence_delta": 1}]
        )
        self.assertEqual(
            candidate["coincidences"], [{"claim": "a lucky break", "supported_by": "thread-a"}]
        )
        self.assertEqual(candidate["prophecy_claim"], "destiny")
        self.assertEqual(result["consumed"], ["thread-a"])


class RunPipelineTests(unittest.TestCase):
    def test_composes_all_four_steps_in_order(self) -> None:
        request = _live_play_request()
        result = generation_pipeline.run_pipeline(
            request,
            haiku_response={"entry_requires_threads": ["thread-a"]},
            capable_prose="The crates were moved last night.",
            known_entities=["thread-a"],
        )
        self.assertEqual(result["consumed"], ["thread-a"])
        self.assertEqual(len(result["checks"]), 5)
        self.assertEqual(result["candidate"]["body"], "The crates were moved last night.")

    def test_result_committable_via_generation_commit_with_no_reshaping(self) -> None:
        request = _live_play_request()
        result = generation_pipeline.run_pipeline(
            request,
            haiku_response={"entry_requires_threads": ["thread-a"]},
            capable_prose="The crates were moved last night.",
            known_entities=["thread-a"],
        )
        self.assertTrue(generation_commit.can_commit(result))

    def test_setting_authoring_scale_and_campaign_spine(self) -> None:
        for scale in ("beat", "arc", "campaign-spine"):
            with self.subTest(scale=scale):
                written_for = None if scale == "campaign-spine" else 4
                request = _setting_authoring_request(scale=scale, written_for=written_for)
                self.assertIsNone(generation.validate_request(request))
                result = generation_pipeline.run_pipeline(
                    request,
                    haiku_response={},
                    capable_prose="A quiet street under an invented name.",
                    known_entities=["a-known-place"],
                )
                self.assertEqual(result["consumed"], ["a-known-place"])
                # Not necessarily committable (no named_entities asserted here), but always
                # shaped correctly for generation_checks/generation_commit to consume unchanged.
                self.assertEqual(set(result.keys()), {"candidate", "checks", "consumed"})

    def test_campaign_spine_shape_is_an_ordinary_arc_request(self) -> None:
        request = _live_play_request(scale="campaign-spine")
        self.assertTrue(generation.is_campaign_spine_shape(request))
        result = generation_pipeline.run_pipeline(
            request,
            haiku_response={},
            capable_prose="The spine of the campaign begins here.",
            known_entities=["thread-a"],
        )
        self.assertEqual(result["consumed"], ["thread-a"])

    def test_reject_outcomes_are_actually_reachable_through_run_pipeline(self) -> None:
        # Proves generation_checks' five checks have real teeth when driven through this
        # pipeline, not just when called directly against a hand-built candidate: an
        # ungrounded, non-invented named entity must be rejected by FR-007 end to end.
        request = _live_play_request()
        result = generation_pipeline.run_pipeline(
            request,
            haiku_response={},
            capable_prose="A stranger nobody has heard of.",
            known_entities=["thread-a"],
            named_entities=["someone-never-mentioned-anywhere"],
        )
        self.assertFalse(generation_commit.can_commit(result))
        outcomes = {entry["rule"]: entry["outcome"] for entry in result["checks"]}
        self.assertEqual(outcomes["FR-007"], "reject")

    def test_prophecy_reject_is_reachable_through_run_pipeline(self) -> None:
        request = _live_play_request(
            tone_contract={"prophecy": "forbidden", "scale_drift": "allowed"}
        )
        result = generation_pipeline.run_pipeline(
            request,
            haiku_response={},
            capable_prose="It was foretold.",
            known_entities=["thread-a"],
            prophecy_claim="destiny",
        )
        self.assertFalse(generation_commit.can_commit(result))
        outcomes = {entry["rule"]: entry["outcome"] for entry in result["checks"]}
        self.assertEqual(outcomes["FR-008"], "reject")


if __name__ == "__main__":
    unittest.main()
