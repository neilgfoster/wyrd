"""Tests for engine/wyrd/corpus_provenance.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import corpus_provenance as cp  # noqa: E402


class BuildProvenanceRecordTests(unittest.TestCase):
    def test_library_origin_needs_no_reference(self) -> None:
        record = cp.build_provenance_record(origin="library")
        self.assertEqual(record, {"origin": "library", "reference": None})

    def test_public_origin_with_reference(self) -> None:
        record = cp.build_provenance_record(
            origin="public", reference="Public Domain Bestiary, 1911, p. 42"
        )
        self.assertEqual(record["origin"], "public")
        self.assertEqual(record["reference"], "Public Domain Bestiary, 1911, p. 42")

    def test_invalid_origin_raises(self) -> None:
        with self.assertRaises(ValueError):
            cp.build_provenance_record(origin="internet")

    def test_public_origin_missing_reference_raises(self) -> None:
        with self.assertRaises(ValueError):
            cp.build_provenance_record(origin="public")

    def test_public_origin_blank_reference_raises(self) -> None:
        with self.assertRaises(ValueError):
            cp.build_provenance_record(origin="public", reference="   ")

    def test_library_origin_with_reference_raises(self) -> None:
        with self.assertRaises(ValueError):
            cp.build_provenance_record(origin="library", reference="anything")


if __name__ == "__main__":
    unittest.main()
