"""Tests for engine/wyrd/log.py: the Archival memory tier reader/writer (#402).

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). Run with PYTHONPATH=engine.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import log  # noqa: E402


class AppendAndReadLogTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.chronicle_dir = pathlib.Path(self._tmp.name)
        self.chronicle_name = "test-chronicle"

    def tearDown(self):
        self._tmp.cleanup()

    def _append(self, beat_id: str, mode: str = "played", resolved_at: float = 0.0) -> None:
        log.append_beat(
            self.chronicle_dir,
            self.chronicle_name,
            {"beat_id": beat_id, "mode": mode, "resolved_at": resolved_at},
        )

    def test_read_log_requires_exactly_one_of_last_or_since(self):
        with self.assertRaises(ValueError):
            log.read_log(self.chronicle_dir, self.chronicle_name)
        with self.assertRaises(ValueError):
            log.read_log(self.chronicle_dir, self.chronicle_name, last=1, since="beat-1")

    def test_missing_log_file_returns_empty_list(self):
        result = log.read_log(self.chronicle_dir, self.chronicle_name, last=5)
        self.assertEqual(result, [])

    def test_append_then_read_sees_it_immediately(self):
        self._append("beat-1")
        result = log.read_log(self.chronicle_dir, self.chronicle_name, last=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["beat_id"], "beat-1")

    def test_last_returns_exactly_the_n_most_recent_in_beat_order(self):
        for beat_id in ("beat-1", "beat-2", "beat-3", "beat-4"):
            self._append(beat_id)
        result = log.read_log(self.chronicle_dir, self.chronicle_name, last=2)
        self.assertEqual([entry["beat_id"] for entry in result], ["beat-3", "beat-4"])

    def test_last_exceeding_total_returns_the_whole_log(self):
        for beat_id in ("beat-1", "beat-2"):
            self._append(beat_id)
        result = log.read_log(self.chronicle_dir, self.chronicle_name, last=100)
        self.assertEqual([entry["beat_id"] for entry in result], ["beat-1", "beat-2"])

    def test_since_returns_entries_from_that_beat_onward_inclusive(self):
        for beat_id in ("beat-1", "beat-2", "beat-3"):
            self._append(beat_id)
        result = log.read_log(self.chronicle_dir, self.chronicle_name, since="beat-2")
        self.assertEqual([entry["beat_id"] for entry in result], ["beat-2", "beat-3"])

    def test_since_unknown_beat_returns_empty_list(self):
        self._append("beat-1")
        result = log.read_log(self.chronicle_dir, self.chronicle_name, since="never-logged")
        self.assertEqual(result, [])

    def test_each_record_is_well_formed_json_lines(self):
        self._append("beat-1", mode="summarised", resolved_at=123.5)
        result = log.read_log(self.chronicle_dir, self.chronicle_name, last=1)
        self.assertEqual(
            result[0], {"beat_id": "beat-1", "mode": "summarised", "resolved_at": 123.5}
        )


if __name__ == "__main__":
    unittest.main()
