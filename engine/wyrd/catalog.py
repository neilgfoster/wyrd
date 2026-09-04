"""TOOLS -- the single source of truth for every verb this engine exposes.

Pure data. `client.py`'s argparse dispatch and `describe` are both built FROM this catalog,
so discovery and execution can never drift (docs/design/27-tooling.md section 3). A later
feature adds its own verb here; nothing else about `client.py`'s dispatch changes.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import advancement

TOOLS: dict[str, dict] = {
    "roll": {
        "name": "roll",
        "description": (
            "Roll a die (default d100) through the deterministic dice tool. Use this "
            "whenever a rule calls for a random result -- never narrate a roll without "
            "calling this first."
        ),
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "sides": {"type": "integer", "minimum": 1, "default": 100},
                "seed": {"type": "integer"},
            },
            "required": [],
        },
    },
    "opposed-test": {
        "name": "opposed-test",
        "description": (
            "Resolve a single player-facing opposed test: one roll on the acting side "
            "only, against effective% derived from the skill gap. The opponent's dice "
            "are never consulted. Use this whenever a player character or companion is "
            "opposed by an NPC/opponent."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill": {"type": "integer"},
                "opponent": {"type": "integer"},
                "seed": {"type": "integer"},
                "declaration": {
                    "type": "string",
                    "enum": [
                        "specific",
                        "specific_leveraging",
                        "brief",
                        "against_nature",
                        "removes_risk",
                    ],
                },
                "helper_skill": {"type": "integer", "minimum": 0, "maximum": 100},
                "helper_can_attempt": {"type": "boolean", "default": True},
            },
            "required": ["skill", "opponent"],
        },
    },
    "declaration-bonus": {
        "name": "declaration-bonus",
        "description": (
            "Look up the fixed point value for a declaration category (specific, "
            "specific_leveraging, brief, against_nature, removes_risk). Never derives a "
            "bonus from length -- the caller judges the category from the actual "
            "declared action."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "specific",
                        "specific_leveraging",
                        "brief",
                        "against_nature",
                        "removes_risk",
                    ],
                },
            },
            "required": ["category"],
        },
    },
    "assistance-bonus": {
        "name": "assistance-bonus",
        "description": (
            "Look up a helper's assistance bonus: a tenth of their own skill, rounded "
            "down, capped at +10. Zero if they could not attempt the task alone."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "helper_skill": {"type": "integer", "minimum": 0, "maximum": 100},
                "can_attempt": {"type": "boolean", "default": True},
            },
            "required": ["helper_skill"],
        },
    },
    "group-test": {
        "name": "group-test",
        "description": (
            "Resolve a group test: select the most- or least-capable member's skill "
            "(untrained 10% for a member with none relevant), then resolve one opposed "
            "test against it. A group rolls once, never once per member."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "member_skills": {"type": "array", "items": {"type": ["integer", "null"]}},
                "mode": {"type": "string", "enum": ["most_capable", "least_capable"]},
                "opponent": {"type": "integer"},
                "seed": {"type": "integer"},
            },
            "required": ["member_skills", "mode", "opponent"],
        },
    },
    "extended-task-interval": {
        "name": "extended-task-interval",
        "description": (
            "Resolve one interval of an extended task: one opposed test, adding "
            "max(1, degrees) to progress on success, nothing on failure. Reports whether "
            "the task is now done. Does not persist progress -- the caller carries it "
            "into the next interval."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill": {"type": "integer"},
                "opponent": {"type": "integer"},
                "progress": {"type": "integer", "minimum": 0},
                "target": {"type": "integer", "minimum": 1},
                "seed": {"type": "integer"},
            },
            "required": ["skill", "opponent", "progress", "target"],
        },
    },
    "character-save": {
        "name": "character-save",
        "description": (
            "Save a player-character entity to a file, validating wound rules before writing."
        ),
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "frontmatter": {"type": "object"},
                "body": {"type": "string", "default": ""},
            },
            "required": ["path", "frontmatter"],
        },
    },
    "character-load": {
        "name": "character-load",
        "description": (
            "Load a player-character entity from a file, validating its wounds against "
            "the documented load-error rules."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    "skill-scale": {
        "name": "skill-scale",
        "description": (
            "Report the skill-scale constants: the value a skill opens at, the amount it "
            "rises per advance, and the untrained flat rate."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    "validate-allocation": {
        "name": "validate-allocation",
        "description": (
            "Validate an 8-advance allocation against a career (optionally widened by an "
            "ancestry), per docs/design/11-character-creation.md section 3. Does not "
            "generate an allocation -- a character is chosen, not rolled (ADR 0014)."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "career_json": {"type": "string"},
                "ancestry_json": {"type": "string"},
                "actions_json": {"type": "string"},
            },
            "required": ["career_json", "actions_json"],
        },
    },
    "award-advance": {
        "name": "award-advance",
        "description": (
            "Award one advance against a named session trigger -- Learned, Drove, Practised "
            "or Endured -- per docs/design/03-rules.md section 6. Verifies that the claimed "
            "award is legal; it never judges whether the fiction met the trigger, which is "
            "the GM's call."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "trigger": {"type": "string", "enum": list(advancement.TRIGGERS)},
                "awarded": {"type": "array", "items": {"type": "string"}},
                "advances_unspent": {"type": "integer"},
            },
            "required": ["trigger"],
        },
    },
    "begin-session": {
        "name": "begin-session",
        "description": (
            "Open a new session: every award trigger becomes available again and the "
            "unspent-advance balance carries over untouched "
            "(docs/design/03-rules.md section 6)."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "awarded": {"type": "array", "items": {"type": "string"}},
                "advances_unspent": {"type": "integer"},
            },
            "required": [],
        },
    },
    "create-character": {
        "name": "create-character",
        "description": (
            "Run the 8-step character-creation procedure: validate an advance allocation "
            "and, on success, produce a complete player-character entity with the fixed "
            "starting values from docs/design/11-character-creation.md section 2."
        ),
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "name": {"type": "string"},
                "career_json": {"type": "string"},
                "ancestry_json": {"type": "string"},
                "actions_json": {"type": "string"},
                "loyalty": {"type": "string"},
                "mortality": {"type": "string", "enum": ["low", "standard", "high"]},
                "drives_json": {"type": "string", "default": "[]"},
                "misfortune": {"type": "string"},
                "fault_line": {"type": "string"},
            },
            "required": [
                "path",
                "name",
                "career_json",
                "actions_json",
                "loyalty",
                "mortality",
                "fault_line",
            ],
        },
    },
    "propose": {
        "name": "propose",
        "description": (
            "Resolve one roll against an actor's own state (looked up by the engine, not "
            "supplied by the caller) and stage any implied mutation. Writes nothing -- "
            "state on disk is unchanged until a matching commit. Returns a proposal id."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "actor": {"type": "string"},
                "mechanic": {
                    "type": "string",
                    "enum": ["ordinary-test", "exposure", "combat-attack"],
                },
                "skill": {"type": "string"},
                "target": {"type": "string"},
                "difficulty": {
                    "type": "string",
                    "enum": [
                        "easy",
                        "average",
                        "challenging",
                        "difficult",
                        "hard",
                        "very_hard",
                    ],
                    "default": "average",
                },
                "declaration_bonus": {"type": "integer", "default": 0},
                "tier": {"type": "string", "enum": ["minor", "moderate", "major"]},
                "weapon_dice": {"type": "string"},
                "armour_dice": {"type": "string"},
                "damage_type": {
                    "type": "string",
                    "enum": ["slashing", "piercing", "blunt", "searing"],
                },
                "dread_witnessed": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "On an ordinary-test only: the caller's own already-decided fictional "
                        "judgment that target was seen by someone who has not made their peace "
                        "with its transformation, so target's total Dread penalises the roll "
                        "(docs/design/07-transformations.md 'Dread')."
                    ),
                },
                "seed": {"type": "integer"},
            },
            "required": ["actor", "mechanic"],
        },
    },
    "commit": {
        "name": "commit",
        "description": (
            "Apply exactly a proposal's staged mutations to state, atomically, and "
            "invalidate the id. Errors, rather than silently no-opping, if the id does "
            "not resolve to a currently-open proposal."
        ),
        "annotations": {
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {"proposal_id": {"type": "string"}},
            "required": ["proposal_id"],
        },
    },
    "discard": {
        "name": "discard",
        "description": (
            "Invalidate a proposal id without writing anything. Errors if the id does "
            "not resolve to a currently-open proposal."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {"proposal_id": {"type": "string"}},
            "required": ["proposal_id"],
        },
    },
    "reroll": {
        "name": "reroll",
        "description": (
            "Spend a reroll resource (resolve, fortune, bargain) against one staged step: "
            "discard exactly its downstream set (itself and everything that depends on "
            "it) and freshly resolve it under the resource's own modifier, re-cascading "
            "under the same rule propose uses. Everything outside the downstream set is "
            "untouched. Does not invalidate the proposal id -- only commit/discard do."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "proposal_id": {"type": "string"},
                "step": {"type": "integer"},
                "resource": {"type": "string", "enum": ["resolve", "fortune", "bargain"]},
                "seed": {"type": "integer"},
            },
            "required": ["proposal_id", "step", "resource"],
        },
    },
}
