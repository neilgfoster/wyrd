"""End-to-end functional test across the whole engine (issue #375, specs/143).

stdlib unittest, no pytest (docs/design/27-tooling.md section 6). One player character is
constructed via `creation.create_character` and carried through every major subsystem area in
sequence -- creation, action resolution, conflict, harm/recovery, adversaries, condition tracks,
economies, systems of power, solo procedures, session/campaign structure, chronicle bootstrap --
in one test method, so the whole run is a single pass/fail result (spec.md FR-004). Every
adjacent handoff asserts a concrete value the earlier area actually produced (spec.md FR-003),
not merely that a call didn't raise.

Every seeded roll below reuses a seed already computed and verified by an existing unit test
(the combat chain and the Exposure/transformation worked example in `test_resolution.py`) or was
computed directly by running `resolution.propose` against this file's own fixture and reading the
result back (CLAUDE.md "check the maths": never eyeball a probability or a seed's outcome) --
none is a guess. Two of the created character's own fields (`swordplay`, `stamina`) are
deliberately overridden immediately before the combat step to the exact values
`test_resolution.py`'s `CombatChainTest` already verified seed 2 against, so this suite does not
have to re-derive that chain's dice itself; every other field this suite reads was produced by an
earlier step in this same test, not by a second, independent fixture.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))

from wyrd import (  # noqa: E402
    advancement,
    adversary,
    character,
    chronicle,
    combat,
    creation,
    downtime,
    economy,
    journey,
    overrides,
    rally,
    resolution,
    session,
    state,
)

#: The one career/allocation this suite's character is created with -- an entry career granting
#: `stealth`/`swordplay`, matching `tests/engine/test_creation.py`'s own `CAREER`/`VALID_ACTIONS`
#: (open+raise costs verified there, not re-derived here).
CAREER = {"skills": {"stealth": 55, "swordplay": 45}, "entry_point": True}
VALID_ACTIONS = (
    [
        {"action": "open", "skill": "stealth"},
        {"action": "open", "skill": "swordplay"},
    ]
    + [{"action": "raise", "skill": "stealth"}] * 4
    + [{"action": "raise", "skill": "swordplay"}] * 2
)

#: `test_resolution.py`'s `CombatChainTest`: attacker swordplay 60 vs. target swordplay 0,
#: target Stamina 5/5, weapon 1d8, armour 1d3, seed 2 -- a telling, doubled, armour-reduced blow
#: that drops the target's Stamina below 0 and stages a non-mortal slashing critical.
COMBAT_ATTACKER_SWORDPLAY = 60
COMBAT_TARGET_SWORDPLAY = 0
COMBAT_TARGET_STAMINA = {"current": 5, "max": 5}
COMBAT_SEED = 2

#: `test_resolution.py`'s `WorkedExampleTest`/taint-crossing fixture: bargaining 35, Taint 1,
#: major (3) Exposure, seed 5 -- fails, gains +3 Taint, crosses the threshold at 3, and stages a
#: transformation that rolls row 5 (severity 3), netting Taint back to 1, Dread +3, and setting
#: the hidden threshold to 5 on this character's first-ever Transformation.
EXPOSURE_BARGAINING = 35
EXPOSURE_STARTING_TAINT = 1
EXPOSURE_SEED = 5

#: Computed directly against this suite's own fixture (CLAUDE.md "check the maths") by running
#: `resolution.propose` for each candidate seed and reading the result back -- see this feature's
#: research.md. Seed 8: untrained (10%) `invocation` at average difficulty (eff. 10%) fails and
#: reads Ill Omen, staging both a Strain mutation and an Ill-Omen Taint mutation.
SYSTEM_OF_POWER_SEED = 8
#: Seed 1: untrained-adjacent `athletics` (20%) at Challenging (eff. 10%) fails -- used for the
#: journey hazard's own ordinary-test.
JOURNEY_HAZARD_SEED = 1


class EndToEndSequenceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.pc_path = self.root / "aria.md"
        self.attacker_path = self.root / "attacker.md"
        self.creature_path = self.root / "the-hunter.md"
        self.state_path = self.root / "state.yaml"
        self.bestiary_path = self.root / "bestiary.yaml"
        self.chronicle_path = self.root / "chronicle.yaml"

    def tearDown(self):
        self._tmp.cleanup()

    def load_pc(self):
        return character.load(self.pc_path)

    def test_end_to_end_sequence_across_every_subsystem(self):
        # -- Area 1: creation --------------------------------------------------------------
        created = creation.create_character(
            path=self.pc_path,
            name="Aria Nightingale",
            career=CAREER,
            actions=VALID_ACTIONS,
            loyalty="the-old-guard",
            mortality="standard",
            fault_line="She trusts no one, because the guild sold her out once.",
        )
        self.assertTrue(created["valid"])
        pc = created["frontmatter"]
        # open (25) + 4 raises (+5 each) = 45; open (25) + 2 raises (+5 each) = 35 -- the exact
        # allocation `career.validate_allocation` computes for VALID_ACTIONS against CAREER.
        self.assertEqual(pc["skills"], {"stealth": 45, "swordplay": 35})
        self.assertEqual(pc["stamina"], {"current": 6, "max": 6})
        self.assertEqual(pc["wounds"], [])

        # -- Area 2: action resolution (an ordinary test, propose -> commit) ----------------
        propose_result = resolution.propose(
            actor=self.pc_path, mechanic="ordinary-test", skill="stealth", seed=1
        )
        # An ordinary test alone implies no lasting consequence (resolution.py's own
        # `_mutate_ordinary_test`) -- the handoff into area 3 is that nothing here changed the
        # skill value area 3 is about to read.
        self.assertEqual(propose_result["mutations"], [])
        committed = resolution.commit(propose_result["proposal_id"])
        self.assertEqual(committed["mutations"], [])
        frontmatter, _ = self.load_pc()
        self.assertEqual(frontmatter["skills"], pc["skills"])

        # -- Area 3: conflict (combat) -------------------------------------------------------
        # Override this same character's swordplay/Stamina to the exact values
        # `CombatChainTest` already verified seed 2 against (module docstring) -- the character
        # entity is still the one area 1 created, not a fresh fixture.
        frontmatter, body = self.load_pc()
        frontmatter["skills"]["swordplay"] = COMBAT_TARGET_SWORDPLAY
        frontmatter["stamina"] = dict(COMBAT_TARGET_STAMINA)
        character.save(frontmatter, body, self.pc_path)

        character.save(
            {
                "id": "attacker",
                "type": "character",
                "skills": {"swordplay": COMBAT_ATTACKER_SWORDPLAY},
            },
            "",
            self.attacker_path,
        )

        scene = combat.start_combat(
            sides={
                "the-party": {"armed": True, "wounds": []},
                "the-attacker": {"armed": True, "wounds": []},
            },
            started_by="the-attacker",
            player_side="the-party",
            state_path=self.state_path,
        )
        self.assertEqual(scene["first_actor"], "the-attacker")

        attack_result = resolution.propose(
            actor=self.attacker_path,
            mechanic="combat-attack",
            skill="swordplay",
            target=self.pc_path,
            weapon_dice="1d8",
            armour_dice="1d3",
            seed=COMBAT_SEED,
        )
        mechanics = [step["mechanic"] for step in attack_result["steps"]]
        self.assertEqual(mechanics, ["combat-attack", "weapon-damage", "armour", "critical"])
        self.assertTrue(attack_result["steps"][0]["roll"]["telling"])
        self.assertFalse(attack_result["steps"][3]["roll"]["mortal"])
        resolution.commit(attack_result["proposal_id"])
        frontmatter, _ = self.load_pc()
        self.assertEqual(frontmatter["stamina"]["current"], -2)
        self.assertEqual(len(frontmatter["wounds"]), 1)
        wound_from_combat = frontmatter["wounds"][0]
        self.assertEqual(wound_from_combat["effect"], {"dread": 1})
        self.assertIsNone(wound_from_combat["closed"])

        # -- Area 4: harm/recovery (the Downtime loop, then Mend on that exact wound) --------
        dt = downtime.new_downtime_state()
        dt = downtime.advance_downtime(dt, "destination")
        dt = downtime.advance_downtime(dt, "upkeep")
        dt = downtime.advance_downtime(dt, "advances")
        dt = downtime.advance_downtime(dt, "undertaking", undertaking="mend")
        dt = downtime.advance_downtime(dt, "rest")
        self.assertEqual(dt["step"], "rest")
        self.assertEqual(dt["undertaking"], "mend")

        frontmatter, body = self.load_pc()
        mend_result = downtime.apply_mend(wound_from_combat["id"], frontmatter["wounds"])
        self.assertTrue(mend_result["success"])
        self.assertTrue(mend_result["closed"])
        frontmatter["wounds"] = mend_result["wounds"]
        frontmatter["stamina"]["current"] = downtime.apply_rest(frontmatter["stamina"]["max"])
        character.save(frontmatter, body, self.pc_path)
        frontmatter, _ = self.load_pc()
        self.assertIsNotNone(frontmatter["wounds"][0]["closed"])
        self.assertEqual(frontmatter["stamina"]["current"], frontmatter["stamina"]["max"])

        # -- Area 5: adversaries (a bestiary block, loaded and danger-scaled) ---------------
        self.bestiary_path.write_text(
            "creatures:\n"
            "  - id: the-hunter\n"
            "    name: A named antagonist\n"
            "    baseline: 35\n"
            "    stamina_max: 7\n"
            "    armour: modest\n"
            "    skills:\n"
            "      blade: 55\n"
            "    damage: 1d6\n"
            "    damage_type: slashing\n"
        )
        block = adversary.load("the-hunter", self.bestiary_path)
        self.assertEqual(block["skills"]["blade"], 55)
        # party == written_for -> danger_ratio is exactly 1, so the adjustment is exactly 0: the
        # scaled value equals the block's own written value, asserted rather than assumed.
        scaled_blade = adversary.adjusted_skill(block, "blade", party=4, written_for=4)
        self.assertEqual(scaled_blade, block["skills"]["blade"])
        character.save(
            {
                "id": "the-hunter",
                "type": "creature",
                "skills": {"blade": scaled_blade},
                "stamina": {"current": block["stamina_max"], "max": block["stamina_max"]},
            },
            "",
            self.creature_path,
        )
        creature_frontmatter, _ = character.load(self.creature_path)
        self.assertEqual(creature_frontmatter["skills"]["blade"], scaled_blade)

        # -- Area 6: condition tracks (Exposure, crossing a Taint threshold into Transformation)
        frontmatter, body = self.load_pc()
        frontmatter["skills"]["bargaining"] = EXPOSURE_BARGAINING
        frontmatter["taint"] = EXPOSURE_STARTING_TAINT
        character.save(frontmatter, body, self.pc_path)

        exposure_result = resolution.propose(
            actor=self.pc_path,
            mechanic="exposure",
            skill="bargaining",
            tier="major",
            seed=EXPOSURE_SEED,
        )
        self.assertEqual(
            [step["mechanic"] for step in exposure_result["steps"]],
            ["exposure", "transformation"],
        )
        transformation_step = exposure_result["steps"][1]
        self.assertEqual(transformation_step["roll"]["severity"], 3)
        resolution.commit(exposure_result["proposal_id"])
        frontmatter, _ = self.load_pc()
        # +3 (Exposure) then -3 (Transformation) -- net unchanged, but only because both steps
        # actually ran against the same character (spec.md User Story 2).
        self.assertEqual(frontmatter["taint"], EXPOSURE_STARTING_TAINT)
        self.assertEqual(frontmatter["dread"], 3)
        self.assertEqual(frontmatter["hidden_threshold"], 5)
        self.assertEqual(frontmatter["transformations"], [5])

        # -- Area 7: economies (coin, Standing, Allegiance) ----------------------------------
        frontmatter, body = self.load_pc()
        frontmatter["coin"] = 10
        catalog = [{"id": "shortsword", "name": "A plain shortsword", "price": 4}]
        spend_result = economy.spend_coin("shortsword", frontmatter["coin"], catalog)
        self.assertTrue(spend_result["success"])
        frontmatter["coin"] = spend_result["coin"]
        standing_result = economy.adjust_standing(frontmatter["reputation"]["score"], delta=-1)
        frontmatter["reputation"]["score"] = standing_result["standing"]
        # `holdings` (unlike `allegiances`) is not one of `entity.py`'s reference fields
        # (`_REFERENCE_FIELDS`), so it can be exercised against a loose entity file the same way
        # every other area here is, with no chronicle-root/entities-tree dependency this
        # feature's scope excludes (spec.md Assumptions).
        holding_result = economy.gain_holding("a-safehouse", frontmatter["holdings"])
        frontmatter["holdings"] = holding_result["holdings"]
        character.save(frontmatter, body, self.pc_path)
        frontmatter, _ = self.load_pc()
        self.assertEqual(frontmatter["coin"], 6)
        self.assertEqual(frontmatter["reputation"]["score"], -1)
        self.assertIn("a-safehouse", frontmatter["holdings"])

        # -- Area 8: specialist subsystems / systems of power --------------------------------
        resolved_overrides = overrides.resolve([("engine", {}), ("setting", {}), ("chronicle", {})])
        self.assertNotIn("invocation", resolved_overrides.disabled)

        power = {
            "skill": "invocation",
            "strain_cost": 1,
            "requires_training": False,
            "resolve_cost": 0,
            "ill_omen_taint": 1,
            "disabled_tracks": [],
        }
        power_result = resolution.propose(
            actor=self.pc_path,
            mechanic="system-of-power",
            skill="invocation",
            power=power,
            difficulty="average",
            seed=SYSTEM_OF_POWER_SEED,
        )
        self.assertEqual(power_result["roll"]["outcome"], "fail")
        self.assertEqual(power_result["roll"]["wyrd_die"], "ill_omen")
        # No `pending_omen` mutation here: area 6's own Exposure roll already left this same
        # character's persisted `pending_omen` at -10 (an Ill Omen), and this roll's fresh Wyrd
        # die reads Ill Omen again -- the token is read, applied as this roll's own declaration
        # penalty, and re-set to the *same* value, so resolution.py's own "only a value change is
        # staged" rule (module docstring) stages nothing further for that field (a genuine
        # cross-area handoff this suite would miss entirely if area 8 used a fresh fixture
        # instead of this same carried-forward character).
        mutated_fields = {mutation["field"] for mutation in power_result["mutations"]}
        self.assertEqual(mutated_fields, {"strain", "taint"})
        resolution.commit(power_result["proposal_id"])
        frontmatter, _ = self.load_pc()
        self.assertEqual(frontmatter["strain"], 1)
        self.assertEqual(frontmatter["taint"], EXPOSURE_STARTING_TAINT + 1)

        # -- Area 9: solo procedures (a journey leg and its hazard roll) ---------------------
        paced_journey = {
            "id": "the-road-to-the-shrine",
            "type": "arc",
            "scale": "journey",
            "pace": "one day's travel",
            "hazard_rating": 4,
            "hazards": {
                "1-2": {
                    "name": "washed-out ford",
                    "skill": "athletics",
                    "difficulty": "challenging",
                }
            },
            "children": [
                {"id": "first-days-road", "mode": "played"},
                {"id": "the-washed-out-ford", "mode": "summarised", "span": 2},
            ],
        }
        legs = journey.legs_for(paced_journey)
        self.assertEqual([leg["id"] for leg in legs], ["first-days-road", "the-washed-out-ford"])
        beat_result = journey.resolve_leg(legs[0])
        self.assertEqual(beat_result, {"kind": "beat", "leg": legs[0]})

        hazard = journey.roll_hazard(paced_journey, wyrd_roll=30, table_roll=1)
        self.assertTrue(hazard["activated"])
        self.assertEqual(hazard["matched"]["skill"], "athletics")
        frontmatter, body = self.load_pc()
        frontmatter["skills"]["athletics"] = 20
        character.save(frontmatter, body, self.pc_path)
        hazard_test = resolution.propose(
            actor=self.pc_path, seed=JOURNEY_HAZARD_SEED, **hazard["request"]
        )
        self.assertEqual(hazard_test["roll"]["outcome"], "fail")
        # Left open deliberately -- area 11 discards it at a Rally, closing the whole chronicle
        # lifecycle rather than a second, unrelated proposal.
        open_proposal_id = hazard_test["proposal_id"]

        closed_journey = journey.close_journey(paced_journey, legs_reached=[beat_result])
        self.assertEqual(closed_journey["reached"], [beat_result])
        not_reached_ids = [leg["id"] for leg in closed_journey["not_reached"]]
        self.assertEqual(not_reached_ids, ["the-washed-out-ford"])

        # -- Area 10: session / campaign structure (the session loop, Rally, an advance spend)
        loop = session.new_loop_state()
        loop = session.advance_loop(loop, "orient")
        loop = session.advance_loop(loop, "recap")
        loop = session.advance_loop(loop, "beat", beat_id="first-days-road")
        self.assertEqual(loop["beats_this_session"], ["first-days-road"])

        frontmatter, body = self.load_pc()
        rally_result = rally.apply_rally(
            strain=frontmatter["strain"],
            stamina=frontmatter["stamina"]["current"],
            stamina_max=frontmatter["stamina"]["max"],
            advancement_record=advancement.new_record(),
            trigger="endured",
        )
        self.assertTrue(rally_result["award"]["awarded"])
        self.assertEqual(rally_result["award"]["record"]["advances_unspent"], 1)
        frontmatter["strain"] = rally_result["strain"]
        frontmatter["stamina"]["current"] = rally_result["stamina"]
        frontmatter["advances_unspent"] = rally_result["award"]["record"]["advances_unspent"]
        character.save(frontmatter, body, self.pc_path)

        loop = session.advance_loop(loop, "close")
        self.assertTrue(loop["closed"])
        session.run_close(steps=[])

        frontmatter, body = self.load_pc()
        view = advancement.new_view(
            career="wanderer",
            skills=frontmatter["skills"],
            advances_unspent=frontmatter["advances_unspent"],
            stamina_max=frontmatter["stamina"]["max"],
        )
        spend_result = advancement.spend_advance("raise", view, CAREER, skill="stealth")
        self.assertTrue(spend_result["spent"])
        raised_stealth = frontmatter["skills"]["stealth"] + 5
        self.assertEqual(spend_result["view"]["skills"]["stealth"], raised_stealth)
        frontmatter["skills"] = spend_result["view"]["skills"]
        frontmatter["advances_unspent"] = spend_result["view"]["advances_unspent"]
        character.save(frontmatter, body, self.pc_path)
        frontmatter, _ = self.load_pc()
        self.assertEqual(frontmatter["skills"]["stealth"], 50)
        self.assertEqual(frontmatter["advances_unspent"], 0)

        # -- Area 11: chronicle bootstrap -----------------------------------------------------
        bootstrap = state.default_chronicle_state(
            name="Integration Test Chronicle",
            engine_repo="wyrd",
            engine_version="0.1.0",
            setting_repo="wyrd-setting-test",
            setting_version="0.1.0",
        )
        state.save_chronicle(bootstrap, self.chronicle_path)
        loaded_chronicle = state.load_chronicle(self.chronicle_path)
        self.assertEqual(loaded_chronicle["name"], "Integration Test Chronicle")
        self.assertIsNone(loaded_chronicle["pending"])

        # Close out the one proposal area 9 deliberately left open, exercising the chronicle's
        # own pending/rolled lifecycle end to end.
        pending = chronicle.record_rolled(None, open_proposal_id)
        self.assertEqual(pending["rolled"], open_proposal_id)
        discard_info = chronicle.discard_at_rally(pending)
        self.assertEqual(discard_info["to_discard"], open_proposal_id)
        self.assertIsNone(discard_info["pending"]["rolled"])
        resolution.discard(open_proposal_id)
        with self.assertRaises(resolution.ProposalError):
            resolution.commit(open_proposal_id)


if __name__ == "__main__":
    unittest.main()
