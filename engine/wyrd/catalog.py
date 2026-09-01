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
            },
            "required": ["skill", "opponent"],
        },
    },
}
