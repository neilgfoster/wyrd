"""Tests for engine/wyrd/corpus_pipeline.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_pipeline as cp  # noqa: E402


def _doc(**overrides) -> dict:
    base = {
        "id": "d1",
        "path": "library/core.pdf",
        "system": "a setting",
        "edition": "1st",
        "document_type": "rules",
        "page_count": 10,
        "extraction_method": "text-layer",
        "setting": "s1",
        "text": "",
    }
    base.update(overrides)
    return base


class BuildSettingCorpusIndexesTests(unittest.TestCase):
    def test_multi_setting_scoping(self) -> None:
        doc_a = _doc(id="d1", setting="s1", text="Fear Tests\n\nOsric the Fair rolled.\n")
        doc_b = _doc(id="d2", setting="s2", text="Terror rules affect Mara the Bold, who rolled.\n")
        bundle = cp.build_setting_corpus_indexes([doc_a, doc_b])

        self.assertEqual({r["id"] for r in bundle["documents"]}, {"d1", "d2"})
        self.assertEqual(
            {r["setting"] for r in bundle["documents"]},
            {"s1", "s2"},
        )
        self.assertTrue(all(p["setting"] == "s1" for p in bundle["nouns"]["Osric"]))
        self.assertTrue(all(p["setting"] == "s2" for p in bundle["nouns"]["Mara"]))
        self.assertTrue(all(p["setting"] == "s1" for p in bundle["terms"]["fear"]))
        self.assertTrue(all(p["setting"] == "s2" for p in bundle["terms"]["terror"]))

    def test_same_setting_duplicate_id_raises(self) -> None:
        doc_a = _doc(id="d1", setting="s1")
        doc_b = _doc(id="d1", setting="s1")
        with self.assertRaises(ValueError):
            cp.build_setting_corpus_indexes([doc_a, doc_b])

    def test_cross_setting_duplicate_id_is_not_an_error(self) -> None:
        doc_a = _doc(id="d1", setting="s1")
        doc_b = _doc(id="d1", setting="s2")
        bundle = cp.build_setting_corpus_indexes([doc_a, doc_b])
        self.assertEqual(len(bundle["documents"]), 2)

    def test_empty_document_list(self) -> None:
        bundle = cp.build_setting_corpus_indexes([])
        self.assertEqual(bundle, {"documents": [], "nouns": {}, "terms": {}, "tables": []})


class WorldBuildingRoutingTests(unittest.TestCase):
    _TRICKY_TEXT = "Fear Tests\n\nOsric the Fair rolled.\n01-05 A shudder\n06-10 A scream\n"

    def test_world_building_document_excluded_from_mechanical_indexes(self) -> None:
        for category in cp.WORLD_BUILDING_CATEGORIES:
            with self.subTest(category=category):
                doc = _doc(id=f"g-{category}", world_category=category, text=self._TRICKY_TEXT)
                bundle = cp.build_setting_corpus_indexes([doc])

                self.assertEqual(len(bundle["documents"]), 1)
                self.assertIn("Osric", bundle["nouns"])
                self.assertEqual(bundle["terms"], {})
                self.assertEqual(bundle["tables"], [])

    def test_untagged_document_indexed_by_all_four_builders(self) -> None:
        doc = _doc(id="d1", text=self._TRICKY_TEXT)
        bundle = cp.build_setting_corpus_indexes([doc])

        self.assertEqual(len(bundle["documents"]), 1)
        self.assertIn("Osric", bundle["nouns"])
        self.assertIn("fear", bundle["terms"])
        self.assertTrue(bundle["tables"])

    def test_invalid_world_category_raises(self) -> None:
        doc = _doc(id="d1", world_category="not-a-real-category")
        with self.assertRaises(ValueError):
            cp.build_setting_corpus_indexes([doc])


class ScenarioCacheStatusTests(unittest.TestCase):
    def test_missing(self) -> None:
        self.assertEqual(cp.scenario_cache_status("d1", "s1", "h1", 1, {}), "missing")

    def test_fresh(self) -> None:
        cache = {("s1", "d1"): {"content_hash": "h1", "schema_version": 1, "record": {}}}
        self.assertEqual(cp.scenario_cache_status("d1", "s1", "h1", 1, cache), "fresh")

    def test_stale_content_hash(self) -> None:
        cache = {("s1", "d1"): {"content_hash": "h1", "schema_version": 1, "record": {}}}
        self.assertEqual(cp.scenario_cache_status("d1", "s1", "h2", 1, cache), "stale")

    def test_stale_schema_version(self) -> None:
        cache = {("s1", "d1"): {"content_hash": "h1", "schema_version": 1, "record": {}}}
        self.assertEqual(cp.scenario_cache_status("d1", "s1", "h1", 2, cache), "stale")


class BuildScenarioIndexTests(unittest.TestCase):
    def test_all_four_freshness_cases_call_generator_exactly_for_non_fresh(self) -> None:
        cache = {
            ("s1", "fresh-doc"): {
                "content_hash": "h1",
                "schema_version": 1,
                "record": {"id": "fresh-doc"},
            },
            ("s1", "hash-stale-doc"): {
                "content_hash": "old-hash",
                "schema_version": 1,
                "record": {"id": "hash-stale-doc", "stale": True},
            },
            ("s1", "schema-stale-doc"): {
                "content_hash": "h1",
                "schema_version": 0,
                "record": {"id": "schema-stale-doc", "stale": True},
            },
        }
        documents = [
            {"id": "fresh-doc", "setting": "s1", "content_hash": "h1"},
            {"id": "hash-stale-doc", "setting": "s1", "content_hash": "h1"},
            {"id": "schema-stale-doc", "setting": "s1", "content_hash": "h1"},
            {"id": "missing-doc", "setting": "s1", "content_hash": "h1"},
        ]
        calls = []

        def generate(document):
            calls.append(document["id"])
            return {"id": document["id"], "generated": True}

        records, updated_cache = cp.build_scenario_index(
            documents, cache, generate, schema_version=1
        )

        self.assertEqual(sorted(calls), ["hash-stale-doc", "missing-doc", "schema-stale-doc"])
        self.assertEqual(len(records), 4)
        fresh_record = next(r for r in records if r["id"] == "fresh-doc")
        self.assertEqual(fresh_record, {"id": "fresh-doc"})
        for doc_id in ["hash-stale-doc", "schema-stale-doc", "missing-doc"]:
            self.assertEqual(updated_cache[("s1", doc_id)]["content_hash"], "h1")
            self.assertEqual(updated_cache[("s1", doc_id)]["schema_version"], 1)

    def test_rerun_unchanged_calls_generator_zero_times(self) -> None:
        documents = [{"id": "d1", "setting": "s1", "content_hash": "h1"}]
        calls = []

        def generate(document):
            calls.append(document["id"])
            return {"id": document["id"]}

        _, cache = cp.build_scenario_index(documents, {}, generate, schema_version=1)
        self.assertEqual(calls, ["d1"])

        calls.clear()
        cp.build_scenario_index(documents, cache, generate, schema_version=1)
        self.assertEqual(calls, [])

    def test_original_cache_argument_is_not_mutated(self) -> None:
        documents = [{"id": "d1", "setting": "s1", "content_hash": "h1"}]
        original_cache: dict = {}

        cp.build_scenario_index(
            documents, original_cache, lambda doc: {"id": doc["id"]}, schema_version=1
        )

        self.assertEqual(original_cache, {})

    def test_empty_document_list(self) -> None:
        records, cache = cp.build_scenario_index([], {}, lambda doc: {}, schema_version=1)
        self.assertEqual(records, [])
        self.assertEqual(cache, {})

    def test_generator_exception_preserves_already_computed_entries(self) -> None:
        documents = [
            {"id": "ok-doc", "setting": "s1", "content_hash": "h1"},
            {"id": "bad-doc", "setting": "s1", "content_hash": "h1"},
        ]

        def generate(document):
            if document["id"] == "bad-doc":
                raise RuntimeError("model call failed")
            return {"id": document["id"]}

        with self.assertRaises(RuntimeError) as ctx:
            cp.build_scenario_index(documents, {}, generate, schema_version=1)

        self.assertIn(("s1", "ok-doc"), ctx.exception.partial_cache)
        self.assertNotIn(("s1", "bad-doc"), ctx.exception.partial_cache)
        self.assertEqual([r["id"] for r in ctx.exception.partial_records], ["ok-doc"])


if __name__ == "__main__":
    unittest.main()
