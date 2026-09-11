"""Tests for engine/wyrd/thread.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "engine"))

from wyrd import thread  # noqa: E402


def _thread(heat: int) -> dict:
    return thread.new_thread(
        id="the-one-who-paid",
        opened={"year": 0, "month": None},
        summary="whoever funded it walked away, and you would know them again",
        hooks=["money", "influence"],
        heat=heat,
    )


class NewThreadTests(unittest.TestCase):
    def test_all_fields_carried(self) -> None:
        t = thread.new_thread(
            id="x", opened={"year": 1, "month": 2}, summary="s", hooks=["a", "b"], heat=3
        )
        self.assertEqual(t["id"], "x")
        self.assertEqual(t["opened"], {"year": 1, "month": 2})
        self.assertEqual(t["summary"], "s")
        self.assertEqual(t["hooks"], ["a", "b"])
        self.assertEqual(t["heat"], 3)

    def test_default_heat_is_zero(self) -> None:
        t = thread.new_thread(id="x", opened={"year": 0, "month": None}, summary="s", hooks=[])
        self.assertEqual(t["heat"], 0)

    def test_rejects_heat_above_max(self) -> None:
        with self.assertRaises(ValueError):
            thread.new_thread(id="x", opened={}, summary="s", hooks=[], heat=6)

    def test_rejects_negative_heat(self) -> None:
        with self.assertRaises(ValueError):
            thread.new_thread(id="x", opened={}, summary="s", hooks=[], heat=-1)


class TouchTests(unittest.TestCase):
    def test_rises_by_one_at_each_value(self) -> None:
        for heat in range(0, 5):
            with self.subTest(heat=heat):
                touched = thread.touch(_thread(heat))
                self.assertEqual(touched["heat"], heat + 1)

    def test_caps_at_max(self) -> None:
        touched = thread.touch(_thread(5))
        self.assertEqual(touched["heat"], 5)

    def test_other_fields_unchanged(self) -> None:
        t = _thread(2)
        touched = thread.touch(t)
        self.assertEqual(touched["id"], t["id"])
        self.assertEqual(touched["hooks"], t["hooks"])


class DecayTests(unittest.TestCase):
    def test_one_year_drops_by_one(self) -> None:
        decayed = thread.decay(_thread(2), elapsed_days=365)
        self.assertEqual(decayed["heat"], 1)

    def test_partial_year_is_no_op(self) -> None:
        decayed = thread.decay(_thread(2), elapsed_days=200)
        self.assertEqual(decayed["heat"], 2)

    def test_multi_year_span_drops_by_full_count(self) -> None:
        decayed = thread.decay(_thread(4), elapsed_days=365 * 3)
        self.assertEqual(decayed["heat"], 1)

    def test_floors_at_zero_without_closing_mid_span(self) -> None:
        decayed = thread.decay(_thread(1), elapsed_days=365 * 3)
        self.assertEqual(decayed["heat"], 0)
        self.assertNotIn("status", decayed)

    def test_closes_with_reason_once_already_at_floor(self) -> None:
        decayed = thread.decay(_thread(0), elapsed_days=365)
        self.assertEqual(decayed["status"], "closed")
        self.assertEqual(decayed["close_reason"], "never resolved")

    def test_zero_elapsed_days_at_floor_stays_open(self) -> None:
        decayed = thread.decay(_thread(0), elapsed_days=100)
        self.assertNotIn("status", decayed)
        self.assertEqual(decayed["heat"], 0)


if __name__ == "__main__":
    unittest.main()
