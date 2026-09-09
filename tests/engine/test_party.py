"""Tests for wyrd.party: companion validation, Tension/Bond arithmetic, Loyalty gating, roster.

Run with PYTHONPATH=engine (see tests/engine/test_character.py for the same pattern).
"""

from __future__ import annotations

import pytest
from wyrd import party


def make_companion(**overrides) -> dict:
    companion = {
        "role": "companion",
        "status": "with-party",
        "objective": {"wants": "clear her brother's name", "next_step": "find the ledger"},
        "flaw": "will not abandon a debt",
        "secret": "the ledger implicates her too",
        "arc": "confess or burn the ledger",
        "career": "hedge-lawyer",
        "bond": 1,
        "taint": 0,
        "strain": 0,
        "wounds": [],
    }
    companion.update(overrides)
    return companion


# --- User Story 1: companion validation ---------------------------------------------------


def test_validate_companion_accepts_well_formed_record():
    assert party.validate_companion(make_companion()) == {"valid": True}


def test_validate_companion_rejects_missing_field():
    companion = make_companion()
    del companion["bond"]
    result = party.validate_companion(companion)
    assert result["valid"] is False
    assert "bond" in result["error"]


def test_validate_companion_rejects_extra_field():
    companion = make_companion(cohesion=2)
    result = party.validate_companion(companion)
    assert result["valid"] is False
    assert "cohesion" in result["error"]


def test_validate_companion_rejects_out_of_range_bond():
    result = party.validate_companion(make_companion(bond=4))
    assert result["valid"] is False
    assert "bond" in result["error"]


def test_validate_companion_rejects_non_integer_bond():
    result = party.validate_companion(make_companion(bond=1.5))
    assert result["valid"] is False


# --- User Story 2: Tension / Bond arithmetic ------------------------------------------------


@pytest.mark.parametrize(
    ("bond", "expected"),
    [
        (3, 0),
        (1, 0),
        (0, 1),
        (-2, 3),
    ],
)
def test_tension_delta_matches_design_table(bond, expected):
    assert party.tension_delta(1, bond=bond, strained_pairing=False) == expected


def test_tension_delta_unaffected_when_no_companion_named():
    assert party.tension_delta(1, bond=None, strained_pairing=False) == 1
    assert party.tension_delta(2, bond=None, strained_pairing=False) == 2


def test_tension_delta_doubles_under_strained_pairing():
    assert party.tension_delta(1, bond=0, strained_pairing=True) == 2
    assert party.tension_delta(1, bond=None, strained_pairing=True) == 2
    assert party.tension_delta(1, bond=3, strained_pairing=True) == 0


def test_apply_tension_breaks_and_resets_at_six():
    assert party.apply_tension(current=5, delta=2) == {"tension": 0, "broke": True}
    assert party.apply_tension(current=6, delta=0) == {"tension": 0, "broke": True}


def test_apply_tension_does_not_go_negative():
    assert party.apply_tension(current=0, delta=0) == {"tension": 0, "broke": False}


def test_apply_tension_normal_increment():
    assert party.apply_tension(current=2, delta=1) == {"tension": 3, "broke": False}


def test_downtime_and_beat_spend_reduce_tension_floored_at_zero():
    assert party.apply_tension_decrement(3) == 2
    assert party.apply_tension_decrement(0) == 0


# --- User Story 3: Loyalty relations and join gating ----------------------------------------


def test_loyalty_relation_defaults_to_undeclared():
    assert party.loyalty_relation("a", "b", {}) == "undeclared"


def test_loyalty_relation_is_symmetric():
    relations = {("crown", "free-companies"): "irreconcilable"}
    assert party.loyalty_relation("crown", "free-companies", relations) == "irreconcilable"
    assert party.loyalty_relation("free-companies", "crown", relations) == "irreconcilable"


def test_can_join_refuses_irreconcilable_pairing_and_names_it():
    relations = {("crown", "free-companies"): "irreconcilable"}
    result = party.can_join("free-companies", ["crown"], relations, party_size=1)
    assert result["allowed"] is False
    assert "irreconcilable" in result["reason"]


def test_can_join_refuses_when_party_full():
    result = party.can_join("crown", ["a", "b", "c", "d", "e"], {}, party_size=5)
    assert result["allowed"] is False
    assert "full" in result["reason"]


def test_can_join_allows_strained_and_undeclared_pairings():
    relations = {("crown", "free-companies"): "strained"}
    assert party.can_join("free-companies", ["crown"], relations, party_size=1) == {"allowed": True}
    assert party.can_join("crown", ["crown"], {}, party_size=1) == {"allowed": True}


def test_has_strained_pairing():
    relations = {("crown", "free-companies"): "strained"}
    assert party.has_strained_pairing(["crown", "free-companies"], relations) is True
    assert party.has_strained_pairing(["crown"], relations) is False


def test_loyalty_change_to_irreconcilable_breaks_tension_immediately():
    relations = {("crown", "free-companies"): "irreconcilable"}
    assert party.recheck_loyalty_change(["crown", "free-companies"], relations) is True
    result = party.apply_tension(current=1, delta=party.TENSION_BREAK)
    assert result == {"tension": 0, "broke": True}


def test_recheck_loyalty_change_no_conflict():
    assert party.recheck_loyalty_change(["crown", "crown"], {}) is False


# --- User Story 4: party roster --------------------------------------------------------------


def test_roster_returns_both_layers_unchanged():
    companion = make_companion()
    result = party.roster([companion])
    assert result == [companion]
    assert result[0]["objective"]["wants"] == "clear her brother's name"
    assert result[0]["bond"] == 1


def test_roster_handles_full_five_companion_party():
    companions = [make_companion(career=f"career-{i}") for i in range(party.MAX_PARTY_SIZE)]
    result = party.roster(companions)
    assert len(result) == party.MAX_PARTY_SIZE
    assert result == companions
