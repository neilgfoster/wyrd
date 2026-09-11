"""Tests for engine/wyrd/era.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import era  # noqa: E402

ERAS = [
    {"id": "the-long-thaw", "name": "The Long Thaw", "ambient": "hope returning, guardedly"},
    {"id": "the-second-winter", "name": "The Second Winter", "ambient": "the cold came back"},
]


class AmbientRegisterTests(unittest.TestCase):
    def test_correct_lookup(self) -> None:
        self.assertEqual(era.ambient_register(ERAS, "the-long-thaw"), "hope returning, guardedly")

    def test_era_none_returns_none(self) -> None:
        self.assertIsNone(era.ambient_register(ERAS, None))

    def test_empty_eras_list_returns_none(self) -> None:
        self.assertIsNone(era.ambient_register([], "the-long-thaw"))

    def test_unmatched_era_id_returns_none(self) -> None:
        self.assertIsNone(era.ambient_register(ERAS, "no-such-era"))


class CrossEraTests(unittest.TestCase):
    def test_first_crossing_from_null(self) -> None:
        result = era.cross_era(ERAS, None, to="the-long-thaw", at={"year": 1, "month": 3})
        self.assertEqual(result["era"], "the-long-thaw")
        self.assertEqual(
            result["crossing"], {"from": None, "to": "the-long-thaw", "at": {"year": 1, "month": 3}}
        )

    def test_later_crossing(self) -> None:
        result = era.cross_era(
            ERAS, "the-long-thaw", to="the-second-winter", at={"year": 4, "month": None}
        )
        self.assertEqual(result["era"], "the-second-winter")
        self.assertEqual(result["crossing"]["from"], "the-long-thaw")
        self.assertEqual(result["crossing"]["to"], "the-second-winter")

    def test_rejects_undeclared_target(self) -> None:
        with self.assertRaises(ValueError):
            era.cross_era(ERAS, None, to="not-declared", at={"year": 1, "month": None})

    def test_rejects_no_op_target(self) -> None:
        with self.assertRaises(ValueError):
            era.cross_era(ERAS, "the-long-thaw", to="the-long-thaw", at={"year": 2, "month": None})

    def test_rejects_target_against_empty_eras(self) -> None:
        with self.assertRaises(ValueError):
            era.cross_era([], None, to="the-long-thaw", at={"year": 1, "month": None})


if __name__ == "__main__":
    unittest.main()
