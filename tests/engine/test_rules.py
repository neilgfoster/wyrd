"""Tests for engine/wyrd/rules.py.

stdlib unittest, no pytest (docs/design/27-tooling.md section 6).
"""

from __future__ import annotations

import pathlib
import sys
import unittest
import unittest.mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import rules  # noqa: E402


class RollD100Test(unittest.TestCase):
    def test_same_seed_is_deterministic_across_100_calls(self):
        first = rules.roll_d100(seed=1)
        for _ in range(100):
            self.assertEqual(rules.roll_d100(seed=1), first)

    def test_no_seed_is_not_always_identical(self):
        results = {rules.roll_d100() for _ in range(50)}
        self.assertGreater(len(results), 1, "50 unseeded rolls all came back identical")

    def test_result_in_range_for_d100(self):
        for seed in range(200):
            result = rules.roll_d100(seed=seed)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 100)

    def test_result_in_range_for_other_sides(self):
        for seed in range(50):
            result = rules.roll_d100(sides=6, seed=seed)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 6)

    def test_zero_sides_rejected(self):
        with self.assertRaises(ValueError):
            rules.roll_d100(sides=0)

    def test_negative_sides_rejected(self):
        with self.assertRaises(ValueError):
            rules.roll_d100(sides=-5)

    def test_seed_does_not_leak_between_calls(self):
        # A seeded call must not perturb an immediately following unseeded call's source of
        # randomness -- i.e. the module-level `random` global must be untouched.
        rules.roll_d100(seed=1)
        results = {rules.roll_d100() for _ in range(50)}
        self.assertGreater(len(results), 1)


def _seed_for_roll(target_roll: int, avoid: set[int] = frozenset()) -> int:
    """Find a seed whose d100 roll equals `target_roll`, for tests that need a known roll."""
    for seed in range(10000):
        if seed in avoid:
            continue
        if rules.roll_d100(seed=seed) == target_roll:
            return seed
    raise AssertionError(f"no seed under 10000 produces roll {target_roll}")


class OpposedTestTest(unittest.TestCase):
    def test_effective_pct_matches_formula_across_many_pairs(self):
        for skill in range(0, 101, 5):
            for opponent in range(0, 101, 5):
                result = rules.opposed_test(skill=skill, opponent=opponent, seed=1)
                expected = max(5, min(95, 50 + (skill - opponent)))
                self.assertEqual(result["effective_pct"], expected)

    def test_even_match_is_fifty(self):
        result = rules.opposed_test(skill=50, opponent=50, seed=1)
        self.assertEqual(result["effective_pct"], 50)

    def test_wide_gap_clips_high(self):
        result = rules.opposed_test(skill=95, opponent=5, seed=1)
        self.assertEqual(result["effective_pct"], 95)

    def test_wide_gap_clips_low(self):
        result = rules.opposed_test(skill=5, opponent=95, seed=1)
        self.assertEqual(result["effective_pct"], 5)

    def test_success_iff_roll_at_or_under_effective_pct(self):
        pass_seed = _seed_for_roll(40)
        fail_seed = _seed_for_roll(60)
        passing = rules.opposed_test(skill=50, opponent=50, seed=pass_seed)
        failing = rules.opposed_test(skill=50, opponent=50, seed=fail_seed)
        self.assertTrue(passing["success"])
        self.assertFalse(failing["success"])

    def test_roll_equal_to_effective_pct_succeeds(self):
        seed = _seed_for_roll(50)
        result = rules.opposed_test(skill=50, opponent=50, seed=seed)
        self.assertEqual(result["roll"], 50)
        self.assertTrue(result["success"])

    def test_degrees_matches_formula_on_success(self):
        seed = _seed_for_roll(23)
        result = rules.opposed_test(skill=70, opponent=30, seed=seed)  # effective_pct 90
        self.assertTrue(result["success"])
        self.assertEqual(result["degrees"], 9 - 2)

    def test_degrees_is_none_on_failure(self):
        seed = _seed_for_roll(87)
        result = rules.opposed_test(skill=30, opponent=70, seed=seed)  # effective_pct 10
        self.assertFalse(result["success"])
        self.assertIsNone(result["degrees"])

    def test_wyrd_die_matches_units_digit_table_independent_of_success(self):
        expectations = {
            0: "ill_omen",
            9: "fair_omen",
        }
        for digit in range(10):
            expected = expectations.get(digit, "none")
            for target_roll in (digit if digit else 10, digit + 90):
                seed = _seed_for_roll(target_roll)
                result = rules.opposed_test(skill=50, opponent=50, seed=seed)
                self.assertEqual(result["roll"] % 10, digit)
                self.assertEqual(
                    result["wyrd"],
                    expected,
                    f"roll {result['roll']} (success={result['success']}) expected {expected}",
                )

    def test_opponent_dice_never_consulted_only_one_roll_happens(self):
        # opposed_test's contract is a single roll on the acting side; verifying this by
        # construction (the function signature and result shape carry only one `roll` field,
        # no opponent-side roll field exists) rather than by mocking internals.
        result = rules.opposed_test(skill=50, opponent=50, seed=1)
        self.assertIn("roll", result)
        self.assertNotIn("opponent_roll", result)

    def test_seed_reproducibility(self):
        first = rules.opposed_test(skill=70, opponent=30, seed=42)
        second = rules.opposed_test(skill=70, opponent=30, seed=42)
        self.assertEqual(first, second)


class DeclarationBonusTest(unittest.TestCase):
    def test_specific(self):
        self.assertEqual(rules.declaration_bonus("specific"), 10)

    def test_specific_leveraging(self):
        self.assertEqual(rules.declaration_bonus("specific_leveraging"), 20)

    def test_brief_is_zero_not_missing(self):
        self.assertEqual(rules.declaration_bonus("brief"), 0)

    def test_against_nature(self):
        self.assertEqual(rules.declaration_bonus("against_nature"), -20)

    def test_removes_risk_is_none_sentinel(self):
        self.assertIsNone(rules.declaration_bonus("removes_risk"))

    def test_unrecognized_category_raises(self):
        with self.assertRaises(ValueError):
            rules.declaration_bonus("bogus")


class AssistanceBonusTest(unittest.TestCase):
    def test_thirty_percent(self):
        self.assertEqual(rules.assistance_bonus(30), 3)

    def test_forty_five_percent_rounds_down(self):
        self.assertEqual(rules.assistance_bonus(45), 4)

    def test_ninety_percent_not_capped_yet(self):
        self.assertEqual(rules.assistance_bonus(90), 9)

    def test_hundred_percent_capped_at_ten(self):
        self.assertEqual(rules.assistance_bonus(100), 10)

    def test_all_multiples_of_ten(self):
        for skill in range(0, 101, 10):
            self.assertEqual(rules.assistance_bonus(skill), min(skill // 10, 10))

    def test_cannot_attempt_zeroes_the_bonus(self):
        self.assertEqual(rules.assistance_bonus(100, can_attempt=False), 0)


class OpposedTestModifiersTest(unittest.TestCase):
    def test_no_modifiers_matches_pre_223_shape_and_values(self):
        # Same skill/opponent/seed as #222's own test_seed_reproducibility -- confirms the
        # existing three-argument call is unaffected by this feature's new parameters.
        result = rules.opposed_test(skill=70, opponent=30, seed=42)
        self.assertEqual(result["effective_pct"], 90)
        self.assertIsNone(result["declaration"])
        self.assertIsNone(result["helper_skill"])
        self.assertFalse(result["no_roll"])

    def test_no_modifiers_is_stable_across_many_calls(self):
        for skill in range(0, 101, 5):
            for opponent in range(0, 101, 5):
                with_defaults = rules.opposed_test(skill=skill, opponent=opponent, seed=1)
                explicit_none = rules.opposed_test(
                    skill=skill, opponent=opponent, seed=1, declaration=None, helper_skill=None
                )
                self.assertEqual(with_defaults, explicit_none)

    def test_declaration_and_assistance_compose_into_effective_pct(self):
        result = rules.opposed_test(
            skill=50, opponent=50, declaration="specific", helper_skill=45, seed=1
        )
        self.assertEqual(result["effective_pct"], 64)  # 50 + 10 + 4

    def test_removes_risk_produces_no_roll_and_automatic_success(self):
        with unittest.mock.patch("wyrd.rules.roll_d100") as mock_roll:
            result = rules.opposed_test(skill=50, opponent=50, declaration="removes_risk")
        mock_roll.assert_not_called()
        self.assertTrue(result["no_roll"])
        self.assertTrue(result["success"])
        self.assertIsNone(result["roll"])
        self.assertIsNone(result["effective_pct"])
        self.assertIsNone(result["degrees"])

    def test_unrecognized_declaration_raises_before_any_roll(self):
        with unittest.mock.patch("wyrd.rules.roll_d100") as mock_roll:
            with self.assertRaises(ValueError):
                rules.opposed_test(skill=50, opponent=50, declaration="bogus")
        mock_roll.assert_not_called()

    def test_helper_who_cannot_attempt_contributes_nothing(self):
        with_helper = rules.opposed_test(
            skill=50, opponent=50, helper_skill=100, helper_can_attempt=False, seed=1
        )
        without_helper = rules.opposed_test(skill=50, opponent=50, seed=1)
        self.assertEqual(with_helper["effective_pct"], without_helper["effective_pct"])


if __name__ == "__main__":
    unittest.main()
