"""docs/design/12-the-adversary.md section 2 ("The block") /
specs/094-adversary-block-loading."""

from __future__ import annotations

import pathlib
import tempfile
import unittest

from wyrd import adversary, state

VALID_ENTRY = """
creatures:
  - id: the-hunter
    name: A named antagonist
    baseline: 35
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
      tracking: 60
    damage: 1d6
    damage_type: slashing
    traits:
      - name: Unhurried
        effect:
          difficulty: -10
"""


class AdversaryLoadingTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self._tmp.name) / "bestiary.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, text: str) -> None:
        self.path.write_text(text)

    # -- User Story 1: load by id -------------------------------------------------

    def test_load_valid_entry_by_id(self):
        self._write(VALID_ENTRY)
        block = adversary.load("the-hunter", self.path)
        self.assertEqual(block["baseline"], 35)
        self.assertEqual(block["skills"], {"blade": 55, "tracking": 60})
        self.assertEqual(block["damage"], "1d6")
        self.assertEqual(block["damage_type"], "slashing")

    def test_load_unknown_id_raises(self):
        self._write(VALID_ENTRY)
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("nobody", self.path)
        self.assertIn("nobody", str(ctx.exception))

    # -- User Story 2: rejection classes --------------------------------------------

    def test_load_missing_required_field_raises(self):
        self._write("""
creatures:
  - id: no-baseline
    name: Missing its baseline
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("no-baseline", self.path)
        self.assertIn("baseline", str(ctx.exception))

    def test_load_unrecognised_field_raises(self):
        self._write("""
creatures:
  - id: extra-field
    name: Has an extra field
    baseline: 20
    stamina_max: 5
    armour: none
    skills:
      blade: 40
    speed: 30
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("extra-field", self.path)
        self.assertIn("speed", str(ctx.exception))

    def test_load_damage_without_damage_type_raises(self):
        self._write("""
creatures:
  - id: half-armed
    name: Declares damage but not its type
    baseline: 20
    stamina_max: 5
    armour: none
    skills:
      blade: 40
    damage: 1d6
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("half-armed", self.path)
        self.assertIn("damage_type", str(ctx.exception))

    def test_load_damage_type_without_damage_raises(self):
        self._write("""
creatures:
  - id: type-only
    name: Declares a type but no damage
    baseline: 20
    stamina_max: 5
    armour: none
    skills:
      blade: 40
    damage_type: slashing
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("type-only", self.path)
        self.assertIn("damage", str(ctx.exception))

    def test_load_no_attack_at_all_is_legal(self):
        self._write("""
creatures:
  - id: obstacle
    name: Dangerous by being present
    baseline: 10
    stamina_max: 3
    armour: none
    skills:
      presence: 30
""")
        block = adversary.load("obstacle", self.path)
        self.assertNotIn("damage", block)
        self.assertNotIn("damage_type", block)

    def test_load_out_of_range_baseline_raises(self):
        self._write("""
creatures:
  - id: too-high
    name: Baseline out of range
    baseline: 150
    stamina_max: 5
    armour: none
    skills:
      blade: 40
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("too-high", self.path)
        self.assertIn("baseline", str(ctx.exception))

    def test_load_unknown_armour_rank_raises(self):
        self._write("""
creatures:
  - id: odd-armour
    name: Unknown armour rank
    baseline: 20
    stamina_max: 5
    armour: plate
    skills:
      blade: 40
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("odd-armour", self.path)
        self.assertIn("armour", str(ctx.exception))

    def test_load_trait_outside_closed_vocabulary_raises(self):
        self._write("""
creatures:
  - id: odd-trait
    name: Has an invented trait effect
    baseline: 20
    stamina_max: 5
    armour: none
    skills:
      blade: 40
    traits:
      - name: Regenerates
        effect:
          regeneration: 1
""")
        with self.assertRaises(state.StateError) as ctx:
            adversary.load("odd-trait", self.path)
        self.assertIn("regeneration", str(ctx.exception))

    # -- User Story 3: ranged default ------------------------------------------------

    def test_load_ranged_defaults_false(self):
        self._write(VALID_ENTRY)
        block = adversary.load("the-hunter", self.path)
        self.assertIs(block["ranged"], False)

    def test_load_ranged_true_passes_through(self):
        self._write("""
creatures:
  - id: archer
    name: A ranged opponent
    baseline: 25
    stamina_max: 5
    armour: light
    skills:
      bow: 50
    ranged: true
""")
        block = adversary.load("archer", self.path)
        self.assertIs(block["ranged"], True)

    # -- Edge cases ---------------------------------------------------------------

    def test_load_missing_file_raises(self):
        with self.assertRaises(state.StateError):
            adversary.load("anyone", pathlib.Path(self._tmp.name) / "does-not-exist.yaml")

    def test_load_no_creatures_key_raises(self):
        self._write("schema_version: 1\n")
        with self.assertRaises(state.StateError):
            adversary.load("anyone", self.path)


if __name__ == "__main__":
    unittest.main()
