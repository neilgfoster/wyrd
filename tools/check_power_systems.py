#!/usr/bin/env python3
"""Validate a setting's systems-of-power declarations against the schema.

docs/design/09-systems-of-power.md defines the schema a setting fills in to declare a system of
power: what skill it tests, what it costs, whether it requires training, and what an Ill Omen
costs on top. ADR 0036 decided this is one configurable mechanism rather than a set of
engine-defined mechanism shapes -- the unrecognised-field rejection below is what actually
enforces that decision at the tooling level, the same way check_bestiary.py and check_gear.py
already enforce it for the adversary block and the gear schema.

This validator fails loudly on four classes, mirroring check_bestiary.py exactly:

1. **A missing required field.**
2. **An unrecognised field** -- rejected rather than ignored, since an unrecognised field is the
   quiet path by which a setting adds a mechanism the schema does not have.
3. **A value outside the range the engine can absorb** -- a non-positive cost, a malformed id.
4. **A `skill` the setting never declared**, when a skill list is supplied for cross-checking.

Every failure is reported, not just the first, and every one names the entry and the field.

Usage:
    python3 tools/check_power_systems.py <path-to-power.yaml> [...]
    python3 tools/check_power_systems.py --format json <path>
    python3 tools/check_power_systems.py            # runs the embedded self-test only

Python 3.11+, standard library only (docs/design/27-tooling.md section 2). YAML is read by the same
small internal reader tools/check_bestiary.py uses, for the restricted subset Wyrd uses -- there
is deliberately no third-party YAML dependency.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import tempfile

# --- The schema, from docs/design/09-systems-of-power.md ----------------------

REQUIRED_FIELDS = {"id", "name", "skill", "strain_cost", "requires_training"}
OPTIONAL_FIELDS = {"resolve_cost", "ill_omen_taint", "description", "intensity_tiers"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # docs/design/25-entities.md: kebab-case

DEFAULT_ILL_OMEN_TAINT = 1

# The six difficulty-ladder rungs, docs/design/03-rules.md section 1's table -- intensity_tiers
# names one of these rather than inventing a second scale.
TIER_REQUIRED_FIELDS = {
    "label",
    "difficulty",
    "cost_multiplier",
    "ill_omen_taint_bonus",
}
DIFFICULTY_RUNGS = {"easy", "average", "challenging", "difficult", "hard", "very hard"}


# --- The small internal reader ----------------------------------------------
# The restricted subset: nested mappings, lists of mappings or scalars, scalars, comments,
# blank lines. Indentation must be consistent within a block, but its width is free, and a
# sequence may sit either indented under its key or at the key's own indentation -- both are
# legal YAML and both get written. Anything outside the subset is an error rather than a guess.
# This is the same reader tools/check_bestiary.py carries; duplicated rather than imported so
# this validator has no dependency on another tool's module staying stable underneath it.


class YamlError(Exception):
    pass


def _scalar(text: str):
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~", ""):
        return None
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def _parse_block(lines: list[tuple[int, int, str]], start: int, indent: int):
    """Parse one block at the given indentation. Returns (value, next_index)."""
    i = start
    items: list = []
    mapping: dict = {}
    while i < len(lines):
        lineno, ind, text = lines[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"line {lineno}: unexpected indentation")
        if items and not text.startswith("- "):
            break
        if text.startswith("- "):
            rest = text[2:].strip()
            if ":" in rest and not rest.startswith(('"', "'")):
                key, _, val = rest.partition(":")
                sub_lines = [(lineno, indent + 2, f"{key.strip()}:{val}")]
                j = i + 1
                while j < len(lines) and lines[j][1] > indent:
                    sub_lines.append(lines[j])
                    j += 1
                value, _ = _parse_block(sub_lines, 0, indent + 2)
                items.append(value)
                i = j
                continue
            items.append(_scalar(rest))
            i += 1
            continue
        if ":" not in text:
            raise YamlError(f"line {lineno}: expected 'key: value' or '- item'")
        key, _, val = text.partition(":")
        key = key.strip()
        val = val.strip()
        if val:
            mapping[key] = _scalar(val)
            i += 1
            continue
        j = i + 1
        if j < len(lines) and lines[j][1] > indent:
            value, j = _parse_block(lines, j, lines[j][1])
            mapping[key] = value
        elif j < len(lines) and lines[j][1] == indent and lines[j][2].startswith("- "):
            value, j = _parse_block(lines, j, indent)
            mapping[key] = value
        else:
            mapping[key] = None
        i = j
    if items and mapping:
        raise YamlError("a block is either a list or a mapping, never both")
    return (items if items else mapping), i


def read_yaml(path: pathlib.Path):
    raw = path.read_text(encoding="utf-8").splitlines()
    lines: list[tuple[int, int, str]] = []
    for lineno, line in enumerate(raw, 1):
        if "#" in line:
            line = line.split("#", 1)[0]
        if not line.strip():
            continue
        if line.lstrip().startswith("---"):
            continue
        lines.append((lineno, len(line) - len(line.lstrip()), line.strip()))
    if not lines:
        return {}
    value, _ = _parse_block(lines, 0, lines[0][1])
    return value


# --- The checks ---------------------------------------------------------------


def check_tier(tier, index: int, label: str, bad) -> None:
    """Validate one entry of a system of power's intensity_tiers list.

    docs/design/09-systems-of-power.md's Intensity tiers section: a tier is malformed the same
    four ways check_entry already rejects a system of power -- a missing/empty required field or
    a value outside the range the engine can absorb. Failures are named by tier position, since a
    tier has no id of its own to identify it by.
    """
    tier_label = f"intensity_tiers[{index}]"
    if not isinstance(tier, dict):
        bad(tier_label, "entry is not a mapping")
        return

    for field in sorted(TIER_REQUIRED_FIELDS - set(tier)):
        bad(f"{tier_label}.{field}", "required field is missing")
    for field in sorted(set(tier) - TIER_REQUIRED_FIELDS):
        bad(f"{tier_label}.{field}", "field is not defined by the intensity-tier schema")

    if "label" in tier and (not isinstance(tier["label"], str) or not tier["label"]):
        bad(f"{tier_label}.label", f"{tier['label']!r} is not a non-empty label")

    if "difficulty" in tier:
        difficulty = tier["difficulty"]
        if not isinstance(difficulty, str) or difficulty not in DIFFICULTY_RUNGS:
            bad(
                f"{tier_label}.difficulty",
                f"{difficulty!r} is not one of the six recognised difficulty rungs "
                f"({', '.join(sorted(DIFFICULTY_RUNGS))})",
            )

    if "cost_multiplier" in tier:
        multiplier = tier["cost_multiplier"]
        if not isinstance(multiplier, (int, float)) or isinstance(multiplier, bool):
            bad(f"{tier_label}.cost_multiplier", f"{multiplier!r} is not a number")
        elif multiplier <= 0:
            bad(
                f"{tier_label}.cost_multiplier",
                f"{multiplier} must be a positive number",
            )

    if "ill_omen_taint_bonus" in tier:
        bonus = tier["ill_omen_taint_bonus"]
        if not isinstance(bonus, int) or isinstance(bonus, bool):
            bad(f"{tier_label}.ill_omen_taint_bonus", f"{bonus!r} is not a whole number")
        elif bonus < 0:
            bad(f"{tier_label}.ill_omen_taint_bonus", f"{bonus} must not be negative")


def check_entry(entry, where: str, known_skills: set[str] | None = None) -> list[str]:
    problems: list[str] = []

    if not isinstance(entry, dict):
        return [f"{where}: entry is not a mapping"]

    ident = entry.get("id")
    label = f"{where}[{ident}]" if isinstance(ident, str) else where

    def bad(field: str, why: str) -> None:
        problems.append(f"{label}: {field}: {why}")

    for field in sorted(REQUIRED_FIELDS - set(entry)):
        bad(field, "required field is missing")
    for field in sorted(set(entry) - ALL_FIELDS):
        bad(field, "field is not defined by the system-of-power schema")

    if isinstance(ident, str) and not ID_RE.match(ident):
        bad("id", f"{ident!r} is not a stable kebab-case identifier")

    skill = entry.get("skill")
    if "skill" in entry:
        if not isinstance(skill, str) or not skill:
            bad("skill", f"{skill!r} is not a skill name")
        elif known_skills is not None and skill not in known_skills:
            bad("skill", f"{skill!r} is not a skill this setting has declared")

    for field in ("strain_cost", "resolve_cost", "ill_omen_taint"):
        if field in entry:
            value = entry[field]
            if not isinstance(value, int) or isinstance(value, bool):
                bad(field, f"{value!r} is not a whole number")
            elif value <= 0:
                bad(field, f"{value} must be a positive number")

    if "requires_training" in entry and not isinstance(entry["requires_training"], bool):
        bad("requires_training", f"{entry['requires_training']!r} is not true or false")

    if "description" in entry and not isinstance(entry["description"], str):
        bad("description", "must be text")

    if "intensity_tiers" in entry:
        tiers = entry["intensity_tiers"]
        if not isinstance(tiers, list):
            bad("intensity_tiers", f"{tiers!r} is not a list")
        else:
            for index, tier in enumerate(tiers):
                check_tier(tier, index, label, bad)

    return problems


def check_file(path: pathlib.Path, known_skills: set[str] | None = None) -> list[str]:
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [f"{path}: {exc}"]
    except OSError as exc:
        return [f"{path}: {exc}"]

    if not isinstance(data, dict) or "systems_of_power" not in data:
        return [f"{path}: expected a top-level 'systems_of_power:' list"]
    systems = data["systems_of_power"]
    if not isinstance(systems, list) or not systems:
        return [f"{path}: 'systems_of_power' must be a non-empty list"]

    problems: list[str] = []
    seen: dict[str, int] = {}
    for n, entry in enumerate(systems):
        problems.extend(check_entry(entry, f"{path}:systems_of_power[{n}]", known_skills))
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            if entry["id"] in seen:
                problems.append(
                    f"{path}:systems_of_power[{n}][{entry['id']}]: id: duplicates "
                    f"systems_of_power[{seen[entry['id']]}] -- an id is stable and unique"
                )
            seen[entry["id"]] = n
    return problems


# --- Resolution trace ---------------------------------------------------------
# Confirms, for a given entry, exactly what docs/design/09-systems-of-power.md claims: cost is
# applied on resolution regardless of outcome, and the declared ill_omen_taint (or the default)
# is what an Ill Omen applies. This does not touch docs/design/03-rules.md section 1's own
# resolution maths (difficulty, degrees, the Wyrd die) -- nothing about a power test perturbs
# it, so this
# script makes no claim about it and imports nothing from check_mapping.py.


def resolution_trace(entry: dict, tier_label: str | None = None) -> dict:
    """The cost and Ill Omen Taint an invocation actually pays/risks.

    With no tier_label, this is unchanged from before intensity_tiers existed -- the base
    strain_cost/resolve_cost/ill_omen_taint, applied exactly as docs/design/09-systems-of-power.md's
    Resolution and Ill Omen sections state. With tier_label naming one of the system's declared
    intensity_tiers, the Intensity tiers section's formulas apply on top: cost is multiplied by
    the tier's cost_multiplier, ill_omen_taint gains the tier's ill_omen_taint_bonus.
    """
    strain = entry["strain_cost"]
    resolve = entry.get("resolve_cost", 0)
    ill_omen_taint = entry.get("ill_omen_taint", DEFAULT_ILL_OMEN_TAINT)

    if tier_label is not None:
        tiers = entry.get("intensity_tiers", [])
        matches = [t for t in tiers if isinstance(t, dict) and t.get("label") == tier_label]
        if not matches:
            raise KeyError(f"no intensity tier labelled {tier_label!r} on this entry")
        tier = matches[0]
        strain *= tier["cost_multiplier"]
        resolve *= tier["cost_multiplier"]
        ill_omen_taint += tier["ill_omen_taint_bonus"]

    return {
        "strain_paid": strain,
        "resolve_paid": resolve,
        "ill_omen_taint": ill_omen_taint,
    }


# --- Embedded worked examples / self-test -------------------------------------

EMBER_CRAFT_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    resolve_cost: 1
    requires_training: true
    ill_omen_taint: 1
    description: "Drawing heat and light from the practitioner's own reserve."
"""

SIGNAL_ATTUNEMENT_YAML = """
systems_of_power:
  - id: signal-attunement
    name: Signal attunement
    skill: signal-attunement
    strain_cost: 3
    requires_training: true
    ill_omen_taint: 2
    description: "Reading the ambient dataflow past an augmentation's rating."
"""

MISSING_FIELD_YAML = """
systems_of_power:
  - id: broken-one
    name: Broken One
    skill: broken-one
    requires_training: true
"""

UNRECOGNISED_FIELD_YAML = """
systems_of_power:
  - id: broken-two
    name: Broken Two
    skill: broken-two
    strain_cost: 2
    requires_training: false
    mana_pool: 20
"""

BAD_ID_YAML = """
systems_of_power:
  - id: Broken_Three
    name: Broken Three
    skill: broken-three
    strain_cost: 2
    requires_training: false
"""

NON_POSITIVE_COST_YAML = """
systems_of_power:
  - id: broken-four
    name: Broken Four
    skill: broken-four
    strain_cost: 0
    requires_training: false
"""

TIERED_EMBER_CRAFT_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    resolve_cost: 1
    requires_training: true
    ill_omen_taint: 1
    intensity_tiers:
      - label: minor
        difficulty: average
        cost_multiplier: 1
        ill_omen_taint_bonus: 0
      - label: moderate
        difficulty: hard
        cost_multiplier: 2
        ill_omen_taint_bonus: 1
      - label: major
        difficulty: very hard
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
"""

BAD_TIER_DIFFICULTY_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
    intensity_tiers:
      - label: major
        difficulty: apocalyptic
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
"""

BAD_TIER_MULTIPLIER_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
    intensity_tiers:
      - label: major
        difficulty: very hard
        cost_multiplier: 0
        ill_omen_taint_bonus: 3
"""

BAD_TIER_TAINT_BONUS_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
    intensity_tiers:
      - label: major
        difficulty: very hard
        cost_multiplier: 4
        ill_omen_taint_bonus: -1
"""

MISSING_TIER_LABEL_YAML = """
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    requires_training: true
    intensity_tiers:
      - difficulty: very hard
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
"""


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)

        ember_path = tmpdir / "ember.yaml"
        ember_path.write_text(EMBER_CRAFT_YAML, encoding="utf-8")
        problems = check_file(ember_path)
        assert not problems, f"ember-craft fixture should validate clean, got: {problems}"

        signal_path = tmpdir / "signal.yaml"
        signal_path.write_text(SIGNAL_ATTUNEMENT_YAML, encoding="utf-8")
        problems = check_file(signal_path)
        assert not problems, f"signal-attunement fixture should validate clean, got: {problems}"

        # Both worked examples validate against the identical schema (spec SC-003): neither
        # needed a field the other does not use.
        ember_data = read_yaml(ember_path)["systems_of_power"][0]
        signal_data = read_yaml(signal_path)["systems_of_power"][0]
        assert set(ember_data) <= ALL_FIELDS | {"id"}
        assert set(signal_data) <= ALL_FIELDS | {"id"}

        # Resolution trace: cost applied on resolution, matching docs/design/09-systems-of-power.md.
        ember_trace = resolution_trace(ember_data)
        assert ember_trace == {"strain_paid": 2, "resolve_paid": 1, "ill_omen_taint": 1}
        signal_trace = resolution_trace(signal_data)
        assert signal_trace == {
            "strain_paid": 3,
            "resolve_paid": 0,
            "ill_omen_taint": 2,
        }

        # Ill Omen trace: default applies when a fixture omits ill_omen_taint.
        no_taint_field = dict(ember_data)
        del no_taint_field["ill_omen_taint"]
        assert resolution_trace(no_taint_field)["ill_omen_taint"] == DEFAULT_ILL_OMEN_TAINT

        missing_path = tmpdir / "missing.yaml"
        missing_path.write_text(MISSING_FIELD_YAML, encoding="utf-8")
        problems = check_file(missing_path)
        assert any("strain_cost" in p and "missing" in p for p in problems), problems

        unrecognised_path = tmpdir / "unrecognised.yaml"
        unrecognised_path.write_text(UNRECOGNISED_FIELD_YAML, encoding="utf-8")
        problems = check_file(unrecognised_path)
        assert any("mana_pool" in p for p in problems), problems

        bad_id_path = tmpdir / "bad_id.yaml"
        bad_id_path.write_text(BAD_ID_YAML, encoding="utf-8")
        problems = check_file(bad_id_path)
        assert any("id" in p and "kebab-case" in p for p in problems), problems

        non_positive_path = tmpdir / "non_positive.yaml"
        non_positive_path.write_text(NON_POSITIVE_COST_YAML, encoding="utf-8")
        problems = check_file(non_positive_path)
        assert any("strain_cost" in p and "positive" in p for p in problems), problems

        # A skill the setting never declared is rejected when a skill list is supplied.
        problems = check_file(ember_path, known_skills={"signal-attunement"})
        assert any("skill" in p and "ember-craft" in p for p in problems), problems

        # intensity_tiers: a well-formed tiered declaration validates clean (spec User Story 1).
        tiered_path = tmpdir / "tiered.yaml"
        tiered_path.write_text(TIERED_EMBER_CRAFT_YAML, encoding="utf-8")
        problems = check_file(tiered_path)
        assert not problems, f"tiered ember-craft fixture should validate clean, got: {problems}"

        # A system of power with no intensity_tiers is unaffected -- same fixture, same trace,
        # as before this feature existed (spec User Story 2, FR-003/FR-006).
        assert resolution_trace(ember_data) == {
            "strain_paid": 2,
            "resolve_paid": 1,
            "ill_omen_taint": 1,
        }

        # Resolution trace at a non-default tier: hand-computed expected values, not a
        # re-derivation of the formula under test (CLAUDE.md: assert prior numbers).
        # major: cost_multiplier 4, ill_omen_taint_bonus 3 -> strain 2*4=8, resolve 1*4=4,
        # taint 1+3=4.
        tiered_data = read_yaml(tiered_path)["systems_of_power"][0]
        major_trace = resolution_trace(tiered_data, tier_label="major")
        assert major_trace == {
            "strain_paid": 8,
            "resolve_paid": 4,
            "ill_omen_taint": 4,
        }, major_trace
        # minor: cost_multiplier 1, ill_omen_taint_bonus 0 -> identical to the untiered base.
        minor_trace = resolution_trace(tiered_data, tier_label="minor")
        assert minor_trace == {
            "strain_paid": 2,
            "resolve_paid": 1,
            "ill_omen_taint": 1,
        }, minor_trace

        # Each malformed-tier class is rejected, naming the tier at fault (spec User Story 3).
        bad_difficulty_path = tmpdir / "bad_tier_difficulty.yaml"
        bad_difficulty_path.write_text(BAD_TIER_DIFFICULTY_YAML, encoding="utf-8")
        problems = check_file(bad_difficulty_path)
        assert any("intensity_tiers[0].difficulty" in p and "apocalyptic" in p for p in problems), (
            problems
        )

        bad_multiplier_path = tmpdir / "bad_tier_multiplier.yaml"
        bad_multiplier_path.write_text(BAD_TIER_MULTIPLIER_YAML, encoding="utf-8")
        problems = check_file(bad_multiplier_path)
        assert any(
            "intensity_tiers[0].cost_multiplier" in p and "positive" in p for p in problems
        ), problems

        bad_taint_bonus_path = tmpdir / "bad_tier_taint_bonus.yaml"
        bad_taint_bonus_path.write_text(BAD_TIER_TAINT_BONUS_YAML, encoding="utf-8")
        problems = check_file(bad_taint_bonus_path)
        assert any(
            "intensity_tiers[0].ill_omen_taint_bonus" in p and "negative" in p for p in problems
        ), problems

        missing_label_path = tmpdir / "missing_tier_label.yaml"
        missing_label_path.write_text(MISSING_TIER_LABEL_YAML, encoding="utf-8")
        problems = check_file(missing_label_path)
        assert any("intensity_tiers[0].label" in p and "missing" in p for p in problems), problems

    print(
        "Self-test passed: both worked examples validate clean, every rejection class fires, "
        "and the resolution/Ill Omen trace matches the declared costs."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=pathlib.Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    if not args.paths:
        self_test()
        return 0

    problems: list[str] = []
    for path in args.paths:
        problems.extend(check_file(path))

    if args.format == "json":
        print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    elif problems:
        print(f"FAILED ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
    else:
        checked = ", ".join(str(p) for p in args.paths)
        print(f"All systems of power hold. ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
