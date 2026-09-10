#!/usr/bin/env python3
"""Validate a setting's setting.yaml against the identity and tone-contract shape.

docs/design/24-authoring-a-setting.md gives setting.yaml's shape -- identity (name, title, line),
engine version compatibility (requires_engine), the setting's own version, and the tone contract
-- but until this script existed nothing checked a setting author actually filled it in correctly.
A setting whose requires_engine the running engine cannot satisfy, or whose tone contract omits a
key or uses a value outside its closed vocabulary, would otherwise only surface as a confusing
failure somewhere downstream.

This is the validator for docs/design/24-authoring-a-setting.md's setting.yaml section. It fails
loudly on five classes:

1. **A missing required field**, top-level or within the tone contract.
2. **An unrecognised top-level field.** Rejected rather than ignored -- the same reasoning as
   check_bestiary.py's unrecognised-field rejection.
3. **A tone value outside its closed vocabulary.**
4. **A requires_engine range the running engine does not satisfy**, or one that is not written in
   the closed comparator syntax this script understands.
5. **An `overrides:` block naming anything outside the engine's closed overridable set**, or
   using an override kind (disable/rename/tables/extend) a mechanism does not support --
   delegated to `wyrd.overrides.validate_block`, the same validator the engine's own
   resolution (`describe --overridable`, #316) is built on, so this script and the engine can
   never disagree about what is overridable.

Every failure is reported, not just the first, and every one names the offending field.

Usage:
    python3 tools/check_setting.py <path-to-setting.yaml> [...]
    python3 tools/check_setting.py --format json <path>

Python 3.11+, standard library only (docs/design/27-tooling.md section 2). YAML is read by
check_bestiary.py's small internal reader, the same restricted subset check_gear.py already
reuses -- there is deliberately no third-party YAML dependency and no second reader.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "engine"))

from check_bestiary import YamlError, read_yaml  # noqa: E402
from wyrd import __version__ as ENGINE_VERSION  # noqa: E402
from wyrd import overrides as wyrd_overrides  # noqa: E402

# --- The shape, from docs/design/24-authoring-a-setting.md ----------------------

REQUIRED_FIELDS = {"name", "title", "line", "requires_engine", "version", "description", "tone"}
# `overrides` is a real setting.yaml key, owned by a separate feature (the overrides mechanism,
# #316) -- recognised here so it is never wrongly flagged as an unrecognised field. Its contents
# ARE validated below, against the same closed overridable set the engine itself resolves.
OPTIONAL_FIELDS = {"overrides"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

TONE_VOCAB = {
    "prophecy": ("forbidden", "rare", "central"),
    "victory": ("mitigation", "mixed", "triumph"),
    "power_curve": ("flat", "moderate", "heroic"),
    "scope": ("personal", "regional", "world"),
    "scale_drift": ("suppressed", "allowed"),
    "mortality": ("low", "standard", "high"),
}
# `register` is free text -- the setting's own line naming its voice, not a closed vocabulary.
TONE_REQUIRED_FIELDS = set(TONE_VOCAB) | {"register"}

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
COMPARATOR_RE = re.compile(r"^(>=|<=|==|>|<)(\d+\.\d+\.\d+)$")


# --- requires_engine comparison ----------------------------------------------


def _parse_version(text: str) -> tuple[int, int, int]:
    match = VERSION_RE.match(text)
    if not match:
        raise ValueError(f"{text!r} is not a MAJOR.MINOR.PATCH version")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _parse_requires_engine(spec: str) -> list[tuple[str, tuple[int, int, int]]]:
    """Parse a closed comparator syntax: >=, <=, ==, >, < joined by commas (AND)."""
    clauses = []
    for raw in spec.split(","):
        raw = raw.strip()
        match = COMPARATOR_RE.match(raw)
        if not match:
            raise ValueError(
                f"{raw!r} is not a supported comparator "
                "(expected one of >=, <=, ==, >, < followed by MAJOR.MINOR.PATCH)"
            )
        op, version_text = match.groups()
        clauses.append((op, _parse_version(version_text)))
    if not clauses:
        raise ValueError("requires_engine has no clauses")
    return clauses


_OPS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
}


def _engine_satisfies(requires_engine: str, engine_version: str) -> bool:
    clauses = _parse_requires_engine(requires_engine)
    current = _parse_version(engine_version)
    return all(_OPS[op](current, bound) for op, bound in clauses)


# --- The checks ----------------------------------------------------------------


def validate(data, path, engine_version: str = ENGINE_VERSION) -> list[str]:
    problems: list[str] = []

    if not isinstance(data, dict):
        return [f"{path}: expected a top-level mapping"]

    def bad(field: str, why: str) -> None:
        problems.append(f"{path}: {field}: {why}")

    for field in sorted(REQUIRED_FIELDS - set(data)):
        bad(field, "required field is missing")
    for field in sorted(set(data) - ALL_FIELDS):
        bad(field, "field is not defined by setting.yaml's shape")

    for field in ("name", "title", "line", "description"):
        if field in data and not (isinstance(data[field], str) and data[field].strip()):
            bad(field, f"{data[field]!r} is not a non-empty string")

    if "version" in data:
        version = data["version"]
        if not isinstance(version, str) or not VERSION_RE.match(version):
            bad("version", f"{version!r} is not a MAJOR.MINOR.PATCH version")

    if "requires_engine" in data:
        requires_engine = data["requires_engine"]
        if not isinstance(requires_engine, str):
            bad("requires_engine", f"{requires_engine!r} is not a string")
        else:
            try:
                if not _engine_satisfies(requires_engine, engine_version):
                    bad(
                        "requires_engine",
                        f"declares {requires_engine!r}, which running engine "
                        f"{engine_version} does not satisfy",
                    )
            except ValueError as exc:
                bad("requires_engine", str(exc))

    if "tone" in data:
        tone = data["tone"]
        if not isinstance(tone, dict):
            bad("tone", "must be a mapping")
        else:
            for field in sorted(TONE_REQUIRED_FIELDS - set(tone)):
                bad(f"tone.{field}", "required field is missing")
            for field in sorted(set(tone) - TONE_REQUIRED_FIELDS):
                bad(f"tone.{field}", "field is not defined by the tone contract")
            for field, vocab in TONE_VOCAB.items():
                if field in tone and tone[field] not in vocab:
                    bad(f"tone.{field}", f"{tone[field]!r} is not one of {', '.join(vocab)}")
            if "register" in tone and not (
                isinstance(tone["register"], str) and tone["register"].strip()
            ):
                bad("tone.register", f"{tone['register']!r} is not a non-empty string")

    if "overrides" in data:
        for problem in wyrd_overrides.validate_block(data["overrides"], layer=str(path)):
            problems.append(problem)

    return problems


def load_setting(path: pathlib.Path, engine_version: str = ENGINE_VERSION) -> dict:
    """Read and validate a setting.yaml, returning its parsed data on success.

    Raises YamlError carrying every problem found, joined into one message, on failure -- whether
    that failure is a YAML parse error or a validation problem.
    """
    data = read_yaml(path)
    problems = validate(data, path, engine_version)
    if problems:
        raise YamlError("; ".join(problems))
    return data


def check_file(path: pathlib.Path) -> list[str]:
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [f"{path}: {exc}"]
    except OSError as exc:
        return [f"{path}: {exc}"]
    return validate(data, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

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
        print(f"setting.yaml holds. ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
