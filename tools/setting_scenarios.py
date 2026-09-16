#!/usr/bin/env python3
"""Trigger scenarios.json's lazy, cached, per-adventure extraction (#418).

`docs/design/26-corpus-index.md` ("5. scenarios.json", "Build and maintenance") describes the
fifth corpus index as lazy and model-assisted: "an adventure gets its thematic record the first
time anything asks for it," cached by content hash and regenerated only when the record schema
changes. `engine/wyrd/corpus_pipeline.py` (#356) already implements that lazy/cached decision as
pure functions (`scenario_cache_status`, `documents_needing_scenario_generation`,
`build_scenario_index`) -- what has never existed is a way for a setting repo's own tooling to
actually call them. This script is that trigger, mirroring `tools/setting_build.py`'s existing
CLI convention exactly.

Like `generation_pipeline.py`'s `assemble_pacing`/`write_prose` (#423), this script never calls a
model itself -- "the engine decides freshness; it never performs the model call itself"
(26-corpus-index.md). Its `commit` verb takes a JSON file of already-produced scenario records (a
document id mapped to a record already extracted by whatever model call the caller made) as an
ordinary argument.

Two verbs:

    plan    -- report which documents (filtered by --path-prefix) are missing/stale/fresh in the
               setting's scenario cache, so a caller knows what still needs generating.
    commit  -- fold a caller-supplied records file into index/scenarios.json and
               index/scenario_build_cache.json, regenerating only what plan would have reported
               as not fresh. All-or-nothing: if any needed record is absent or fails schema
               validation, nothing is written for this run.

This script never reads `library/`, never fetches or embeds source material, and operates only on
a <setting-dir> the caller supplies -- CLAUDE.md's repository table. It reads a setting's own
`index/corpus_build_cache.json` (written by `tools/setting_build.py`) for the current
`(path, content-hash)` set, and never hardcodes any setting's own directory names -- the caller's
own `--path-prefix` selects which documents count as candidates for this setting.

Usage:
    python3 tools/setting_scenarios.py <setting-dir> plan [--path-prefix PREFIX]
    python3 tools/setting_scenarios.py <setting-dir> commit --records <file> [--path-prefix PREFIX]

Python 3.11+, standard library only (docs/design/27-tooling.md section 2).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO_ROOT / "engine"))

from check_bestiary import YamlError, read_yaml  # noqa: E402
from wyrd import corpus_pipeline, corpus_scenario  # noqa: E402

SCHEMA_VERSION = 1
CORPUS_CACHE_FILENAME = "corpus_build_cache.json"
SCENARIO_CACHE_FILENAME = "scenario_build_cache.json"
SCENARIOS_FILENAME = "scenarios.json"


def resolve_setting_id(setting_dir: Path) -> str:
    """The setting id stamped into every corpus index record: `setting.yaml`'s own `name:`
    field, falling back to the directory's basename -- the same resolution
    `tools/setting_build.py`'s `resolve_setting_id` already uses (#399), duplicated rather than
    imported to keep this script runnable standalone against a bare fixture directory."""
    setting_yaml = setting_dir / "setting.yaml"
    if setting_yaml.is_file():
        try:
            data = read_yaml(setting_yaml)
        except YamlError:
            data = None
        if isinstance(data, dict):
            name = data.get("name")
            if isinstance(name, str) and name:
                return name
    return setting_dir.name


def load_corpus_documents(setting_dir: Path, setting: str, path_prefix: str) -> list[dict]:
    """`{id, setting, content_hash}` for every path in the setting's own
    `index/corpus_build_cache.json` that starts with `path_prefix` (empty matches every path)."""
    cache_path = setting_dir / "index" / CORPUS_CACHE_FILENAME
    if not cache_path.is_file():
        return []
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    documents = data.get("documents", {})
    return [
        {"id": path, "setting": setting, "content_hash": content_hash}
        for path, content_hash in sorted(documents.items())
        if path.startswith(path_prefix)
    ]


def load_scenario_cache(setting_dir: Path) -> dict[tuple[str, str], dict]:
    """The on-disk `scenario_build_cache.json`, reshaped into the `(setting, id) -> entry` dict
    `corpus_pipeline.build_scenario_index`/`scenario_cache_status` expect. Absent file -> empty
    cache (every document reported `missing`)."""
    cache_path = setting_dir / "index" / SCENARIO_CACHE_FILENAME
    if not cache_path.is_file():
        return {}
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    cache: dict[tuple[str, str], dict] = {}
    for entry in data.get("entries", []):
        key = (entry["setting"], entry["id"])
        cache[key] = {
            "content_hash": entry["content_hash"],
            "schema_version": entry["schema_version"],
            "record": entry["record"],
        }
    return cache


def write_scenario_cache(setting_dir: Path, cache: dict[tuple[str, str], dict]) -> Path:
    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    path = index_dir / SCENARIO_CACHE_FILENAME
    entries = [
        {
            "setting": setting,
            "id": doc_id,
            "content_hash": entry["content_hash"],
            "schema_version": entry["schema_version"],
            "record": entry["record"],
        }
        for (setting, doc_id), entry in sorted(cache.items())
    ]
    path.write_text(json.dumps({"entries": entries}, indent=2, sort_keys=False) + "\n", "utf-8")
    return path


def write_scenarios_index(setting_dir: Path, records: list[dict]) -> Path:
    index_dir = setting_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    path = index_dir / SCENARIOS_FILENAME
    path.write_text(json.dumps(records, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return path


def run_plan(setting_dir: Path, path_prefix: str) -> dict:
    """Report each candidate document's scenario-cache status: `missing`, `stale`, or `fresh`
    (spec.md Acceptance Scenario 1, 4)."""
    setting = resolve_setting_id(setting_dir)
    documents = load_corpus_documents(setting_dir, setting, path_prefix)
    cache = load_scenario_cache(setting_dir)
    statuses = [
        {
            "id": doc["id"],
            "status": corpus_pipeline.scenario_cache_status(
                doc["id"], doc["setting"], doc["content_hash"], SCHEMA_VERSION, cache
            ),
        }
        for doc in documents
    ]
    return {"setting": setting, "documents": statuses}


class MissingRecordError(ValueError):
    """A document needing generation has no entry in the caller-supplied records file."""


def run_commit(setting_dir: Path, path_prefix: str, records_path: Path) -> dict:
    """Fold `records_path`'s already-produced scenario records into the setting's
    `scenarios.json`/`scenario_build_cache.json`, regenerating only what `plan` would report as
    not fresh (spec.md Acceptance Scenario 2, 3). All-or-nothing: raises, and writes nothing,
    when any needed document has no valid record in `records_path` (Acceptance Scenario 5, Edge
    Cases)."""
    setting = resolve_setting_id(setting_dir)
    documents = load_corpus_documents(setting_dir, setting, path_prefix)
    cache = load_scenario_cache(setting_dir)
    supplied = json.loads(records_path.read_text(encoding="utf-8"))

    def generate(doc: dict) -> dict:
        record = supplied.get(doc["id"])
        if record is None:
            raise MissingRecordError(f"no scenario record supplied for document {doc['id']!r}")
        return corpus_scenario.validate_scenario_record(record)

    records, updated_cache = corpus_pipeline.build_scenario_index(
        documents, cache, generate, SCHEMA_VERSION
    )

    write_scenarios_index(setting_dir, records)
    write_scenario_cache(setting_dir, updated_cache)

    return {"setting": setting, "documents": len(records)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("setting_dir", help="path to a setting repo (or fixture) with an index/")
    sub = parser.add_subparsers(dest="verb", required=True)

    plan_parser = sub.add_parser("plan", help="report each candidate document's cache status")
    plan_parser.add_argument("--path-prefix", default="")

    commit_parser = sub.add_parser("commit", help="fold supplied records into scenarios.json")
    commit_parser.add_argument("--path-prefix", default="")
    commit_parser.add_argument(
        "--records", required=True, help="JSON file: document id -> already-produced record"
    )

    args = parser.parse_args(argv)
    setting_dir = Path(args.setting_dir)
    if not setting_dir.is_dir():
        print(f"error: {setting_dir} is not a directory", file=sys.stderr)
        return 1

    try:
        if args.verb == "plan":
            result = run_plan(setting_dir, args.path_prefix)
        else:
            result = run_commit(setting_dir, args.path_prefix, Path(args.records))
    except (MissingRecordError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
