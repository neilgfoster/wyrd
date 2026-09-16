"""Tests for engine/wyrd/generation_commit.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import entity, generation, generation_commit, state, thread, threat  # noqa: E402

_PASSING_CHECKS = [
    {"rule": "FR-007", "outcome": "pass", "detail": ""},
    {"rule": "FR-008", "outcome": "pass", "detail": ""},
    {"rule": "FR-009", "outcome": "narrowed", "detail": "narrowed to fit the band"},
]
_REJECTING_CHECKS = [
    {"rule": "FR-007", "outcome": "pass", "detail": ""},
    {"rule": "FR-009", "outcome": "reject", "detail": "danger too high"},
]


def _passing_result(**overrides) -> dict:
    base = generation.new_result(
        candidate={"danger": 3}, checks=_PASSING_CHECKS, consumed=["the-ledger"]
    )
    base.update(overrides)
    return base


def _rejecting_result(**overrides) -> dict:
    base = generation.new_result(
        candidate={"danger": 99}, checks=_REJECTING_CHECKS, consumed=["the-ledger"]
    )
    base.update(overrides)
    return base


def _accept_kwargs(path: pathlib.Path, **overrides) -> dict:
    base = {
        "entity_id": "a-new-beat",
        "entity_type": "beat",
        "name": "A New Beat",
        "setting": "some-setting",
        "mode": "live-play",
        "body": "What happens in play.",
        "path": path,
    }
    base.update(overrides)
    return base


class CanCommitTests(unittest.TestCase):
    def test_false_for_empty_checks(self) -> None:
        self.assertFalse(generation_commit.can_commit(generation.new_result(candidate={})))

    def test_true_for_all_pass_or_narrowed(self) -> None:
        self.assertTrue(generation_commit.can_commit(_passing_result()))

    def test_false_for_any_reject(self) -> None:
        self.assertFalse(generation_commit.can_commit(_rejecting_result()))


class RejectResultTests(unittest.TestCase):
    """User Story 2 (FR-005/FR-015): an explicit decline always writes nothing."""

    def test_always_declines_even_a_passing_result(self) -> None:
        outcome = generation_commit.reject_result(_passing_result())
        self.assertEqual(outcome, {"committed": False, "reason": "declined"})

    def test_writes_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generation_commit.reject_result(_passing_result())
            self.assertEqual(list(pathlib.Path(tmp).iterdir()), [])


class AcceptResultRejectionPathTests(unittest.TestCase):
    """User Story 2 (FR-015): a result the checks reject writes nothing."""

    def test_rejecting_result_writes_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            outcome = generation_commit.accept_result(_rejecting_result(), **_accept_kwargs(path))
            self.assertFalse(outcome["committed"])
            self.assertEqual(outcome["reason"], "checks_failed")
            self.assertIn("danger too high", outcome["detail"])
            self.assertFalse(path.exists())

    def test_empty_checks_treated_as_not_evaluated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            result = generation.new_result(candidate={"danger": 1})
            outcome = generation_commit.accept_result(result, **_accept_kwargs(path))
            self.assertFalse(outcome["committed"])
            self.assertEqual(outcome["reason"], "checks_failed")
            self.assertEqual(outcome["detail"], ["no checks were run"])
            self.assertFalse(path.exists())

    def test_rejecting_result_mutates_no_live_state(self) -> None:
        live_threads = {
            "t1": thread.new_thread(
                id="t1", opened={"year": 0, "month": None}, summary="s", hooks=[]
            )
        }
        live_entities = {"e1": {"id": "e1", "type": "character"}}
        before_threads = dict(live_threads)
        before_entities = dict(live_entities)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            generation_commit.accept_result(
                _rejecting_result(),
                **_accept_kwargs(
                    path,
                    thread_updates=[{"action": "touch", "id": "t1"}],
                    threat_updates=[],
                    live_threads=live_threads,
                    live_entities=live_entities,
                ),
            )
        self.assertEqual(live_threads, before_threads)
        self.assertEqual(live_entities, before_entities)


class AcceptResultWritePathTests(unittest.TestCase):
    """User Story 1 (FR-001-004): a passing result is committed as an ordinary entity."""

    def test_writes_drafted_entity_with_generated_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(_passing_result(), **_accept_kwargs(path))

            self.assertTrue(outcome["committed"])
            self.assertEqual(outcome["path"], path)

            frontmatter, _body = state.load_entity(path)
            self.assertEqual(frontmatter["status"], "drafted")
            self.assertEqual(frontmatter["id"], "a-new-beat")
            self.assertEqual(frontmatter["type"], "beat")
            self.assertEqual(frontmatter["setting"], "some-setting")
            self.assertEqual(
                frontmatter["sources"],
                [{"generated": True, "mode": "live-play", "consumed": ["the-ledger"]}],
            )

    def test_rejects_entity_type_outside_arc_or_beat(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            with self.assertRaises(ValueError):
                generation_commit.accept_result(
                    _passing_result(), **_accept_kwargs(path, entity_type="character")
                )
            self.assertFalse(path.exists())

    def test_written_frontmatter_passes_entity_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(_passing_result(), **_accept_kwargs(path))
            self.assertEqual(entity.validate(outcome["entity"]), {"valid": True})

    def test_thread_new_action_calls_thread_new_thread(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            update = {
                "action": "new",
                "id": "the-one-who-paid",
                "opened": {"year": 1, "month": None},
                "summary": "whoever funded it walked away",
                "hooks": ["money"],
            }
            outcome = generation_commit.accept_result(
                _passing_result(),
                **_accept_kwargs(path, thread_updates=[update], live_threads={}),
            )
            expected = thread.new_thread(
                id="the-one-who-paid",
                opened={"year": 1, "month": None},
                summary="whoever funded it walked away",
                hooks=["money"],
            )
            self.assertEqual(outcome["threads"]["the-one-who-paid"], expected)

    def test_thread_touch_action_calls_thread_touch(self) -> None:
        existing = thread.new_thread(
            id="t1", opened={"year": 0, "month": None}, summary="s", hooks=[], heat=1
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(
                _passing_result(),
                **_accept_kwargs(
                    path,
                    thread_updates=[{"action": "touch", "id": "t1"}],
                    live_threads={"t1": existing},
                ),
            )
            self.assertEqual(outcome["threads"]["t1"], thread.touch(existing))

    def test_thread_touch_unknown_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            with self.assertRaises(ValueError):
                generation_commit.accept_result(
                    _passing_result(),
                    **_accept_kwargs(
                        path,
                        thread_updates=[{"action": "touch", "id": "nonexistent"}],
                        live_threads={},
                    ),
                )

    def test_threat_new_calls_threat_promote(self) -> None:
        target = {"id": "the-quiet-hollow", "type": "place"}
        update = {
            "entity_id": None,
            "target_entity_id": "the-quiet-hollow",
            "objective": "spread unseen",
            "imminence": 2,
            "connection": "the player character's home village",
            "ambient_add": ["a chill in the air"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(
                _passing_result(),
                **_accept_kwargs(
                    path,
                    threat_updates=[update],
                    live_entities={"the-quiet-hollow": target},
                ),
            )
            expected = threat.promote(
                target,
                {
                    "imminence": 2,
                    "connection": "the player character's home village",
                    "ambient": ["a chill in the air"],
                    "effects": {},
                },
                "spread unseen",
            )
            self.assertEqual(outcome["entities"]["the-quiet-hollow"], expected)

    def test_threat_existing_applies_imminence_delta_and_ambient_directly(self) -> None:
        target = {
            "id": "the-drowned-count",
            "type": "character",
            "threat": {"imminence": 2, "ambient": ["a chill"], "effects": {}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(
                _passing_result(),
                **_accept_kwargs(
                    path,
                    threat_updates=[
                        {
                            "entity_id": "the-drowned-count",
                            "imminence_delta": 1,
                            "ambient_add": ["a rumour"],
                        }
                    ],
                    live_entities={"the-drowned-count": target},
                ),
            )
            updated = outcome["entities"]["the-drowned-count"]
            self.assertEqual(updated["threat"]["imminence"], 3)
            self.assertEqual(updated["threat"]["ambient"], ["a chill", "a rumour"])
            self.assertEqual(updated["id"], "the-drowned-count")

    def test_new_threat_missing_required_fields_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            with self.assertRaises(ValueError):
                generation_commit.accept_result(
                    _passing_result(),
                    **_accept_kwargs(
                        path,
                        threat_updates=[{"entity_id": None}],
                        live_entities={},
                    ),
                )

    def test_threat_update_unknown_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "should-not-exist.md"
            with self.assertRaises(ValueError):
                generation_commit.accept_result(
                    _passing_result(),
                    **_accept_kwargs(
                        path,
                        threat_updates=[{"entity_id": "nonexistent", "imminence_delta": 1}],
                        live_entities={},
                    ),
                )

    def test_no_thread_or_threat_updates_still_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "a-new-beat.md"
            outcome = generation_commit.accept_result(_passing_result(), **_accept_kwargs(path))
            self.assertTrue(outcome["committed"])
            self.assertEqual(outcome["threads"], {})
            self.assertEqual(outcome["entities"], {})


class NoRetconPathTests(unittest.TestCase):
    """User Story 3 (FR-007 of this feature's own spec): no regeneration/retcon path exists."""

    def test_module_exposes_only_the_three_documented_public_names(self) -> None:
        # Excludes imported modules/symbols this module uses internally (pathlib, the sibling
        # wyrd.* modules it calls, and __future__'s own 'annotations' binding) -- only the
        # functions this module itself defines are the contract under test.
        _imported = (
            "pathlib",
            "entity",
            "state",
            "thread",
            "threat",
            "generation",
            "arc_selection",
            "annotations",
        )
        public_names = {
            name
            for name in dir(generation_commit)
            if not name.startswith("_") and name not in _imported
        }
        self.assertEqual(public_names, {"can_commit", "accept_result", "reject_result"})

    def test_two_accepted_results_produce_independent_untouched_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path_a = pathlib.Path(tmp) / "beat-a.md"
            path_b = pathlib.Path(tmp) / "beat-b.md"

            generation_commit.accept_result(
                _passing_result(), **_accept_kwargs(path_a, entity_id="beat-a")
            )
            content_a_before = path_a.read_text()

            generation_commit.accept_result(
                _passing_result(), **_accept_kwargs(path_b, entity_id="beat-b")
            )

            self.assertEqual(path_a.read_text(), content_a_before)
            self.assertNotEqual(path_a.read_text(), path_b.read_text())


if __name__ == "__main__":
    unittest.main()
