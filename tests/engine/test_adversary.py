"""docs/design/12-the-adversary.md section 2 ("The block") / section 3 ("The baseline") /
specs/094-adversary-block-loading / specs/095-adversary-baseline-resolution."""

from __future__ import annotations

import pathlib
import tempfile
import unittest

from wyrd import adversary, rules, state

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


class AdversaryBaselineResolutionTest(unittest.TestCase):
    """docs/design/12-the-adversary.md section 3 ("The baseline") /
    specs/095-adversary-baseline-resolution."""

    def setUp(self):
        self.block = {
            "id": "the-hunter",
            "name": "A named antagonist",
            "baseline": 35,
            "stamina_max": 7,
            "armour": "modest",
            "skills": {"blade": 55, "stealth": 20},
            "ranged": False,
        }

    def test_resolve_skill_unlisted_returns_baseline(self):
        self.assertEqual(adversary.resolve_skill(self.block, "tracking"), 35)

    def test_resolve_skill_listed_returns_listed_value(self):
        self.assertEqual(adversary.resolve_skill(self.block, "blade"), 55)

    def test_resolve_skill_listed_below_baseline_not_raised(self):
        # stealth (20) sits below baseline (35) -- the baseline is not a floor.
        self.assertEqual(adversary.resolve_skill(self.block, "stealth"), 20)

    def test_resolve_skill_baseline_equal_to_untrained_still_reads_block(self):
        block = dict(self.block, baseline=rules.UNTRAINED_SKILL)
        self.assertEqual(adversary.resolve_skill(block, "tracking"), rules.UNTRAINED_SKILL)
        # Changing the block's own baseline changes the result -- it traces to the field,
        # not to the shared constant.
        block["baseline"] = rules.UNTRAINED_SKILL + 15
        self.assertEqual(adversary.resolve_skill(block, "tracking"), rules.UNTRAINED_SKILL + 15)

    def test_select_group_skill_unaffected_by_adversary_resolution(self):
        # rules.select_group_skill's own untrained fallback is untouched by this feature.
        self.assertEqual(
            rules.select_group_skill([None], mode="most_capable"), rules.UNTRAINED_SKILL
        )


class AdversaryTraitEffectsTest(unittest.TestCase):
    """docs/design/12-the-adversary.md section 5 ("Traits") /
    specs/096-adversary-trait-effects."""

    def setUp(self):
        self.block = {
            "id": "the-hunter",
            "name": "A named antagonist",
            "baseline": 35,
            "stamina_max": 7,
            "armour": "modest",
            "skills": {"blade": 55},
            "damage": "1d6",
            "damage_type": "slashing",
            "ranged": False,
        }

    # -- effective_block: stamina_max / armour_rank (User Story 1) -------------------

    def test_effective_block_stamina_max_trait(self):
        block = dict(self.block, traits=[{"name": "Tough", "effect": {"stamina_max": 2}}])
        self.assertEqual(adversary.effective_block(block)["stamina_max"], 9)

    def test_effective_block_stacks_two_stamina_max_traits(self):
        block = dict(
            self.block,
            traits=[
                {"name": "Tough", "effect": {"stamina_max": 1}},
                {"name": "Tougher", "effect": {"stamina_max": 2}},
            ],
        )
        self.assertEqual(adversary.effective_block(block)["stamina_max"], 10)

    def test_effective_block_armour_rank_trait_and_floor_clamp(self):
        block = dict(
            self.block, traits=[{"name": "Lightly armoured", "effect": {"armour_rank": -1}}]
        )
        self.assertEqual(adversary.effective_block(block)["armour"], "light")

        block_at_floor = dict(
            self.block,
            armour="none",
            traits=[{"name": "Unarmoured", "effect": {"armour_rank": -1}}],
        )
        self.assertEqual(adversary.effective_block(block_at_floor)["armour"], "none")

    # -- effective_block: damage / damage_type (User Story 2) -----------------------

    def test_effective_block_damage_dice_trait_add_and_remove(self):
        add = dict(self.block, traits=[{"name": "Heavy blows", "effect": {"damage": 1}}])
        self.assertEqual(adversary.effective_block(add)["damage"], "2d6")

        remove = dict(self.block, damage="2d6", traits=[{"name": "Weak", "effect": {"damage": -1}}])
        self.assertEqual(adversary.effective_block(remove)["damage"], "1d6")

    def test_effective_block_damage_dice_floor_at_one(self):
        block = dict(self.block, traits=[{"name": "Weak", "effect": {"damage": -5}}])
        self.assertEqual(adversary.effective_block(block)["damage"], "1d6")

    def test_effective_block_damage_type_trait_overrides(self):
        block = dict(
            self.block, traits=[{"name": "Fire-touched", "effect": {"damage_type": "searing"}}]
        )
        self.assertEqual(adversary.effective_block(block)["damage_type"], "searing")

    def test_effective_block_damage_trait_on_attackless_adversary_is_inert(self):
        block = {
            "id": "obstacle",
            "name": "Dangerous by being present",
            "baseline": 10,
            "stamina_max": 3,
            "armour": "none",
            "skills": {"presence": 30},
            "ranged": False,
            "traits": [{"name": "Heavy blows", "effect": {"damage": 1}}],
        }
        result = adversary.effective_block(block)
        self.assertNotIn("damage", result)

    def test_effective_block_no_traits_returns_unmodified_fields(self):
        result = adversary.effective_block(self.block)
        self.assertEqual(result["stamina_max"], self.block["stamina_max"])
        self.assertEqual(result["armour"], self.block["armour"])
        self.assertEqual(result["damage"], self.block["damage"])
        self.assertEqual(result["damage_type"], self.block["damage_type"])

    def test_effective_block_does_not_mutate_input(self):
        block = dict(self.block, traits=[{"name": "Tough", "effect": {"stamina_max": 2}}])
        original_stamina = block["stamina_max"]
        adversary.effective_block(block)
        self.assertEqual(block["stamina_max"], original_stamina)

    # -- shift_difficulty (User Story 3) ---------------------------------------------

    def test_shift_difficulty_moves_along_ladder(self):
        self.assertEqual(adversary.shift_difficulty("average", -1), "challenging")
        self.assertEqual(adversary.shift_difficulty("challenging", 1), "average")

    def test_shift_difficulty_clamps_at_both_ends(self):
        self.assertEqual(adversary.shift_difficulty("very_hard", -1), "very_hard")
        self.assertEqual(adversary.shift_difficulty("easy", 1), "easy")

    # -- wyrd_band_width (User Story 4) -----------------------------------------------

    def test_wyrd_band_width_sums_traits(self):
        block = dict(
            self.block,
            traits=[
                {"name": "Uncanny", "effect": {"wyrd": 1}},
                {"name": "Doubly uncanny", "effect": {"wyrd": 1}},
            ],
        )
        self.assertEqual(adversary.wyrd_band_width(block), 2)

    def test_wyrd_band_width_no_traits_is_zero(self):
        self.assertEqual(adversary.wyrd_band_width(self.block), 0)


if __name__ == "__main__":
    unittest.main()
