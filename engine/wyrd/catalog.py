"""TOOLS -- the single source of truth for every verb this engine exposes.

Pure data. `client.py`'s argparse dispatch and `describe` are both built FROM this catalog,
so discovery and execution can never drift (docs/design/27-tooling.md section 3). A later
feature adds its own verb here; nothing else about `client.py`'s dispatch changes.

Python 3.11+, standard library only.
"""

from __future__ import annotations

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
}
