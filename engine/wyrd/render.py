"""Output formatting: JSON (default) and --format text.

Every verb emits a structured result; this module is the one place that turns it into
what actually reaches stdout (docs/design/27-tooling.md section 3, "structured output by
default"). Python 3.11+, standard library only.
"""

from __future__ import annotations

import json


def to_json(obj: dict) -> str:
    """Render a verb's structured result as stable, sorted-key JSON."""
    return json.dumps(obj, sort_keys=True)


def to_text(obj: dict) -> str:
    """Render a verb's structured result as a short human-readable line.

    Only the shapes this feature's own verbs produce are handled; a later feature's verb
    adds its own case here rather than this function guessing at an unknown shape.
    """
    if "error" in obj:
        error = obj["error"]
        return f"error: {error.get('reason', error)}"
    if obj.get("verb") == "roll":
        return f"d{obj['sides']}: {obj['result']}"
    if obj.get("verb") == "opposed-test":
        if obj.get("no_roll"):
            return "opposed-test: success (no roll -- the plan simply works)"
        outcome = "success" if obj["success"] else "failure"
        detail = (
            f"degrees {obj['degrees']}, wyrd: {obj['wyrd']}"
            if obj["success"]
            else f"wyrd: {obj['wyrd']}"
        )
        return f"opposed-test: {outcome} ({detail})"
    if obj.get("verb") == "declaration-bonus":
        if obj["no_roll"]:
            return f"declaration-bonus: {obj['category']} (no roll)"
        return f"declaration-bonus: {obj['category']} ({obj['bonus']:+d})"
    if obj.get("verb") == "assistance-bonus":
        return f"assistance-bonus: helper {obj['helper_skill']}% -> {obj['bonus']:+d}"
    if obj.get("verb") == "group-test":
        outcome = "success" if obj["success"] else "failure"
        return f"group-test: {obj['mode']} -> skill {obj['selected_skill']}%, {outcome}"
    if obj.get("verb") == "character-save":
        return f"character-save: {obj['path']}"
    if obj.get("verb") == "character-load":
        return f"character-load: {obj['path']} ({obj['frontmatter'].get('id', '?')})"
    if obj.get("verb") == "validate-allocation":
        if obj["valid"]:
            skills = ", ".join(f"{k}: {v}%" for k, v in obj["skills"].items())
            return f"validate-allocation: valid ({skills})"
        return f"validate-allocation: invalid ({obj['error']})"
    if obj.get("verb") == "skill-scale":
        return (
            f"skill-scale: opens {obj['open_value']}%, +{obj['advance_step']}%/advance, "
            f"untrained {obj['untrained']}%"
        )
    if obj.get("verb") == "extended-task-interval":
        done = " (done)" if obj["done"] else ""
        progress = f"{obj['progress']}/{obj['target']}"
        return f"extended-task-interval: +{obj['gained']} -> {progress}{done}"
    if obj.get("verb") == "describe":
        tools = obj.get("tools", [])
        return ", ".join(tool["name"] for tool in tools) if tools else "(no tools)"
    if "name" in obj and "inputSchema" in obj:
        # A single catalog entry, as returned by `describe --name <verb>`.
        return f"{obj['name']}: {obj['description']}"
    raise NotImplementedError(f"no text rendering for {obj!r}")
