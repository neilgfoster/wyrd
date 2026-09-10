"""The setting overrides mechanism: the closed overridable set, override-block validation,
and the three-layer resolution order.

docs/design/27-tooling.md section 4 and docs/design/24-authoring-a-setting.md ("Rules
overrides -- the hard rule"): a setting may disable, rename, retune (`tables:`) or extend
what the engine provides, and may never add a mechanism the engine does not have.
Overridability is a **closed set the engine publishes** (`describe --overridable`); an
override naming anything outside it is a **load error**, never a silent no-op. Resolution
follows `engine defaults -> setting overrides -> chronicle houserules`, last wins, and each
layer may only **narrow** what came before -- a layer may never touch a mechanism an earlier
layer already disabled.

Declarative only: a setting supplies data recognised by this closed set, never code. There is
no hook or plugin path here for a setting to run its own logic.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

#: The four override kinds a setting.yaml or houserules.yaml `overrides:` block may use.
#: These are also its top-level keys -- see docs/design/24-authoring-a-setting.md's example.
OVERRIDE_KEYS = ("disable", "rename", "tables", "extend")

#: The closed overridable set (docs/design/27-tooling.md section 4). Each entry names which
#: override kinds are legal against it, and what other mechanism it depends on -- the
#: dependency graph an engine-known contradiction check (a disabled mechanism a retained
#: rule still fires on) is checked against. `describe --overridable` publishes this set
#: verbatim; naming anything outside it is a load error.
OVERRIDABLE: dict[str, dict] = {
    "taint": {"kinds": ("disable", "rename"), "depends_on": ()},
    "trauma": {"kinds": ("disable", "rename"), "depends_on": ()},
    "oracle-prompt-npc-objective": {"kinds": ("tables", "extend"), "depends_on": ()},
    "oracle-prompt-situation-truth": {"kinds": ("tables", "extend"), "depends_on": ()},
    "oracle-prompt-thread-turn": {"kinds": ("tables", "extend"), "depends_on": ()},
    "oracle-prompt-complication": {"kinds": ("tables", "extend"), "depends_on": ()},
    "skills": {"kinds": ("extend",), "depends_on": ()},
}

#: Mechanisms a `track` verb call may name -- the subset of the overridable set that is also
#: a trackable numeric mechanism on an entity (docs/design/27-tooling.md's own worked example,
#: `wyrd track <id> taint +1`).
TRACKABLE_MECHANISMS = ("taint", "trauma")


class OverrideError(Exception):
    """An override block names something outside the closed set, or a layer widens what an
    earlier layer already narrowed."""


def describe_overridable() -> list[dict]:
    """The closed overridable set, as `describe --overridable` reports it."""
    return [
        {"name": name, "kinds": list(info["kinds"]), "depends_on": list(info["depends_on"])}
        for name, info in sorted(OVERRIDABLE.items())
    ]


def _require_kind(name: str, kind: str, layer: str) -> None:
    info = OVERRIDABLE.get(name)
    if info is None:
        raise OverrideError(f"{layer}: {name!r} is not in the engine's overridable set")
    if kind not in info["kinds"]:
        raise OverrideError(f"{layer}: {name!r} does not support {kind!r}")


def validate_block(block: dict, *, layer: str = "overrides") -> list[str]:
    """Validate one override block in isolation (no cross-layer narrowing check).

    Returns a list of problems, empty on success -- the shape `tools/check_setting.py`'s own
    validation style uses. Raising is reserved for `resolve()`, which needs to fail an entire
    load rather than collect a list.
    """
    problems: list[str] = []
    if not isinstance(block, dict):
        return [f"{layer}: overrides must be a mapping"]
    for key in block:
        if key not in OVERRIDE_KEYS:
            problems.append(f"{layer}: {key!r} is not a recognised override kind")

    disable = block.get("disable") or []
    rename = block.get("rename") or {}
    tables = block.get("tables") or {}
    extend = block.get("extend") or {}

    for name in disable:
        try:
            _require_kind(name, "disable", layer)
        except OverrideError as exc:
            problems.append(str(exc))
    for name in rename:
        try:
            _require_kind(name, "rename", layer)
        except OverrideError as exc:
            problems.append(str(exc))
    for name in tables:
        try:
            _require_kind(name, "tables", layer)
        except OverrideError as exc:
            problems.append(str(exc))
    for name in extend:
        try:
            _require_kind(name, "extend", layer)
        except OverrideError as exc:
            problems.append(str(exc))

    # A mechanism may not be disabled and simultaneously renamed/retuned/extended in the same
    # layer -- declaring `disable: [taint]` while retaining a table that fires on Taint is a
    # contradiction the engine refuses (docs/design/27-tooling.md section 4).
    touched_alive = set(rename) | set(tables) | set(extend)
    contradiction = touched_alive & set(disable)
    if contradiction:
        problems.append(
            f"{layer}: {sorted(contradiction)} named as disabled and also overridden "
            "in the same layer"
        )

    return problems


def _validate_layer(block: dict, *, layer: str, disabled_so_far: frozenset[str]) -> None:
    problems = validate_block(block, layer=layer)
    if problems:
        raise OverrideError("; ".join(problems))

    disable = block.get("disable") or []
    rename = block.get("rename") or {}
    tables = block.get("tables") or {}
    extend = block.get("extend") or {}
    touched = set(disable) | set(rename) | set(tables) | set(extend)

    # Narrowing only: a layer may never touch a mechanism an earlier layer already disabled --
    # there is no `enable:` key in this vocabulary, so any later mention of a disabled
    # mechanism is by definition an attempt to widen what came before.
    widened = touched & disabled_so_far
    if widened:
        raise OverrideError(
            f"{layer}: {sorted(widened)} already disabled by an earlier layer -- a later "
            "layer may only narrow, never widen, what came before"
        )


@dataclass(frozen=True)
class ResolvedConfig:
    """The single configuration produced by resolving engine defaults, setting overrides and
    chronicle houserules, in that order. What `describe` reflects once a setting is active."""

    disabled: frozenset[str] = field(default_factory=frozenset)
    renames: dict[str, str] = field(default_factory=dict)
    tables: dict[str, str] = field(default_factory=dict)
    extends: dict[str, list[str]] = field(default_factory=dict)

    def label(self, mechanism: str) -> str:
        """The presented word for `mechanism`: a rename if one applies, else the engine's own
        name. Presentation-only -- never what is stored (docs/design/24-authoring-a-setting.md:
        "Renames are presentation-only and never reach state")."""
        return self.renames.get(mechanism, mechanism)

    def is_enabled(self, mechanism: str) -> bool:
        return mechanism not in self.disabled


def resolve(layers: list[tuple[str, dict]]) -> ResolvedConfig:
    """Resolve `layers` -- ordered `(layer_name, overrides_block)` pairs, engine defaults
    first, then the setting's own overrides, then chronicle houserules last -- into one
    `ResolvedConfig`.

    Raises `OverrideError`, naming the offending layer and key, on any override outside the
    closed set or any layer that widens what an earlier layer already narrowed.
    """
    disabled: set[str] = set()
    renames: dict[str, str] = {}
    tables: dict[str, str] = {}
    extends: dict[str, list[str]] = {}

    for layer_name, block in layers:
        if not block:
            continue
        _validate_layer(block, layer=layer_name, disabled_so_far=frozenset(disabled))
        disabled |= set(block.get("disable") or [])
        renames.update(block.get("rename") or {})
        tables.update(block.get("tables") or {})
        # Extend is additive by nature (docs/design/15-oracle-prompts.md: rows are appended,
        # never replaced) -- each layer's extension file joins the ones before it rather than
        # overwriting them.
        for name, path in (block.get("extend") or {}).items():
            extends.setdefault(name, []).append(path)

    return ResolvedConfig(
        disabled=frozenset(disabled), renames=renames, tables=tables, extends=extends
    )


def filter_tools(tools: dict[str, dict], resolved: ResolvedConfig) -> dict[str, dict]:
    """Filter a `TOOLS` catalog by `resolved`'s disabled set.

    docs/design/27-tooling.md: "a disabled mechanism must not merely be hidden -- its verbs
    are absent from `describe`." A tool naming `mechanisms` in its catalog entry is dropped
    outright once every one of those mechanisms is disabled; if only some are, the tool
    survives with its allowed set (and, where present, its `mechanism` input enum) narrowed.
    A tool with no `mechanisms` entry is untouched -- it is not mechanism-specific.
    """
    filtered: dict[str, dict] = {}
    for name, tool in tools.items():
        mechanisms = tool.get("mechanisms")
        if not mechanisms:
            filtered[name] = tool
            continue
        remaining = [m for m in mechanisms if resolved.is_enabled(m)]
        if not remaining:
            continue
        if remaining == mechanisms:
            filtered[name] = tool
            continue
        narrowed = copy.deepcopy(tool)
        narrowed["mechanisms"] = remaining
        enum_holder = narrowed.get("inputSchema", {}).get("properties", {}).get("mechanism")
        if enum_holder is not None and "enum" in enum_holder:
            enum_holder["enum"] = list(remaining)
        filtered[name] = narrowed
    return filtered
